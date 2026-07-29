"""Privacy-conscious structured logging for the service."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from src.core.config import settings

_STANDARD_RECORD_FIELDS = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    }
)
_ALLOWED_EXTRA_FIELDS = frozenset(
    {
        "event",
        "request_id",
        "method",
        "path",
        "status",
        "duration_ms",
        "error_type",
        "model_status",
    }
)


class PrivacyJSONFormatter(logging.Formatter):
    """Serialize an allowlisted event record without tracebacks or arguments."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": settings.PROJECT_NAME,
            "service_version": settings.VERSION,
            "message": record.getMessage().replace("\r", "\\r").replace("\n", "\\n"),
        }
        for field in _ALLOWED_EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(level: int = logging.INFO) -> None:
    """Configure one JSON stdout handler unless the process is already configured."""
    root = logging.getLogger()
    if any(
        isinstance(handler.formatter, PrivacyJSONFormatter) for handler in root.handlers
    ):
        root.setLevel(level)
        return

    handler = logging.StreamHandler()
    handler.setFormatter(PrivacyJSONFormatter())
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def safe_extra(**values: Any) -> dict[str, Any]:
    """Return only bounded structured fields accepted by the formatter."""
    return {
        key: value
        for key, value in values.items()
        if key in _ALLOWED_EXTRA_FIELDS
        and key not in _STANDARD_RECORD_FIELDS
        and isinstance(value, (str, int, float, bool))
    }
