# Configuration Guide

This guide explains how to configure the Rollbar Python Integration project using YAML files and environment variables.

## Overview

The application uses a multi-source configuration system built on Pydantic Settings and PyYAML. Configuration is loaded from multiple sources in priority order:

1. **Environment variables** (highest priority)
2. **.env file**
3. **settings.{environment}.yaml** (e.g., settings.local.yaml)
4. **settings.yaml** (base configuration, lowest priority)

This approach provides:

- Type-safe configuration with automatic validation
- Environment-specific configuration files
- Flexible override mechanism
- Clear separation between code and configuration
- Secure storage of sensitive data (tokens, API keys)

## Quick Start

### 1. Create Your Local Configuration

From the `app` directory, copy the example configuration:

```bash
cp settings.yaml.example settings.local.yaml
```

### 2. Add Your Rollbar Access Token

Edit `settings.local.yaml`:

```yaml
rollbar:
  access_token: your_rollbar_access_token_here
```

### 3. (Optional) Set Environment

The environment defaults to "local". To change it, either:

**Option A: Environment variable**

```bash
export ENVIRONMENT=staging
```

**Option B: .env file**

```bash
echo "ENVIRONMENT=staging" > .env
```

That's it! The application will automatically load your configuration.

## Configuration Sources

### 1. Environment Variables (Highest Priority)

Environment variables can override any setting using a nested delimiter:

```bash
# Set rollbar access token
export ROLLBAR__ACCESS_TOKEN=your_token_here

# Set environment name
export ENVIRONMENT=production

# Set code version
export ROLLBAR__CODE_VERSION=v1.2.3
```

**Nested delimiter:** Use `__` (double underscore) to set nested values.

Example: `ROLLBAR__ACCESS_TOKEN` sets `rollbar.access_token` in the configuration.

**Case insensitive:** `ROLLBAR__ACCESS_TOKEN` and `rollbar__access_token` are equivalent.

### 2. .env File

Create an `.env` file in the `app` directory for local development:

```bash
# .env
ROLLBAR__ACCESS_TOKEN=your_token_here
ENVIRONMENT=local
```

The `.env` file is git-ignored for security.

### 3. Environment-Specific YAML Files

Create environment-specific configuration files:

- `settings.local.yaml` - Local development
- `settings.staging.yaml` - Staging environment
- `settings.production.yaml` - Production environment

The application loads `settings.{ENVIRONMENT}.yaml` based on the `ENVIRONMENT` variable.

**Example `settings.local.yaml`:**

```yaml
rollbar:
  access_token: your_local_dev_token
  # code_version will auto-detect from git if not specified
```

**Example `settings.production.yaml`:**

```yaml
rollbar:
  access_token: your_production_token
  code_version: ${CI_COMMIT_SHA} # Set via environment variable in CI/CD
```

### 4. Base YAML File (Lowest Priority)

`settings.yaml` contains base configuration and defaults:

```yaml
rollbar:
  access_token: # Override in environment-specific file
  # code_version will auto-detect from git if not specified
```

## Configuration Schema

### Rollbar Settings

```yaml
rollbar:
  access_token: string # Required
  code_version: string # Optional (auto-detected from git)
```

#### rollbar.access_token (Required)

Your Rollbar project access token.

- **Type:** String
- **Required:** Yes
- **Default:** None

**How to get your token:** See the [Rollbar Setup Guide](rollbar-setup.md).

**Security:**

- Never commit tokens to git
- Use environment-specific files (git-ignored)
- Use different tokens for dev/staging/production

#### rollbar.code_version (Optional)

Version identifier for your deployment.

- **Type:** String
- **Required:** No
- **Default:** Auto-detected from git commit hash

**Auto-detection:** If not set, the application runs `git rev-parse HEAD` to get the current commit hash.

**Manual override:**

```yaml
rollbar:
  code_version: v1.2.3
```

Or via environment variable:

```bash
export ROLLBAR__CODE_VERSION=v1.2.3
```

### Environment Detection

The `ENVIRONMENT` variable determines which settings file to load:

- `ENVIRONMENT=local` → loads `settings.local.yaml`
- `ENVIRONMENT=staging` → loads `settings.staging.yaml`
- `ENVIRONMENT=production` → loads `settings.production.yaml`

**Default:** `local`

## Configuration Priority Example

Given these files and variables:

**settings.yaml:**

```yaml
rollbar:
  access_token: base_token
  code_version: v1.0.0
```

**settings.local.yaml:**

```yaml
rollbar:
  access_token: local_token
```

**.env:**

```bash
ROLLBAR__CODE_VERSION=v2.0.0
```

**Environment variable:**

```bash
export ROLLBAR__ACCESS_TOKEN=env_token
```

