"""Pluggable model-registry adapters with explicit evidence boundaries.

Only :class:`SealedModelRegistry` can return a serving-eligible release. The
synthetic provider exists exclusively for deterministic software-contract tests
and must never be represented as model provenance or clinical evidence.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PureWindowsPath
from typing import Protocol

from src.core.manifest import (
    ModelArtifactVerificationError,
    ModelManifest,
    resolve_model_root,
    sha256_file,
    verify_model_manifest,
)


class RegistryKind(StrEnum):
    """Stable identifiers for supported registry adapters."""

    SEALED = "sealed_manifest_registry"
    SYNTHETIC_TEST = "synthetic_test_registry"


@dataclass(frozen=True, slots=True)
class RegistryRequest:
    """Immutable inputs required to resolve one exact model release."""

    model_name: str
    revision: str | None
    local_files_only: bool
    manifest_path: str
    manifest_sha256: str | None
    model_source_id: str
    expected_labels: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RegistryResolution:
    """Resolved release and its trust/evidence classification."""

    kind: RegistryKind
    model_root: Path | None
    manifest_path: Path | None
    manifest: ModelManifest | None
    manifest_sha256: str | None
    artifact_verified: bool
    independent_trust_anchor: bool
    serving_permitted: bool
    evidence_scope: str


class ModelRegistry(Protocol):
    """Interface implemented by model-release providers."""

    def resolve(self, request: RegistryRequest) -> RegistryResolution:
        """Resolve one release or raise a fail-closed verification error."""
        ...


class SealedModelRegistry:
    """Resolve and verify a manifest-sealed local or immutable snapshot release."""

    def resolve(self, request: RegistryRequest) -> RegistryResolution:
        model_root = resolve_model_root(
            request.model_name,
            revision=request.revision,
            local_files_only=request.local_files_only,
        )
        manifest_path = (
            Path(request.manifest_path)
            if request.manifest_path.strip()
            else model_root / "model_manifest.json"
        )
        configured_path = Path(request.model_name)
        is_local_path = (
            configured_path.is_absolute()
            or PureWindowsPath(request.model_name).is_absolute()
            or configured_path.exists()
        )
        expected_model_id = request.model_source_id.strip()
        if not expected_model_id and not is_local_path:
            expected_model_id = request.model_name

        manifest = verify_model_manifest(
            model_root=model_root,
            manifest_path=manifest_path,
            expected_manifest_sha256=request.manifest_sha256,
            expected_model_id=expected_model_id,
            expected_revision=request.revision,
            expected_labels=list(request.expected_labels),
        )
        actual_manifest_digest = sha256_file(manifest_path.resolve())
        return RegistryResolution(
            kind=RegistryKind.SEALED,
            model_root=model_root,
            manifest_path=manifest_path.resolve(),
            manifest=manifest,
            manifest_sha256=actual_manifest_digest,
            artifact_verified=True,
            independent_trust_anchor=request.manifest_sha256 is not None,
            serving_permitted=True,
            evidence_scope="SOFTWARE_ARTIFACT_INTEGRITY_ONLY",
        )


class SyntheticTestRegistry:
    """Deterministic simulation provider that is forbidden outside test mode."""

    def __init__(self, *, environment: str, seed: str = "malaria-cv-api") -> None:
        if environment != "test":
            raise ModelArtifactVerificationError(
                "Synthetic registry is permitted only in the test environment."
            )
        self._seed = seed.encode("utf-8")

    def resolve(self, request: RegistryRequest) -> RegistryResolution:
        del request
        return RegistryResolution(
            kind=RegistryKind.SYNTHETIC_TEST,
            model_root=None,
            manifest_path=None,
            manifest=None,
            manifest_sha256=None,
            artifact_verified=False,
            independent_trust_anchor=False,
            serving_permitted=False,
            evidence_scope="SIMULATION_ONLY_NOT_MODEL_OR_CLINICAL_EVIDENCE",
        )

    def deterministic_score(self, payload: bytes) -> float:
        """Return a stable test score; this is not ML inference."""
        digest = hashlib.sha256(self._seed + payload).digest()
        integer = int.from_bytes(digest[:8], byteorder="big", signed=False)
        return integer / ((1 << 64) - 1)
