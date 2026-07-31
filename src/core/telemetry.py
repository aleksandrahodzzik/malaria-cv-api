"""Dependency-free, bounded-cardinality operational metrics."""

from __future__ import annotations

import math
import threading
import time
from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.config import settings

_DURATION_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
_KNOWN_METHODS = frozenset({"DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"})
_UNMATCHED_ROUTE = "__unmatched__"


def _known_raw_routes() -> frozenset[str]:
    versioned = settings.API_V1_STR.rstrip("/")
    api_paths = {
        "/health",
        "/ready",
        "/capabilities",
        "/methodology",
        "/analyze",
        "/analyze/slide",
    }
    return frozenset(
        {
            "/",
            "/docs",
            "/docs/oauth2-redirect",
            "/redoc",
            "/openapi.json",
            "/metrics",
            *api_paths,
            *(f"{versioned}{path}" for path in api_paths),
        }
    )


_KNOWN_RAW_ROUTES = _known_raw_routes()


def route_label(scope: Mapping[str, Any]) -> str:
    """Return a code-controlled route template, never an unrestricted raw path."""
    raw_path = scope.get("path")
    if isinstance(raw_path, str):
        if raw_path == "/assets" or raw_path.startswith("/assets/"):
            return "/assets/{path}"
        if raw_path in _KNOWN_RAW_ROUTES:
            return raw_path

    route = scope.get("route")
    template = getattr(route, "path", None)
    if isinstance(template, str) and template.startswith("/") and len(template) <= 128:
        return template
    return _UNMATCHED_ROUTE


def _method_label(method: str) -> str:
    normalized = method.upper()
    return normalized if normalized in _KNOWN_METHODS else "OTHER"


def _status_class(status_code: int) -> str:
    return f"{status_code // 100}xx" if 100 <= status_code <= 599 else "unknown"


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


class MetricsRegistry:
    """Thread-safe registry for the API metrics defined in the metric catalog."""

    def __init__(self, buckets: tuple[float, ...] = _DURATION_BUCKETS) -> None:
        if not buckets or any(
            bucket <= 0 or not math.isfinite(bucket) for bucket in buckets
        ):
            raise ValueError("Metric duration buckets must be finite and positive.")
        if tuple(sorted(set(buckets))) != buckets:
            raise ValueError("Metric duration buckets must be unique and increasing.")
        self.buckets = buckets
        self._lock = threading.Lock()
        self._active_requests = 0
        self._request_counts: defaultdict[tuple[str, str, str], int] = defaultdict(int)
        self._duration_counts: defaultdict[tuple[str, str], int] = defaultdict(int)
        self._duration_sums: defaultdict[tuple[str, str], float] = defaultdict(float)
        self._duration_buckets: dict[tuple[str, str], list[int]] = {}

    def request_started(self) -> None:
        """Increment the active-request gauge."""
        with self._lock:
            self._active_requests += 1

    def request_finished(
        self,
        *,
        method: str,
        route: str,
        status_code: int,
        duration_seconds: float,
    ) -> None:
        """Record one completed request and decrement the active gauge."""
        safe_method = _method_label(method)
        safe_route = route if route else _UNMATCHED_ROUTE
        safe_duration = max(0.0, duration_seconds)
        duration_key = (safe_method, safe_route)
        with self._lock:
            self._active_requests = max(0, self._active_requests - 1)
            self._request_counts[
                (safe_method, safe_route, _status_class(status_code))
            ] += 1
            self._duration_counts[duration_key] += 1
            self._duration_sums[duration_key] += safe_duration
            bucket_counts = self._duration_buckets.setdefault(
                duration_key, [0] * len(self.buckets)
            )
            for index, upper_bound in enumerate(self.buckets):
                if safe_duration <= upper_bound:
                    bucket_counts[index] += 1

    def render_prometheus(self) -> str:
        """Render an atomic Prometheus text-format snapshot."""
        with self._lock:
            active_requests = self._active_requests
            request_counts = dict(self._request_counts)
            duration_counts = dict(self._duration_counts)
            duration_sums = dict(self._duration_sums)
            duration_buckets = {
                key: list(values) for key, values in self._duration_buckets.items()
            }

        lines = [
            "# HELP malaria_api_active_requests Requests currently being processed.",
            "# TYPE malaria_api_active_requests gauge",
            f"malaria_api_active_requests {active_requests}",
            "# HELP malaria_api_http_requests_total Completed HTTP requests.",
            "# TYPE malaria_api_http_requests_total counter",
        ]
        for (method, route, status_class), count in sorted(request_counts.items()):
            labels = (
                f'method="{_escape_label(method)}",'
                f'route="{_escape_label(route)}",'
                f'status_class="{_escape_label(status_class)}"'
            )
            lines.append(f"malaria_api_http_requests_total{{{labels}}} {count}")

        lines.extend(
            [
                "# HELP malaria_api_http_request_duration_seconds "
                "HTTP request latency.",
                "# TYPE malaria_api_http_request_duration_seconds histogram",
            ]
        )
        for method, route in sorted(duration_counts):
            escaped_method = _escape_label(method)
            escaped_route = _escape_label(route)
            prefix = f'method="{escaped_method}",route="{escaped_route}"'
            for upper_bound, count in zip(
                self.buckets, duration_buckets[(method, route)], strict=True
            ):
                lines.append(
                    "malaria_api_http_request_duration_seconds_bucket"
                    f'{{{prefix},le="{upper_bound:g}"}} {count}'
                )
            total_count = duration_counts[(method, route)]
            lines.append(
                "malaria_api_http_request_duration_seconds_bucket"
                f'{{{prefix},le="+Inf"}} {total_count}'
            )
            lines.append(
                "malaria_api_http_request_duration_seconds_sum"
                f"{{{prefix}}} {duration_sums[(method, route)]:.9g}"
            )
            lines.append(
                "malaria_api_http_request_duration_seconds_count"
                f"{{{prefix}}} {total_count}"
            )
        return "\n".join(lines) + "\n"


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    """Collect HTTP counters and latency with bounded, non-sensitive labels."""

    def __init__(
        self,
        app: Any,
        *,
        registry: MetricsRegistry,
        enabled: bool,
    ) -> None:
        super().__init__(app)
        self.registry = registry
        self.enabled = enabled

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not self.enabled:
            return await call_next(request)

        self.registry.request_started()
        started_at = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            self.registry.request_finished(
                method=request.method,
                route=route_label(request.scope),
                status_code=status_code,
                duration_seconds=time.perf_counter() - started_at,
            )
