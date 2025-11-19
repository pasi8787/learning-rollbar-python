# Configuration Guide

This guide explains how to configure the Rollbar Python Integration project using environment variables.

## Overview

The application uses Pydantic Settings to load configuration from environment variables, which are stored in a `.env` file. This approach provides:

- Type-safe configuration with automatic validation
- Clear separation between code and configuration
- Easy environment-specific settings
- Secure storage of sensitive data (tokens, API keys)

## Setting Up Your Configuration

### 1. Create the .env File

From the `app` directory, copy the example configuration:

```bash
cp .env.example .env
```

### 2. Edit the Configuration

Open `.env` in your text editor and configure the following variables:

```bash
# REQUIRED: Your Rollbar access token
ROLLBAR_ACCESS_TOKEN=your_rollbar_access_token_here

# OPTIONAL: Environment name (default: production)
ENVIRONMENT=local

# OPTIONAL: Version identifier (default: auto-detected from git)
# CODE_VERSION=1.0.0
```

## Environment Variables Reference

### ROLLBAR_ACCESS_TOKEN (Required)

Your Rollbar project access token. This is required for the application to communicate with Rollbar.

- **Type:** String
- **Required:** Yes
- **Example:** `ROLLBAR_ACCESS_TOKEN=abc123def456...`

**How to get your token:**

See the [Rollbar Setup Guide](rollbar-setup.md) for step-by-step instructions on obtaining your access token.

**Security Notes:**
- Keep this token secret and never commit it to git
- The `.env` file is already in `.gitignore` to prevent accidental commits
- Use the **post_client_item** or **post_server_item** token scope for error reporting
- Different tokens can be used for different environments

### ENVIRONMENT (Optional)

Identifies which environment errors originate from. This helps you filter and organize errors in the Rollbar dashboard.

- **Type:** String
- **Required:** No
- **Default:** `production`
- **Common values:** `local`, `development`, `staging`, `production`

**Example:**

```bash
ENVIRONMENT=local
```

**Use cases:**
- Filter errors by environment in the Rollbar dashboard
- Set up different alert rules per environment
- Avoid mixing development errors with production errors
- Track error rates across different deployment environments

**Best practices:**
- Use `local` or `development` for local development
- Use `staging` for staging/QA environments
- Use `production` for production deployments
- Be consistent with naming across your infrastructure

### CODE_VERSION (Optional)

Version identifier for your deployment. Helps track which version of your code introduced specific errors.

- **Type:** String
- **Required:** No
- **Default:** Auto-detected from git commit hash
- **Example:** `CODE_VERSION=v1.2.3` or `CODE_VERSION=abc123`

**Auto-detection:**

If not explicitly set, the application automatically detects your current git commit hash:

1. Runs `git rev-parse HEAD` to get the current commit
2. Uses the full commit hash as the version
3. Falls back to `"unknown"` if git is unavailable

**Manual override:**

Set this explicitly in production or CI/CD:

```bash
# Semantic version
CODE_VERSION=v1.2.3

# Short git hash
CODE_VERSION=$(git rev-parse --short HEAD)

# Build number
CODE_VERSION=build-456
```

**Use cases:**
- Track when bugs were introduced
- Correlate errors with specific deployments
- Identify which version needs to be rolled back
- Generate release notes from error patterns

## Configuration in Code

The configuration is loaded and validated using Pydantic Settings in [src/config.py](../app/src/config.py):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    rollbar_access_token: str              # Required
    environment: str = "production"        # Optional with default
    code_version: str = "unknown"          # Auto-detected from git

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

**Key features:**
- Automatic `.env` file loading
- Type validation (raises error if required fields are missing)
- Git commit hash auto-detection via validator
- Environment variable override (can set via shell: `export ENVIRONMENT=staging`)

## Environment-Specific Configuration

### Local Development

```bash
ROLLBAR_ACCESS_TOKEN=your_dev_token
ENVIRONMENT=local
# CODE_VERSION will auto-detect from git
```

### Staging/QA

```bash
ROLLBAR_ACCESS_TOKEN=your_staging_token
ENVIRONMENT=staging
CODE_VERSION=${CI_COMMIT_SHA}  # From CI/CD pipeline
```

### Production

```bash
ROLLBAR_ACCESS_TOKEN=your_production_token
ENVIRONMENT=production
CODE_VERSION=v1.2.3  # Or build number from CI/CD
```

## Configuration Validation

When the application starts, Pydantic automatically validates the configuration:

**Missing required token:**
```
ValidationError: 1 validation error for Settings
rollbar_access_token
  Field required [type=missing]
```

**Invalid type:**
```
ValidationError: 1 validation error for Settings
environment
  Input should be a valid string [type=string_type]
```

Fix validation errors by checking your `.env` file syntax and ensuring all required fields are present.

## Best Practices

### Security

1. **Never commit `.env` files** - Already in `.gitignore`, but double-check
2. **Use different tokens per environment** - Separate dev/staging/production tokens
3. **Rotate tokens regularly** - Update tokens periodically for security
4. **Use secret management in production** - Consider AWS Secrets Manager, HashiCorp Vault, etc.

### Organization

1. **Keep `.env.example` updated** - Document all available variables
2. **Use comments** - Explain what each variable does
3. **Provide examples** - Show example values for clarity
4. **Document defaults** - Make it clear which variables are optional

### Deployment

1. **Set CODE_VERSION in CI/CD** - Don't rely on git in production
2. **Use environment variables** - Override `.env` with shell variables in containers
3. **Validate on startup** - Let Pydantic catch configuration errors early
4. **Log configuration** - Log non-sensitive config values on startup for debugging

## Troubleshooting

### Environment variables not loading

**Symptoms:** Application uses default values or raises validation errors

**Solutions:**
- Ensure `.env` file exists in the `app` directory (same level as `pyproject.toml`)
- Check `.env` file encoding is UTF-8
- Verify no syntax errors in `.env` (no spaces around `=`)
- Check file permissions (must be readable)

### Git commit not detected

**Symptoms:** CODE_VERSION shows as "unknown"

**Solutions:**
- Ensure you're in a git repository (`git status` should work)
- Check that `.git` directory exists
- Run `git rev-parse HEAD` manually to test git access
- Set `CODE_VERSION` explicitly in `.env` if git is unavailable

### Invalid access token error

**Symptoms:** Errors not appearing in Rollbar, authentication errors in logs

**Solutions:**
- Verify `ROLLBAR_ACCESS_TOKEN` is set correctly in `.env`
- Ensure you're using the correct token type (post_client_item or post_server_item)
- Check that the token belongs to the correct Rollbar project
- Verify the token hasn't been revoked in Rollbar settings

## Next Steps

- Follow the [Rollbar Setup Guide](rollbar-setup.md) to obtain your access token
- Review the [Code Walkthrough](code-walkthrough.md) to understand how configuration is used
- Check the [Troubleshooting Guide](troubleshooting.md) for more help with common issues

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Rollbar Access Tokens](https://docs.rollbar.com/docs/access-tokens)
- [12-Factor App: Config](https://12factor.net/config)
