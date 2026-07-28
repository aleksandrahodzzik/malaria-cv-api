"""Custom ASGI Middleware for request tracking and performance monitoring."""

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logger
logger = logging.getLogger("malaria_api.middleware")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """ASGI Middleware to assign unique Request-IDs and compute processing latency."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract existing Request-ID header or generate new UUID4
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"Request failed | ID: {request_id} | Path: {request.url.path} | "
                f"Latency: {duration_ms:.2f}ms | Error: {exc}"
            )
            raise

        process_time_ms = (time.perf_counter() - start_time) * 1000.0

        # Inject tracing headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{process_time_ms:.2f}"

        logger.info(
            f"Method: {request.method} | Path: {request.url.path} | "
            f"Status: {response.status_code} | Latency: {process_time_ms:.2f}ms | ID: {request_id}"
        )

        return response
