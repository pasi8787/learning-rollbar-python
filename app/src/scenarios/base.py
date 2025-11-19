"""Base class for all Rollbar demo scenarios."""

from abc import ABC, abstractmethod


class BaseScenario(ABC):
    """Abstract base class for demo scenarios.

    Each scenario must implement the name, description, and run methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of the scenario."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Execute the demo scenario.

        This method should:
        1. Print information about what's being demonstrated
        2. Send appropriate messages/errors to Rollbar
        3. Provide explanatory notes to the user
        """
        pass
