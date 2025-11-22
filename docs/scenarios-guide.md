# Scenarios Guide

This guide provides detailed documentation for each of the 8 interactive demo scenarios included in the Rollbar Python Integration application.

## Overview

The application features a menu-driven interface that lets you explore different Rollbar capabilities through practical scenarios. Each scenario demonstrates a specific feature or use case, sending real data to Rollbar so you can see the results in your dashboard.

## Running Scenarios

Start the interactive demo:

```bash
cd app
poetry run python -m src.main
```

The menu will display all available scenarios. Select a number to run that scenario, then check your Rollbar dashboard to see the results.

## The Scenarios

### 1. Person Tracking

**Demonstrates:** Associating errors with specific users

**What it does:**

- Sends errors for three different user profiles
- Each error includes user ID, username, email, and subscription level
- Shows how to track which users are affected by issues

**Example output in Rollbar:**

- People tab shows all affected users
- Each user has their complete profile information
- Search by user ID, username, or email
- See all errors affecting a specific user

**Key concepts:**

```python
payload_data={
    "person": {
        "id": "user_123",
        "username": "alice_smith",
        "email": "alice@example.com",
        "subscription": "premium",
    }
}
```

**Use cases:**

- Track error rates per user
- Contact users about bugs they experienced
- Identify if errors are user-specific or system-wide
- Prioritize fixes based on affected user count

### 2. Custom Data

**Demonstrates:** Attaching metadata and context to errors

**What it does:**

- Sends errors with rich custom metadata
- Shows three different error types with relevant context:
  - Payment processing failure with transaction details
  - API rate limit exceeded with usage metrics
  - Database query timeout with performance data

**Example custom fields:**

```python
extra_data={
    "payment_id": "pay_abc123",
    "payment_method": "credit_card",
    "amount": 149.99,
    "currency": "USD",
    "attempt_number": 3,
}
```

**Rollbar features:**

- All custom fields are searchable: `custom[payment_id]:pay_abc123`
- Group errors by custom fields
- Create alerts based on custom field values
- Filter dashboard by any custom field

**Use cases:**

- Add transaction IDs for debugging
- Include request/response data
- Track feature flags state
- Add correlation IDs for distributed tracing

### 3. Error Levels

**Demonstrates:** All five severity levels

**What it does:**

- Sends one message at each severity level:
  - **debug** - Development/diagnostic information
  - **info** - Informational messages
  - **warning** - Potential issues that need attention
  - **error** - Actual errors requiring investigation
  - **critical** - Critical failures requiring immediate action

**Example:**

```python
rollbar.report_message("Database connection lost", level="critical")
```

**Rollbar features:**

- Filter dashboard by severity level
- Set up different alert rules per level
- Track trends for each severity
- Critical errors trigger immediate notifications

**Use cases:**

- Prioritize which issues to address first
- Different on-call procedures per severity
- Track warning trends before they become errors
- Debug logs in development, errors in production

### 4. Exception vs Message

**Demonstrates:** Comparing exception and message reporting methods

**What it does:**

- Sends a message report (manual text log)
- Sends an exception report (caught Python exception)
- Highlights the differences between the two approaches

**Message reporting:**

```python
rollbar.report_message(
    "User attempted invalid operation",
    level="warning",
    extra_data={"operation": "delete_admin_account"}
)
```

**Exception reporting:**

```python
try:
    _ = 100 / 0
except ZeroDivisionError:
    rollbar.report_exc_info(
        extra_data={"operation": "calculate_average"}
    )
```

**Key differences:**

| Feature         | Message         | Exception       |
| --------------- | --------------- | --------------- |
| Stack trace     | No              | Yes (automatic) |
| Exception type  | N/A             | Captured        |
| Local variables | No              | Optional        |
| Use case        | Business events | Actual errors   |

**When to use each:**

- **Messages:** Business events, audit logs, milestones, warnings
- **Exceptions:** Caught errors, try/except blocks, actual failures

### 5. Searchable Fields

**Demonstrates:** Making data searchable and filterable in Rollbar

**What it does:**

- Sends errors with structured, searchable data
- Demonstrates various data types (strings, numbers, booleans, nested objects)
- Shows how to organize data for efficient searching

**Example:**

```python
extra_data={
    "environment": "production",
    "region": "us-east-1",
    "server_id": "web-server-42",
    "request": {
        "method": "POST",
        "path": "/api/orders",
        "status_code": 500,
    }
}
```

**Search examples in Rollbar:**

- `custom[region]:us-east-1` - All errors from that region
- `custom[server_id]:web-server-42` - Errors from specific server
- `custom[request.method]:POST` - POST request errors
- `custom[request.status_code]:500` - All 500 errors

**Use cases:**

- Debug issues in specific environments or regions
- Track down server-specific problems
- Analyze errors by request type
- Create custom dashboard views

### 6. Multiple Errors

**Demonstrates:** Sending a sequence of related errors

**What it does:**

- Simulates a cascading failure scenario
- Sends multiple related errors showing cause and effect
- Demonstrates how to track error sequences

**Example sequence:**

