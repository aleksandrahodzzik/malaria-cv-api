"""Main FastAPI Application Entrypoint with Lifespan Context Manager."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.core.config import settings
from src.core.middleware import RequestTrackingMiddleware
from src.services.inference import MalariaClassifierService

logger = logging.getLogger("malaria_api.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI Lifespan Manager.

    Loads the HuggingFace ViT Model ONLY inside startup lifespan,
    storing the service instance in `app.state.classifier_service`.
    """
    logger.info("Initializing Malaria Cell Classification Microservice lifespan...")

    # Initialize ML Inference service singleton
    classifier_service = MalariaClassifierService(model_name=settings.MODEL_NAME)

    try:
        classifier_service.load_model()
        app.state.classifier_service = classifier_service
        logger.info("Lifespan startup complete: ML Model ready for requests.")
    except RuntimeError as exc:
        logger.critical(f"Failed to load ML Model during startup lifespan: {exc}")
        app.state.classifier_service = None

    yield  # Application processes requests here

    # Lifespan Shutdown Teardown
    logger.info("Tearing down lifespan context and cleaning up resources...")
    app.state.classifier_service = None


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
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register custom observability and tracing middleware
    app.add_middleware(RequestTrackingMiddleware)

    # Mount API routers (both at root for health/ready and under API v1 prefix)
    app.include_router(api_router, tags=["Malaria Cell Classification API"])
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
