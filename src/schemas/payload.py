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
                "version": "1.5.0",
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
    artifact_verified: bool = Field(
        default=False,
        description="True only after every manifest-declared artifact passes SHA-256",
    )
    independent_trust_anchor: bool = Field(
        default=False,
        description="Whether an independently configured manifest digest was checked",
    )
    model_revision: str | None = Field(
        default=None,
        description="Exact immutable model revision from the verified manifest",
    )
    manifest_sha256: str | None = Field(
        default=None,
        description="Digest of the verified local manifest",
    )
    registry_kind: str | None = Field(
        default=None,
        description="Model registry adapter that produced the serving release",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ready",
                "model_loaded": True,
                "model_name": "organization/approved-malaria-cell-model",
                "reason": None,
                "artifact_verified": True,
                "independent_trust_anchor": True,
                "model_revision": "0123456789abcdef0123456789abcdef01234567",
                "manifest_sha256": "0" * 64,
                "registry_kind": "sealed_manifest_registry",
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


class QualityControlSummary(BaseModel):
    """Deterministic engineering QC attached to an accepted image."""

    passed: Literal[True] = True
    policy_version: str
    clinically_validated: Literal[False] = False
    metrics: dict[str, float | int]


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
    quality_control: QualityControlSummary | None = Field(
        default=None,
        description=(
            "Engineering QC measurements when QC is enabled. Passing this policy "
            "does not establish microscopy suitability or clinical validity."
        ),
    )
    calibrated: Literal[False] = Field(
        default=False,
        description="The current service does not provide calibrated probabilities",
    )
    intended_use: Literal["research_only"] = Field(
        default="research_only",
        description="This prototype is restricted to research and engineering use",
    )
    task: Literal["pre_cropped_single_cell_classification"] = Field(
        default="pre_cropped_single_cell_classification",
        description="Exact task implemented by this endpoint",
    )
    analysis_level: Literal["cell"] = Field(
        default="cell",
        description="Unit represented by this prediction",
    )
    technical_input_validation_passed: Literal[True] = Field(
        default=True,
        description=(
            "Encoded file and serving-contract checks passed. This is not "
            "microscopy quality control."
        ),
    )
    human_review_required: Literal[True] = Field(
        default=True,
        description="The research output must not trigger an automated clinical action",
    )
    patient_diagnosis_supported: Literal[False] = Field(
        default=False,
        description="A single-cell output is not a patient diagnosis",
    )
    parasitemia_supported: Literal[False] = Field(
        default=False,
        description="The endpoint does not count cells or estimate parasitemia",
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
                "task": "pre_cropped_single_cell_classification",
                "analysis_level": "cell",
                "technical_input_validation_passed": True,
                "human_review_required": True,
                "patient_diagnosis_supported": False,
                "parasitemia_supported": False,
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
    reasons: list[str] | None = Field(
        default=None,
        description="Stable rejection reasons when more than one QC rule failed",
    )
    qc_metrics: dict[str, float | int] | None = Field(
        default=None,
        description="Non-sensitive deterministic measurements for QC rejection",
    )


class CapabilitiesResponse(BaseModel):
    """Public, non-sensitive API capabilities for clients and the local UI."""

    api_version: str
    intended_use: Literal["research_only"] = "research_only"
    task: Literal["pre_cropped_single_cell_classification"] = (
        "pre_cropped_single_cell_classification"
    )
    analysis_level: Literal["cell"] = "cell"
    model_configured: bool
    api_key_required: bool
    accepted_content_types: list[str]
    max_upload_size_mb: int
    max_image_pixels: int
    probabilities_calibrated: Literal[False] = False
    patient_diagnosis_supported: Literal[False] = False
    slide_aggregation_supported: Literal[True] = True
    research_parasitemia_summary_supported: Literal[True] = True
    parasitemia_supported: Literal[False] = False
    human_review_required: Literal[True] = True


class WilsonIntervalResponse(BaseModel):
    """Wilson 95% interval expressed as percentage points."""

    lower_percent: float = Field(ge=0.0, le=100.0)
    upper_percent: float = Field(ge=0.0, le=100.0)
    confidence_level: float = Field(default=0.95, ge=0.95, le=0.95)


class SlideAnalysisResponse(BaseModel):
    """Research-only aggregation of model-predicted pre-cropped cells."""

    slide_id: str
    analysis_level: Literal["slide_summary"] = "slide_summary"
    total_cells: int = Field(ge=1)
    predicted_parasitized_cells: int = Field(ge=0)
    predicted_uninfected_cells: int = Field(ge=0)
    parasitemia_percent: float = Field(ge=0.0, le=100.0)
    wilson_95_interval: WilsonIntervalResponse
    cell_predictions: list[PredictionResponse]
    claim_boundary: Literal["RESEARCH_ONLY_UNCALIBRATED_SLIDE_SUMMARY"] = (
        "RESEARCH_ONLY_UNCALIBRATED_SLIDE_SUMMARY"
    )
    calibrated: Literal[False] = False
    patient_diagnosis_supported: Literal[False] = False
    clinically_validated_parasitemia: Literal[False] = False
    human_review_required: Literal[True] = True
    limitations: list[str] = Field(
        default_factory=lambda: [
            "Counts are based only on uploaded pre-cropped cells.",
            "Wilson bounds quantify binomial sampling only; model error and "
            "within-slide dependence are not included.",
            "This response is not a patient diagnosis or validated parasitemia result.",
        ]
    )


class PipelineStage(BaseModel):
    """One explicit link in the microscopy-to-clinical-action chain."""

    order: int = Field(..., ge=1)
    stage: str
    status: Literal["implemented", "partial", "missing", "unvalidated"]
    evidence: str


class MethodologyResponse(BaseModel):
    """Exact intended task and unsupported downstream clinical workflow."""

    intended_task: Literal["pre_cropped_single_cell_classification"] = (
        "pre_cropped_single_cell_classification"
    )
    deployment_scope: Literal["research_demonstration"] = "research_demonstration"
    supported_task_codes: list[Literal["A", "F"]] = ["A", "F"]
    unsupported_task_codes: list[Literal["B", "C", "D", "E"]] = [
        "B",
        "C",
        "D",
        "E",
    ]
    pipeline: list[PipelineStage]
    domain_assumptions_unvalidated: list[str]
    clinical_action_supported: Literal[False] = False
    human_review_required: Literal[True] = True
