"""FastAPI Dependency Injection helpers."""

from fastapi import HTTPException, Request, status

from src.services.inference import MalariaClassifierService


def get_classifier_service(request: Request) -> MalariaClassifierService:
    """Provide the loaded classifier service through FastAPI dependency injection."""
    service: MalariaClassifierService | None = getattr(
        request.app.state, "classifier_service", None
    )

    if service is None or not service.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The approved model is not configured, loaded, or ready.",
            headers={"Retry-After": "5"},
        )

    return service
