# Development Guide

This guide covers the development tools and workflows for working with the Rollbar Python Integration project.

## Overview

This project uses modern Python development tools to ensure code quality, type safety, and consistent formatting:

- **mypy** - Static type checker for catching type errors before runtime
- **Ruff** - Fast linter and formatter (replaces flake8, black, isort, and more)
- **Poetry** - Dependency management and virtual environment handling

All development tools are automatically installed when you run `poetry install`.

## Type Checking with mypy

mypy performs static type analysis to catch type-related bugs before runtime.

### Running Type Checks

From the `app` directory:

```bash
poetry run mypy src
```

**Expected output (no errors):**

```
Success: no issues found in 3 source files
```

### Type Checking Configuration

This project uses strict mypy configuration in `pyproject.toml`:

```toml
[tool.mypy]
strict = true
warn_unreachable = true
warn_unused_ignores = true
```

**What strict mode includes:**

- `disallow_untyped_defs` - All functions must have type annotations
- `disallow_any_unimported` - Prevents accidental use of `Any`
- `disallow_any_expr` - Requires explicit types
- `no_implicit_optional` - Explicit `Optional` required for `None` defaults
- `warn_return_any` - Warns when returning `Any`
- `warn_unused_ignores` - Catches unnecessary `type: ignore` comments

### Integration with VS Code

The project includes VS Code tasks for type checking:

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "Tasks: Run Task"
3. Select "Python: Type Check with mypy"

Or add to your VS Code settings:

```json
{
  "python.linting.mypyEnabled": true,
  "python.linting.enabled": true
}
```

## Linting with Ruff

Ruff is an extremely fast Python linter that checks for code quality issues, bugs, and style violations.

### Running Linting

Check all code:

```bash
poetry run ruff check src
```

**Example output:**

```
All checks passed!
```

Check a specific file:

```bash
poetry run ruff check src/main.py
```

### Auto-fixing Issues

Many issues can be automatically fixed:

```bash
poetry run ruff check --fix src
```

This will automatically fix:

- Unused imports
- Import sorting
- Unnecessary list/dict/set literals
- And more

### Ruff Configuration

Configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "C4", "PL"]
```

**Selected rule sets:**

- `E` - pycodestyle errors (PEP 8 violations)
- `F` - Pyflakes (undefined names, unused imports)
- `I` - isort (import sorting)
- `N` - pep8-naming (naming conventions)
- `UP` - pyupgrade (modern Python syntax)
- `B` - flake8-bugbear (likely bugs)
- `A` - flake8-builtins (shadowing builtins)
- `C4` - flake8-comprehensions (list/dict comprehension improvements)
- `PL` - Pylint (additional code quality checks)

### Common Linting Issues

**Unused imports:**

```python
# ❌ Error: Unused import
import sys
from typing import Optional

def hello() -> str:
    return "hello"

# ✅ Fixed: Remove unused imports
def hello() -> str:
    return "hello"
```

**Import sorting:**

```python
# ❌ Error: Imports not sorted
from typing import Any
import sys
from rollbar import rollbar

# ✅ Fixed: Sorted imports (stdlib → third-party → local)
import sys
from typing import Any

from rollbar import rollbar
```

**Shadowing builtins:**

```python
# ❌ Error: Shadowing built-in 'list'
def process(list: list[int]) -> None:
    ...

# ✅ Fixed: Rename parameter
def process(items: list[int]) -> None:
    ...
```

## Code Formatting with Ruff

Ruff also provides fast code formatting (Black-compatible).

### Running Formatter

Format all code:

```bash
poetry run ruff format src
```

Format a specific file:

```bash
poetry run ruff format src/main.py
```

Check formatting without making changes:

```bash
poetry run ruff format --check src
```

### Formatting Rules

Ruff follows these formatting conventions:

- **Line length:** 88 characters (Black-compatible)
- **Quotes:** Double quotes for strings
- **Indentation:** 4 spaces
- **Trailing commas:** Added for multi-line structures
- **Import sorting:** Automatic with `ruff check --fix`

### Auto-format on Save in VS Code

Add to your VS Code settings (`.vscode/settings.json`):

```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

Requires the Ruff VS Code extension.

## Running the Application

### Standard Execution

Run the demo application:

```bash
poetry run python -m src.main
```

### With Type Checking First

Check types before running:

```bash
poetry run mypy src && poetry run python -m src.main
```

### Full Quality Check

Run all checks before executing:

```bash
poetry run mypy src && poetry run ruff check src && poetry run python -m src.main
```

## VS Code Integration

### Recommended Extensions

Install these VS Code extensions for the best development experience:

1. **Python** (`ms-python.python`) - Python language support
2. **Pylance** (`ms-python.vscode-pylance`) - Fast Python language server
3. **Ruff** (`charliermarsh.ruff`) - Ruff linting and formatting

### VS Code Tasks

