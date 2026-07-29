"""API endpoints for Health checks, System Readiness, and Cell Image Analysis."""

import logging
import unicodedata
from pathlib import PurePath
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)

from src.api.dependencies import get_classifier_service, require_api_key
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
    SlideAnalysisResponse,
    WilsonIntervalResponse,
)
from src.services.aggregation import aggregate_slide_predictions
from src.services.inference import (
    InferenceCapacityError,
    InferenceTimeoutError,
    MalariaClassifierService,
)
from src.services.qc import QualityControlError

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


def _sanitize_slide_id(slide_id: str) -> str:
    """Return a non-empty, bounded identifier without control characters."""
    sanitized = "".join(
        character
        for character in slide_id
        if not unicodedata.category(character).startswith("C")
    ).strip()
    if not sanitized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="slide_id must contain a visible non-control character.",
        )
    return sanitized[: settings.MAX_SLIDE_ID_LENGTH]


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
                    "Deterministic blur, contrast, stain-color, resolution and "
                    "aspect-ratio rejection exists; thresholds are not clinically "
                    "validated and do not constitute a proven OOD detector."
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
                status="partial",
                evidence=(
                    "Uploaded pre-cropped cell predictions can be counted with a "
                    "Wilson interval; sampling, model error, clustering and clinical "
                    "parasitemia remain unvalidated."
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


async def _read_upload(file: UploadFile) -> tuple[str, bytes, str]:
    """Read one bounded upload and return its safe name, bytes and MIME type."""
    filename = _sanitize_filename(file.filename or "unknown_image.png")
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
    return filename, image_bytes, file.content_type.lower()


async def _execute_inference(
    *,
    service: MalariaClassifierService,
    image_bytes: bytes,
    filename: str,
    declared_content_type: str,
) -> PredictionResponse:
    """Execute inference and translate internal failures to stable HTTP contracts."""
    try:
        return await service.analyze_image(
            image_bytes=image_bytes,
            filename=filename,
            declared_content_type=declared_content_type,
        )
    except QualityControlError:
        raise
    except ValueError as val_err:
        logger.info("Invalid image payload.")
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


_ANALYZE_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"model": ErrorResponse, "description": "Invalid image payload"},
    401: {"model": ErrorResponse, "description": "API key required"},
    403: {"model": ErrorResponse, "description": "API key forbidden"},
    413: {"model": ErrorResponse, "description": "Upload exceeds size limit"},
    415: {"model": ErrorResponse, "description": "Unsupported media type"},
    422: {"model": ErrorResponse, "description": "Validation or QC rejection"},
    429: {"model": ErrorResponse, "description": "Inference quota exceeded"},
    500: {"model": ErrorResponse, "description": "Safe internal failure"},
    503: {"model": ErrorResponse, "description": "Inference engine unavailable"},
    504: {"model": ErrorResponse, "description": "Inference timeout"},
}


@router.post(
    "/analyze",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Malaria Cell Image",
    description=(
        "Upload one pre-cropped microscopic cell image. Deterministic engineering "
        "QC runs before uncalibrated model inference. Not a patient diagnosis."
    ),
    responses=_ANALYZE_ERROR_RESPONSES,
)
async def analyze_cell_image(
    file: Annotated[
        UploadFile,
        File(description="Microscopic cell image file upload"),
    ],
    _auth: Annotated[None, Depends(require_api_key)],
    service: Annotated[
        MalariaClassifierService,
        Depends(get_classifier_service),
    ],
) -> PredictionResponse:
    """Validate, authenticate and classify one pre-cropped cell image."""
    filename, image_bytes, content_type = await _read_upload(file)
    return await _execute_inference(
        service=service,
        image_bytes=image_bytes,
        filename=filename,
        declared_content_type=content_type,
    )


@router.post(
    "/analyze/slide",
    response_model=SlideAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Aggregate Pre-cropped Cells for One Slide",
    description=(
        "Classify multiple pre-cropped cell images and return a research-only "
        "observed positive-cell fraction with a Wilson 95% interval. The interval "
        "does not incorporate model error, cell dependence or sampling bias."
    ),
    responses=_ANALYZE_ERROR_RESPONSES,
)
async def analyze_slide(
    files: Annotated[
        list[UploadFile],
        File(description="Pre-cropped cell images from one slide"),
    ],
    slide_id: Annotated[
        str,
        Form(description="Pseudonymous slide identifier; do not submit patient PII"),
    ],
    _auth: Annotated[None, Depends(require_api_key)],
    service: Annotated[
        MalariaClassifierService,
        Depends(get_classifier_service),
    ],
) -> SlideAnalysisResponse:
    """Create a bounded, sequential slide summary without patient interpretation."""
    if not settings.SLIDE_MIN_CELLS <= len(files) <= settings.SLIDE_MAX_CELLS:
        for upload in files:
            await upload.close()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Slide analysis requires {settings.SLIDE_MIN_CELLS} to "
                f"{settings.SLIDE_MAX_CELLS} cell images."
            ),
        )

    predictions: list[PredictionResponse] = []
    try:
        safe_slide_id = _sanitize_slide_id(slide_id)
        for file in files:
            filename, image_bytes, content_type = await _read_upload(file)
            predictions.append(
                await _execute_inference(
                    service=service,
                    image_bytes=image_bytes,
                    filename=filename,
                    declared_content_type=content_type,
                )
            )
    finally:
        for upload in files:
            await upload.close()

    aggregation = aggregate_slide_predictions(predictions)
    return SlideAnalysisResponse(
        slide_id=safe_slide_id,
        total_cells=aggregation.total_cells,
        predicted_parasitized_cells=aggregation.parasitized_cells,
        predicted_uninfected_cells=aggregation.uninfected_cells,
        parasitemia_percent=round(aggregation.parasitemia_fraction * 100, 4),
        wilson_95_interval=WilsonIntervalResponse(
            lower_percent=round(aggregation.wilson_95.lower * 100, 4),
            upper_percent=round(aggregation.wilson_95.upper * 100, 4),
        ),
        cell_predictions=predictions,
    )
