"""Custom ASGI Middleware for request tracking and performance monitoring."""

import logging
import re
import time
import uuid
from collections.abc import Collection, Mapping
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core.config import settings
from src.core.logging import safe_extra
from src.core.telemetry import route_label

logger = logging.getLogger("malaria_api.middleware")

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")


class _RequestBodyTooLarge(Exception):
    """Signal that a streamed request crossed the configured byte limit."""


class RequestBodyLimitMiddleware:
    """Reject oversized analysis bodies before multipart parsing.

    The endpoint-level file limit remains authoritative for the uploaded file.
    This earlier transport boundary also covers multipart framing and requests
    without a ``Content-Length`` header.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        max_body_bytes: int,
        limited_paths: Collection[str],
    ) -> None:
        if max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be positive.")
        self.app = app
        self.max_body_bytes = max_body_bytes
        self.limited_paths = frozenset(limited_paths)

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") not in self.limited_paths
        ):
            await self.app(scope, receive, send)
            return

        content_length = self._content_length(scope)
        if content_length is not None and content_length > self.max_body_bytes:
            await self._reject(scope, receive, send)
            return

        received_bytes = 0
        response_started = False

        async def limited_receive() -> Message:
            nonlocal received_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_body_bytes:
                    raise _RequestBodyTooLarge
            return message

        async def tracked_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)
        except _RequestBodyTooLarge:
            if response_started:
                raise
            await self._reject(scope, receive, send)

    @staticmethod
    def _content_length(scope: Scope) -> int | None:
        for raw_name, raw_value in scope.get("headers", []):
            if raw_name.lower() != b"content-length":
                continue
            try:
                value = int(raw_value)
            except ValueError:
                return None
            return value if value >= 0 else None
        return None

    @staticmethod
    async def _reject(scope: Scope, receive: Receive, send: Send) -> None:
        state: Any = scope.get("state", {})
        request_id = state.get("request_id") if isinstance(state, dict) else None
        response = JSONResponse(
            status_code=413,
            content={
                "code": "PAYLOAD_TOO_LARGE",
                "detail": "Request body exceeds the maximum allowed size.",
                "request_id": request_id if isinstance(request_id, str) else None,
            },
        )
        await response(scope, receive, send)


class LegacyRouteDeprecationMiddleware:
    """Attach RFC-style deprecation metadata to compatibility API aliases."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        successors: Mapping[str, str],
    ) -> None:
        self.app = app
        self.successors = dict(successors)

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        successor = (
            self.successors.get(scope.get("path", ""))
            if scope["type"] == "http"
            else None
        )
        if successor is None:
            await self.app(scope, receive, send)
            return

        async def deprecation_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        (b"deprecation", b"true"),
                        (
                            b"link",
                            f'<{successor}>; rel="successor-version"'.encode("ascii"),
                        ),
                    ]
                )
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, deprecation_send)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """ASGI Middleware to assign unique Request-IDs and compute processing latency."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Accept a client correlation ID only when it is bounded and log-safe.
        candidate = request.headers.get("X-Request-ID", "")
        request_id = (
            candidate if _REQUEST_ID_PATTERN.fullmatch(candidate) else str(uuid.uuid4())
        )
        request.state.request_id = request_id

        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                "Request failed.",
                extra=safe_extra(
                    event="request_failed",
                    request_id=request_id,
                    method=request.method,
                    path=route_label(request.scope),
                    duration_ms=round(duration_ms, 2),
                    error_type=type(exc).__name__,
                ),
            )
            raise

        process_time_ms = (time.perf_counter() - start_time) * 1000.0

        # Inject tracing headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{process_time_ms:.2f}"
        response.headers["X-Service-Version"] = settings.VERSION
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        if request.url.path.startswith("/api/") or request.url.path in {
            "/health",
            "/ready",
            "/analyze",
        }:
            response.headers["Cache-Control"] = "no-store"
        if request.url.path == "/" or request.url.path.startswith("/assets/"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; img-src 'self' blob: data:; "
                "connect-src 'self'; script-src 'self'; style-src 'self'; "
                "base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
            )

        logger.info(
            "Request completed.",
            extra=safe_extra(
                event="request_completed",
                request_id=request_id,
                method=request.method,
                path=route_label(request.scope),
                status=response.status_code,
                duration_ms=round(process_time_ms, 2),
            ),
        )

        return response