The project can include pre-configured tasks. Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Python: Type Check with mypy",
      "type": "shell",
      "command": "poetry run mypy src",
      "problemMatcher": [],
      "group": "test"
    },
    {
      "label": "Python: Lint with Ruff",
      "type": "shell",
      "command": "poetry run ruff check src",
      "problemMatcher": [],
      "group": "test"
    },
    {
      "label": "Python: Format with Ruff",
      "type": "shell",
      "command": "poetry run ruff format src",
      "problemMatcher": [],
      "group": "none"
    },
    {
      "label": "Python: Run Application",
      "type": "shell",
      "command": "poetry run python -m src.main",
      "problemMatcher": [],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

Access tasks via Command Palette → "Tasks: Run Task"

### VS Code Settings

Recommended settings in `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/app/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  },
  "python.analysis.typeCheckingMode": "strict",
  "python.linting.mypyEnabled": true,
  "python.linting.enabled": true
}
```

## Development Workflow

### Recommended Workflow

1. **Write code** with type annotations
2. **Format** with `ruff format src`
3. **Lint** with `ruff check --fix src`
4. **Type check** with `mypy src`
5. **Test** by running `python -m src.main`
6. **Commit** changes

### Pre-commit Checks

Consider adding a pre-commit hook. Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
cd app
poetry run mypy src || exit 1
poetry run ruff check src || exit 1
echo "✅ Pre-commit checks passed"
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

### CI/CD Integration

For CI/CD pipelines (GitHub Actions, GitLab CI, etc.), add these checks:

```yaml
# Example GitHub Actions
- name: Install dependencies
  run: |
    cd app
    poetry install

- name: Type check
  run: |
    cd app
    poetry run mypy src

- name: Lint
  run: |
    cd app
    poetry run ruff check src

- name: Format check
  run: |
    cd app
    poetry run ruff format --check src
```

## Troubleshooting

### mypy issues

**Module not found:**

```
error: Cannot find implementation or library stub for module named 'rollbar'
```

**Solution:** Install dependencies and ensure mypy can find them:

```bash
poetry install
poetry run mypy src
```

**Too many errors:**
Start with specific files and work up:

```bash
poetry run mypy src/main.py
```

### Ruff issues

**Ruff not found:**

```bash
poetry install
```

**Configuration not loaded:**
Ensure you're running from the `app` directory where `pyproject.toml` exists.

### VS Code not using virtual environment

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Python: Select Interpreter"
3. Choose the Poetry virtualenv (`.venv/bin/python`)

## Working with YAML Configuration

The project uses YAML configuration files (`settings.yaml`, `settings.local.yaml`). Here's how to work with them effectively:

### YAML Validation

Validate YAML syntax before running:

**Using Python:**

```bash
poetry run python -c "import yaml; yaml.safe_load(open('settings.local.yaml'))"
```

**Using yamllint (if installed):**

```bash
yamllint settings.local.yaml
```

### Common YAML Issues

**Indentation errors:**

```yaml
# ❌ Error: Inconsistent indentation
rollbar:
 access_token: abc123
  code_version: v1.0

# ✅ Fixed: Consistent 2-space indentation
rollbar:
  access_token: abc123
  code_version: v1.0
```

**Type errors:**

```yaml
# ❌ Error: String needed but found number
rollbar:
  access_token: 12345

# ✅ Fixed: Quoted string
rollbar:
  access_token: "12345"
```

### VS Code YAML Support

Install the YAML extension for better editing:

- **YAML** (`redhat.vscode-yaml`) - YAML language support with validation

## Working with msgspec

The project uses [msgspec](https://jcristharif.com/msgspec/) for efficient serialization. Here are some tips:

### Defining Structured Data

```python
import msgspec

class CustomData(msgspec.Struct):
    user_id: str
    action: str
    timestamp: int

# Serialize to dict
data = CustomData(user_id="123", action="login", timestamp=1234567890)
payload["data"]["custom"] = msgspec.to_builtins(data)
```

### Type Checking with msgspec

mypy understands msgspec.Struct types:

```python
data = CustomData(user_id="123", action="login", timestamp="invalid")
# mypy error: Argument "timestamp" has incompatible type "str"; expected "int"
```

### Benefits of msgspec

- **10-80x faster** than Pydantic for serialization
- **Type-safe** with full mypy support
- **Zero-copy** operations where possible
- **Compact** - Smaller memory footprint

## Best Practices

1. **Always use type annotations** - Helps catch bugs early
2. **Run checks before committing** - Prevents broken code from entering the repository
3. **Fix warnings promptly** - Don't let technical debt accumulate
4. **Use auto-formatting** - Let tools handle style, focus on logic
5. **Enable editor integration** - Get instant feedback while coding
6. **Validate YAML files** - Check syntax before running the application
7. **Use msgspec for performance** - Prefer msgspec.Struct over dict for structured data

## Next Steps

- Review the [Code Walkthrough](code-walkthrough.md) to understand the codebase structure
- Explore the [Customization Guide](customization.md) to adapt the code for your needs
- Check out [mypy documentation](https://mypy.readthedocs.io/) for advanced type checking
- Read [Ruff documentation](https://docs.astral.sh/ruff/) for all available rules

---

Happy coding with confidence! 🚀
