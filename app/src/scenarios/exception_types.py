"""Different exception types demonstration scenario."""

from datetime import datetime

import rollbar

from ..utils import wait_for_user
from .base import BaseScenario


class ExceptionTypesScenario(BaseScenario):
    """Demonstrate different Python exception types."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "Exception Types"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Various Python exceptions"

    def run(self) -> None:
        """Execute the exception types demo."""
        print("\n>> DEMO: Different Exception Types")
        print("Triggering various Python exceptions...\n")

        exceptions = [
            ("AttributeError", lambda: None.some_attribute),
            ("KeyError", lambda: {}["nonexistent_key"]),
            ("IndexError", lambda: [][10]),
            ("TypeError", lambda: "string" + 123),
            ("ValueError", lambda: int("not_a_number")),
        ]

        for exc_name, trigger in exceptions:
            try:
                print(f"  - Triggering {exc_name}...")
                trigger()
            except Exception:
                rollbar.report_exc_info(
                    extra_data={
                        "exception_demo": exc_name,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        print("\nNote: Each exception type is captured with full stack trace.")
        print("Rollbar groups similar exceptions together automatically.")
        wait_for_user()
