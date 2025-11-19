# Rollbar Python Integration

A Python project demonstrating how to integrate and customize the [Rollbar](https://rollbar.com) error monitoring and tracking service. This project showcases payload enrichment techniques, and custom metadata injection.

This project demonstrates:

- Setting up Rollbar in a Python application
- Enriching error payloads with custom metadata
- User/person tracking for error attribution
- Injecting trace IDs, feature flags, and custom data
- Filtering errors by severity level
- Auto-detecting git commit versions for deployment tracking

## Quick Start

1. **Set up the development environment:**
   ```bash
   cd app
   poetry install
   ```

2. **Configure your environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Rollbar access token
   ```

3. **Run the demo:**
   ```bash
   poetry run python -m src.main
   ```

For detailed setup instructions, see the [Installation Guide](docs/installation.md).

## Project Structure

```
LICENSE                       # License file
README.md                     # This file - project overview
app/                          # Main application
├── README.md                 # Detailed application documentation
├── pyproject.toml            # Python project & dependency config
├── .env.example              # Environment variable template
├── .env                      # Your local config (git-ignored)
└── src/                      # Source code
    ├── config.py             # Settings management with Pydantic
    ├── rollbar.py            # Rollbar integration & payload enrichment
    └── main.py               # Demo script
```

## Documentation

### Getting Started

- **[Installation Guide](docs/installation.md)** - Complete setup instructions
- **[Rollbar Setup Guide](docs/rollbar-setup.md)** - Get your Rollbar account and access token
- **[Configuration Guide](docs/configuration.md)** - Environment variables and settings

### Understanding the Code

- **[Code Walkthrough](docs/code-walkthrough.md)** - Detailed explanation of the integration
- **[Customization Guide](docs/customization.md)** - Adapt for your application
- **[Development Guide](docs/development.md)** - Type checking, linting, and tools

### Reference

- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Rollbar Documentation](https://docs.rollbar.com/)** - Official Rollbar docs
- **[Rollbar Python SDK](https://docs.rollbar.com/docs/python)** - SDK documentation
