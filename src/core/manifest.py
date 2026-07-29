"""Fail-closed model artifact provenance and integrity verification."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Annotated, Any, Literal

from huggingface_hub import snapshot_download
from pydantic import BaseModel, ConfigDict, Field, ValidationError

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ModelArtifactVerificationError(RuntimeError):
    """Raised when an artifact cannot satisfy the local trust policy."""

    code = "MODEL_ARTIFACT_NOT_VERIFIED"


class LicenseMetadata(BaseModel):
    """Machine-readable license assertion approved by the model owner."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    spdx_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    commercial_use: Literal["allowed", "prohibited", "unknown"]


class ModelManifest(BaseModel):
    """Validated local trust document for one immutable model release."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"]
    model_id: str = Field(min_length=1)
    revision: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    artifacts: dict[str, Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]]
    id2label: dict[int, str] = Field(min_length=2)
    input_resolution: tuple[int, int]
    processor_type: str = Field(min_length=1)
    license: LicenseMetadata


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Return a streaming SHA-256 digest without loading the file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        while chunk := artifact.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_model_root(
    model_name: str,
    *,
    revision: str | None,
    local_files_only: bool,
) -> Path:
    """Resolve a local directory or an immutable Hugging Face snapshot."""
    configured_path = Path(model_name)
    if configured_path.is_absolute() or configured_path.exists():
        if not configured_path.is_dir():
            raise ModelArtifactVerificationError(
                "Configured local model directory does not exist."
            )
        return configured_path.resolve()

    if revision is None or not _REVISION_PATTERN.fullmatch(revision.lower()):
        raise ModelArtifactVerificationError(
            "Remote model resolution requires an exact commit revision."
        )

    try:
        snapshot_path = snapshot_download(
            repo_id=model_name,
            revision=revision,
            local_files_only=local_files_only,
        )
    except Exception as exc:
        raise ModelArtifactVerificationError(
            "Immutable model snapshot could not be resolved."
        ) from exc
    return Path(snapshot_path).resolve()


def _load_manifest(path: Path) -> ModelManifest:
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
        return ModelManifest.model_validate(raw)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise ModelArtifactVerificationError(
            "Model manifest is missing, unreadable, or invalid."
        ) from exc


def verify_model_manifest(
    *,
    model_root: Path,
    manifest_path: Path,
    expected_manifest_sha256: str | None,
    expected_model_id: str,
    expected_revision: str | None,
    expected_labels: list[str],
) -> ModelManifest:
    """Verify the trust document and every declared artifact before model loading."""
    root = model_root.resolve()
    manifest_file = manifest_path.resolve()
    if not manifest_file.is_file():
        raise ModelArtifactVerificationError("Model manifest file is missing.")

    if expected_manifest_sha256 is not None:
        expected_digest = expected_manifest_sha256.lower()
        if not _SHA256_PATTERN.fullmatch(expected_digest):
            raise ModelArtifactVerificationError(
                "Configured manifest SHA-256 is invalid."
            )
        if sha256_file(manifest_file) != expected_digest:
            raise ModelArtifactVerificationError(
                "Model manifest SHA-256 does not match the trust anchor."
            )

    manifest = _load_manifest(manifest_file)
    if expected_model_id and manifest.model_id != expected_model_id:
        raise ModelArtifactVerificationError("Manifest model_id mismatch.")
    if expected_revision is not None and manifest.revision != expected_revision.lower():
        raise ModelArtifactVerificationError("Manifest revision mismatch.")

    actual_labels = [
        manifest.id2label[index] for index in sorted(manifest.id2label)
    ]
    if set(manifest.id2label) != set(range(len(manifest.id2label))):
        raise ModelArtifactVerificationError(
            "Manifest label indices must be contiguous from zero."
        )
    if actual_labels != expected_labels:
        raise ModelArtifactVerificationError("Manifest label mapping mismatch.")
    if min(manifest.input_resolution) <= 0:
        raise ModelArtifactVerificationError(
            "Manifest input resolution must be positive."
        )

    artifact_names = set(manifest.artifacts)
    if "config.json" not in artifact_names:
        raise ModelArtifactVerificationError("Manifest must include config.json.")
    if "preprocessor_config.json" not in artifact_names:
        raise ModelArtifactVerificationError(
            "Manifest must include preprocessor_config.json."
        )
    if not any(name.endswith(".safetensors") for name in artifact_names):
        raise ModelArtifactVerificationError(
            "Manifest must include at least one safetensors artifact."
        )
    loadable_artifacts = {
        artifact.relative_to(root).as_posix()
        for artifact in root.rglob("*.safetensors")
    }
    index_file = root / "model.safetensors.index.json"
    if index_file.is_file():
        loadable_artifacts.add("model.safetensors.index.json")
    undeclared_loadable = loadable_artifacts - artifact_names
    if undeclared_loadable:
        raise ModelArtifactVerificationError(
            "Model directory contains an undeclared loadable weight artifact."
        )

    for relative_name, expected_digest in manifest.artifacts.items():
        relative_path = Path(relative_name)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ModelArtifactVerificationError(
                "Manifest contains an unsafe artifact path."
            )
        artifact = (root / relative_path).resolve()
        if not artifact.is_relative_to(root) or not artifact.is_file():
            raise ModelArtifactVerificationError(
                "A declared model artifact is missing or outside the model root."
            )
        if sha256_file(artifact) != expected_digest:
            raise ModelArtifactVerificationError(
                "A declared model artifact failed SHA-256 verification."
            )

    return manifest
