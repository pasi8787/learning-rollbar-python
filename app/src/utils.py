"""Utility functions for the Rollbar demo application."""

import os


def clear_screen():
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("ROLLBAR PYTHON SDK - INTERACTIVE DEMO")
    print("=" * 60)
    print()


def wait_for_user():
    """Wait for user to press Enter to continue."""
    input("\nPress Enter to continue...")
