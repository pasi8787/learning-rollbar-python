"""Error levels demonstration scenario."""

import rollbar

from ..utils import wait_for_user
from .base import BaseScenario


class ErrorLevelsScenario(BaseScenario):
    """Demonstrate all five error severity levels."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "Error Levels"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Demonstrate all severity levels"

    def run(self) -> None:
        """Execute the error levels demo."""
        print("\n>> DEMO: Error Levels")
        print("Sending messages at all severity levels...\n")

        levels = [
            ("debug", "Debug: Variable value = 42"),
            ("info", "Info: User logged in successfully"),
            ("warning", "Warning: Disk space running low (15% remaining)"),
            ("error", "Error: Failed to connect to external API"),
            ("critical", "Critical: Database connection lost"),
        ]

        for level, message in levels:
            print(f"  - {level.upper():8} | {message}")
            rollbar.report_message(message, level=level)

        print("\nNote: You can filter by level in Rollbar dashboard.")
        print("Levels help prioritize which issues to address first.")
        wait_for_user()
