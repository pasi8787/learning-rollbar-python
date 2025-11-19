# Code Walkthrough

This guide provides a detailed walkthrough of the Rollbar integration code, explaining how each component works and how they fit together.

## Project Structure

```
app/
├── src/
│   ├── config.py      # Settings management with Pydantic
│   ├── rollbar.py     # Rollbar integration & payload enrichment
│   └── main.py        # Demo script
├── pyproject.toml     # Project dependencies and configuration
├── .env.example       # Environment variable template
└── .env               # Your local configuration (git-ignored)
```

## [config.py](../app/src/config.py) - Settings Management

This module manages application configuration using Pydantic Settings, providing type-safe configuration loading from environment variables.

### Settings Class

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    rollbar_access_token: str              # Required field
    environment: str = "production"        # Optional with default
    code_version: str = "unknown"          # Auto-detected from git

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

**Key features:**

- **Automatic loading:** Reads from `.env` file automatically
- **Type validation:** Pydantic ensures `rollbar_access_token` is present and is a string
- **Default values:** `environment` defaults to `"production"` if not specified
- **Extra fields ignored:** Unknown environment variables don't cause errors

### Auto-detection of Git Commit Hash

The `code_version` field is automatically populated with the current git commit hash:

```python
@field_validator("code_version", mode="before")
@classmethod
def get_git_commit(cls, v: str) -> str:
    if v != "unknown":
        return v  # Use explicitly set value

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"  # Fallback if git unavailable
```

**How it works:**

1. Checks if `CODE_VERSION` is explicitly set in `.env`
2. If not, runs `git rev-parse HEAD` to get the current commit hash
3. Returns the full commit hash as the version
4. Falls back to `"unknown"` if git command fails or `.git` directory doesn't exist

**Benefits:**

- Automatic version tracking in deployments
- Helps identify which commit introduced errors
- No manual version updates needed during development

### Singleton Pattern

```python
settings = Settings()
```

A single instance of `Settings` is created and shared across the application, ensuring consistent configuration.

## [rollbar.py](../app/src/rollbar.py) - Rollbar Integration

This module contains the core Rollbar integration, including initialization and payload enrichment logic.

### Initialization

```python
def setup_rollbar() -> None:
    """Initialize Rollbar and register the payload handler."""
    rollbar.init(
        access_token=settings.rollbar_access_token,
        environment=settings.environment,
        code_version=settings.code_version,
    )
    rollbar.events.add_payload_handler(_payload_handler)
```

**What it does:**

1. **Initializes Rollbar SDK** with credentials from settings
2. **Registers payload handler** - called for every error before sending to Rollbar
3. Should be **called once at application startup**

### Payload Handler - The Heart of Enrichment

The `_payload_handler` function is where all the magic happens. It's called for every error payload before it's sent to Rollbar, allowing you to modify, enrich, or filter errors.

```python
def _payload_handler(payload: dict, **_kw: Any) -> bool:
    """
    Enriches error payloads before sending to Rollbar.

    Returns:
        False to prevent sending (filter out)
        True or None to allow sending
    """
```

### Filtering by Severity Level

```python
# Only send errors, not info or warning messages
if payload["data"]["level"] != "error":
    print("Not an error, ignoring")
    return False  # Don't send to Rollbar
```

**Why filter?**

- Reduces noise in your error tracking
- Saves your Rollbar event quota
- Keeps focus on actual errors
- Info/warning messages are logged locally but not sent

**Available levels:**
- `"critical"` - Critical errors
- `"error"` - Regular errors
- `"warning"` - Warnings
- `"info"` - Informational messages
- `"debug"` - Debug messages

**Customization example:**
```python
# Send errors and critical messages only
if payload["data"]["level"] not in ["error", "critical"]:
    return False
```

### Person/User Tracking

```python
payload["data"]["person"] = {
    "id": "1234",           # Required: unique user identifier
    "tenant": "tenant_name" # Optional: custom context field
}
```

**Purpose:**

Person tracking links errors to specific users, enabling you to:
- See all errors affecting a particular user
- Contact users about bugs they experienced
- Track error rates per user or tenant
- Identify if errors are user-specific or system-wide

**Required field:**
- `id` - Unique identifier for the user (string or number)

**Optional standard fields:**
- `username` - Display name
- `email` - Contact email

**Custom fields:**
- Any additional fields (like `tenant`, `organization_id`, etc.)

**Real-world example:**
```python
def _get_person() -> dict:
    user = get_current_user()  # Your auth system
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "tenant": user.tenant_id,
        "subscription_tier": user.subscription_tier,
    }

payload["data"]["person"] = _get_person()
```

### Custom Metadata Injection

```python
payload["data"]["custom"] = {
    "trace_id": uuid4().hex,           # Unique trace ID
    "feature_flags": ["feature_1", "feature_2"],  # Active features
    # Merge with any existing custom data
    **payload["data"].get("custom", {}),
}
```

