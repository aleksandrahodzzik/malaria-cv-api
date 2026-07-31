"""Centralized, stable and privacy-safe API error handling."""

import logging
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.telemetry import route_label
from src.schemas.payload import ErrorResponse
from src.services.qc import QualityControlError

logger = logging.getLogger("malaria_api.errors")

_STATUS_CODES: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "INVALID_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHENTICATED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_413_CONTENT_TOO_LARGE: "PAYLOAD_TOO_LARGE",
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "UNSUPPORTED_MEDIA_TYPE",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "VALIDATION_ERROR",
    status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMITED",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_ERROR",
    status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
    status.HTTP_504_GATEWAY_TIMEOUT: "INFERENCE_TIMEOUT",
}


def _request_id(request: Request) -> str | None:
    value: Any = getattr(request.state, "request_id", None)
    return value if isinstance(value, str) else None


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    detail: str,
    headers: Mapping[str, str] | None = None,
    reasons: list[str] | None = None,
    qc_metrics: dict[str, float | int] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        code=code,
        detail=detail,
        request_id=_request_id(request),
        reasons=reasons,
        qc_metrics=qc_metrics,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json", exclude_none=True),
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register one externally stable error envelope for the application."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return _error_response(
            request,
            status_code=exc.status_code,
            code=_STATUS_CODES.get(exc.status_code, "REQUEST_FAILED"),
            detail=detail,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.info(
            "Request validation failed | ID: %s | Path: %s | Errors: %s",
            _request_id(request),
            route_label(request.scope),
            len(exc.errors()),
        )
        return _error_response(
            request,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="VALIDATION_ERROR",
            detail="Request validation failed.",
        )

    @app.exception_handler(QualityControlError)
    async def quality_control_exception_handler(
        request: Request, exc: QualityControlError
    ) -> JSONResponse:
        return _error_response(
            request,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code=exc.primary_reason,
            detail="Image rejected by the pre-inference quality-control policy.",
            reasons=[reason.value for reason in exc.reasons],
            qc_metrics=exc.metrics.as_dict(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled request failure | ID: %s | Path: %s",
            _request_id(request),
            route_label(request.scope),
            exc_info=exc,
        )
        return _error_response(
            request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR",
            detail="An unexpected internal error occurred.",
        )
