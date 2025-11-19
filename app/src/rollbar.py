"""
Module providing a small wrapper around the Rollbar Python SDK to initialize
Rollbar and enrich outgoing error payloads with application-specific context.
"""

from uuid import uuid4

import msgspec

import rollbar

from .config import app_settings
from .environment import app_environment


class CustomMetadata(msgspec.Struct):
    foo: str
    bar: dict[str, int]


def setup_rollbar() -> None:
    """Initialize Rollbar with application settings."""
    print(f"Rollbar access token: {app_settings.rollbar.access_token}")
    rollbar.init(
        access_token=app_settings.rollbar.access_token,
        environment=app_environment.name,
        code_version=app_settings.rollbar.code_version,
    )
    rollbar.events.add_payload_handler(_payload_handler)


def _get_person() -> dict:
    """Get the person dictionary for Rollbar payloads.

    Returns:
        A dictionary containing person information.
    """
    return {
        "id": "1234",
        "tenant": "tenant_name",
    }


def _get_custom_data() -> dict:
    """Get custom metadata for Rollbar payloads.

    Returns:
        A dictionary containing custom metadata.
    """
    return {
        "trace_id": uuid4().hex,
        "feature_flags": [
            "feature_1",
            "feature_2",
        ],
    }


def _payload_handler(payload: dict, **_kw: object) -> dict | bool:
    """Enrich Rollbar error payloads with custom user and metadata.

    Args:
        payload: The Rollbar payload dictionary to modify.
        **_kw: Additional keyword arguments (unused).

    Returns:
        The modified payload dictionary with added person and custom data.
    """
    if payload["data"]["level"] != "error":
        print("Not an error, ignoring")
        return False

    exception = payload["data"].get("body", {}).get("trace", {}).get("exception", {})
    if exception:
        print(f"exception={exception}")
        class_name = exception.get("class", "")
        message = exception.get("message", "")
        print(f"Exception class: {class_name}")
        print(f"Exception message: {message}")

    # Adding info about the user affected by this event (optional)
    # The 'id' field is required, anything else is optional
    payload["data"]["person"] = _get_person()

    # Example of adding arbitrary metadata (optional)
    payload["data"]["custom"] = {
        **_get_custom_data(),
        **payload["data"].get("custom", {}),
    }
    payload["data"]["foo_key"] = {
        "bar_key": "bar_value",
        "baz_key": [1, 2, 3],
        "deep": {
            "nested": {
                "structure": True,
            }
        },
    }
    payload["data"]["empty_value"] = None
    payload["data"]["base_model_custom"] = msgspec.to_builtins(
        {
            "the_model": CustomMetadata(
                foo="foo_value",
                bar={"key1": 10, "key2": 20},
            )
        },
    )

    payload["data"]["framework"] = "oreore_framework 1.0"

    return payload