**Purpose:**

Custom metadata adds application-specific context to every error, helping with:
- Distributed tracing (trace IDs)
- Understanding which features were active
- Correlating errors with external systems
- Debugging with additional context

**Common custom metadata:**

```python
payload["data"]["custom"] = {
    # Tracing
    "trace_id": request_trace_id,
    "request_id": request_id,
    "correlation_id": correlation_id,

    # Feature flags
    "feature_flags": get_active_features(),
    "experiment_variant": get_ab_test_variant(),

    # Business context
    "tenant_id": current_tenant,
    "organization_id": current_org,
    "user_role": user_role,

    # Technical context
    "deployment_id": os.getenv("DEPLOYMENT_ID"),
    "pod_name": os.getenv("HOSTNAME"),
    "region": os.getenv("AWS_REGION"),
}
```

### Arbitrary Data Injection

```python
payload["data"]["foo_key"] = {
    "bar_key": "bar_value",
    "baz_key": [1, 2, 3],
    "deep": {
        "nested": {"structure": True}
    }
}
```

**Purpose:**

You can add any JSON-serializable data directly to the payload. This is useful for:
- Domain-specific data structures
- Complex nested information
- Data that doesn't fit in the `custom` section

**What you can add:**
- Strings, numbers, booleans
- Lists and dictionaries
- Nested structures
- Dates (as ISO strings)
- Any JSON-serializable data

**What to avoid:**
- Binary data (encode as base64 first)
- Circular references
- Sensitive data (passwords, tokens, PII)

### Pydantic Model Serialization

```python
from pydantic import BaseModel, TypeAdapter

class CustomMetadata(BaseModel):
    foo: str
    bar: dict[str, int]

payload["data"]["base_model_custom"] = TypeAdapter(dict[str, Any]).dump_python({
    "the_model": CustomMetadata(
        foo="foo_value",
        bar={"key1": 10, "key2": 20}
    )
})
```

**Purpose:**

Demonstrates how to serialize Pydantic models for inclusion in error payloads. This is useful when you have structured configuration or state objects.

**Why use TypeAdapter:**
- Properly serializes Pydantic models to dictionaries
- Handles nested models and complex types
- Ensures JSON-serializable output

**Alternative approaches:**
```python
# Method 1: model_dump()
payload["data"]["my_model"] = my_model.model_dump()

# Method 2: model_dump_json() then parse
import json
payload["data"]["my_model"] = json.loads(my_model.model_dump_json())

# Method 3: TypeAdapter (shown above)
```

### Framework Identification

```python
payload["data"]["framework"] = "oreore_framework 1.0"
```

**Purpose:**

Identifies which framework or library version is being used. Useful for:
- Tracking framework-specific issues
- Identifying which framework version introduced bugs
- Filtering errors by framework

**Real-world examples:**
```python
payload["data"]["framework"] = f"FastAPI {fastapi.__version__}"
payload["data"]["framework"] = f"Django {django.__version__}"
payload["data"]["framework"] = "MyCustomFramework 2.3.1"
```

## [main.py](../app/src/main.py) - Demo Script

This module demonstrates two ways to report errors to Rollbar.

### Application Setup

```python
from src.rollbar import setup_rollbar

setup_rollbar()
```

Call `setup_rollbar()` once at application startup, before any errors might occur.

### Manual Message Reporting

```python
rollbar.report_message(
    "Rollbar is configured correctly!",
    level="info",  # Will be filtered out by our handler
    extra_data={"trace_id": "test_trace_id"},
    payload_data={"foo_key": "bar", "bar_key": "baz"}
)
```

**Parameters:**

- **message** - Text message to log
- **level** - Severity level (`"info"`, `"warning"`, `"error"`, `"critical"`)
- **extra_data** - Goes into `payload["data"]["custom"]`
- **payload_data** - Merged directly into `payload["data"]`

**Note:** This info message is filtered out by the payload handler since it's not an error level.

### Exception Reporting

```python
try:
    a: None = None
    a.hello()  # AttributeError: 'NoneType' object has no attribute 'hello'
except Exception:
    rollbar.report_exc_info()  # Automatically captures exception details
```

**How it works:**

1. Exception occurs within try block
2. `report_exc_info()` captures the exception info from the current except block
3. Rollbar SDK constructs a payload with:
   - Exception type and message
   - Full stack trace
   - Local variables (optional, configured via SDK)
4. Payload handler enriches the payload
5. Enriched payload is sent to Rollbar

**Alternative approaches:**

```python
# Capture specific exception
try:
    risky_operation()
except ValueError as e:
    rollbar.report_exc_info(exc_info=(type(e), e, e.__traceback__))

# Report without being in except block
import sys
try:
    dangerous_function()
except Exception:
    exc_info = sys.exc_info()
    rollbar.report_exc_info(exc_info=exc_info)
```

## Key Features Demonstrated

