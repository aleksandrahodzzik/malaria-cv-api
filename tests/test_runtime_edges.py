"""Failure-path tests for runtime configuration, lifespan and inference."""

from __future__ import annotations

import asyncio
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import torch
from fastapi import FastAPI
from PIL import Image
from pydantic import SecretStr, ValidationError

from src.core.config import Settings
from src.core.manifest import ModelArtifactVerificationError
from src.main import create_application, lifespan
from src.schemas.payload import ClassProbability
from src.services.inference import MalariaClassifierService
from src.services.qc import QCMetrics, QCResult
from src.services.registry import RegistryKind, RegistryResolution


@pytest.fixture
def sample_image_bytes() -> bytes:
    image = Image.new("RGB", (64, 64), color=(200, 100, 160))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"MODEL_EXPECTED_LABELS": ["A", "A"]}, "unique"),
        ({"MODEL_EXPECTED_LABELS": ["A", " "]}, "blank"),
        ({"API_KEY_REQUIRED": True}, "at least one"),
        (
            {"API_KEY_REQUIRED": True, "API_KEYS": [SecretStr(" ")]},
            "blank values",
        ),
        (
            {
                "API_KEY_REQUIRED": True,
                "API_KEYS": [SecretStr("same"), SecretStr("same")],
            },
            "unique",
        ),
        ({"SLIDE_MIN_CELLS": 11, "SLIDE_MAX_CELLS": 10}, "SLIDE_MIN"),
        ({"QC_MIN_WIDTH": 100, "QC_MAX_WIDTH": 99}, "QC_MIN_WIDTH"),
        ({"QC_MIN_HEIGHT": 100, "QC_MAX_HEIGHT": 99}, "QC_MIN_HEIGHT"),
        ({"MODEL_MANIFEST_SHA256": "bad"}, "64 hexadecimal"),
        ({"METRICS_ENABLED": True}, "requires METRICS_API_KEY"),
        ({"METRICS_API_KEY": SecretStr("short")}, "at least 32"),
        (
            {"ENVIRONMENT": "production"},
            "API_KEY_REQUIRED=true",
        ),
        (
            {
                "ENVIRONMENT": "production",
                "DEBUG": True,
                "API_KEY_REQUIRED": True,
                "API_KEYS": [SecretStr("p" * 32)],
            },
            "DEBUG",
        ),
        (
            {
                "ENVIRONMENT": "production",
                "API_KEY_REQUIRED": True,
                "API_KEYS": [SecretStr("too-short")],
            },
            "at least 32",
        ),
        (
            {
                "ENVIRONMENT": "production",
                "API_KEY_REQUIRED": True,
                "API_KEYS": [SecretStr("p" * 32)],
                "RATE_LIMIT_ENABLED": False,
            },
            "rate limiting",
        ),
        (
            {
                "ENVIRONMENT": "production",
                "API_KEY_REQUIRED": True,
                "API_KEYS": [SecretStr("p" * 32)],
                "MODEL_NAME": "C:\\model",
                "MODEL_SOURCE_ID": "approved/model",
                "MODEL_REVISION": "a" * 40,
                "MODEL_MANIFEST_SHA256": None,
            },
            "trust anchor",
        ),
        (
            {
                "ENVIRONMENT": "production",
                "API_KEY_REQUIRED": True,
                "API_KEYS": [SecretStr("p" * 32)],
                "MODEL_NAME": "C:\\model",
                "MODEL_REVISION": "a" * 40,
                "MODEL_MANIFEST_SHA256": "0" * 64,
            },
            "MODEL_SOURCE_ID",
        ),
        (
            {
                "ENVIRONMENT": "production",
                "API_KEY_REQUIRED": True,
                "API_KEYS": [SecretStr("p" * 32)],
                "MODEL_NAME": "C:\\model",
                "MODEL_REVISION": "a" * 40,
                "MODEL_REQUIRE_MANIFEST": False,
            },
            "cannot disable",
        ),
    ],
)
def test_settings_invariants(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        Settings(**kwargs)


def test_api_key_settings_accept_secret_values() -> None:
    configured = Settings(
        API_KEY_REQUIRED=True,
        API_KEYS=[SecretStr("secret")],
    )
    assert configured.API_KEYS[0].get_secret_value() == "secret"


def test_blank_optional_metrics_key_is_treated_as_unset() -> None:
    configured = Settings(METRICS_API_KEY="")
    assert configured.METRICS_API_KEY is None


class FakeClassifier:
    def __init__(self, failure: Exception | None = None) -> None:
        self.failure = failure
        self.loaded = False

    def load_model(self) -> None:
        if self.failure is not None:
            raise self.failure
        self.loaded = True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("failure", "expected_code"),
    [
        (None, None),
        (
            ModelArtifactVerificationError("unverified"),
            "MODEL_ARTIFACT_NOT_VERIFIED",
        ),
        (RuntimeError("loader failure"), "MODEL_INITIALIZATION_FAILED"),
    ],
)
async def test_lifespan_model_states(
    failure: Exception | None,
    expected_code: str | None,
) -> None:
    application = FastAPI()
    fake = FakeClassifier(failure)
    with (
        patch("src.main.settings.MODEL_NAME", "approved/model"),
        patch("src.main.MalariaClassifierService", return_value=fake),
    ):
        async with lifespan(application):
            assert application.state.model_error_code == expected_code
            if failure is None:
                assert application.state.classifier_service is fake
            else:
                assert application.state.classifier_service is None
    assert application.state.classifier_service is None
    assert application.state.model_error_code == "SERVICE_STOPPED"


