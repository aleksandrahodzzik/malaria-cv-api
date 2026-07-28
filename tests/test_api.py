"""Comprehensive Pytest test suite for Malaria Classification FastAPI microservice."""

import io
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image
from starlette.testclient import TestClient

from src.main import app
from src.schemas.payload import ClassProbability, PredictionResponse
from src.services.inference import MalariaClassifierService


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Initialize TestClient without downloading model weights."""
    with (
        patch.object(MalariaClassifierService, "load_model", return_value=None),
        TestClient(app) as test_client,
    ):
        yield test_client


@pytest.fixture
def mock_classifier_service() -> MagicMock:
    """Fixture providing a mock MalariaClassifierService instance."""
    mock_service = MagicMock(spec=MalariaClassifierService)
    mock_service.is_ready.return_value = True

    dummy_response = PredictionResponse(
        filename="test_cell.png",
        diagnosis="Parasitized",
        confidence=0.985,
        probabilities=[
            ClassProbability(label="Parasitized", confidence=0.985),
            ClassProbability(label="Uninfected", confidence=0.015),
        ],
        execution_time_ms=25.4,
    )

    async def async_analyze(image_bytes: bytes, filename: str) -> PredictionResponse:
        return dummy_response

    mock_service.analyze_image.side_effect = async_analyze
    return mock_service


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Fixture generating valid PNG image byte buffer for testing."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def test_health_check_endpoint(client: TestClient) -> None:
    """Verify /health endpoint returns HTTP 200 and valid JSON schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers


def test_readiness_check_endpoint_ready(
    client: TestClient, mock_classifier_service: MagicMock
) -> None:
    """Verify /ready endpoint returns readiness details when model loaded."""
    app.state.classifier_service = mock_classifier_service
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["model_loaded"] is True
    assert "model_name" in data


def test_readiness_check_endpoint_uninitialized(client: TestClient) -> None:
    """Verify /ready returns a structured HTTP 503 response when uninitialized."""
    app.state.classifier_service = None
    response = client.get("/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["model_loaded"] is False
    assert "model_name" in data


def test_analyze_endpoint_success(
    client: TestClient,
    mock_classifier_service: MagicMock,
    sample_image_bytes: bytes,
) -> None:
    """Verify /analyze endpoint successfully processes uploaded image."""
    app.state.classifier_service = mock_classifier_service

    files = {
        "file": ("test_cell.png", sample_image_bytes, "image/png"),
    }
    response = client.post("/analyze", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "test_cell.png"
    assert data["diagnosis"] == "Parasitized"
    assert data["confidence"] == 0.985
    assert len(data["probabilities"]) == 2
    assert data["probabilities"][0]["label"] == "Parasitized"


def test_analyze_endpoint_unsupported_media_type(
    client: TestClient,
    mock_classifier_service: MagicMock,
) -> None:
    """Verify /analyze endpoint rejects non-image MIME types with HTTP 400."""
    app.state.classifier_service = mock_classifier_service

    files = {
        "file": ("test_document.txt", b"plain text content", "text/plain"),
    }
    response = client.post("/analyze", files=files)
    assert response.status_code == 400
    assert "Unsupported content type" in response.json()["detail"]


def test_analyze_endpoint_empty_file(
    client: TestClient,
    mock_classifier_service: MagicMock,
) -> None:
    """Verify /analyze endpoint rejects empty file uploads with HTTP 400."""
    app.state.classifier_service = mock_classifier_service

    files = {
        "file": ("empty.png", b"", "image/png"),
    }
    response = client.post("/analyze", files=files)
    assert response.status_code == 400
    assert "Uploaded file payload is empty" in response.json()["detail"]


def test_analyze_endpoint_rejects_missing_content_type(
    client: TestClient,
    mock_classifier_service: MagicMock,
) -> None:
    """Verify uploads with no supported MIME type are rejected."""
    app.state.classifier_service = mock_classifier_service

    files = {
        "file": ("cell.bin", b"not an image", None),
    }
    response = client.post("/analyze", files=files)
    assert response.status_code == 400
    assert "Unsupported content type" in response.json()["detail"]


def test_analyze_endpoint_oversized_file(
    client: TestClient,
    mock_classifier_service: MagicMock,
) -> None:
    """Verify /analyze endpoint enforces file size limit and returns HTTP 413."""
    app.state.classifier_service = mock_classifier_service

    with patch("src.core.config.settings.MAX_UPLOAD_SIZE_MB", 0.0001):  # ~100 bytes
        files = {
            "file": ("large.png", b"x" * 200, "image/png"),
        }
        response = client.post("/analyze", files=files)
        assert response.status_code == 413
        assert "exceeds maximum threshold" in response.json()["detail"]


def test_inference_service_rejects_corrupt_image() -> None:
    """Verify corrupt image bytes fail validation before model execution."""
    service = MalariaClassifierService()
    service.processor = MagicMock()
    service.model = MagicMock()
    service._is_ready = True

    with pytest.raises(ValueError, match="Invalid image file"):
        service._predict_sync(b"not a valid encoded image")
