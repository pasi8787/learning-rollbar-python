# Code Walkthrough

This guide provides a detailed walkthrough of the Rollbar integration code, explaining how each component works and how they fit together.

## Project Structure

```
app/
├── src/
│   ├── scenarios/          # Demo scenarios (8 different demos)
│   │   ├── __init__.py
│   │   ├── base.py        # Abstract base class for scenarios
│   │   └── *.py           # Individual scenario implementations
│   ├── config.py          # YAML-based settings management
│   ├── environment.py     # Environment configuration
│   ├── main.py            # Interactive menu application
│   ├── menu.py            # Menu system
│   ├── rollbar.py         # Rollbar integration & payload enrichment
│   └── utils.py           # Utility functions
├── .env                   # (optional) Environment variables (git-ignored)
├── settings.yaml          # Base configuration
├── settings.local.yaml    # Local environment config (git-ignored)
└── pyproject.toml         # Project dependencies and configuration
```

## [environment.py](../app/src/environment.py) - Environment Configuration

This module provides environment-specific configuration and path management.

### ApplicationEnvironment Class

```python
class ApplicationEnvironment(BaseSettings):
    name: str = Field(default="local", validation_alias="ENVIRONMENT")

    @property
    def root_path(self) -> Path:
        return _APP_ROOT

    def from_root(self, relative_path: Path | str) -> Path:
        return _APP_ROOT / relative_path
```

**Key features:**

- **Environment detection:** Reads from `ENVIRONMENT` variable or defaults to "local"
- **Path utilities:** Provides helpers for resolving paths from the app root
- **CLI support:** Can parse environment from command-line arguments

## [config.py](../app/src/config.py) - Settings Management

This module manages application configuration using YAML files and Pydantic Settings, providing a multi-source configuration hierarchy.

### Configuration Structure

The configuration uses a nested structure with specialized models:

```python
class RollbarSettings(BaseModel):
    access_token: str = Field(description="Rollbar access token")
    code_version: str = Field(default="")
```

```python
class ApplicationSettings(BaseSettings):
    rollbar: RollbarSettings = Field(description="Rollbar settings")
```

### Multi-Source Configuration Hierarchy

Settings are loaded from multiple sources in priority order:

1. **Environment variables** (highest priority)
2. **.env file**
3. **settings.{environment}.yaml** (e.g., settings.local.yaml)
4. **settings.yaml** (base configuration, lowest priority)

```python
@classmethod
def settings_customise_sources(cls, ...) -> tuple[PydanticBaseSettingsSource, ...]:
    return (
        env_settings,
        dotenv_settings,
        YamlConfigSettingsSource(settings_cls,
            app_environment.from_root(f"settings.{app_environment.name}.yaml")),
        YamlConfigSettingsSource(settings_cls,
            app_environment.from_root("settings.yaml")),
        init_settings,
    )
```

### Nested Configuration Support

Environment variables can use nested delimiters:

```python
model_config = SettingsConfigDict(
    env_nested_delimiter="__",  # Use ROLLBAR__ACCESS_TOKEN
    case_sensitive=False,
    extra="ignore",
)
```

Example: `ROLLBAR__ACCESS_TOKEN=abc123` maps to `rollbar.access_token`

### Auto-detection of Git Commit Hash

The `code_version` field is automatically populated with the current git commit hash:

```python
@field_validator("code_version", mode="before")
@classmethod
def not_empty_value_or_git_commit(cls, value: str) -> str:
    if value:
        return value

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
            cwd=app_environment.root_path,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"
```

**Benefits:**

- Automatic version tracking in deployments
- Helps identify which commit introduced errors
- No manual version updates needed

### Configuration Access

```python
app_settings = ApplicationSettings()
```

A single instance provides access to all configuration throughout the application.

## [rollbar.py](../app/src/rollbar.py) - Rollbar Integration

This module contains the core Rollbar integration, including initialization and payload enrichment logic.

### Initialization

```python
def setup_rollbar() -> None:
    """Initialize Rollbar with application settings."""
    rollbar.init(
        access_token=app_settings.rollbar.access_token,
        environment=app_environment.name,
        code_version=app_settings.rollbar.code_version,
    )
    rollbar.events.add_payload_handler(_payload_handler)
```

**What it does:**

