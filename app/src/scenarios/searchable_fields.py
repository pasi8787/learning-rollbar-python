"""Searchable fields demonstration scenario."""

import rollbar

from ..utils import wait_for_user
from .base import BaseScenario


class SearchableFieldsScenario(BaseScenario):
    """Demonstrate using context and custom fields for searching."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "Searchable Fields"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Use context and custom fields"

    def run(self) -> None:
        """Execute the searchable fields demo."""
        print("\n>> DEMO: Searchable Fields")
        print("Sending errors with searchable context and custom fields...\n")

        contexts = [
            {
                "context": "checkout#payment",
                "message": "Payment gateway timeout",
                "custom": {
                    "gateway": "stripe",
                    "order_id": "ORD-2024-001",
                    "amount": 299.99,
                },
            },
            {
                "context": "checkout#shipping",
                "message": "Invalid shipping address",
                "custom": {
                    "address_validator": "usps",
                    "order_id": "ORD-2024-002",
                    "country": "US",
                },
            },
            {
                "context": "user#authentication",
                "message": "Failed login attempt",
                "custom": {
                    "username": "testuser",
                    "ip_address": "192.168.1.50",
                    "attempt_count": 5,
                },
            },
            {
                "context": "api#external",
                "message": "Third-party API failure",
                "custom": {
                    "api_name": "weather_service",
                    "endpoint": "/api/forecast",
                    "status_code": 503,
                },
            },
        ]

        for item in contexts:
            print(f"  - Context: {item['context']}")
            print(f"    Message: {item['message']}")
            rollbar.report_message(
                item["message"],
                level="error",
                extra_data=item["custom"],
                payload_data={"context": item["context"]},
            )

        print("\nNote: In Rollbar search:")
        print("  - Use 'context:checkout#payment' to find checkout payment errors")
        print("  - Use 'custom[gateway]:stripe' to find Stripe-related issues")
        print("  - Use 'custom[order_id]:ORD-2024-001' to find specific order")
        wait_for_user()
