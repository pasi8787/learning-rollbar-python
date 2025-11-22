"""Interactive Rollbar Demo Application.

This application demonstrates various Rollbar features through an interactive menu.
Each option sends one or more messages/errors to Rollbar to showcase different capabilities.

This is the main entry point for the application. The actual logic is organized
into separate modules following SOLID principles:
- utils: Shared utility functions
- scenarios: Individual demo scenarios
- menu: Menu display and user interaction
"""

from .menu import create_menu
from .rollbar import setup_rollbar


def main():
    """Main application entry point.

    This function:
    1. Initializes Rollbar
    2. Creates the menu
    3. Starts the interactive loop
    """
    # Initialize Rollbar
    setup_rollbar()

    print("\nRollbar initialized successfully!")
    print("Starting interactive demo...\n")

    # Create and run the menu
    menu = create_menu()
    menu.run()


if __name__ == "__main__":
    main()
