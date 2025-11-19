# Rollbar Notificator

A Python application demonstrating advanced Rollbar integration with custom payload enrichment, user tracking, and metadata injection.

## Overview

This application showcases how to:

- Initialize Rollbar with environment-based configuration
- Enrich error payloads with custom data using payload handlers
- Track users/persons affected by errors
- Inject trace IDs, feature flags, and arbitrary metadata
- Filter errors by severity level (only send errors, not info/warnings)
- Serialize Pydantic models into Rollbar payloads
- Auto-detect git commit hashes for version tracking

## Quick Start

### Installation

```bash
# From the app directory
poetry install
```

### Configuration

```bash
cp .env.example .env
# Edit .env and add your Rollbar access token
```

### Run the Demo

```bash
poetry run python -m src.main
```

This will:
1. Initialize Rollbar with your configuration
2. Send an info message (will be filtered out by the payload handler)
3. Trigger an exception (will be sent to Rollbar with enriched data)

Check your Rollbar dashboard to see the error report with all the custom metadata!

## Key Features Demonstrated

### 1. Payload Handlers

The `_payload_handler` function is called for every error before sending to Rollbar, allowing you to:
- Add authentication context (user ID, tenant, session)
- Inject request tracing IDs
- Include feature flag states
- Add custom application state
- Filter errors by severity or other criteria

### 2. Person/User Tracking

Track which users experience errors:
```python
payload["data"]["person"] = {
    "id": "1234",                    # Required
    "username": "john.doe",          # Optional
    "email": "john@example.com",     # Optional
    "tenant": "acme_corp"            # Optional - custom field
}
```

This enables you to:
- See all errors affecting a specific user
- Contact users about bugs they encountered
- Track error rates per user or tenant

### 3. Custom Metadata

Add application-specific context:
```python
payload["data"]["custom"] = {
    "trace_id": request_trace_id,
    "feature_flags": get_active_features(),
    "experiment_variant": get_ab_test_variant(),
    "request_id": request_id,
    "correlation_id": correlation_id
}
```

### 4. Version Tracking

Automatically track which deployment introduced an error:
- Git commit hash is auto-detected
- Helps identify when bugs were introduced
- Enables rolling back to previous versions

### 5. Environment Filtering

Separate errors by environment:
- Development errors don't pollute production data
- Different alert rules per environment
- Easier debugging with environment-specific context

## Documentation

For detailed information, see the comprehensive documentation in the [docs/](../docs/) directory:

### Getting Started

- **[Installation Guide](../docs/installation.md)** - Complete setup instructions and prerequisites
- **[Rollbar Setup Guide](../docs/rollbar-setup.md)** - Create account and get access token
- **[Configuration Guide](../docs/configuration.md)** - Environment variables and settings reference

### Understanding the Code

- **[Code Walkthrough](../docs/code-walkthrough.md)** - Detailed explanation of each module
  - [config.py](src/config.py) - Settings management with Pydantic
  - [rollbar.py](src/rollbar.py) - Rollbar integration & payload enrichment
  - [main.py](src/main.py) - Demo script

### Customizing for Your App

- **[Customization Guide](../docs/customization.md)** - Adapt for your application
  - Replace demo user data with real authentication
  - Customize metadata for your needs
  - Adjust severity filtering
  - Add request/response data for web apps
  - Integration examples for Flask, FastAPI, Django

### Development

- **[Development Guide](../docs/development.md)** - Type checking, linting, and formatting
  - Type checking with mypy
  - Linting and formatting with Ruff
  - VS Code integration

### Help

- **[Troubleshooting Guide](../docs/troubleshooting.md)** - Common issues and solutions

## Viewing Errors in Rollbar

After running the demo, check your Rollbar dashboard:

1. **Items** tab shows all errors
2. Click on the `AttributeError` to see details
3. **People** tab shows the affected user (ID: 1234)
4. **Custom data** section shows:
   - `trace_id` - Unique identifier
   - `feature_flags` - Array of enabled features
   - `foo_key` - Nested custom data
   - `base_model_custom` - Serialized Pydantic model
5. **Occurrences** tab shows when the error happened
6. **Environment** shows "local" (from your `.env`)
7. **Code version** shows your git commit hash

## Next Steps

1. Run the demo and explore the Rollbar dashboard
2. Review the [Code Walkthrough](../docs/code-walkthrough.md) to understand how it works
3. Follow the [Customization Guide](../docs/customization.md) to adapt for your application
4. Set up alert rules in Rollbar for critical errors
5. Configure integrations (Slack, PagerDuty, Jira, etc.)

## References

- **[Rollbar Python SDK Documentation](https://docs.rollbar.com/docs/python)** - Official SDK guide
- **[Access Tokens](https://docs.rollbar.com/docs/access-tokens)** - Token types and scopes
- **[Payload Structure](https://docs.rollbar.com/docs/items-json)** - Understanding the payload format
- **[Person Tracking](https://docs.rollbar.com/docs/person-tracking)** - Detailed guide on user tracking
- **[Pydantic Documentation](https://docs.pydantic.dev/)** - Settings and validation
- **[Poetry Documentation](https://python-poetry.org/docs/)** - Dependency management
