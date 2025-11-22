"""Custom data demonstration scenario."""

import rollbar

from ..utils import wait_for_user
from .base import BaseScenario


class CustomDataScenario(BaseScenario):
    """Demonstrate adding custom metadata to errors."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "Custom Data"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Attach metadata to error reports"

    def run(self) -> None:
        """Execute the custom data demo."""
        print("\n>> DEMO: Custom Data")
        print("Sending errors with rich custom metadata...\n")

        scenarios = [
            {
                "message": "Payment processing failed",
                "custom": {
                    "payment_id": "pay_abc123",
                    "payment_method": "credit_card",
                    "amount": 149.99,
                    "currency": "USD",
                    "merchant_id": "merchant_xyz",
                    "attempt_number": 3,
                },
            },
            {
                "message": "API rate limit exceeded",
                "custom": {
                    "api_endpoint": "/api/v1/users",
                    "rate_limit": 100,
                    "current_usage": 105,
                    "window": "1 minute",
                    "client_ip": "192.168.1.100",
                },
            },
            {
                "message": "Database query timeout",
                "custom": {
                    "query": "SELECT * FROM orders WHERE date > ?",
                    "timeout_ms": 5000,
                    "actual_time_ms": 8500,
                    "table": "orders",
                    "row_count": 150000,
                },
            },
        ]

        for scenario in scenarios:
            print(f"  - {scenario['message']}")
            print(f"    Custom data: {list(scenario['custom'].keys())}")
            rollbar.report_message(
                scenario["message"], level="error", extra_data=scenario["custom"]
            )

        print("\nNote: All custom data fields are searchable in Rollbar using:")
        print("  custom[payment_id]:pay_abc123")
        print("  custom[api_endpoint]:/api/v1/users")
        wait_for_user()
