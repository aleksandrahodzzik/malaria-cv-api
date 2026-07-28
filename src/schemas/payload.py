"""Pydantic schemas for request payload and API response validation."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Schema for service liveness endpoint response."""

    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(..., description="API Version")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 UTC timestamp",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-07-27T18:00:00Z",
            }
        }
    )


class ReadinessResponse(BaseModel):
    """Schema for service readiness endpoint response."""

    status: str = Field(default="ready", description="Service readiness status")
    model_loaded: bool = Field(
        ..., description="Indicates whether ML model is loaded into memory"
    )
    model_name: str | None = Field(
        default=None, description="Configured model identifier or local path"
    )
    reason: str | None = Field(
        default=None,
        description="Stable machine-readable reason while the service is not ready",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ready",
                "model_loaded": True,
                "model_name": "organization/approved-malaria-cell-model",
                "reason": None,
            }
        }
    )


class ClassProbability(BaseModel):
    """Schema representing probability score for an individual class label."""

    label: str = Field(
        ..., description="Target class label (e.g., Parasitized, Uninfected)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Uncalibrated softmax score in [0, 1]. It is not a guaranteed "
            "probability that the prediction is correct."
        ),
    )


class PredictionResponse(BaseModel):
    """Schema for research-only cell-image classification response."""

    filename: str = Field(..., description="Uploaded image filename")
    predicted_cell_class: str = Field(
        ...,
        description="Top predicted class for the uploaded pre-cropped cell image",
    )
    diagnosis: str = Field(
        ...,
        deprecated=True,
        description=(
            "Deprecated compatibility alias for predicted_cell_class. "
            "This field is not a patient diagnosis."
        ),
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Top uncalibrated softmax score",
    )
    probabilities: list[ClassProbability] = Field(
        ..., description="Uncalibrated softmax scores for every model class"
    )
    calibrated: Literal[False] = Field(
        default=False,
        description="The current service does not provide calibrated probabilities",
    )
    intended_use: Literal["research_only"] = Field(
        default="research_only",
        description="This prototype is restricted to research and engineering use",
    )
    limitations: list[str] = Field(
        default_factory=lambda: [
            "Not a patient-level diagnosis.",
            "Not validated for treatment decisions.",
            "A single-cell result cannot exclude malaria.",
        ],
        description="Material limitations that must accompany the result",
    )
    execution_time_ms: float = Field(
        ..., description="Model inference duration in milliseconds"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 UTC timestamp",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "cell_sample_01.png",
                "predicted_cell_class": "Parasitized",
                "diagnosis": "Parasitized",
                "confidence": 0.9845,
                "probabilities": [
                    {"label": "Parasitized", "confidence": 0.9845},
                    {"label": "Uninfected", "confidence": 0.0155},
                ],
                "calibrated": False,
                "intended_use": "research_only",
                "limitations": [
                    "Not a patient-level diagnosis.",
                    "Not validated for treatment decisions.",
                    "A single-cell result cannot exclude malaria.",
                ],
                "execution_time_ms": 42.15,
                "timestamp": "2026-07-27T18:00:00Z",
            }
        }
    )


class ErrorResponse(BaseModel):
    """Schema for standardized API error responses."""

    code: str = Field(..., description="Stable machine-readable error code")
    detail: str = Field(..., description="Human-readable error explanation")
    request_id: str | None = Field(
        default=None, description="Unique correlation request ID"
    )


class CapabilitiesResponse(BaseModel):
    """Public, non-sensitive API capabilities for clients and the local UI."""

    api_version: str
    intended_use: Literal["research_only"] = "research_only"
    model_configured: bool
    accepted_content_types: list[str]
    max_upload_size_mb: int
    max_image_pixels: int
    probabilities_calibrated: Literal[False] = False