**Result:**

```yaml
rollbar:
  access_token: env_token # From environment variable (highest priority)
  code_version: v2.0.0 # From .env file
```

## Environment-Specific Configuration

### Local Development

**settings.local.yaml:**

```yaml
rollbar:
  access_token: your_dev_token
  # code_version auto-detected from git
```

Set environment:

```bash
export ENVIRONMENT=local  # Or default
```

### Staging/QA

**settings.staging.yaml:**

```yaml
rollbar:
  access_token: your_staging_token
```

Override in CI/CD:

```bash
export ENVIRONMENT=staging
export ROLLBAR__CODE_VERSION=${CI_COMMIT_SHA}
```

### Production

**settings.production.yaml:**

```yaml
rollbar:
  access_token: your_production_token
```

Override in CI/CD:

```bash
export ENVIRONMENT=production
export ROLLBAR__CODE_VERSION=v1.2.3
```

## Configuration in Code

Configuration is loaded in [src/config.py](../app/src/config.py):

```python
class RollbarSettings(BaseModel):
    access_token: str = Field(description="Rollbar access token")
    code_version: str = Field(default="")

class ApplicationSettings(BaseSettings):
    rollbar: RollbarSettings

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(cls, ...):
        return (
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls, f"settings.{env}.yaml"),
            YamlConfigSettingsSource(settings_cls, "settings.yaml"),
            init_settings,
        )
```

**Key features:**

- Multi-source loading with priority
- Nested configuration structure
- Type validation via Pydantic
- Environment variable override with `__` delimiter

## Best Practices

### Security

1. **Never commit tokens** - Use git-ignored files:

   ```bash
   # .gitignore already includes:
   settings.local.yaml
   settings.*.local.yaml
   .env
   ```

2. **Use different tokens per environment** - Separate dev/staging/production

3. **Use secret management in production** - AWS Secrets Manager, HashiCorp Vault, etc.

4. **Set tokens via environment variables** - More secure than files in production

### Organization

1. **Keep settings.yaml as template** - Document all available options

2. **Create settings.yaml.example** - Example file for new developers

3. **Use comments** - Explain what each setting does

4. **Document environment-specific files** - Maintain a list of expected files

### Deployment

1. **Set environment explicitly** - Don't rely on defaults in production

2. **Override CODE_VERSION in CI/CD** - Use build number or commit hash:

   ```bash
   export ROLLBAR__CODE_VERSION=${CI_COMMIT_SHA}
   ```

3. **Validate on startup** - Pydantic validates automatically

4. **Log configuration** - Application logs environment name on startup

## Troubleshooting

### Configuration not loading

**Symptoms:** Application uses default values or raises validation errors

**Solutions:**

- Check that settings.{environment}.yaml exists for your environment
- Verify YAML syntax is correct (use a YAML validator)
- Ensure file encoding is UTF-8
- Check file permissions (must be readable)

### Environment variable not overriding

**Symptoms:** YAML value used instead of environment variable

**Solutions:**

- Use double underscore `__` for nested paths: `ROLLBAR__ACCESS_TOKEN`
- Check variable name is uppercase (case-insensitive but uppercase is standard)
- Verify the variable is exported: `echo $ROLLBAR__ACCESS_TOKEN`
- Check the variable is set before running the app

### Git commit not detected

**Symptoms:** code_version shows as "unknown"

**Solutions:**

- Ensure you're in a git repository: `git status`
- Check that `.git` directory exists
- Run `git rev-parse HEAD` manually to test
- Set explicitly in YAML or environment variable if git unavailable

### Invalid access token

**Symptoms:** Errors not appearing in Rollbar

**Solutions:**

- Verify token in Rollbar dashboard: Settings → Project Access Tokens
- Check token scope (needs post_client_item or post_server_item)
- Ensure token belongs to correct Rollbar project
- Verify token hasn't been revoked

### Wrong environment file loaded

**Symptoms:** Unexpected configuration values

**Solutions:**

- Check `ENVIRONMENT` variable: `echo $ENVIRONMENT`
- Verify settings.{environment}.yaml exists
- Check application startup logs for "ENVIRONMENT=..." message
- Set `ENVIRONMENT` explicitly before running

## Next Steps

- Create your `settings.local.yaml` file
- Follow the [Rollbar Setup Guide](rollbar-setup.md) to obtain your access token
- Review the [Code Walkthrough](code-walkthrough.md) to understand how configuration is used
- Check the [Troubleshooting Guide](troubleshooting.md) for more help

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [Rollbar Access Tokens](https://docs.rollbar.com/docs/access-tokens)
- [12-Factor App: Config](https://12factor.net/config)