def test_application_factory_builds_cors_profile() -> None:
    with patch("src.main.settings.CORS_ORIGINS", ["https://lab.example"]):
        application = create_application()
    assert any(
        middleware.cls.__name__ == "CORSMiddleware"
        for middleware in application.user_middleware
    )


def test_load_model_propagates_trust_failure_and_wraps_loader_failure() -> None:
    service = MalariaClassifierService("approved/model")
    failure = ModelArtifactVerificationError("not verified")
    with (
        patch(
            "src.services.inference.SealedModelRegistry.resolve",
            side_effect=failure,
        ),
        pytest.raises(ModelArtifactVerificationError),
    ):
        service.load_model()
    assert service.is_ready() is False

    with (
        patch(
            "src.services.inference.resolve_model_root",
            return_value=Path("C:\\approved"),
        ),
        patch("src.services.inference.settings.MODEL_REQUIRE_MANIFEST", False),
        patch(
            "src.services.inference.AutoImageProcessor.from_pretrained",
            side_effect=OSError("loader"),
        ),
        pytest.raises(RuntimeError, match="initialization"),
    ):
        service.load_model()
    assert service.is_ready() is False


def test_load_model_rejects_non_serving_registry_resolution() -> None:
    service = MalariaClassifierService("synthetic")
    resolution = RegistryResolution(
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
    with (
        patch(
            "src.services.inference.SealedModelRegistry.resolve",
            return_value=resolution,
        ),
        pytest.raises(ModelArtifactVerificationError, match="not eligible"),
    ):
        service.load_model()
    assert service.is_ready() is False


def test_processor_contract_variants() -> None:
    service = MalariaClassifierService("approved")
    service._manifest = MagicMock(input_resolution=(224, 224))

    service.processor = MagicMock()
    service.processor.size = {"shortest_edge": 224}
    service._validate_processor_contract()

    service._manifest = None
    service._validate_processor_contract()
    service._manifest = MagicMock(input_resolution=(224, 224))

    for size, message in [
        (None, "does not expose"),
        ({"longest_edge": 224}, "unsupported"),
        ({"height": 128, "width": 128}, "does not match"),
    ]:
        service.processor = MagicMock()
        service.processor.size = size
        with pytest.raises(RuntimeError, match=message):
            service._validate_processor_contract()


@pytest.mark.parametrize(
    ("mapping", "num_labels", "message"),
    [
        ({}, 0, "does not define"),
        ({"not-an-int": "Parasitized"}, 1, "must be integers"),
        ({0: "Parasitized", 2: "Uninfected"}, 2, "contiguous"),
        ({0: "Parasitized", 1: "Uninfected"}, 3, "num_labels"),
    ],
)
def test_model_contract_failure_variants(
    mapping: dict[object, str],
    num_labels: int,
    message: str,
) -> None:
    service = MalariaClassifierService("approved")
    service.model = SimpleNamespace(
        config=SimpleNamespace(id2label=mapping, num_labels=num_labels)
    )
    with pytest.raises(RuntimeError, match=message):
        service._validate_model_contract()


def _ready_service_with_logits(logits: torch.Tensor) -> MalariaClassifierService:
    service = MalariaClassifierService("approved")
    service.processor = MagicMock(return_value={"pixel_values": torch.ones(1, 3, 2, 2)})
    service.model = MagicMock(return_value=MagicMock(logits=logits))
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True
    return service


def test_predict_requires_ready_service_and_valid_logits(
    sample_image_bytes: bytes,
) -> None:
    with pytest.raises(RuntimeError, match="not initialized"):
        MalariaClassifierService("approved")._predict_sync(sample_image_bytes)

    for logits, message in [
        (torch.tensor([1.0, 2.0]), "shape"),
        (torch.tensor([[1.0, 2.0, 3.0]]), "logits count"),
    ]:
        service = _ready_service_with_logits(logits)
        with (
            patch("src.services.inference.settings.QC_ENABLED", False),
            pytest.raises(RuntimeError, match=message),
        ):
            service._predict_sync(sample_image_bytes, "image/png")


@pytest.mark.asyncio
async def test_analyze_image_attaches_qc_summary() -> None:
    service = MalariaClassifierService("approved")
    qc_result = QCResult(
        passed=True,
        metrics=QCMetrics(64, 64, 1.0, 20.0, 100.0, 0.5),
    )
    prediction = {
        "predicted_cell_class": "Parasitized",
        "confidence": 0.9,
        "probabilities": [
            ClassProbability(label="Parasitized", confidence=0.9),
            ClassProbability(label="Uninfected", confidence=0.1),
        ],
        "quality_control": qc_result,
    }
    with patch.object(service, "_predict_sync", return_value=prediction):
        response = await service.analyze_image(b"image", "cell.png", "image/png")
    assert response.quality_control is not None
    assert response.quality_control.metrics["laplacian_variance"] == 100.0


@pytest.mark.asyncio
async def test_background_release_handles_cancelled_task() -> None:
    service = MalariaClassifierService("approved")

    async def pending() -> dict[str, object]:
        await asyncio.sleep(10)
        return {}

    task = asyncio.create_task(pending())
    service._background_inference_tasks.add(task)  # type: ignore[arg-type]
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    service._release_background_inference(task)  # type: ignore[arg-type]
    assert task not in service._background_inference_tasks
