# Rollbar Python Integration

An interactive demo application showcasing [Rollbar](https://rollbar.com) error monitoring and tracking capabilities. Features a menu-driven interface with multiple scenarios demonstrating different aspects of error tracking, payload enrichment, and custom metadata injection.

## Quick Start

1. **Install dependencies:**
   ```bash
   cd app
   poetry install
   ```

2. **Configure Rollbar:**
   - Copy `settings.yaml.example` to `settings.local.yaml`
   - Add your Rollbar access token
   - See [Configuration Guide](docs/configuration.md) for details

3. **Run the interactive demo:**
   ```bash
   poetry run python -m src.main
   ```

For complete setup instructions, see the [Installation Guide](docs/installation.md).

## Documentation

### Getting Started

- **[Installation Guide](docs/installation.md)** - Complete setup instructions
- **[Rollbar Setup Guide](docs/rollbar-setup.md)** - Get your Rollbar account and access token
- **[Configuration Guide](docs/configuration.md)** - YAML configuration and settings

### Using the Demo

- **[Scenarios Guide](docs/scenarios-guide.md)** - Interactive demo scenarios and usage
- **[Code Walkthrough](docs/code-walkthrough.md)** - Detailed code and project structure explanation
- **[Customization Guide](docs/customization.md)** - Extending and adapting the code

### Development

- **[Development Guide](docs/development.md)** - Type checking, linting, and tools
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions

### External Resources

- **[Rollbar Documentation](https://docs.rollbar.com/)** - Official Rollbar docs
- **[Rollbar Python SDK](https://docs.rollbar.com/docs/python)** - SDK documentation
