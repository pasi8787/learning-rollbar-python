"""Multiple related errors demonstration scenario."""

import rollbar

from ..utils import wait_for_user
from .base import BaseScenario


class MultipleErrorsScenario(BaseScenario):
    """Send multiple related errors to demonstrate grouping."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "Multiple Errors"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Send a sequence of related errors"

    def run(self) -> None:
        """Execute the multiple errors demo."""
        print("\n>> DEMO: Multiple Related Errors")
        print("Sending a sequence of related errors...\n")

        print("Simulating a cascade of failures:")

        # Error 1: Database connection issue
        print("  1. Database connection slow")
        rollbar.report_message(
            "Database connection latency detected",
            level="warning",
            extra_data={
                "latency_ms": 2500,
                "threshold_ms": 1000,
                "db_host": "db-primary.example.com",
            },
        )

        # Error 2: Query timeout
        print("  2. Query timeout")
        try:
            # Simulate a timeout error
            raise TimeoutError("Query exceeded 5 second timeout")
        except TimeoutError:
            rollbar.report_exc_info(
                extra_data={"query": "SELECT * FROM large_table", "timeout_seconds": 5}
            )

        # Error 3: Service degradation
        print("  3. Service degradation warning")
        rollbar.report_message(
            "Service performance degraded",
            level="error",
            extra_data={
                "service": "api_server",
                "response_time_ms": 8000,
                "error_rate": 0.15,
            },
        )

        # Error 4: Circuit breaker triggered
        print("  4. Circuit breaker triggered")
        rollbar.report_message(
            "Circuit breaker opened for database",
            level="critical",
            extra_data={"failures": 5, "threshold": 3, "timeout_seconds": 60},
        )

        print("\nNote: These errors will appear in Rollbar with timestamps.")
        print("You can track the sequence of events leading to the critical failure.")
        wait_for_user()
