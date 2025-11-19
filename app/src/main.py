"""Module to test Rollbar integration."""

import rollbar

from .rollbar import setup_rollbar

setup_rollbar()

rollbar.report_message(
    "Rollbar is configured correctly!",
    level="info",
    extra_data={"trace_id": "test_trace_id"},
    payload_data={"foo_key": "bar", "bar_key": "baz"},
)

try:
    a: None = None
    a.hello()  # type: ignore[attr-defined]
except Exception:
    rollbar.report_exc_info()
