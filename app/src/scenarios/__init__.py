"""Rollbar demo scenarios module.

This module contains all available demo scenarios.
Each scenario demonstrates a specific feature of the Rollbar SDK.
"""

from .base import BaseScenario
from .business_events import BusinessEventsScenario
from .custom_data import CustomDataScenario
from .error_levels import ErrorLevelsScenario
from .exception_types import ExceptionTypesScenario
from .exception_vs_message import ExceptionVsMessageScenario
from .multiple_errors import MultipleErrorsScenario
from .person_tracking import PersonTrackingScenario
from .searchable_fields import SearchableFieldsScenario

# List of all available scenarios in display order
ALL_SCENARIOS = [
    PersonTrackingScenario(),
    CustomDataScenario(),
    ErrorLevelsScenario(),
    ExceptionVsMessageScenario(),
    SearchableFieldsScenario(),
    MultipleErrorsScenario(),
    ExceptionTypesScenario(),
    BusinessEventsScenario(),
]

__all__ = [
    "BaseScenario",
    "PersonTrackingScenario",
    "CustomDataScenario",
    "ErrorLevelsScenario",
    "ExceptionVsMessageScenario",
    "SearchableFieldsScenario",
    "MultipleErrorsScenario",
    "ExceptionTypesScenario",
    "BusinessEventsScenario",
    "ALL_SCENARIOS",
]
