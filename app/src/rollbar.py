"""
Module providing a small wrapper around the Rollbar Python SDK to initialize
Rollbar and enrich outgoing error payloads with application-specific context.
"""

import msgspec

import rollbar

from .config import app_settings
from .environment import app_environment


class CustomMetadata(msgspec.Struct):
    dict_value: dict[str, int]
    empty_value: None
    list_value: list[str]
    simple_value: str


def setup_rollbar() -> None:
    """Initialize Rollbar with application settings."""
    print(f"Rollbar access token: {app_settings.rollbar.access_token}")
    rollbar.init(
        access_token=app_settings.rollbar.access_token,
        environment=app_environment.name,
        code_version=app_settings.rollbar.code_version,
    )
    rollbar.events.add_payload_handler(_payload_handler)


def _payload_handler(payload: dict, **_kw: object) -> dict | bool:
    """Enrich Rollbar error payloads with custom user and metadata.

    Args:
        payload: The Rollbar payload dictionary to modify.
        **_kw: Additional keyword arguments (unused).

    Returns:
        The modified payload dictionary with added person and custom data.
    """
    level = payload["data"]["level"]
    print(f"Processing {level} level event")

    payload["data"]["framework"] = "oreore_framework 1.0"

    payload["data"]["base_model_custom"] = msgspec.to_builtins(
        {
            "the_model": CustomMetadata(
                empty_value=None,
                dict_value={"key1": 10, "key2": 20},
                list_value=[1, 2, 3],
                simple_value="foo_value",
            )
        },
    )

    return payload