1. **Initializes Rollbar SDK** with credentials from YAML configuration
2. **Registers payload handler** - called for every error before sending to Rollbar
3. Should be **called once at application startup**

### Payload Handler

The `_payload_handler` function is called for every error payload before it's sent to Rollbar, allowing you to enrich or modify errors.

```python
def _payload_handler(payload: dict, **_kw: object) -> dict | bool:
    """Enrich Rollbar error payloads with custom metadata."""
    level = payload["data"]["level"]
    print(f"Processing {level} level event")

    payload["data"]["framework"] = "oreore_framework 1.0"
    payload["data"]["base_model_custom"] = msgspec.to_builtins({
        "the_model": CustomMetadata(...)
    })

    return payload
```

**Key points:**

- **All events are sent** - No filtering by level (scenarios control what they send)
- **Logs event level** - Prints the level for demonstration purposes
- **Returns modified payload** - Returning the dict sends it; returning False would filter it out

### Framework Identification

```python
payload["data"]["framework"] = "oreore_framework 1.0"
```

Adds framework information to every error payload, useful for:

- Tracking framework-specific issues
- Identifying which framework version introduced bugs
- Filtering errors by framework

### Structured Data Serialization with msgspec

```python
import msgspec

class CustomMetadata(msgspec.Struct):
    dict_value: dict[str, int]
    empty_value: None
    list_value: list[str]
    simple_value: str
```

