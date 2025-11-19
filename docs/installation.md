# Installation Guide

This guide walks you through setting up the Rollbar Python Integration project.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13.9** - Download from [python.org](https://www.python.org/downloads/)
- **Poetry 2.2.1** - Python dependency management tool
- **Rollbar Account** - Sign up at [rollbar.com](https://rollbar.com) to get an access token

## Installation Steps

### 1. Clone the Repository

If you haven't already, clone or download this repository:

```bash
git clone <repository-url>
cd rollbar
```

### 2. Set Up the Development Environment

**Install Python 3.13.9:**

Download and install Python 3.13.9 from [python.org/downloads](https://www.python.org/downloads/). During installation on Windows, make sure to check "Add Python to PATH".

Verify the installation:

```bash
python --version
# Should output: Python 3.13.9
```

**Install Poetry 2.2.1:**

Install Poetry using the official installer:

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

Verify the installation:

```bash
poetry --version
# Should output: Poetry (version 2.2.1)
```

### 3. Install Python Dependencies

Navigate to the `app` directory and install the project dependencies:

```bash
cd app
poetry install
```

This installs the following packages:

**Runtime Dependencies:**

- `rollbar` - Rollbar Python SDK for error monitoring
- `pydantic` - Data validation and settings management
- `pydantic-settings` - Environment variable loading with Pydantic
- `python-dotenv` - Support for loading `.env` files
- `msgspec` - High-performance serialization library
- `pyyaml` - YAML configuration file support

**Development Dependencies:**

- `mypy` - Static type checker for Python
- `ruff` - Fast Python linter and formatter

### 4. Configure Your Rollbar Token

Create your local configuration file:

```bash
cp settings.yaml.example settings.local.yaml
```

Then edit `settings.local.yaml` to add your Rollbar access token:

```yaml
rollbar:
  access_token: your_rollbar_token_here
```

See the [Configuration Guide](configuration.md) for detailed information about YAML configuration, environment-specific files, and the multi-source configuration system.

For instructions on obtaining your Rollbar access token, see the [Rollbar Setup Guide](rollbar-setup.md).

## Verify Installation

Test that everything is installed correctly by running the interactive demo:

```bash
poetry run python -m src.main
```

This will:

1. Initialize Rollbar with your configuration
2. Display an interactive menu with 8 demo scenarios
3. Let you explore different Rollbar features

Select any scenario to send demo data to Rollbar, then check your dashboard to see the results!

See the [Scenarios Guide](scenarios-guide.md) for detailed information about each demo scenario.

## Next Steps

- Read the [Configuration Guide](configuration.md) to understand all available settings
- Follow the [Rollbar Setup Guide](rollbar-setup.md) to get your access token
- Explore the [Code Walkthrough](code-walkthrough.md) to understand how the integration works
- Review the [Development Guide](development.md) for information about type checking and linting

## Troubleshooting

### Poetry not found

If Poetry is not found in your PATH after installation, you may need to add it manually. The installer will show you the path to add.

On Windows, Poetry is typically installed to:

```
%APPDATA%\Python\Scripts
```

On macOS/Linux:

```
$HOME/.local/bin
```

### Python version issues

Ensure you're using Python 3.13.9:

```bash
python --version
# Should output: Python 3.13.9
```

If you have multiple Python versions installed, you may need to use `python3.13` explicitly or specify the full path to your Python 3.13.9 installation.

### Dependencies fail to install

Try updating pip and poetry:

```bash
poetry self update
poetry update
```

For more troubleshooting help, see the [Troubleshooting Guide](troubleshooting.md).
