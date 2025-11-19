"""Exception vs message reporting demonstration scenario."""

import rollbar

from ..utils import wait_for_user
from .base import BaseScenario


class ExceptionVsMessageScenario(BaseScenario):
    """Compare exception reporting vs message reporting."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "Exception vs Message"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Compare reporting methods"

    def run(self) -> None:
        """Execute the exception vs message demo."""
        print("\n>> DEMO: Exception vs Message Reporting")
        print("Comparing two reporting methods...\n")

        # First: Message reporting
        print("1. Message Reporting (manual log)")
        print("   - No automatic stack trace")
        print("   - Manual text description")
        print("   - Good for business events\n")
        rollbar.report_message(
            "User attempted invalid operation",
            level="warning",
            extra_data={
                "operation": "delete_admin_account",
                "reason": "insufficient_permissions",
            },
        )

        # Second: Exception reporting
        print("2. Exception Reporting (caught exception)")
        print("   - Automatic stack trace capture")
        print("   - Exception type and message")
        print("   - Good for actual errors\n")

        try:
            # Simulate a division by zero error
            _ = 100 / 0
        except ZeroDivisionError:
            rollbar.report_exc_info(
                extra_data={"operation": "calculate_average", "denominator": 0}
            )

        print("Note: Check Rollbar to see the difference:")
        print("  - Message reports show up as log entries")
        print("  - Exception reports include full stack traces")
        wait_for_user()