1. Database connection pool exhausted
2. Cache write failed (due to #1)
3. Request timeout (due to #1 and #2)

**Key technique:**

```python
correlation_id = "cascade_abc123"

rollbar.report_message("Database pool exhausted",
    extra_data={"correlation_id": correlation_id, "sequence": 1})

rollbar.report_message("Cache write failed",
    extra_data={"correlation_id": correlation_id, "sequence": 2})
```

**Rollbar features:**

- Search by correlation ID to see full sequence
- Group related errors together
- Track cascading failures
- Identify root causes

**Use cases:**

- Debug cascading failures
- Track request flows through microservices
- Correlate errors across systems
- Identify root cause in error chains

### 7. Exception Types

**Demonstrates:** Different Python exception types

**What it does:**

- Triggers 5 different Python exception types
- Shows how Rollbar handles various exceptions
- Demonstrates exception type grouping

**Exception types demonstrated:**

1. **ValueError** - Invalid value for data type
2. **KeyError** - Missing dictionary key
3. **TypeError** - Wrong data type
4. **AttributeError** - Missing attribute
5. **IndexError** - Invalid list index

**Example:**

```python
try:
    my_dict = {"name": "Alice"}
    _ = my_dict["age"]  # KeyError
except KeyError:
    rollbar.report_exc_info()
```

**Rollbar features:**

- Automatically groups by exception type
- Shows exception hierarchy
- Tracks occurrence count per type
- Different alert rules per exception type

**Use cases:**

- Identify most common exception types
- Track exception trends over time
- Different handling per exception type
- Debug specific exception patterns

### 8. Business Events

**Demonstrates:** Tracking non-error application events

**What it does:**

- Logs important business events and milestones
- Shows that Rollbar isn't just for errors
- Demonstrates tracking application health and metrics

**Example events:**

- User completed onboarding (info level)
- Subscription upgraded (info level)
- Unusual activity detected (warning level)
- Daily backup completed (info level)

**Example:**

```python
rollbar.report_message(
    "User completed onboarding",
    level="info",
    extra_data={
        "user_id": "user_new_123",
        "onboarding_steps": 5,
        "time_to_complete_minutes": 8,
    }
)
```

**Use cases:**

- Track user onboarding completion
- Monitor subscription changes
- Log successful operations
- Track system maintenance tasks
- Monitor application health metrics
- Audit important business actions

## Creating Your Own Scenarios

Each scenario follows a simple pattern. Here's how to create a new one:

### 1. Create a New Scenario File

Create `app/src/scenarios/my_scenario.py`:

```python
"""My custom scenario demonstration."""

import rollbar
from ..utils import wait_for_user
from .base import BaseScenario


class MyScenario(BaseScenario):
    """Demonstrate my custom feature."""

    @property
    def name(self) -> str:
        """Return the display name of the scenario."""
        return "My Feature"

    @property
    def description(self) -> str:
        """Return a brief description of what this scenario demonstrates."""
        return "Demonstrate my custom feature"

    def run(self) -> None:
        """Execute the demo scenario."""
        print("\n>> DEMO: My Custom Feature")
        print("Demonstrating something interesting...\n")

        # Your Rollbar integration code here
        rollbar.report_message(
            "My custom event",
            level="info",
            extra_data={"custom_field": "custom_value"}
        )

        print("\nNote: Check Rollbar to see the results!")
        wait_for_user()
```

### 2. Register Your Scenario

Add it to `app/src/scenarios/__init__.py`:

```python
from .my_scenario import MyScenario

ALL_SCENARIOS = [
    PersonTrackingScenario(),
    CustomDataScenario(),
    # ... existing scenarios ...
    MyScenario(),  # Add your scenario
]
```

### 3. Run and Test

Your scenario will automatically appear in the menu!

## Best Practices for Scenarios

1. **Keep them focused** - One scenario, one feature
2. **Print explanations** - Help users understand what's happening
3. **Include notes** - Tell users what to look for in Rollbar
4. **Use wait_for_user()** - Give users time to check Rollbar
5. **Add meaningful data** - Use realistic examples
6. **Show variations** - Demonstrate different use cases

## Viewing Results in Rollbar

After running scenarios:

1. **Go to your Rollbar dashboard** - https://rollbar.com/
2. **Select your project**
3. **Items tab** - See all errors and messages
4. **People tab** - See affected users (from Person Tracking scenario)
5. **Search** - Try searching by custom fields
6. **Filter** - Use level, environment, or custom field filters

### Useful Search Queries

```
# Find errors from Person Tracking scenario
person.username:alice_smith

# Find errors with custom payment data
custom[payment_id]:pay_abc123

# Find all critical errors
level:critical

# Find errors from specific scenario
custom[scenario]:person_tracking
```

## Next Steps

- Run all scenarios to see different Rollbar features
- Check the [Code Walkthrough](code-walkthrough.md) to understand implementation
- Read the [Customization Guide](customization.md) to adapt for your app
- Explore Rollbar dashboard features with your demo data

## References

- [Rollbar Documentation](https://docs.rollbar.com/)
- [Person Tracking](https://docs.rollbar.com/docs/person-tracking)
- [Custom Data](https://docs.rollbar.com/docs/custom-data)
- [Search Syntax](https://docs.rollbar.com/docs/search-items)
