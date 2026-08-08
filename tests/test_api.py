"""API, security and inference-contract tests for the research service."""

import asyncio
import io
import json
import re
import threading
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import torch
from PIL import Image
from pydantic import SecretStr, ValidationError
from starlette.testclient import TestClient

from src.core.config import Settings, settings
from src.core.manifest import ModelManifest
from src.core.middleware import RequestBodyLimitMiddleware
from src.main import app
from src.schemas.payload import ClassProbability, PredictionResponse
from src.services.inference import (
    InferenceCapacityError,
    InferenceTimeoutError,
    MalariaClassifierService,
)
from src.services.qc import QCMetrics, QCReason, QualityControlError
from src.services.registry import RegistryKind, RegistryResolution


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Initialize TestClient without downloading model weights."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_classifier_service() -> MagicMock:
    """Provide a ready classifier with deterministic research-only output."""
    mock_service = MagicMock(spec=MalariaClassifierService)
    mock_service.is_ready.return_value = True

    async def async_analyze(
        image_bytes: bytes,
        filename: str,
        declared_content_type: str | None = None,
    ) -> PredictionResponse:
        assert image_bytes
        assert declared_content_type in {
            "image/jpeg",
            "image/png",
            "image/webp",
        }
        return PredictionResponse(
            filename=filename,
            predicted_cell_class="Parasitized",
            diagnosis="Parasitized",
            confidence=0.985,
            probabilities=[
                ClassProbability(label="Parasitized", confidence=0.985),
                ClassProbability(label="Uninfected", confidence=0.015),
            ],
            execution_time_ms=25.4,
        )

    mock_service.analyze_image.side_effect = async_analyze
    return mock_service


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Generate a valid PNG image byte buffer."""
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_research_ui_and_static_assets(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Исследовательский прототип" in response.text
    assert response.headers["Content-Security-Policy"].startswith("default-src 'self'")
    assert response.headers["X-Frame-Options"] == "DENY"

    script = client.get("/assets/app.js")
    stylesheet = client.get("/assets/styles.css")
    cell_crew = client.get("/assets/cell-crew.webp")
    assert script.status_code == 200
    assert stylesheet.status_code == 200
    assert cell_crew.status_code == 200
    assert cell_crew.headers["content-type"] == "image/webp"
    assert len(cell_crew.content) < 250_000
    assert 'src="/assets/cell-crew.webp"' in response.text
    assert "innerHTML" not in script.text
    assert "style.width" not in script.text
    assert 'document.createElement("progress")' in script.text
    assert "elements.fileInput.disabled = loading" in script.text
    assert 'elements.dropZone.setAttribute("aria-disabled"' in script.text
    assert "scopeAccepted" in script.text
    assert "resetScopeConfirmation" in script.text
    assert "/api/v1/methodology" in script.text
    assert "Изображение отклонено QC" in script.text
    assert "Превышена квота запросов" in script.text
    assert "MODEL_ARTIFACT_NOT_VERIFIED" in script.text


def test_health_check_and_tracking_headers(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.5.0"
    assert "timestamp" in data
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        response.headers["X-Request-ID"],
    )
    assert "X-Response-Time-Ms" in response.headers
    assert response.headers["X-Service-Version"] == "1.5.0"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"


def test_valid_client_request_id_is_preserved(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "client-request_42"})
    assert response.headers["X-Request-ID"] == "client-request_42"


def test_unsafe_client_request_id_is_replaced(client: TestClient) -> None:
    unsafe = "x" * 100
    response = client.get("/health", headers={"X-Request-ID": unsafe})
    assert response.headers["X-Request-ID"] != unsafe
    assert len(response.headers["X-Request-ID"]) == 36


def test_capabilities_are_explicitly_research_only(client: TestClient) -> None:
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["intended_use"] == "research_only"
    assert data["task"] == "pre_cropped_single_cell_classification"
    assert data["analysis_level"] == "cell"
    assert data["probabilities_calibrated"] is False
    assert data["patient_diagnosis_supported"] is False
    assert data["slide_aggregation_supported"] is True
    assert data["research_parasitemia_summary_supported"] is True
    assert data["parasitemia_supported"] is False
    assert data["human_review_required"] is True
    assert data["model_configured"] is False
    assert data["api_key_required"] is settings.API_KEY_REQUIRED
    assert data["max_upload_size_mb"] == settings.MAX_UPLOAD_SIZE_MB
    assert data["accepted_content_types"] == settings.ALLOWED_CONTENT_TYPES


def test_methodology_separates_pipeline_levels(client: TestClient) -> None:
    response = client.get("/api/v1/methodology")
    assert response.status_code == 200
    data = response.json()
    assert data["intended_task"] == "pre_cropped_single_cell_classification"
    assert data["deployment_scope"] == "research_demonstration"
    assert data["supported_task_codes"] == ["A", "F"]
    assert data["unsupported_task_codes"] == ["B", "C", "D", "E"]
    assert data["clinical_action_supported"] is False
    assert data["human_review_required"] is True

    stages = {item["stage"]: item["status"] for item in data["pipeline"]}
    assert stages["input_image"] == "implemented"
    assert stages["image_quality_control"] == "partial"
    assert stages["cell_detection_or_segmentation"] == "missing"
    assert stages["cell_classification"] == "unvalidated"
    assert stages["slide_level_aggregation"] == "partial"
    assert stages["patient_level_interpretation"] == "missing"
    assert stages["clinical_action"] == "missing"


def test_openapi_documents_safe_contract(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    analyze = schema["paths"]["/api/v1/analyze"]["post"]
    assert {"400", "413", "415", "422", "500", "503", "504"} <= set(
        analyze["responses"]
    )

    prediction = schema["components"]["schemas"]["PredictionResponse"]["properties"]
    assert "predicted_cell_class" in prediction
    assert prediction["diagnosis"]["deprecated"] is True
    assert prediction["calibrated"]["const"] is False
    assert prediction["analysis_level"]["const"] == "cell"
    assert prediction["human_review_required"]["const"] is True
    assert prediction["patient_diagnosis_supported"]["const"] is False
    assert "/api/v1/methodology" in schema["paths"]
    assert "/api/v1/analyze/slide" in schema["paths"]

    error = schema["components"]["schemas"]["ErrorResponse"]
    assert {"code", "detail"} <= set(error["required"])
    assert "/analyze" not in schema["paths"]
    assert "/ready" not in schema["paths"]
    assert "/capabilities" not in schema["paths"]


def test_framework_404_uses_stable_error_envelope(client: TestClient) -> None:
    response = client.get("/path-that-does-not-exist")
    assert response.status_code == 404
    assert response.json() == {
        "code": "NOT_FOUND",
        "detail": "Not Found",
        "request_id": response.headers["X-Request-ID"],
    }


def test_settings_reject_wildcard_cors() -> None:
    with pytest.raises(ValidationError, match="Wildcard CORS"):
        Settings(CORS_ORIGINS=["*"])


def test_production_remote_model_requires_revision() -> None:
    with pytest.raises(ValidationError, match="exact 40-character"):
        Settings(
            ENVIRONMENT="production",
            API_KEY_REQUIRED=True,
            API_KEYS=[SecretStr("p" * 32)],
            MODEL_NAME="organization/model",
            MODEL_LOCAL_FILES_ONLY=False,
            MODEL_REVISION=None,
        )


def test_production_local_model_requires_complete_trust_configuration() -> None:
    configured = Settings(
        ENVIRONMENT="production",
        API_KEY_REQUIRED=True,
        API_KEYS=[SecretStr("p" * 32)],
        MODEL_NAME="C:\\models\\approved",
        MODEL_SOURCE_ID="approved/malaria",
        MODEL_LOCAL_FILES_ONLY=True,
        MODEL_REVISION="a" * 40,
        MODEL_MANIFEST_SHA256="0" * 64,
    )
    assert configured.MODEL_LOCAL_FILES_ONLY is True


def test_readiness_ready(
    client: TestClient, mock_classifier_service: MagicMock
) -> None:
    manifest = MagicMock(spec=ModelManifest)
    manifest.revision = "a" * 40
    mock_classifier_service.registry_resolution = RegistryResolution(
        kind=RegistryKind.SEALED,
        model_root=Path("C:\\approved-model"),
        manifest_path=Path("C:\\approved-model\\model_manifest.json"),
        manifest=manifest,
        manifest_sha256="b" * 64,
        artifact_verified=True,
        independent_trust_anchor=True,
        serving_permitted=True,
        evidence_scope="SOFTWARE_ARTIFACT_INTEGRITY_ONLY",
    )
    app.state.classifier_service = mock_classifier_service
    app.state.model_error_code = None
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "model_loaded": True,
        "model_name": None,
        "reason": None,
        "artifact_verified": True,
        "independent_trust_anchor": True,
        "model_revision": "a" * 40,
        "manifest_sha256": "b" * 64,
        "registry_kind": "sealed_manifest_registry",
    }


def test_readiness_does_not_disclose_local_model_path(
    client: TestClient,
    mock_classifier_service: MagicMock,
) -> None:
    app.state.classifier_service = mock_classifier_service
    app.state.model_error_code = None
    with (
        patch("src.api.routes.settings.MODEL_NAME", "C:\\secret\\approved-model"),
        patch("src.api.routes.settings.MODEL_LOCAL_FILES_ONLY", True),
    ):
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["model_name"] == "local-artifact"
    assert "secret" not in response.text


def test_readiness_without_configured_model(client: TestClient) -> None:
    app.state.classifier_service = None
    app.state.model_error_code = "MODEL_NOT_CONFIGURED"
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["reason"] == "MODEL_NOT_CONFIGURED"
    assert response.json()["model_loaded"] is False


def test_analyze_success_is_research_only(
    client: TestClient,
    mock_classifier_service: MagicMock,
    sample_image_bytes: bytes,
) -> None:
    app.state.classifier_service = mock_classifier_service
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("test_cell.png", sample_image_bytes, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_cell.png"
    assert data["predicted_cell_class"] == "Parasitized"
    assert data["diagnosis"] == "Parasitized"
    assert data["confidence"] == 0.985
    assert data["calibrated"] is False
    assert data["intended_use"] == "research_only"
    assert data["task"] == "pre_cropped_single_cell_classification"
    assert data["analysis_level"] == "cell"
    assert data["technical_input_validation_passed"] is True
    assert data["human_review_required"] is True
    assert data["patient_diagnosis_supported"] is False
    assert data["parasitemia_supported"] is False
    assert len(data["limitations"]) == 3


def test_filename_is_sanitized(
    client: TestClient,
    mock_classifier_service: MagicMock,
    sample_image_bytes: bytes,
) -> None:
    app.state.classifier_service = mock_classifier_service
    response = client.post(
        "/analyze",
        files={"file": ("..\\private\\cell.png", sample_image_bytes, "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "cell.png"
    assert response.headers["Deprecation"] == "true"
    assert response.headers["Link"] == '</api/v1/analyze>; rel="successor-version"'


def test_unicode_filename_is_preserved_without_control_characters(
    client: TestClient,
    mock_classifier_service: MagicMock,
    sample_image_bytes: bytes,
) -> None:
    app.state.classifier_service = mock_classifier_service
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("..\\данные\\клетка.png", sample_image_bytes, "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "клетка.png"


def test_filename_extension_is_non_authoritative(
    client: TestClient,
    mock_classifier_service: MagicMock,
    sample_image_bytes: bytes,
) -> None:
    app.state.classifier_service = mock_classifier_service
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("cell.jpg", sample_image_bytes, "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "cell.jpg"


def test_unsupported_media_type_uses_stable_error_envelope(
    client: TestClient,
    mock_classifier_service: MagicMock,
) -> None:
    app.state.classifier_service = mock_classifier_service
    response = client.post(
        "/analyze",
        files={"file": ("test.txt", b"plain text", "text/plain")},
    )
    assert response.status_code == 415
    data = response.json()
    assert data["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert "Unsupported content type" in data["detail"]
    assert data["request_id"] == response.headers["X-Request-ID"]


def test_missing_file_uses_validation_error_envelope(client: TestClient) -> None:
    app.state.classifier_service = MagicMock(spec=MalariaClassifierService)
    app.state.classifier_service.is_ready.return_value = True
    response = client.post("/analyze")
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert response.json()["detail"] == "Request validation failed."


def test_empty_file_is_rejected(
    client: TestClient,
    mock_classifier_service: MagicMock,
) -> None:
    app.state.classifier_service = mock_classifier_service
    response = client.post(
        "/analyze",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_REQUEST"
    assert "empty" in response.json()["detail"]


def test_oversized_file_is_rejected(
    client: TestClient,
    mock_classifier_service: MagicMock,
) -> None:
    app.state.classifier_service = mock_classifier_service
    with patch("src.core.config.settings.MAX_UPLOAD_SIZE_MB", 1):
        response = client.post(
            "/analyze",
            files={"file": ("large.png", b"x" * (1024 * 1024 + 1), "image/png")},
        )
    assert response.status_code == 413
    assert response.json()["code"] == "PAYLOAD_TOO_LARGE"


def test_transport_body_limit_rejects_before_multipart_parsing(
    client: TestClient,
) -> None:
    request_limit = (
        settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        + settings.MAX_MULTIPART_OVERHEAD_BYTES
    )
    response = client.post(
        "/api/v1/analyze",
        content=b"not-a-multipart-payload",
        headers={
            "Content-Type": "application/octet-stream",
            "Content-Length": str(request_limit + 1),
            "X-Request-ID": "oversized-at-transport",
        },
    )
    assert response.status_code == 413
    assert response.json() == {
        "code": "PAYLOAD_TOO_LARGE",
        "detail": "Request body exceeds the maximum allowed size.",
        "request_id": "oversized-at-transport",
    }
    assert response.headers["X-Request-ID"] == "oversized-at-transport"


@pytest.mark.asyncio
async def test_transport_body_limit_counts_stream_without_content_length() -> None:
    downstream_called = False
    sent_messages: list[dict[str, Any]] = []
    request_messages = iter(
        [
            {"type": "http.request", "body": b"123456", "more_body": True},
            {"type": "http.request", "body": b"789012", "more_body": False},
        ]
    )

    async def downstream(
        scope: dict[str, Any],
        receive: Any,
        send: Any,
    ) -> None:
        nonlocal downstream_called
        downstream_called = True
        while True:
            message = await receive()
            if not message.get("more_body", False):
                break
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    async def receive() -> dict[str, Any]:
        return next(request_messages)

    async def send(message: dict[str, Any]) -> None:
        sent_messages.append(message)

    middleware = RequestBodyLimitMiddleware(
        downstream,
        max_body_bytes=10,
        limited_paths={"/analyze"},
    )
    await middleware(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/analyze",
            "raw_path": b"/analyze",
            "query_string": b"",
            "headers": [],
            "client": ("test", 123),
            "server": ("test", 80),
            "state": {"request_id": "stream-limit"},
        },
        receive,
        send,
    )

    assert downstream_called is True
    assert sent_messages[0]["status"] == 413
    payload = json.loads(sent_messages[1]["body"])
    assert payload["code"] == "PAYLOAD_TOO_LARGE"
    assert payload["request_id"] == "stream-limit"


def test_corrupt_image_has_safe_error_message(
    client: TestClient,
    sample_image_bytes: bytes,
) -> None:
    service = MagicMock(spec=MalariaClassifierService)
    service.is_ready.return_value = True
    service.analyze_image.side_effect = ValueError("decoder secret detail")
    app.state.classifier_service = service
    response = client.post(
        "/analyze",
        files={"file": ("broken.png", sample_image_bytes, "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or unsupported image payload."
    assert "secret" not in response.text


def test_internal_inference_error_is_not_disclosed(
    client: TestClient,
    sample_image_bytes: bytes,
) -> None:
    service = MagicMock(spec=MalariaClassifierService)
    service.is_ready.return_value = True
    service.analyze_image.side_effect = RuntimeError("C:\\secret\\model.safetensors")
    app.state.classifier_service = service
    response = client.post(
        "/analyze",
        files={"file": ("cell.png", sample_image_bytes, "image/png")},
    )
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert response.json()["detail"] == "Inference failed."
    assert "safetensors" not in response.text


def test_capacity_error_returns_retry_after(
    client: TestClient,
    sample_image_bytes: bytes,
) -> None:
    service = MagicMock(spec=MalariaClassifierService)
    service.is_ready.return_value = True
    service.analyze_image.side_effect = InferenceCapacityError("busy")
    app.state.classifier_service = service
    response = client.post(
        "/analyze",
        files={"file": ("cell.png", sample_image_bytes, "image/png")},
    )
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "2"
    assert response.json()["code"] == "SERVICE_UNAVAILABLE"


def test_inference_timeout_has_stable_504_contract(
    client: TestClient,
    sample_image_bytes: bytes,
) -> None:
    service = MagicMock(spec=MalariaClassifierService)
    service.is_ready.return_value = True
    service.analyze_image.side_effect = InferenceTimeoutError("timed out")
    app.state.classifier_service = service

    response = client.post(
        "/api/v1/analyze",
        files={"file": ("cell.png", sample_image_bytes, "image/png")},
    )

    assert response.status_code == 504
    assert response.json()["code"] == "INFERENCE_TIMEOUT"
    assert "Capacity remains reserved" in response.json()["detail"]


def test_inference_service_rejects_corrupt_image() -> None:
    service = MalariaClassifierService("approved-model")
    service.processor = MagicMock()
    service.model = MagicMock()
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True

    with pytest.raises(ValueError, match="Invalid image file"):
        service._predict_sync(b"not a valid encoded image")


def test_model_contract_accepts_exact_expected_labels() -> None:
    service = MalariaClassifierService("approved-model")
    service.model = MagicMock()
    service.model.config.id2label = {0: "Parasitized", 1: "Uninfected"}
    service.model.config.num_labels = 2
    assert service._validate_model_contract() == {
        0: "Parasitized",
        1: "Uninfected",
    }


def test_model_contract_rejects_inverted_labels() -> None:
    service = MalariaClassifierService("approved-model")
    service.model = MagicMock()
    service.model.config.id2label = {0: "Uninfected", 1: "Parasitized"}
    service.model.config.num_labels = 2
    with pytest.raises(RuntimeError, match="do not match"):
        service._validate_model_contract()


def test_load_model_requires_explicit_artifact() -> None:
    service = MalariaClassifierService("")
    with pytest.raises(RuntimeError, match="MODEL_NAME is not configured"):
        service.load_model()


def test_load_model_uses_revision_and_validates_contract() -> None:
    processor = MagicMock()
    processor.size = {"height": 224, "width": 224}
    model = MagicMock()
    model.config.id2label = {0: "Parasitized", 1: "Uninfected"}
    model.config.num_labels = 2
    manifest = MagicMock(spec=ModelManifest)
    manifest.input_resolution = (224, 224)
    model_root = Path("C:\\approved-model")
    release = RegistryResolution(
        kind=RegistryKind.SEALED,
        model_root=model_root,
        manifest_path=model_root / "model_manifest.json",
        manifest=manifest,
        manifest_sha256="b" * 64,
        artifact_verified=True,
        independent_trust_anchor=True,
        serving_permitted=True,
        evidence_scope="SOFTWARE_ARTIFACT_INTEGRITY_ONLY",
    )

    with (
        patch(
            "src.services.inference.settings.MODEL_REVISION",
            "a" * 40,
        ),
        patch("src.services.inference.settings.MODEL_LOCAL_FILES_ONLY", True),
        patch(
            "src.services.inference.SealedModelRegistry.resolve",
            return_value=release,
        ),
        patch(
            "src.services.inference.AutoImageProcessor.from_pretrained",
            return_value=processor,
        ) as processor_loader,
        patch(
            "src.services.inference.AutoModelForImageClassification.from_pretrained",
            return_value=model,
        ) as model_loader,
    ):
        service = MalariaClassifierService("approved/model")
        service.load_model()

    common_options = {
        "local_files_only": True,
        "trust_remote_code": False,
    }
    processor_loader.assert_called_once_with(str(model_root), **common_options)
    model_loader.assert_called_once_with(
        str(model_root),
        use_safetensors=True,
        **common_options,
    )
    model.eval.assert_called_once()
    assert service.is_ready()


def test_predict_sync_returns_validated_labels(sample_image_bytes: bytes) -> None:
    service = MalariaClassifierService("approved-model")
    service.processor = MagicMock(return_value={"pixel_values": torch.ones(1, 3, 2, 2)})
    service.model = MagicMock(return_value=MagicMock(logits=torch.tensor([[3.0, 1.0]])))
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True

    with patch("src.services.inference.settings.QC_ENABLED", False):
        result = service._predict_sync(sample_image_bytes, "image/png")

    assert result["predicted_cell_class"] == "Parasitized"
    assert result["probabilities"][0].label == "Parasitized"
    assert result["confidence"] == pytest.approx(0.8808, abs=0.0001)


def test_predict_sync_rejects_mime_spoof(sample_image_bytes: bytes) -> None:
    service = MalariaClassifierService("approved-model")
    service.processor = MagicMock()
    service.model = MagicMock()
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True

    with pytest.raises(ValueError, match="content type"):
        service._predict_sync(sample_image_bytes, "image/jpeg")


def test_predict_sync_rejects_decoded_pixel_limit(
    sample_image_bytes: bytes,
) -> None:
    service = MalariaClassifierService("approved-model")
    service.processor = MagicMock()
    service.model = MagicMock()
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True

    with (
        patch("src.services.inference.settings.MAX_IMAGE_PIXELS", 9_999),
        pytest.raises(ValueError, match="pixel limit"),
    ):
        service._predict_sync(sample_image_bytes, "image/png")


def test_predict_sync_rejects_truncated_jpeg() -> None:
    image = Image.new("RGB", (64, 64), color="red")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    truncated = buffer.getvalue()[: len(buffer.getvalue()) // 2]

    service = MalariaClassifierService("approved-model")
    service.processor = MagicMock()
    service.model = MagicMock()
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True

    with pytest.raises(ValueError, match="Invalid image file"):
        service._predict_sync(truncated, "image/jpeg")


@pytest.mark.parametrize("mode", ["L", "RGBA"])
def test_predict_sync_normalizes_supported_image_modes(mode: str) -> None:
    image = Image.new(mode, (8, 8))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    service = MalariaClassifierService("approved-model")
    service.processor = MagicMock(return_value={"pixel_values": torch.ones(1, 3, 2, 2)})
    service.model = MagicMock(return_value=MagicMock(logits=torch.tensor([[3.0, 1.0]])))
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True

    with patch("src.services.inference.settings.QC_ENABLED", False):
        result = service._predict_sync(buffer.getvalue(), "image/png")

    assert result["predicted_cell_class"] == "Parasitized"
    processed_image = service.processor.call_args.kwargs["images"]
    assert processed_image.mode == "RGB"


def test_predict_sync_rejects_cmyk_image() -> None:
    image = Image.new("CMYK", (8, 8))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")

    service = MalariaClassifierService("approved-model")
    service.processor = MagicMock()
    service.model = MagicMock()
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True

    with pytest.raises(ValueError, match="CMYK"):
        service._predict_sync(buffer.getvalue(), "image/jpeg")


def test_predict_sync_rejects_multiframe_webp() -> None:
    first = Image.new("RGB", (8, 8), color="red")
    second = Image.new("RGB", (8, 8), color="blue")
    buffer = io.BytesIO()
    first.save(
        buffer,
        format="WEBP",
        save_all=True,
        append_images=[second],
        duration=100,
        loop=0,
    )

    service = MalariaClassifierService("approved-model")
    service.processor = MagicMock()
    service.model = MagicMock()
    service._id2label = {0: "Parasitized", 1: "Uninfected"}
    service._is_ready = True

    with pytest.raises(ValueError, match="Multi-frame"):
        service._predict_sync(buffer.getvalue(), "image/webp")


@pytest.mark.asyncio
async def test_inference_queue_timeout_is_bounded() -> None:
    service = MalariaClassifierService("approved-model")
    await service._inference_semaphore.acquire()

    with (
        patch("src.services.inference.settings.INFERENCE_QUEUE_TIMEOUT_SECONDS", 0.01),
        pytest.raises(InferenceCapacityError),
    ):
        await service.analyze_image(b"payload", "cell.png")


@pytest.mark.asyncio
async def test_execution_timeout_retains_capacity_until_thread_finishes() -> None:
    service = MalariaClassifierService("approved-model")
    started = threading.Event()
    release = threading.Event()

    def blocking_predict(
        image_bytes: bytes,
        declared_content_type: str | None = None,
    ) -> dict[str, Any]:
        started.set()
        release.wait(timeout=5)
        return {
            "predicted_cell_class": "Parasitized",
            "confidence": 0.9,
            "probabilities": [
                ClassProbability(label="Parasitized", confidence=0.9),
                ClassProbability(label="Uninfected", confidence=0.1),
            ],
        }

    with (
        patch.object(service, "_predict_sync", side_effect=blocking_predict),
        patch(
            "src.services.inference.settings.INFERENCE_EXECUTION_TIMEOUT_SECONDS",
            0.01,
        ),
        pytest.raises(InferenceTimeoutError),
    ):
        await service.analyze_image(b"payload", "cell.png", "image/png")

    assert started.is_set()
    assert service._inference_semaphore.locked()
    assert len(service._background_inference_tasks) == 1

    release.set()
    for _ in range(100):
        if not service._inference_semaphore.locked():
            break
        await asyncio.sleep(0.01)

    assert service._inference_semaphore.locked() is False
    assert service._background_inference_tasks == set()


@pytest.mark.asyncio
async def test_cancellation_does_not_release_capacity_before_thread_finishes() -> None:
    service = MalariaClassifierService("approved-model")
    started = threading.Event()
    release = threading.Event()

    def blocking_predict(
        image_bytes: bytes,
        declared_content_type: str | None = None,
    ) -> dict[str, Any]:
        assert image_bytes == b"payload"
        started.set()
        release.wait(timeout=5)
        return {
            "predicted_cell_class": "Parasitized",
            "confidence": 0.9,
            "probabilities": [
                ClassProbability(label="Parasitized", confidence=0.9),
                ClassProbability(label="Uninfected", confidence=0.1),
            ],
        }

    with patch.object(service, "_predict_sync", side_effect=blocking_predict):
        request_task = asyncio.create_task(
            service.analyze_image(b"payload", "cell.png", "image/png")
        )
        assert await asyncio.to_thread(started.wait, 2)
        request_task.cancel()
        await asyncio.sleep(0)

        assert request_task.done() is False
        assert service._inference_semaphore.locked()

        release.set()
        with pytest.raises(asyncio.CancelledError):
            await request_task

    assert service._inference_semaphore.locked() is False


def test_qc_rejection_uses_structured_422_contract(
    client: TestClient,
    sample_image_bytes: bytes,
) -> None:
    service = MagicMock(spec=MalariaClassifierService)
    service.is_ready.return_value = True
    metrics = QCMetrics(64, 64, 1.0, 2.0, 1.0, 0.0)
    service.analyze_image.side_effect = QualityControlError(
        [QCReason.BLURRY_IMAGE, QCReason.NON_MICROSCOPIC_PAYLOAD],
        metrics,
    )
    app.state.classifier_service = service

    response = client.post(
        "/api/v1/analyze",
        files={"file": ("blurred.png", sample_image_bytes, "image/png")},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "BLURRY_IMAGE"
    assert response.json()["reasons"] == [
        "BLURRY_IMAGE",
        "NON_MICROSCOPIC_PAYLOAD",
    ]
    assert response.json()["qc_metrics"]["laplacian_variance"] == 1.0
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_slide_analysis_aggregates_predictions_with_guardrails(
    client: TestClient,
    sample_image_bytes: bytes,
) -> None:
    service = MagicMock(spec=MalariaClassifierService)
    service.is_ready.return_value = True

    async def classify(
        image_bytes: bytes,
        filename: str,
        declared_content_type: str | None = None,
    ) -> PredictionResponse:
        parasitized = int(filename.removeprefix("cell").removesuffix(".png")) < 3
        label = "Parasitized" if parasitized else "Uninfected"
        return PredictionResponse(
            filename=filename,
            predicted_cell_class=label,
            diagnosis=label,
            confidence=0.9,
            probabilities=[
                ClassProbability(label=label, confidence=0.9),
                ClassProbability(
                    label="Uninfected" if parasitized else "Parasitized",
                    confidence=0.1,
                ),
            ],
            execution_time_ms=1.0,
        )

    service.analyze_image.side_effect = classify
    app.state.classifier_service = service
    uploads = [
        ("files", (f"cell{index}.png", sample_image_bytes, "image/png"))
        for index in range(10)
    ]

    response = client.post(
        "/api/v1/analyze/slide",
        data={"slide_id": "research-slide-01"},
        files=uploads,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["slide_id"] == "research-slide-01"
    assert data["total_cells"] == 10
    assert data["predicted_parasitized_cells"] == 3
    assert data["predicted_uninfected_cells"] == 7
    assert data["parasitemia_percent"] == 30.0
    assert data["wilson_95_interval"]["lower_percent"] == pytest.approx(
        10.7791,
        abs=0.0001,
    )
    assert data["wilson_95_interval"]["upper_percent"] == pytest.approx(
        60.3222,
        abs=0.0001,
    )
    assert data["claim_boundary"] == "RESEARCH_ONLY_UNCALIBRATED_SLIDE_SUMMARY"
    assert data["patient_diagnosis_supported"] is False
    assert data["clinically_validated_parasitemia"] is False
    assert data["human_review_required"] is True


def test_slide_analysis_rejects_count_and_blank_identifier(
    client: TestClient,
    mock_classifier_service: MagicMock,
    sample_image_bytes: bytes,
) -> None:
    app.state.classifier_service = mock_classifier_service
    too_few = client.post(
        "/api/v1/analyze/slide",
        data={"slide_id": "slide"},
        files=[("files", ("cell.png", sample_image_bytes, "image/png"))],
    )
    assert too_few.status_code == 422
    assert "requires" in too_few.json()["detail"]

    uploads = [
        ("files", (f"cell{index}.png", sample_image_bytes, "image/png"))
        for index in range(settings.SLIDE_MIN_CELLS)
    ]
    blank = client.post(
        "/api/v1/analyze/slide",
        data={"slide_id": "\u0001"},
        files=uploads,
    )
    assert blank.status_code == 422
    assert "visible" in blank.json()["detail"]
