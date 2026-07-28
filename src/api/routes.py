"""API endpoints for Health checks, System Readiness, and Cell Image Analysis."""

import logging
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
from src.schemas.payload import (
    ErrorResponse,
    HealthResponse,
    PredictionResponse,
    ReadinessResponse,
)
from src.services.inference import MalariaClassifierService

logger = logging.getLogger("malaria_api.routes")

router = APIRouter()


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
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Readiness Probe",
    description="Check whether the HuggingFace ViT model is fully loaded into memory and ready for predictions.",
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
        model_name=settings.MODEL_NAME,
    )


@router.post(
    "/analyze",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Malaria Cell Image",
    description=(
        "Upload a microscopic blood smear cell image (JPEG/PNG/WEBP). "
        "Returns clinical prediction (Parasitized vs Uninfected) with confidence probabilities."
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
        503: {"model": ErrorResponse, "description": "Inference engine uninitialized"},
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
    """Process uploaded cell image and perform non-blocking ML classification."""
    filename = file.filename or "unknown_image.png"

    # Validate MIME Content Type
    if (
        not file.content_type
        or file.content_type.lower() not in settings.ALLOWED_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        logger.error(f"Failed to read upload buffer for file '{filename}': {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read upload file payload: {exc}",
        ) from exc
    finally:
        await file.close()

    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file payload is empty.",
        )

    # Perform inference via offloaded thread execution
    try:
        prediction = await service.analyze_image(
            image_bytes=bytes(contents),
            filename=filename,
        )
        return prediction
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as exc:
        logger.error(f"Inference pipeline execution error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal inference failure: {exc}",
        ) from exc
