"""Business events tracking demonstration scenario."""

import rollbar

from ..utils import wait_for_user
from .base import BaseScenario


class BusinessEventsScenario(BaseScenario):
    """Demonstrate tracking business events and milestones."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "Business Events"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Track important application events"

    def run(self) -> None:
        """Execute the business events demo."""
        print("\n>> DEMO: Business Events Tracking")
        print("Logging important application events...\n")

        events = [
            {
                "level": "info",
                "message": "User completed onboarding",
                "data": {
                    "user_id": "user_new_123",
                    "signup_date": "2024-11-23",
                    "onboarding_steps": 5,
                    "time_to_complete_minutes": 8,
                },
            },
            {
                "level": "info",
                "message": "Subscription upgraded",
                "data": {
                    "user_id": "user_456",
                    "old_plan": "basic",
                    "new_plan": "premium",
                    "mrr_change": 20.00,
                },
            },
            {
                "level": "warning",
                "message": "Unusual activity detected",
                "data": {
                    "user_id": "user_789",
                    "activity": "rapid_api_calls",
                    "count": 500,
                    "time_window_minutes": 1,
                },
            },
            {
                "level": "info",
                "message": "Daily backup completed",
                "data": {
                    "backup_size_gb": 45.2,
                    "duration_minutes": 23,
                    "destination": "s3://backups/daily/",
                    "success": True,
                },
            },
        ]

        for event in events:
            print(f"  - {event['level'].upper():7} | {event['message']}")
            rollbar.report_message(
                event["message"], level=event["level"], extra_data=event["data"]
            )

        print("\nNote: Rollbar isn't just for errors!")
        print("Track important business events, milestones, and system operations.")
        wait_for_user()
