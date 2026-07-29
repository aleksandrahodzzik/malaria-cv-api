"""Model manifest trust and artifact-integrity tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.manifest import (
    ModelArtifactVerificationError,
    resolve_model_root,
    sha256_file,
    verify_model_manifest,
)

REVISION = "a" * 40


def _write_release(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "model"
    root.mkdir(parents=True)
    for name, contents in {
        "config.json": b'{"model_type":"vit"}',
        "preprocessor_config.json": b'{"size":224}',
        "model.safetensors": b"safe-model-weights",
    }.items():
        (root / name).write_bytes(contents)
    manifest = {
        "schema_version": "1.0",
        "model_id": "approved/malaria",
        "revision": REVISION,
        "artifacts": {
            name: sha256_file(root / name)
            for name in (
                "config.json",
                "preprocessor_config.json",
                "model.safetensors",
            )
        },
        "id2label": {"0": "Parasitized", "1": "Uninfected"},
        "input_resolution": [224, 224],
        "processor_type": "ViTImageProcessor",
        "license": {
            "name": "Approved research license",
            "spdx_id": "LicenseRef-Approved",
            "source_url": "https://example.invalid/license",
            "commercial_use": "unknown",
        },
    }
    manifest_path = root / "model_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return root, manifest_path


def _verify(root: Path, manifest_path: Path, **overrides: object) -> object:
    arguments: dict[str, object] = {
        "model_root": root,
        "manifest_path": manifest_path,
        "expected_manifest_sha256": (
            sha256_file(manifest_path) if manifest_path.is_file() else None
        ),
        "expected_model_id": "approved/malaria",
        "expected_revision": REVISION,
        "expected_labels": ["Parasitized", "Uninfected"],
    }
    arguments.update(overrides)
    return verify_model_manifest(**arguments)  # type: ignore[arg-type]


def test_valid_manifest_verifies_all_artifacts(tmp_path: Path) -> None:
    root, manifest_path = _write_release(tmp_path)
    manifest = _verify(root, manifest_path)
    assert manifest.model_id == "approved/malaria"
    assert manifest.input_resolution == (224, 224)


def test_sha256_file_streams_stable_digest(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"abc")
    assert sha256_file(artifact, chunk_size=1) == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data.update(model_id="wrong/model"), "model_id"),
        (lambda data: data.update(revision="b" * 40), "revision"),
        (
            lambda data: data.update(id2label={"0": "Uninfected", "1": "Parasitized"}),
            "label mapping",
        ),
        (
            lambda data: data.update(id2label={"0": "Parasitized", "2": "Uninfected"}),
            "contiguous",
        ),
        (lambda data: data.update(input_resolution=[0, 224]), "resolution"),
    ],
)
def test_manifest_contract_mismatches(
    tmp_path: Path,
    mutation: object,
    message: str,
) -> None:
    root, manifest_path = _write_release(tmp_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert callable(mutation)
    mutation(data)
    manifest_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ModelArtifactVerificationError, match=message):
        _verify(
            root,
            manifest_path,
            expected_manifest_sha256=sha256_file(manifest_path),
        )


@pytest.mark.parametrize(
    ("remove_name", "message"),
    [
        ("config.json", "config.json"),
        ("preprocessor_config.json", "preprocessor_config"),
        ("model.safetensors", "safetensors"),
    ],
)
def test_manifest_requires_serving_artifacts(
    tmp_path: Path,
    remove_name: str,
    message: str,
) -> None:
    root, manifest_path = _write_release(tmp_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    del data["artifacts"][remove_name]
    manifest_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ModelArtifactVerificationError, match=message):
        _verify(
            root,
            manifest_path,
            expected_manifest_sha256=sha256_file(manifest_path),
        )


def test_manifest_rejects_trust_anchor_and_artifact_tampering(tmp_path: Path) -> None:
    root, manifest_path = _write_release(tmp_path)
    with pytest.raises(ModelArtifactVerificationError, match="trust anchor"):
        _verify(root, manifest_path, expected_manifest_sha256="0" * 64)

    (root / "model.safetensors").write_bytes(b"tampered")
    with pytest.raises(ModelArtifactVerificationError, match="SHA-256"):
        _verify(root, manifest_path)


def test_manifest_rejects_undeclared_loadable_weights(tmp_path: Path) -> None:
    root, manifest_path = _write_release(tmp_path)
    (root / "unapproved.safetensors").write_bytes(b"undeclared")
    with pytest.raises(ModelArtifactVerificationError, match="undeclared"):
        _verify(root, manifest_path)


def test_manifest_rejects_missing_invalid_and_unsafe_files(tmp_path: Path) -> None:
    root, manifest_path = _write_release(tmp_path)
    with pytest.raises(ModelArtifactVerificationError, match="missing"):
        _verify(root, root / "missing.json", expected_manifest_sha256=None)

    manifest_path.write_text("{", encoding="utf-8")
    with pytest.raises(ModelArtifactVerificationError, match="invalid"):
        _verify(root, manifest_path, expected_manifest_sha256=None)

    root, manifest_path = _write_release(tmp_path / "second")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["artifacts"]["../escape.safetensors"] = "0" * 64
    manifest_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ModelArtifactVerificationError, match="unsafe"):
        _verify(
            root,
            manifest_path,
            expected_manifest_sha256=sha256_file(manifest_path),
        )


def test_manifest_rejects_invalid_configured_digest(tmp_path: Path) -> None:
    root, manifest_path = _write_release(tmp_path)
    with pytest.raises(ModelArtifactVerificationError, match="Configured"):
        _verify(root, manifest_path, expected_manifest_sha256="not-a-digest")


def test_manifest_can_skip_model_id_and_revision_comparison(tmp_path: Path) -> None:
    root, manifest_path = _write_release(tmp_path)
    manifest = _verify(
        root,
        manifest_path,
        expected_model_id="",
        expected_revision=None,
    )
    assert manifest.revision == REVISION


def test_resolve_local_remote_and_failure_paths(tmp_path: Path) -> None:
    root, _ = _write_release(tmp_path)
    assert resolve_model_root(
        str(root),
        revision=None,
        local_files_only=True,
    ) == root.resolve()

    with pytest.raises(ModelArtifactVerificationError, match="does not exist"):
        resolve_model_root(
            str(tmp_path / "missing"),
            revision=None,
            local_files_only=True,
        )

    with pytest.raises(ModelArtifactVerificationError, match="exact commit"):
        resolve_model_root(
            "approved/model",
            revision="main",
            local_files_only=False,
        )

    with patch(
        "src.core.manifest.snapshot_download",
        return_value=str(root),
    ) as downloader:
        assert resolve_model_root(
            "approved/model",
            revision=REVISION,
            local_files_only=True,
        ) == root.resolve()
    downloader.assert_called_once_with(
        repo_id="approved/model",
        revision=REVISION,
        local_files_only=True,
    )

    with (
        patch("src.core.manifest.snapshot_download", side_effect=OSError("offline")),
        pytest.raises(ModelArtifactVerificationError, match="could not be resolved"),
    ):
        resolve_model_root(
            "approved/model",
            revision=REVISION,
            local_files_only=True,
        )
