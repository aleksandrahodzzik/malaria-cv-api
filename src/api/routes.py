"""API endpoints for Health checks, System Readiness, and Cell Image Analysis."""

import logging
import unicodedata
from pathlib import PurePath
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)

from src.api.dependencies import get_classifier_service
from src.core.config import settings
from src.core.logging import safe_extra
from src.schemas.payload import (
    CapabilitiesResponse,
    ErrorResponse,
    HealthResponse,
    MethodologyResponse,
    PipelineStage,
    PredictionResponse,
    ReadinessResponse,
)
from src.services.inference import (
    InferenceCapacityError,
    InferenceTimeoutError,
    MalariaClassifierService,
)

logger = logging.getLogger("malaria_api.routes")

router = APIRouter()


def _sanitize_filename(filename: str) -> str:
    """Return a bounded display filename without paths or control characters."""
    basename = filename.replace("\\", "/").rsplit("/", maxsplit=1)[-1]
    sanitized = "".join(
        character
        for character in basename
        if not unicodedata.category(character).startswith("C")
    ).strip()
    if not sanitized:
        sanitized = "uploaded_image"
    return sanitized[: settings.MAX_FILENAME_LENGTH]


def _public_model_reference() -> str | None:
    """Return a non-sensitive model reference suitable for a public probe."""
    configured = settings.MODEL_NAME.strip()
    if not configured:
        return None
    if settings.MODEL_LOCAL_FILES_ONLY or PurePath(configured).is_absolute():
        return "local-artifact"
    return configured


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Health Check",
    description="Check whether the API microservice container is up and running.",
)
async def health_check() -> HealthResponse:
    """Return health status and version of the API."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
    )


@router.get(
    "/capabilities",
    response_model=CapabilitiesResponse,
    status_code=status.HTTP_200_OK,
    summary="Public API Capabilities",
    description="Return non-sensitive limits and intended-use metadata for clients.",
)
async def capabilities() -> CapabilitiesResponse:
    """Return stable client configuration without exposing secrets."""
    return CapabilitiesResponse(
        api_version=settings.VERSION,
        model_configured=bool(settings.MODEL_NAME.strip()),
        accepted_content_types=settings.ALLOWED_CONTENT_TYPES,
        max_upload_size_mb=settings.MAX_UPLOAD_SIZE_MB,
        max_image_pixels=settings.MAX_IMAGE_PIXELS,
    )


@router.get(
    "/methodology",
    response_model=MethodologyResponse,
    status_code=status.HTTP_200_OK,
    summary="Intended Use and Pipeline Boundaries",
    description=(
        "Return the exact research task, pipeline coverage, and unsupported "
        "clinical uses."
    ),
)
async def methodology() -> MethodologyResponse:
    """Expose safety-critical task boundaries in a machine-readable form."""
    return MethodologyResponse(
        pipeline=[
            PipelineStage(
                order=1,
                stage="input_image",
                status="implemented",
                evidence="One uploaded encoded image is accepted.",
            ),
            PipelineStage(
                order=2,
                stage="image_quality_control",
                status="partial",
                evidence=(
                    "Technical decoding checks exist; focus, stain, illumination, "
                    "cell morphology, and acquisition quality are not validated."
                ),
            ),
            PipelineStage(
                order=3,
                stage="cell_detection_or_segmentation",
                status="missing",
                evidence="The API requires a pre-cropped single-cell image.",
            ),
            PipelineStage(
                order=4,
                stage="cell_classification",
                status="unvalidated",
                evidence=(
                    "Serving code exists, but no approved reproducible model or "
                    "validation cohort is available."
                ),
            ),
            PipelineStage(
                order=5,
                stage="slide_level_aggregation",
                status="missing",
                evidence=(
                    "No slide identifier, sampling protocol, or aggregation exists."
                ),
            ),
            PipelineStage(
                order=6,
                stage="patient_level_interpretation",
                status="missing",
                evidence="No patient-level reference standard or decision rule exists.",
            ),
            PipelineStage(
                order=7,
                stage="human_review",
                status="partial",
                evidence=(
                    "The UI warns that review is required; no authenticated reviewer "
                    "workflow or sign-off record exists."
                ),
            ),
            PipelineStage(
                order=8,
                stage="clinical_action",
                status="missing",
                evidence="Clinical action is explicitly unsupported.",
            ),
        ],
        domain_assumptions_unvalidated=[
            "stain and staining protocol",
            "microscope and objective",
            "camera and acquisition pipeline",
            "Plasmodium species and life-cycle stage",
            "geography and care setting",
            "age and patient subgroup",
            "real-world prevalence",
            "whole-slide and field-of-view inputs",
        ],
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Readiness Probe",
    description=(
        "Check whether the approved image model is loaded and ready for predictions."
    ),
)
async def readiness_check(
    request: Request,
    response: Response,
) -> ReadinessResponse:
    """Return model readiness status, using HTTP 503 while unavailable."""
    service = getattr(request.app.state, "classifier_service", None)
    is_ready = service is not None and service.is_ready()
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if is_ready else "not_ready",
        model_loaded=is_ready,
        model_name=_public_model_reference(),
        reason=None
        if is_ready
        else getattr(request.app.state, "model_error_code", "model_unavailable"),
    )


@router.post(
    "/analyze",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Malaria Cell Image",
    description=(
        "Upload a microscopic blood smear cell image (JPEG/PNG/WEBP). "
        "Returns a research-only cell-class prediction with uncalibrated "
        "softmax scores. This endpoint does not diagnose a patient."
    ),
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid image payload or content type",
        },
        413: {
            "model": ErrorResponse,
            "description": "Uploaded image file exceeds size limit",
        },
        415: {
            "model": ErrorResponse,
            "description": "Unsupported media type",
        },
        422: {
            "model": ErrorResponse,
            "description": "Request validation failed",
        },
        503: {"model": ErrorResponse, "description": "Inference engine uninitialized"},
        504: {
            "model": ErrorResponse,
            "description": "Inference exceeded the configured request timeout",
        },
        500: {
            "model": ErrorResponse,
            "description": "Safe internal inference failure",
        },
    },
)
async def analyze_cell_image(
    file: Annotated[
        UploadFile,
        File(description="Microscopic cell image file upload"),
    ],
    service: Annotated[
        MalariaClassifierService,
        Depends(get_classifier_service),
    ],
) -> PredictionResponse:
    """Offload synchronous decode, preprocessing and compute from the event loop."""
    filename = _sanitize_filename(file.filename or "unknown_image.png")

    # Validate MIME Content Type
    if (
        not file.content_type
        or file.content_type.lower() not in settings.ALLOWED_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported content type '{file.content_type}'. "
                f"Supported types: {', '.join(settings.ALLOWED_CONTENT_TYPES)}"
            ),
        )

    # Read incrementally so an oversized request is rejected without retaining
    # the entire payload in application memory.
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    contents = bytearray()
    try:
        while chunk := await file.read(1024 * 1024):
            contents.extend(chunk)
            if len(contents) > max_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=(
                        "File size exceeds maximum threshold of "
                        f"{settings.MAX_UPLOAD_SIZE_MB} MB"
                    ),
                )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to read upload buffer.",
            extra=safe_extra(
                event="upload_read_failed",
                error_type=type(exc).__name__,
            ),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read the uploaded file payload.",
        ) from exc
    finally:
        await file.close()

    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file payload is empty.",
        )

    image_bytes = bytes(contents)
    del contents

    # Perform inference via bounded, offloaded thread execution.
    try:
        prediction = await service.analyze_image(
            image_bytes=image_bytes,
            filename=filename,
            declared_content_type=file.content_type.lower(),
        )
        return prediction
    except ValueError as val_err:
        logger.info(
            "Invalid image payload.",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unsupported image payload.",
        ) from val_err
    except InferenceCapacityError as capacity_err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference capacity is temporarily unavailable. Retry later.",
            headers={"Retry-After": "2"},
        ) from capacity_err
    except InferenceTimeoutError as timeout_err:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                "Inference exceeded the request timeout. Capacity remains reserved "
                "until the worker finishes."
            ),
        ) from timeout_err
    except Exception as exc:
        logger.exception(
            "Inference pipeline execution error.",
            extra=safe_extra(
                event="inference_failed",
                error_type=type(exc).__name__,
            ),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference failed.",
        ) from exc
