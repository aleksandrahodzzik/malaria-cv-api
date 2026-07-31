"""Privacy, cardinality and access-control tests for operational metrics."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import Request
from pydantic import SecretStr
from starlette.testclient import TestClient

from src.core.config import settings
from src.core.telemetry import MetricsRegistry, RequestMetricsMiddleware, route_label
from src.main import create_application


def test_metrics_registry_renders_counter_histogram_and_active_gauge() -> None:
    registry = MetricsRegistry(buckets=(0.01, 0.1, 1.0))
    registry.request_started()
    registry.request_started()
    registry.request_finished(
        method="get",
        route="/api/v1/health",
        status_code=200,
        duration_seconds=0.05,
    )

    rendered = registry.render_prometheus()
    assert "malaria_api_active_requests 1" in rendered
    assert (
        'malaria_api_http_requests_total{method="GET",'
        'route="/api/v1/health",status_class="2xx"} 1'
    ) in rendered
    assert (
        'malaria_api_http_request_duration_seconds_bucket{method="GET",'
        'route="/api/v1/health",le="0.01"} 0'
    ) in rendered
    assert (
        'malaria_api_http_request_duration_seconds_bucket{method="GET",'
        'route="/api/v1/health",le="0.1"} 1'
    ) in rendered
    assert (
        'malaria_api_http_request_duration_seconds_count{method="GET",'
        'route="/api/v1/health"} 1'
    ) in rendered


@pytest.mark.parametrize(
    "buckets",
    [(), (0.0,), (1.0, 0.5), (1.0, 1.0)],
)
def test_metrics_registry_rejects_invalid_buckets(
    buckets: tuple[float, ...],
) -> None:
    with pytest.raises(ValueError, match="buckets"):
        MetricsRegistry(buckets=buckets)


def test_route_labels_are_templates_or_bounded_fallbacks() -> None:
    assert route_label({"route": SimpleNamespace(path="/items/{item_id}")}) == (
        "/items/{item_id}"
    )
    assert route_label({"path": "/api/v1/health"}) == "/api/v1/health"
    assert route_label({"path": "/assets/user-controlled-name.png"}) == (
        "/assets/{path}"
    )
    assert route_label({"path": "/patient-name-or-secret"}) == "__unmatched__"
    assert route_label({"path": 123}) == "__unmatched__"


@pytest.mark.asyncio
async def test_metrics_middleware_records_failure_and_releases_gauge() -> None:
    registry = MetricsRegistry()
    middleware = RequestMetricsMiddleware(
        lambda *_: None,  # type: ignore[arg-type]
        registry=registry,
        enabled=True,
    )
    request = Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "CUSTOM",
            "scheme": "http",
            "path": "/secret-in-path",
            "raw_path": b"/secret-in-path",
            "query_string": b"",
            "headers": [],
            "client": ("test", 1),
            "server": ("test", 80),
        }
    )

    async def fail(_: Request) -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await middleware.dispatch(request, fail)  # type: ignore[arg-type]

    rendered = registry.render_prometheus()
    assert "malaria_api_active_requests 0" in rendered
    assert 'method="OTHER",route="__unmatched__",status_class="5xx"' in rendered
    assert "secret-in-path" not in rendered


def test_disabled_metrics_endpoint_is_hidden() -> None:
    application = create_application()
    with TestClient(application) as client:
        response = client.get("/metrics")
        schema = client.get("/openapi.json").json()
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
    assert "/metrics" not in schema["paths"]


def test_metrics_endpoint_requires_dedicated_key_and_hides_raw_paths() -> None:
    metrics_secret = SecretStr("m" * 32)
    with (
        patch.object(settings, "METRICS_ENABLED", True),
        patch.object(settings, "METRICS_API_KEY", metrics_secret),
    ):
        application = create_application()
        with TestClient(application) as client:
            assert client.get("/api/v1/health").status_code == 200
            assert client.get("/patient-name-or-secret").status_code == 404
            missing = client.get("/metrics")
            invalid = client.get("/metrics", headers={"X-Metrics-Key": "invalid"})
            authorized = client.get("/metrics", headers={"X-Metrics-Key": "m" * 32})

    assert missing.status_code == 401
    assert missing.headers["WWW-Authenticate"] == "ApiKey"
    assert invalid.status_code == 403
    assert authorized.status_code == 200
    assert authorized.headers["content-type"].startswith("text/plain; version=0.0.4")
    assert "malaria_api_active_requests 1" in authorized.text
    assert 'route="/api/v1/health"' in authorized.text
    assert 'route="__unmatched__"' in authorized.text
    assert "patient-name-or-secret" not in authorized.text
