"""Main FastAPI Application Entrypoint with Lifespan Context Manager."""

import hashlib
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router as api_router
from src.core.config import settings
from src.core.errors import register_exception_handlers
from src.core.logging import configure_logging, safe_extra
from src.core.manifest import ModelArtifactVerificationError
from src.core.middleware import (
    LegacyRouteDeprecationMiddleware,
    RequestBodyLimitMiddleware,
    RequestTrackingMiddleware,
)
from src.core.ratelimit import RateLimitMiddleware, SlidingWindowRateLimiter
from src.services.inference import MalariaClassifierService

logger = logging.getLogger("malaria_api.main")
UI_ROOT = Path(__file__).resolve().parent / "ui"
configure_logging(getattr(logging, settings.LOG_LEVEL))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI Lifespan Manager.

    Loads the HuggingFace ViT Model ONLY inside startup lifespan,
    storing the service instance in `app.state.classifier_service`.
    """
    logger.info("Initializing Malaria Cell Classification Microservice lifespan...")

    # Initialize ML Inference service singleton
    classifier_service = MalariaClassifierService(model_name=settings.MODEL_NAME)

    if not settings.MODEL_NAME.strip():
        logger.warning(
            "No approved model configured. The API will remain not ready until "
            "MODEL_NAME is provided."
        )
        app.state.classifier_service = None
        app.state.model_error_code = "MODEL_NOT_CONFIGURED"
        yield
        app.state.classifier_service = None
        return

    try:
        classifier_service.load_model()
        app.state.classifier_service = classifier_service
        app.state.model_error_code = None
        logger.info("Lifespan startup complete: ML Model ready for requests.")
    except ModelArtifactVerificationError as exc:
        logger.critical(
            "Model artifact trust verification failed.",
            extra=safe_extra(
                event="model_artifact_not_verified",
                error_type=type(exc).__name__,
                model_status="not_ready",
            ),
        )
        app.state.classifier_service = None
        app.state.model_error_code = ModelArtifactVerificationError.code
    except RuntimeError as exc:
        logger.critical(
            "Approved model initialization failed.",
            extra=safe_extra(
                event="model_initialization_failed",
                error_type=type(exc).__name__,
                model_status="not_ready",
            ),
        )
        app.state.classifier_service = None
        app.state.model_error_code = "MODEL_INITIALIZATION_FAILED"

    yield  # Application processes requests here

    # Lifespan Shutdown Teardown
    logger.info("Tearing down lifespan context and cleaning up resources...")
    app.state.classifier_service = None
    app.state.model_error_code = "SERVICE_STOPPED"


def create_application() -> FastAPI:
    """Factory function creating configured FastAPI application instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS is opt-in and restricted to explicitly configured origins.
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=[
                "Accept",
                "Content-Type",
                "X-API-Key",
                "X-Request-ID",
            ],
        )

    # Add the body boundary first so request tracking remains the outer layer and
    # attaches correlation/security headers to early 413 responses.
    max_request_body_bytes = (
        settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        + settings.MAX_MULTIPART_OVERHEAD_BYTES
    )
    app.add_middleware(
        RequestBodyLimitMiddleware,
        max_body_bytes=max_request_body_bytes,
        limited_paths={"/analyze", f"{settings.API_V1_STR}/analyze"},
    )
    app.add_middleware(
        RequestBodyLimitMiddleware,
        max_body_bytes=settings.MAX_SLIDE_UPLOAD_SIZE_MB * 1024 * 1024,
        limited_paths={
            "/analyze/slide",
            f"{settings.API_V1_STR}/analyze/slide",
        },
    )
    app.add_middleware(
        LegacyRouteDeprecationMiddleware,
        successors={
            "/analyze": f"{settings.API_V1_STR}/analyze",
            "/analyze/slide": f"{settings.API_V1_STR}/analyze/slide",
            "/ready": f"{settings.API_V1_STR}/ready",
            "/capabilities": f"{settings.API_V1_STR}/capabilities",
        },
    )
    app.add_middleware(
        RateLimitMiddleware,
        limiter=SlidingWindowRateLimiter(
            limit=settings.RATE_LIMIT_REQUESTS,
            window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
            max_keys=settings.RATE_LIMIT_MAX_KEYS,
        ),
        limited_paths={
            "/analyze",
            "/analyze/slide",
            f"{settings.API_V1_STR}/analyze",
            f"{settings.API_V1_STR}/analyze/slide",
        },
        enabled=settings.RATE_LIMIT_ENABLED,
        trusted_api_key_digests={
            hashlib.sha256(key.get_secret_value().encode("utf-8")).hexdigest()
            for key in settings.API_KEYS
        },
    )

    # Register custom observability and tracing middleware.
    app.add_middleware(RequestTrackingMiddleware)
    register_exception_handlers(app)

    app.mount("/assets", StaticFiles(directory=UI_ROOT), name="assets")

    @app.get(
        "/",
        include_in_schema=False,
        response_class=FileResponse,
    )
    async def research_ui() -> FileResponse:
        """Serve the dependency-free research interface."""
        return FileResponse(UI_ROOT / "index.html", media_type="text/html")

    # Compatibility aliases remain callable but are hidden from the canonical
    # OpenAPI surface and carry deprecation/successor headers.
    app.include_router(
        api_router,
        tags=["Malaria Cell Classification API"],
        include_in_schema=False,
    )
    app.include_router(api_router, prefix=settings.API_V1_STR, tags=["API v1"])

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
