# Troubleshooting Guide

This guide helps you resolve common issues when setting up and using the Rollbar Python Integration project.

## Installation Issues

### Poetry not found

**Symptom:**

```
bash: poetry: command not found
```

**Solution:**

Install Poetry 2.2.1 using the official installer:

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

If Poetry is not found after installation, add it to your PATH. The installer will show the path to add.

On Windows, Poetry is typically installed to:

```
%APPDATA%\Python\Scripts
```

On macOS/Linux:

```
$HOME/.local/bin
```

Or use your package manager:

```bash
# macOS
brew install poetry

# Linux (via pipx)
pipx install poetry
```

### Python version issues

**Symptom:**

```
Error: Python 3.13+ required
```

**Solution:**

Check your Python version:

```bash
python --version
# or
python3 --version
```

If you need Python 3.13.9:

- Download and install from [python.org/downloads](https://www.python.org/downloads/)
  - On Windows, check "Add Python to PATH" during installation
- Or use pyenv: `pyenv install 3.13.9`
- Or use your package manager (brew, apt, windows store, etc.)

If you have multiple Python versions installed, you may need to use `python3.13` explicitly or specify the full path to your Python 3.13.9 installation.

### Dependencies fail to install

**Symptom:**

```
Error: Failed to install packages
```

**Solution:**

Try these steps in order:

1. Update Poetry:

   ```bash
   poetry self update
   ```

2. Clear Poetry cache:

   ```bash
   poetry cache clear pypi --all
   ```

3. Remove lock file and reinstall:

   ```bash
   rm poetry.lock
   poetry install
   ```

4. Check for system dependencies (Linux):

   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev build-essential

   # Fedora/RHEL
   sudo dnf install python3-devel gcc
   ```

## Configuration Issues

### YAML configuration not loading

**Symptom:**

- Application uses default values
- Validation errors about missing `rollbar.access_token`
- Settings not reflecting YAML file values

**Solutions:**

1. **Check YAML file location:**

   - Files must be in the `app` directory (same level as `pyproject.toml`)
   - Ensure `settings.local.yaml` exists (copy from `settings.yaml.example`)

2. **Verify correct environment file:**

   ```bash
   # Check which environment is active
   echo $ENVIRONMENT
   # Should load settings.{environment}.yaml
   # Default is "local" → settings.local.yaml
   ```

3. **Validate YAML syntax:**

   ```bash
   # Check for syntax errors
   poetry run python -c "import yaml; yaml.safe_load(open('settings.local.yaml'))"
   ```

4. **Common YAML syntax errors:**

   ```yaml
   # ✅ Correct - consistent 2-space indentation
   rollbar:
     access_token: your_token_here
     code_version: v1.0.0

   # ❌ Wrong - inconsistent indentation
   rollbar:
    access_token: your_token_here
     code_version: v1.0.0

   # ❌ Wrong - missing colon
   rollbar
     access_token: your_token_here

   # ❌ Wrong - tabs instead of spaces
   rollbar:
   →access_token: your_token_here
   ```

5. **Check file encoding:**

   - Must be UTF-8
   - No BOM (Byte Order Mark)

6. **Verify file permissions:**
   ```bash
   ls -la settings.local.yaml
   # Should be readable
   ```

### Environment variables not overriding YAML

**Symptom:**

- Environment variable set but YAML value used
- `ROLLBAR__ACCESS_TOKEN` not working

**Solutions:**

1. **Use correct nested delimiter:**

   ```bash
   # ✅ Correct - double underscore for nested values
   export ROLLBAR__ACCESS_TOKEN=your_token

   # ❌ Wrong - single underscore
   export ROLLBAR_ACCESS_TOKEN=your_token

   # ❌ Wrong - dot notation (use for ENVIRONMENT only)
   export ROLLBAR.ACCESS_TOKEN=your_token
   ```

2. **Verify variable is exported:**

   ```bash
   echo $ROLLBAR__ACCESS_TOKEN
   # Should show your token
   ```

3. **Check variable is set before running:**
   ```bash
   # Set and run in same session
   export ROLLBAR__ACCESS_TOKEN=your_token
   poetry run python -m src.main
   ```

### Configuration priority confusion

**Symptom:**

- Not sure which configuration source is being used
- Values from unexpected source

**Explanation:**

Configuration loads in this priority (highest to lowest):

1. Environment variables (`ROLLBAR__ACCESS_TOKEN`)
2. `.env` file
3. `settings.{environment}.yaml` (e.g., `settings.local.yaml`)
4. `settings.yaml` (base configuration)

**Solution:**

Check the application startup logs:

```
ENVIRONMENT=local
Rollbar access token: your_token...
```

If wrong values are loaded, check each source in priority order.

### Invalid access token error

**Symptom:**

```
rollbar.ApiException: Invalid access token
```

Or errors not appearing in Rollbar dashboard.

**Solutions:**

1. **Verify token is set correctly:**

   ```bash
   # Check .env file
   cat .env | grep ROLLBAR_ACCESS_TOKEN
   ```

2. **Ensure correct token type:**

   - Use **post_server_item** or **post_client_item** token
   - NOT read-only tokens
   - NOT admin/configuration tokens

3. **Check token belongs to correct project:**

   - Log into Rollbar
   - Navigate to correct project
   - Go to Settings → Project Access Tokens
   - Verify token matches

4. **Check token hasn't been revoked:**

   - Token might have been deleted or regenerated
   - Generate a new token if needed

5. **Remove any extra whitespace:**
   ```bash
   # Token should be on one line with no spaces
   ROLLBAR_ACCESS_TOKEN=abc123def456...
   ```

### Git commit not detected

**Symptom:**

- CODE_VERSION shows as "unknown" in Rollbar
- Git command fails during startup

**Solutions:**

1. **Ensure you're in a git repository:**

   ```bash
   git status
   # Should show branch info, not "not a git repository"
   ```

2. **Check .git directory exists:**

   ```bash
   ls -la | grep .git
   # Should show .git directory
   ```

3. **Test git command manually:**

   ```bash
   git rev-parse HEAD
   # Should output a commit hash
   ```

4. **Initialize git repository if needed:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

5. **Set CODE_VERSION explicitly:**
   If git is unavailable, set the version in `.env`:
   ```bash
   CODE_VERSION=v1.0.0
   ```

## Runtime Issues

### Errors not appearing in Rollbar

**Symptom:**

- Application runs without errors
- No new items in Rollbar dashboard
- Console shows errors but Rollbar doesn't

**Solutions:**

1. **Check error level:**

   - The payload handler filters non-error levels
   - Only `"error"` level messages are sent by default
   - Info and warning messages are filtered out

2. **Verify internet connection:**

   ```bash
   ping rollbar.com
   # Should show successful responses
   ```

3. **Check Rollbar service status:**

   - Visit [status.rollbar.com](https://status.rollbar.com)
   - Ensure Rollbar services are operational

4. **Look for error messages in console:**

   - Check for authentication errors
   - Look for network errors
   - Review any exception stack traces

5. **Test with a simple error:**

   ```python
   import rollbar
   rollbar.report_message("Test message", level="error")
   ```

6. **Check payload handler return value:**

   - Ensure handler returns `True` or `None` (not `False`)
   - `False` prevents sending to Rollbar

7. **Verify correct project:**
   - Make sure you're looking at the correct Rollbar project
   - Check project name matches your token

### Application crashes on startup

**Symptom:**

```
pydantic.ValidationError: 1 validation error for Settings
rollbar_access_token
  Field required [type=missing]
```

**Solutions:**

1. **Missing required configuration:**

   - Set `ROLLBAR_ACCESS_TOKEN` in `.env` file
   - See [Configuration Guide](configuration.md)

2. **Check .env file is in correct location:**

   ```bash
   ls app/.env
   # Should exist
   ```

3. **Verify .env is readable:**
   ```bash
   cat app/.env
   # Should show your variables
   ```

### Module import errors

**Symptom:**

```
ModuleNotFoundError: No module named 'rollbar'
```

**Solution:**

Install dependencies:

```bash
cd app
poetry install
```

Ensure you're running with Poetry:

```bash
poetry run python -m src.main
```

Not just:

```bash
python -m src.main  # Won't use Poetry virtual environment
```

## Development Tool Issues

### mypy issues

**Symptom:**

```
error: Cannot find implementation or library stub for module named 'rollbar'
```

**Solution:**

Ensure dependencies are installed and mypy can find them:

```bash
poetry install
poetry run mypy src
```

**Symptom:**
Too many type errors to fix at once.

**Solution:**

Start with specific files:

```bash
poetry run mypy src/main.py
poetry run mypy src/config.py
```

### Ruff not found

**Symptom:**

```
bash: ruff: command not found
```

**Solution:**

Install development dependencies:

```bash
poetry install
```

Run with Poetry:

```bash
poetry run ruff check src
```

### Ruff configuration not loaded

**Symptom:**
Ruff uses different settings than expected.

**Solution:**

Ensure you're running from the `app` directory where `pyproject.toml` exists:

```bash
cd app
poetry run ruff check src
```

## VS Code Issues

### VS Code not using Poetry virtual environment

**Symptom:**

- Imports show as errors
- Wrong Python version
- Modules not found

**Solution:**

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "Python: Select Interpreter"
3. Choose the Poetry virtualenv (path contains `.venv` and is in the `app` directory)

**Find Poetry virtualenv path:**

```bash
cd app
poetry env info --path
```

### VS Code Python extension issues

**Symptom:**

- Type checking not working
- Linting not active
- Auto-completion missing

**Solution:**

1. **Install Python extension:**

   - Install "Python" by Microsoft
   - Install "Pylance" by Microsoft

2. **Reload VS Code:**

   ```
   Ctrl+Shift+P → "Developer: Reload Window"
   ```

3. **Check settings:**
   - Verify interpreter is set correctly
   - Check that Pylance is active
   - Review `.vscode/settings.json` configuration

### Format on save not working

**Symptom:**
Code doesn't auto-format when saving files.

**Solution:**

1. **Install Ruff extension:**

   - Install "Ruff" by Astral Software (charliermarsh.ruff)

2. **Configure settings in `.vscode/settings.json`:**

   ```json
   {
     "[python]": {
       "editor.formatOnSave": true,
       "editor.defaultFormatter": "charliermarsh.ruff"
     }
   }
   ```

3. **Reload VS Code window**

## Network/Firewall Issues

### Connection timeout to Rollbar

**Symptom:**

```
requests.exceptions.ConnectionError: Connection timeout
```

**Solutions:**

1. **Check firewall settings:**

   - Ensure outbound HTTPS (port 443) is allowed
   - Whitelist `rollbar.com` and `api.rollbar.com`

2. **Check proxy settings:**

   - If behind corporate proxy, configure proxy:
     ```bash
     export HTTPS_PROXY=http://proxy.company.com:8080
     ```

3. **Test connection:**
   ```bash
   curl -I https://api.rollbar.com
   # Should return HTTP 200 OK
   ```

## Interactive Demo/Scenario Issues

### Menu not displaying

**Symptom:**

- Application starts but no menu appears
- Blank screen or immediate exit

**Solutions:**

1. **Check all scenarios are imported:**

   ```bash
   # Verify scenarios module
   poetry run python -c "from src.scenarios import ALL_SCENARIOS; print(len(ALL_SCENARIOS))"
   # Should output: 8
   ```

2. **Check for import errors:**

   ```bash
   poetry run python -c "from src.menu import create_menu; print('Menu module OK')"
   ```

3. **Run with error output:**
   ```bash
   poetry run python -m src.main 2>&1
   # Check for any error messages
   ```

### Scenario fails to run

**Symptom:**

- Error when selecting a specific scenario
- Scenario starts but crashes mid-execution

**Solutions:**

1. **Check scenario imports:**

   - Ensure all required modules are installed
   - Verify rollbar module is available

2. **Check for rollbar initialization:**

   - Ensure `setup_rollbar()` was called successfully
   - Verify access token is configured

3. **Run scenario directly:**

   ```python
   from src.rollbar import setup_rollbar
   from src.scenarios.person_tracking import PersonTrackingScenario

   setup_rollbar()
   scenario = PersonTrackingScenario()
   scenario.run()
   ```

### Data not appearing in Rollbar dashboard

**Symptom:**

- Scenario runs without errors
- No data shows up in Rollbar dashboard

**Solutions:**

1. **Wait a few moments:**

   - Rollbar may take 10-30 seconds to process events
   - Refresh your dashboard

2. **Check correct Rollbar project:**

   - Verify you're looking at the right project
   - Check environment filter (local, staging, production)

3. **Verify access token:**

   - Must be post_client_item or post_server_item token
   - Not a read-only token

4. **Check network connectivity:**

   - Ensure firewall allows HTTPS to rollbar.com
   - Check proxy settings if behind corporate firewall

5. **Enable debug mode:**
   ```python
   # In src/rollbar.py
   rollbar.init(
       access_token=app_settings.rollbar.access_token,
       environment=app_environment.name,
       code_version=app_settings.rollbar.code_version,
       handler='blocking',  # Add this for debugging
   )
   ```

### Creating custom scenarios

**Symptom:**

- New scenario doesn't appear in menu
- Import errors when adding scenario

**Solutions:**

1. **Check scenario implementation:**

   ```python
   # Must inherit from BaseScenario
   from .base import BaseScenario

   class MyScenario(BaseScenario):
       @property
       def name(self) -> str:
           return "My Scenario"

       @property
       def description(self) -> str:
           return "Description"

       def run(self) -> None:
           # Implementation
           pass
   ```

2. **Register in **init**.py:**

   ```python
   # In src/scenarios/__init__.py
   from .my_scenario import MyScenario

   ALL_SCENARIOS = [
       # ... existing scenarios ...
       MyScenario(),
   ]
   ```

3. **Check for syntax errors:**
   ```bash
   poetry run python -c "from src.scenarios.my_scenario import MyScenario; print('OK')"
   ```

See the [Scenarios Guide](scenarios-guide.md) for detailed instructions.

## Getting More Help

If you're still experiencing issues:

### Check Documentation

- [Installation Guide](installation.md) - Setup instructions
- [Configuration Guide](configuration.md) - Configuration options
- [Rollbar Setup Guide](rollbar-setup.md) - Rollbar-specific setup
- [Code Walkthrough](code-walkthrough.md) - Understanding the code

### Rollbar Resources

- [Rollbar Documentation](https://docs.rollbar.com/)
- [Rollbar Python SDK](https://docs.rollbar.com/docs/python)
- [Rollbar Support](https://rollbar.com/support/)
- [Rollbar Status](https://status.rollbar.com/)

### Debug Mode

Enable debug output to see what's happening:

```python
import rollbar
import logging

logging.basicConfig(level=logging.DEBUG)
rollbar.init(..., handler='blocking')  # Synchronous for debugging
```

### Common Command Reference

```bash
# Check Python version
python --version

# Check Poetry version
poetry --version

# View Poetry virtual environment
poetry env info

# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --sync

# Check .env file
cat app/.env

# Test Rollbar connection
poetry run python -c "import rollbar; print('Rollbar imported successfully')"

# Run with debug output
poetry run python -m src.main
```

---

If none of these solutions work, review the code in [src/rollbar.py](../app/src/rollbar.py) and [src/config.py](../app/src/config.py) to ensure your environment is configured correctly.