The application uses [msgspec](https://jcristharif.com/msgspec/) for efficient serialization:

```python
payload["data"]["base_model_custom"] = msgspec.to_builtins({
    "the_model": CustomMetadata(
        empty_value=None,
        dict_value={"key1": 10, "key2": 20},
        list_value=[1, 2, 3],
        simple_value="foo_value",
    )
})
```

**Why msgspec:**

- **Faster** than json/Pydantic for serialization
- **Type-safe** with msgspec.Struct
- **Clean conversion** - `to_builtins()` converts to JSON-serializable types
- **Zero-copy** operations where possible

**Benefits:**

- Demonstrates structured data in payloads
- Shows type-safe serialization
- Useful for complex application state

### Customization Patterns

The payload handler in scenarios can add additional context:

**Person/User Tracking:**

```python
payload["data"]["person"] = {
    "id": "user123",
    "username": "john.doe",
    "email": "john@example.com"
}
```

**Custom Metadata:**

```python
payload["data"]["custom"] = {
    "trace_id": "abc123",
    "feature_flags": ["new_ui", "beta_features"]
}
```

**Arbitrary Fields:**

```python
payload["data"]["request_context"] = {
    "url": "/api/users",
    "method": "POST",
    "status_code": 500
}
```

See the [Scenarios Guide](scenarios-guide.md) for examples of each pattern.

## [utils.py](../app/src/utils.py) - Utility Functions

Shared utility functions used across the application.

```python
def clear_screen():
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def print_header():
    """Print the application header."""
    print("=" * 60)
    print("ROLLBAR PYTHON SDK - INTERACTIVE DEMO")
    print("=" * 60)

def wait_for_user():
    """Wait for user to press Enter to continue."""
    input("\nPress Enter to continue...")
```

These utilities provide cross-platform console operations and consistent UI elements.

## [menu.py](../app/src/menu.py) - Menu System

The menu system provides an interactive interface for running demo scenarios.

### Menu Class

```python
class Menu:
    def __init__(self, scenarios: list[BaseScenario]):
        self.scenarios = scenarios

    def display(self) -> None:
        """Display the menu options."""
        for idx, scenario in enumerate(self.scenarios, start=1):
            print(f"{idx}. {scenario.name} - {scenario.description}")

    def run(self) -> None:
        """Run the main menu loop."""
        while True:
            clear_screen()
            print_header()
            self.display()
            choice = self.get_user_choice()
            self.handle_choice(choice)
```

**Key features:**

- **Dynamic scenario loading** - Displays all registered scenarios
- **Input validation** - Handles invalid choices gracefully
- **Continuous loop** - Returns to menu after each scenario

### Factory Function

```python
def create_menu() -> Menu:
    """Factory function to create a Menu with all scenarios."""
    return Menu(ALL_SCENARIOS)
```

This pattern allows easy testing and scenario management.

## [scenarios/base.py](../app/src/scenarios/base.py) - Scenario Base Class

Defines the interface for all demo scenarios using the Abstract Base Class pattern.

```python
from abc import ABC, abstractmethod

class BaseScenario(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of the scenario."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Execute the demo scenario."""
        pass
```

**Design benefits:**

- **Consistent interface** - All scenarios implement the same methods
- **Type safety** - IDE autocomplete and type checking work correctly
- **Extensibility** - Easy to add new scenarios
- **SOLID principles** - Single Responsibility, Open/Closed

## [scenarios/](../app/src/scenarios/) - Demo Scenarios

The application includes 8 different scenarios demonstrating various Rollbar features:

1. **Person Tracking** - Associate errors with specific users
2. **Custom Data** - Attach metadata and context to errors
3. **Error Levels** - Demonstrate all 5 severity levels
4. **Exception vs Message** - Compare exception and message reporting
5. **Searchable Fields** - Show how to make data searchable in Rollbar
6. **Multiple Errors** - Send a sequence of related errors
7. **Exception Types** - Demonstrate different Python exception types
8. **Business Events** - Track non-error application events

Each scenario:

- Implements the `BaseScenario` interface
- Prints explanatory information
- Sends appropriate data to Rollbar
- Demonstrates a specific Rollbar feature

See the [Scenarios Guide](scenarios-guide.md) for detailed documentation of each scenario.

## [main.py](../app/src/main.py) - Application Entry Point

The main module is now a simple orchestrator that initializes Rollbar and launches the interactive menu.

```python
def main():
    """Main application entry point."""
    # Initialize Rollbar
    setup_rollbar()

    print("\nRollbar initialized successfully!")
    print("Starting interactive demo...\n")

    # Create and run the menu
    menu = create_menu()
    menu.run()
```

**Architecture notes:**

- **Separation of concerns** - Configuration, UI, and business logic are separate
- **SOLID principles** - Each module has a single responsibility
- **Testability** - Components can be tested independently
- **Extensibility** - New scenarios can be added without modifying main.py

## Architecture Overview

This application follows SOLID principles with clear separation of concerns:

**Configuration Layer:**

- `environment.py` - Environment detection and path management
- `config.py` - Multi-source YAML configuration with Pydantic

**Integration Layer:**

- `rollbar.py` - Rollbar SDK initialization and payload enrichment

**Presentation Layer:**

- `utils.py` - Console UI utilities
- `menu.py` - Interactive menu system
- `main.py` - Application orchestration

**Business Logic Layer:**

- `scenarios/base.py` - Abstract scenario interface
- `scenarios/*.py` - Individual feature demonstrations

**Benefits of this architecture:**

- **Testability** - Each module can be tested independently
- **Extensibility** - Easy to add new scenarios or configuration sources
- **Maintainability** - Clear boundaries between concerns
- **Reusability** - Modules can be adapted for real applications

## Key Technologies

**Configuration:**

- **Pydantic** - Type-safe settings management
- **PyYAML** - YAML configuration file support
- **Multi-source hierarchy** - Environment variables, .env, YAML files

**Serialization:**

- **msgspec** - High-performance structured data serialization
- Faster than JSON or Pydantic for serialization tasks
- Type-safe with `msgspec.Struct`

**Error Tracking:**

- **Rollbar Python SDK** - Error monitoring and tracking
- **Payload handlers** - Custom enrichment before sending
- **Person tracking** - Associate errors with users
- **Custom metadata** - Application-specific context

## Best Practices

**Security:**

- Never log sensitive data (passwords, tokens, PII)
- Scrub sensitive fields from payloads if needed
- Use non-sensitive identifiers when possible

**Performance:**

- Keep payload handlers fast (they run on every error)
- Avoid external API calls in handlers
- Use async sending (built into Rollbar SDK)

**Maintainability:**

- Use type hints for IDE support and type checking
- Document custom fields and their purpose
- Follow SOLID principles when adding features
- Keep scenarios focused on single features

## Next Steps

- Run the interactive demo and explore each scenario
- Read the [Scenarios Guide](scenarios-guide.md) for detailed scenario documentation
- Review the [Configuration Guide](configuration.md) for YAML configuration details
- Explore the [Customization Guide](customization.md) to extend the application
- Check the [Troubleshooting Guide](troubleshooting.md) if you encounter issues

---

Now you understand how the application is structured and how each component works together!
