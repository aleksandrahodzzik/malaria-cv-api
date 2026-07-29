"""Rate limiting and API-key authentication tests."""

import hashlib
import json
import math
from typing import Any
from unittest.mock import patch

import pytest
from fastapi import Request
from pydantic import SecretStr
from starlette.testclient import TestClient

from src.core.middleware import (
    RequestBodyLimitMiddleware,
    RequestTrackingMiddleware,
    _RequestBodyTooLarge,
)
from src.core.ratelimit import RateLimitMiddleware, SlidingWindowRateLimiter
from src.main import app


def test_sliding_window_admission_and_expiration() -> None:
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=10)
    assert limiter.check("client", now=0).remaining == 1
    assert limiter.check("client", now=1).remaining == 0
    denied = limiter.check("client", now=2)
    assert denied.allowed is False
    assert denied.retry_after_seconds == 8
    assert limiter.check("client", now=10.1).allowed is True


@pytest.mark.parametrize(
    ("limit", "window"),
    [(0, 1.0), (1, 0.0), (1, math.inf)],
)
def test_rate_limiter_rejects_invalid_configuration(
    limit: int,
    window: float,
) -> None:
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(limit=limit, window_seconds=window)

    with pytest.raises(ValueError, match="max_keys"):
        SlidingWindowRateLimiter(limit=1, window_seconds=1, max_keys=0)


def test_rate_limiter_bounds_client_key_cardinality() -> None:
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60, max_keys=1)
    assert limiter.check("first", now=0).allowed is True
    assert limiter.check("second", now=0).allowed is True
    assert limiter.check("third", now=0).allowed is False


def test_middleware_uses_only_trusted_api_key_identity() -> None:
    digest = hashlib.sha256(b"approved").hexdigest()
    middleware = RateLimitMiddleware(
        lambda *_: None,  # type: ignore[arg-type]
        limiter=SlidingWindowRateLimiter(limit=1, window_seconds=60),
        limited_paths={"/analyze"},
        trusted_api_key_digests={digest},
    )
    base: dict[str, Any] = {
        "type": "http",
        "client": ("127.0.0.1", 1),
    }
    trusted = {**base, "headers": [(b"x-api-key", b"approved")]}
    fake = {**base, "headers": [(b"x-api-key", b"rotating-fake")]}
    no_key = {**base, "headers": []}
    assert middleware._client_key(trusted) == f"key:{digest}"  # type: ignore[arg-type]
    assert middleware._client_key(fake) == "ip:127.0.0.1"  # type: ignore[arg-type]
    assert middleware._client_key(no_key) == "ip:127.0.0.1"  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_rate_limit_middleware_rejects_with_stable_contract() -> None:
    calls = 0
    sent: list[dict[str, Any]] = []

    async def downstream(scope: Any, receive: Any, send: Any) -> None:
        nonlocal calls
        calls += 1

    middleware = RateLimitMiddleware(
        downstream,
        limiter=SlidingWindowRateLimiter(limit=1, window_seconds=60),
        limited_paths={"/analyze"},
    )
    scope: dict[str, Any] = {
        "type": "http",
        "method": "POST",
        "path": "/analyze",
        "headers": [(b"x-api-key", b"secret")],
        "client": ("127.0.0.1", 1000),
        "state": {"request_id": "rate-id"},
    }

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await middleware(scope, receive, send)
    await middleware(scope, receive, send)
    assert calls == 1
    assert sent[0]["status"] == 429
    headers = dict(sent[0]["headers"])
    assert headers[b"retry-after"] == b"60"
    assert headers[b"x-ratelimit-limit"] == b"1"
    assert json.loads(sent[1]["body"]) == {
        "code": "RATE_LIMITED",
        "detail": "Inference request quota exceeded. Retry later.",
        "request_id": "rate-id",
    }


@pytest.mark.asyncio
async def test_rate_limit_bypass_and_ip_fallback() -> None:
    called = 0

    async def downstream(scope: Any, receive: Any, send: Any) -> None:
        nonlocal called
        called += 1

    middleware = RateLimitMiddleware(
        downstream,
        limiter=SlidingWindowRateLimiter(limit=1, window_seconds=60),
        limited_paths={"/analyze"},
        enabled=False,
    )

    async def noop(*args: Any) -> None:
        return None

    base = {
        "type": "lifespan",
        "method": "POST",
        "path": "/analyze",
        "headers": [],
        "client": None,
    }
    await middleware(base, noop, noop)
    middleware.enabled = True
    await middleware({**base, "type": "http", "method": "GET"}, noop, noop)
    await middleware({**base, "type": "http", "path": "/health"}, noop, noop)
    await middleware({**base, "type": "http"}, noop, noop)
    assert called == 4


def test_api_key_missing_invalid_and_valid() -> None:
    fake_classifier = type(
        "ReadyService",
        (),
        {"is_ready": lambda self: True},
    )()
    with (
        patch("src.api.dependencies.settings.API_KEY_REQUIRED", True),
        patch(
            "src.api.dependencies.settings.API_KEYS",
            [SecretStr("approved-secret")],
        ),
        TestClient(app) as client,
    ):
        app.state.classifier_service = fake_classifier
        missing = client.post("/api/v1/analyze")
        invalid = client.post(
            "/api/v1/analyze",
            headers={"X-API-Key": "wrong"},
        )
        valid = client.post(
            "/api/v1/analyze",
            headers={"X-API-Key": "approved-secret"},
        )
    assert missing.status_code == 401
    assert missing.headers["WWW-Authenticate"] == "ApiKey"
    assert invalid.status_code == 403
    assert valid.status_code == 422


def test_request_body_limit_configuration_and_header_parsing() -> None:
    async def downstream(scope: Any, receive: Any, send: Any) -> None:
        return None

    with pytest.raises(ValueError, match="positive"):
        RequestBodyLimitMiddleware(
            downstream,
            max_body_bytes=0,
            limited_paths={"/analyze"},
        )
    assert (
        RequestBodyLimitMiddleware._content_length(
            {"headers": [(b"content-length", b"invalid")]}  # type: ignore[arg-type]
        )
        is None
    )
    assert (
        RequestBodyLimitMiddleware._content_length(
            {"headers": [(b"content-length", b"-1")]}  # type: ignore[arg-type]
        )
        is None
    )


@pytest.mark.asyncio
async def test_body_limit_reraises_after_response_started() -> None:
    sent: list[dict[str, Any]] = []

    async def downstream(scope: Any, receive: Any, send: Any) -> None:
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await receive()

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"too-large", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    middleware = RequestBodyLimitMiddleware(
        downstream,
        max_body_bytes=2,
        limited_paths={"/analyze"},
    )
    with pytest.raises(_RequestBodyTooLarge):
        await middleware(
            {
                "type": "http",
                "method": "POST",
                "path": "/analyze",
                "headers": [],
            },  # type: ignore[arg-type]
            receive,  # type: ignore[arg-type]
            send,  # type: ignore[arg-type]
        )
    assert sent[0]["status"] == 200


@pytest.mark.asyncio
async def test_request_tracking_reraises_downstream_exception() -> None:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/explode",
        "raw_path": b"/explode",
        "query_string": b"",
        "headers": [],
        "client": ("test", 1),
        "server": ("test", 80),
    }
    request = Request(scope)  # type: ignore[arg-type]

    async def downstream(_: Request) -> Any:
        raise RuntimeError("boom")

    middleware = RequestTrackingMiddleware(lambda *_: None)  # type: ignore[arg-type]
    with pytest.raises(RuntimeError, match="boom"):
        await middleware.dispatch(request, downstream)
