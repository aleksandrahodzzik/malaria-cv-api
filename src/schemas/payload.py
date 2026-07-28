"""Pydantic schemas for request payload and API response validation."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Schema for service liveness endpoint response."""

    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(..., description="API Version")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
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
    model_name: str = Field(..., description="HuggingFace model identifier")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ready",
                "model_loaded": True,
                "model_name": "trpakov/vit-malaria-classification",
            }
        }
    )


class ClassProbability(BaseModel):
    """Schema representing probability score for an individual class label."""

    label: str = Field(
        ..., description="Target class label (e.g., Parasitized, Uninfected)"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized confidence probability [0.0 - 1.0]"
    )


class PredictionResponse(BaseModel):
    """Schema for malaria cell classification response."""

    filename: str = Field(..., description="Uploaded image filename")
    diagnosis: str = Field(..., description="Top predicted clinical diagnosis")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Top prediction confidence score"
    )
    probabilities: list[ClassProbability] = Field(
        ..., description="Full class probability distribution"
    )
    execution_time_ms: float = Field(
        ..., description="Model inference duration in milliseconds"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "cell_sample_01.png",
                "diagnosis": "Parasitized",
                "confidence": 0.9845,
                "probabilities": [
                    {"label": "Parasitized", "confidence": 0.9845},
                    {"label": "Uninfected", "confidence": 0.0155},
                ],
                "execution_time_ms": 42.15,
                "timestamp": "2026-07-27T18:00:00Z",
            }
        }
    )


class ErrorResponse(BaseModel):
    """Schema for standardized API error responses."""

    detail: str = Field(..., description="Human-readable error explanation")
    request_id: str | None = Field(
        default=None, description="Unique correlation request ID"
    )
