"""Privacy and structure tests for operational JSON logs."""

import json
import logging

from src.core.logging import PrivacyJSONFormatter, safe_extra


def test_json_formatter_emits_allowlisted_structured_event() -> None:
    record = logging.LogRecord(
        name="malaria_api.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Request completed.",
        args=(),
        exc_info=None,
    )
    for key, value in safe_extra(
        event="request_completed",
        request_id="request-1",
        method="GET",
        path="/health",
        status=200,
        duration_ms=1.25,
        authorization="Bearer secret",
    ).items():
        setattr(record, key, value)

    payload = json.loads(PrivacyJSONFormatter().format(record))
    assert payload["event"] == "request_completed"
    assert payload["request_id"] == "request-1"
    assert payload["status"] == 200
    assert "authorization" not in payload
    assert "pathname" not in payload
    assert "exc_info" not in payload


def test_json_formatter_escapes_control_characters() -> None:
    record = logging.LogRecord(
        name="malaria_api.test",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="line one\nline two\r",
        args=(),
        exc_info=None,
    )
    encoded = PrivacyJSONFormatter().format(record)
    payload = json.loads(encoded)
    assert payload["message"] == "line one\\nline two\\r"
    assert encoded.count("\n") == 0


def test_safe_extra_rejects_complex_and_unknown_values() -> None:
    assert safe_extra(event="test", unknown="secret", status=[200]) == {"event": "test"}
