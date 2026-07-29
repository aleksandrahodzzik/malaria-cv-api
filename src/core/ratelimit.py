"""Bounded in-memory sliding-window rate limiter for inference endpoints."""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections import defaultdict, deque
from collections.abc import Collection
from dataclasses import dataclass

from starlette.types import ASGIApp, Receive, Scope, Send


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    """Admission result and response metadata."""

    allowed: bool
    remaining: int
    retry_after_seconds: int


class SlidingWindowRateLimiter:
    """Per-process exact sliding-window admission policy."""

    def __init__(
        self,
        *,
        limit: int,
        window_seconds: float,
        max_keys: int = 10_000,
    ) -> None:
        if limit <= 0:
            raise ValueError("limit must be positive.")
        if window_seconds <= 0 or not math.isfinite(window_seconds):
            raise ValueError("window_seconds must be finite and positive.")
        if max_keys <= 0:
            raise ValueError("max_keys must be positive.")
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._events: defaultdict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, *, now: float | None = None) -> RateLimitDecision:
        current = time.monotonic() if now is None else now
        storage_key = key
        if key not in self._events and len(self._events) >= self.max_keys:
            storage_key = "__overflow__"
        events = self._events[storage_key]
        cutoff = current - self.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()

        if len(events) >= self.limit:
            retry_after = max(1, math.ceil(events[0] + self.window_seconds - current))
            return RateLimitDecision(False, 0, retry_after)

        events.append(current)
        return RateLimitDecision(True, self.limit - len(events), 0)


class RateLimitMiddleware:
    """Reject excess POST requests before multipart parsing and inference."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        limiter: SlidingWindowRateLimiter,
        limited_paths: Collection[str],
        enabled: bool = True,
        trusted_api_key_digests: Collection[str] = (),
    ) -> None:
        self.app = app
        self.limiter = limiter
        self.limited_paths = frozenset(limited_paths)
        self.enabled = enabled
        self.trusted_api_key_digests = frozenset(trusted_api_key_digests)

    @staticmethod
    def _header(scope: Scope, name: bytes) -> bytes | None:
        for raw_name, raw_value in scope.get("headers", []):
            if raw_name.lower() == name:
                return bytes(raw_value)
        return None

    def _client_key(self, scope: Scope) -> str:
        api_key = self._header(scope, b"x-api-key")
        if api_key:
            digest = hashlib.sha256(api_key).hexdigest()
            if digest in self.trusted_api_key_digests:
                return "key:" + digest
        client = scope.get("client")
        host = client[0] if client else "unknown"
        return f"ip:{host}"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            not self.enabled
            or scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") not in self.limited_paths
        ):
            await self.app(scope, receive, send)
            return

        decision = self.limiter.check(self._client_key(scope))
        if decision.allowed:
            await self.app(scope, receive, send)
            return

        state = scope.get("state", {})
        request_id = state.get("request_id") if isinstance(state, dict) else None
        payload = json.dumps(
            {
                "code": "RATE_LIMITED",
                "detail": "Inference request quota exceeded. Retry later.",
                "request_id": request_id if isinstance(request_id, str) else None,
            }
        ).encode("utf-8")
        headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(payload)).encode("ascii")),
            (
                b"retry-after",
                str(decision.retry_after_seconds).encode("ascii"),
            ),
            (b"x-ratelimit-limit", str(self.limiter.limit).encode("ascii")),
            (b"x-ratelimit-remaining", b"0"),
        ]
        await send(
            {
                "type": "http.response.start",
                "status": 429,
                "headers": headers,
            }
        )
        await send({"type": "http.response.body", "body": payload})
