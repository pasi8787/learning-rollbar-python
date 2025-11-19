"""Menu system for the Rollbar demo application."""

import sys

from .scenarios import ALL_SCENARIOS, BaseScenario
from .utils import clear_screen, print_header


class Menu:
    """Main menu class that manages scenario selection and execution"""

    def __init__(self, scenarios: list[BaseScenario]):
        """Initialize the menu with a list of scenarios.

        Args:
            scenarios: List of BaseScenario instances to display in the menu.
        """
        self.scenarios = scenarios

    def display(self) -> None:
        """Display the menu options."""
        print("\nAvailable Demos:")
        print("-" * 60)

        for idx, scenario in enumerate(self.scenarios, start=1):
            print(f"{idx}. {scenario.name} - {scenario.description}")

        print("0. Exit")
        print("-" * 60)

    def get_user_choice(self) -> int:
        """Get and validate user's menu choice.

        Returns:
            The user's choice as an integer.
        """
        try:
            choice = input("\nSelect a demo (0-8): ").strip()
            return int(choice)
        except ValueError:
            return -1

    def handle_choice(self, choice: int) -> bool:
        """Handle the selected item.

        Args:
            choice: The user's menu choice.

        Returns:
            True to continue, False to exit.
        """
        if choice == 0:
            print("\nExiting demo. Check your Rollbar dashboard to see all the data!")
            print("You can search, filter, and analyze all the errors sent.\n")
            return False

        num_scenarios = len(self.scenarios)
        if 1 <= choice <= num_scenarios:
            scenario = self.scenarios[choice - 1]
            scenario.run()
            return True

        print(f"\nInvalid choice. Please select 0-{num_scenarios}.")
        input("Press Enter to continue...")
        return True

    def run(self) -> None:
        """Run the main menu loop."""
        while True:
            clear_screen()
            print_header()
            self.display()

            choice = self.get_user_choice()
            should_continue = self.handle_choice(choice)

            if not should_continue:
                sys.exit(0)


def create_menu() -> Menu:
    """Factory function to create a Menu with all scenarios.

    Returns:
        A configured Menu instance.
    """
    return Menu(ALL_SCENARIOS)
