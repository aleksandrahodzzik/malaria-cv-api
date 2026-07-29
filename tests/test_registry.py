"""Pluggable registry and evidence-boundary tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.manifest import ModelArtifactVerificationError, sha256_file
from src.services.registry import (
    RegistryKind,
    RegistryRequest,
    SealedModelRegistry,
    SyntheticTestRegistry,
)

REVISION = "c" * 40


def _release(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "sealed"
    root.mkdir()
    for name, payload in {
        "config.json": b'{"model_type":"vit"}',
        "preprocessor_config.json": b'{"size":224}',
        "model.safetensors": b"test-only-safe-tensor-payload",
    }.items():
        (root / name).write_bytes(payload)
    manifest_path = root / "model_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
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
                    "name": "Test-only license assertion",
                    "spdx_id": "LicenseRef-Test-Only",
                    "source_url": "https://example.invalid/test-license",
                    "commercial_use": "prohibited",
                },
            }
        ),
        encoding="utf-8",
    )
    return root, manifest_path


def _request(
    root: Path,
    manifest: Path,
    *,
    trust_anchor: bool = True,
) -> RegistryRequest:
    return RegistryRequest(
        model_name=str(root),
        revision=REVISION,
        local_files_only=True,
        manifest_path=str(manifest),
        manifest_sha256=sha256_file(manifest) if trust_anchor else None,
        model_source_id="approved/malaria",
        expected_labels=("Parasitized", "Uninfected"),
    )


def test_sealed_registry_returns_verified_serving_release(tmp_path: Path) -> None:
    root, manifest = _release(tmp_path)
    release = SealedModelRegistry().resolve(_request(root, manifest))

    assert release.kind is RegistryKind.SEALED
    assert release.model_root == root.resolve()
    assert release.manifest_path == manifest.resolve()
    assert release.manifest is not None
    assert release.manifest.revision == REVISION
    assert release.manifest_sha256 == sha256_file(manifest)
    assert release.artifact_verified is True
    assert release.independent_trust_anchor is True
    assert release.serving_permitted is True
    assert release.evidence_scope == "SOFTWARE_ARTIFACT_INTEGRITY_ONLY"


def test_sealed_registry_discloses_missing_independent_anchor(
    tmp_path: Path,
) -> None:
    root, manifest = _release(tmp_path)
    release = SealedModelRegistry().resolve(
        _request(root, manifest, trust_anchor=False)
    )
    assert release.artifact_verified is True
    assert release.independent_trust_anchor is False


def test_sealed_registry_uses_remote_identifier_as_expected_model_id(
    tmp_path: Path,
) -> None:
    root, manifest = _release(tmp_path)
    request = RegistryRequest(
        model_name="approved/malaria",
        revision=REVISION,
        local_files_only=True,
        manifest_path=str(manifest),
        manifest_sha256=sha256_file(manifest),
        model_source_id="",
        expected_labels=("Parasitized", "Uninfected"),
    )
    with patch("src.services.registry.resolve_model_root", return_value=root.resolve()):
        release = SealedModelRegistry().resolve(request)
    assert release.manifest is not None
    assert release.manifest.model_id == "approved/malaria"


def test_sealed_registry_rejects_tampering(tmp_path: Path) -> None:
    root, manifest = _release(tmp_path)
    request = _request(root, manifest)
    (root / "model.safetensors").write_bytes(b"tampered")
    with pytest.raises(ModelArtifactVerificationError, match="SHA-256"):
        SealedModelRegistry().resolve(request)


def test_synthetic_registry_is_test_only_and_never_serving_eligible() -> None:
    with pytest.raises(ModelArtifactVerificationError, match="test environment"):
        SyntheticTestRegistry(environment="production")

    registry = SyntheticTestRegistry(environment="test", seed="locked-seed")
    release = registry.resolve(
        RegistryRequest(
            model_name="synthetic",
            revision=None,
            local_files_only=True,
            manifest_path="",
            manifest_sha256=None,
            model_source_id="",
            expected_labels=("Parasitized", "Uninfected"),
        )
    )
    assert release.kind is RegistryKind.SYNTHETIC_TEST
    assert release.model_root is None
    assert release.manifest is None
    assert release.artifact_verified is False
    assert release.serving_permitted is False
    assert release.evidence_scope == "SIMULATION_ONLY_NOT_MODEL_OR_CLINICAL_EVIDENCE"


def test_synthetic_scores_are_bounded_deterministic_and_payload_specific() -> None:
    registry = SyntheticTestRegistry(environment="test", seed="locked-seed")
    first = registry.deterministic_score(b"cell-a")
    assert first == registry.deterministic_score(b"cell-a")
    assert first != registry.deterministic_score(b"cell-b")
    assert 0.0 <= first <= 1.0
