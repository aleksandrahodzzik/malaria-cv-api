"""FastAPI Dependency Injection helpers."""

from fastapi import HTTPException, Request, status

from src.services.inference import MalariaClassifierService


def get_classifier_service(request: Request) -> MalariaClassifierService:
    """Dependency injector providing access to the loaded MalariaClassifierService instance."""
    service: MalariaClassifierService | None = getattr(
        request.app.state, "classifier_service", None
    )

    if service is None or not service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Model inference service is not initialized or still loading.",
        )

    return service
