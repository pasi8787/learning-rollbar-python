"""Person tracking demonstration scenario."""

import rollbar

from ..utils import wait_for_user
from .base import BaseScenario


class PersonTrackingScenario(BaseScenario):
    """Demonstrate associating errors with different user profiles."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "Person Tracking"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Associate errors with different users"

    def run(self) -> None:
        """Execute the person tracking demo."""
        print("\n>> DEMO: Person Tracking")
        print("Sending errors associated with different users...\n")

        users = [
            {
                "id": "user_123",
                "username": "alice_smith",
                "email": "alice@example.com",
                "subscription": "premium",
            },
            {
                "id": "user_456",
                "username": "bob_jones",
                "email": "bob@example.com",
                "subscription": "free",
            },
            {
                "id": "user_789",
                "username": "charlie_brown",
                "email": "charlie@example.com",
                "subscription": "enterprise",
            },
        ]

        for user in users:
            print(f"  - Reporting error for user: {user['username']} ({user['email']})")
            rollbar.report_message(
                f"User action failed for {user['username']}",
                level="error",
                extra_data={"user_action": "checkout", "cart_value": 99.99},
                payload_data={
                    "person": {
                        "id": user["id"],
                        "username": user["username"],
                        "email": user["email"],
                        "subscription": user["subscription"],
                    }
                },
            )

        print(
            "\nNote: In Rollbar, you can now search for errors by user ID, "
            "username, or email."
        )
        wait_for_user()