### 1. Payload Handlers

The `_payload_handler` function is the most powerful feature, enabling:

**Before sending each error, you can:**
- Add authentication context (user ID, tenant, session)
- Inject request tracing IDs for distributed tracing
- Include feature flag states
- Add custom application state
- Filter errors by severity, user, or other criteria
- Scrub sensitive data
- Add timestamps or correlation IDs

**Use cases:**
- Web apps: Add request URL, method, headers
- Microservices: Add service name, instance ID, pod name
- Multi-tenant apps: Add tenant/organization context
- Feature-flagged apps: Add which features were enabled
- Distributed systems: Add trace IDs for correlating across services

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

**This enables you to:**
- See all errors affecting a specific user in Rollbar's People tab
- Contact users about bugs they encountered
- Track error rates per user or tenant
- Identify if errors are widespread or user-specific
- Prioritize fixes based on affected users

### 3. Custom Metadata

Add application-specific context that helps debug issues:

```python
payload["data"]["custom"] = {
    "trace_id": request_trace_id,
    "feature_flags": get_active_features(),
    "experiment_variant": get_ab_test_variant(),
    "request_id": request_id,
    "correlation_id": correlation_id,
    "session_id": session_id,
}
```

**Benefits:**
- Correlate errors with external logs/traces
- Understand application state when error occurred
- Debug feature flag interactions
- Track A/B test variants
- Link to related systems (databases, queues, etc.)

### 4. Version Tracking

Automatically track which deployment introduced an error:

- Git commit hash is auto-detected via `config.py`
- Helps identify when bugs were introduced
- Enables rolling back to previous versions
- Tracks error trends across deployments

**Rollbar Dashboard features:**
- Deployments tab shows error rates per version
- "Introduced in" version for each error
- Compare error rates between versions
- Track if deployments fixed or introduced errors

### 5. Environment Filtering

Separate errors by environment:

```python
environment=settings.environment  # "local", "staging", "production"
```

**Benefits:**
- Development errors don't pollute production data
- Different alert rules per environment
- Environment-specific filtering in dashboard
- Easier debugging with environment-specific context

## Viewing Enriched Data in Rollbar

After running the demo, check your Rollbar dashboard to see all the enriched data:

### Error Details Page

1. **Overview** - Exception type, message, stack trace
2. **Custom Data** section shows:
   - `trace_id` - UUID generated for this error
   - `feature_flags` - Array of feature names
   - `foo_key` - Custom nested data structure
   - `base_model_custom` - Serialized Pydantic model
3. **Person** section shows:
   - ID: 1234
   - Tenant: tenant_name
4. **Environment** shows:
   - Environment: local (or your configured value)
   - Code version: Your git commit hash
   - Framework: oreore_framework 1.0
5. **Occurrences** - Each occurrence includes all custom metadata

### People Tab

- Click "People" in sidebar
- See user ID 1234 listed
- Click to see all errors affecting this user

## Best Practices

### Security

1. **Never log sensitive data:**
   ```python
   # ❌ Bad - Exposes sensitive data
   payload["data"]["custom"]["password"] = user_password
   payload["data"]["custom"]["credit_card"] = cc_number

   # ✅ Good - Log non-sensitive identifiers
   payload["data"]["custom"]["user_id"] = user_id
   payload["data"]["custom"]["payment_method"] = "visa_ending_1234"
   ```

2. **Scrub sensitive data from payloads:**
   ```python
   def _scrub_sensitive_data(data: dict) -> dict:
       sensitive_keys = ["password", "token", "secret", "api_key"]
       for key in sensitive_keys:
           if key in data:
               data[key] = "[REDACTED]"
       return data
   ```

### Performance

1. **Keep payload handlers fast** - They run on every error
2. **Avoid external API calls** - Use cached data or context variables
3. **Don't block** - Rollbar sends asynchronously, but handlers are synchronous

### Maintainability

1. **Organize helper functions:**
   ```python
   def _get_person() -> dict:
       """Get current user information."""
       ...

   def _get_custom_data() -> dict:
       """Get custom metadata for errors."""
       ...

   def _should_send_error(payload: dict) -> bool:
       """Determine if error should be sent to Rollbar."""
       ...
   ```

2. **Use type hints** - Helps with IDE autocomplete and mypy checking
3. **Document custom fields** - Explain what each field means
4. **Keep it DRY** - Don't duplicate enrichment logic

## Next Steps

- Explore the [Customization Guide](customization.md) to adapt this code for your application
- Review the [Troubleshooting Guide](troubleshooting.md) if you encounter issues
- Read [Rollbar's Payload Structure docs](https://docs.rollbar.com/docs/items-json) for advanced customization
- Check out [Rollbar's Person Tracking docs](https://docs.rollbar.com/docs/person-tracking) for more details

---

Now you understand how the Rollbar integration works! Customize it for your needs and start tracking errors effectively.
