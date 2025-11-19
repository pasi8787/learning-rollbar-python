# Rollbar Notificator

An interactive demo application for exploring Rollbar error tracking capabilities through a menu-driven interface with multiple scenarios.

## Quick Start

### Installation

```bash
# From the app directory
poetry install
```

### Configuration

```bash
cp settings.yaml.example settings.local.yaml
# Edit settings.local.yaml and add your Rollbar access token
```

See [Configuration Guide](../docs/configuration.md) for detailed setup.

### Run the Interactive Demo

```bash
poetry run python -m src.main
```

The application will present a menu with 8 different scenarios demonstrating various Rollbar features. See [Scenarios Guide](../docs/scenarios-guide.md) for details on each scenario.

## What You'll Learn

This demo covers:
- Person/user tracking for error attribution
- Custom data and metadata injection
- Different error severity levels
- Exception handling and reporting
- Searchable fields and context
- Multiple error scenarios
- Various Python exception types
- Business event tracking

See [Scenarios Guide](../docs/scenarios-guide.md) for detailed explanation of each demo scenario.

## Documentation

See the [main README](../README.md) for complete documentation index, including:

- [Installation Guide](../docs/installation.md) - Setup instructions
- [Scenarios Guide](../docs/scenarios-guide.md) - Interactive demo scenarios
- [Code Walkthrough](../docs/code-walkthrough.md) - Code explanation
- [Configuration Guide](../docs/configuration.md) - YAML configuration
- [Customization Guide](../docs/customization.md) - Extending the code
- [Development Guide](../docs/development.md) - Development tools
- [Troubleshooting Guide](../docs/troubleshooting.md) - Common issues
