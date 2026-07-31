"""FastAPI dependency injection and endpoint authentication helpers."""

import secrets
from typing import Annotated

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from src.core.config import settings
from src.services.inference import MalariaClassifierService

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_metrics_key_header = APIKeyHeader(name="X-Metrics-Key", auto_error=False)


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


def require_api_key(
    api_key: Annotated[str | None, Security(_api_key_header)],
) -> None:
    """Require a constant-time API-key match only when the policy is enabled."""
    if not settings.API_KEY_REQUIRED:
        return
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-API-Key is required.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    accepted = any(
        secrets.compare_digest(api_key, configured.get_secret_value())
        for configured in settings.API_KEYS
    )
    if not accepted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The supplied API key is not authorized.",
        )


def require_metrics_key(
    metrics_key: Annotated[str | None, Security(_metrics_key_header)],
) -> None:
    """Protect internal telemetry with a dedicated constant-time secret."""
    if not settings.METRICS_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    configured = settings.METRICS_API_KEY
    if metrics_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-Metrics-Key is required.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    if configured is None or not secrets.compare_digest(
        metrics_key, configured.get_secret_value()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The supplied metrics key is not authorized.",
        )
