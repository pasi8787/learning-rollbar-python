# Customization Guide

This guide shows you how to adapt the Rollbar integration for your own application, including real-world examples and web framework integration.

## Overview

The tutorial code is designed to be easily customized for your specific needs. The main customization points are:

1. **Person/User tracking** - Replace demo user data with real authentication
2. **Custom metadata** - Add application-specific context
3. **Severity filtering** - Adjust which errors are sent to Rollbar
4. **Request/response data** - Add HTTP context for web applications
5. **Framework integration** - Integrate with Flask, FastAPI, Django, etc.

## Customizing User Tracking

### Replace Demo User Data

The demo code in [src/rollbar.py](../app/src/rollbar.py) uses hardcoded user data:

```python
# Demo code
payload["data"]["person"] = {
    "id": "1234",
    "tenant": "tenant_name"
}
```

Replace this with real user data from your authentication system:

```python
def _get_person() -> dict[str, Any]:
    """Get current user information from your auth system."""
    user = get_current_user()  # Your authentication function

    if user is None:
        return {}  # No user context available

    return {
        "id": str(user.id),           # Required: unique identifier
        "username": user.username,    # Optional: display name
        "email": user.email,          # Optional: contact email
        "tenant": user.tenant_id,     # Optional: multi-tenant context
    }

# In payload handler
payload["data"]["person"] = _get_person()
```

### Multi-Tenant Applications

For multi-tenant SaaS applications, add tenant context:

```python
def _get_person() -> dict[str, Any]:
    user = get_current_user()
    tenant = get_current_tenant()

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        # Tenant-specific fields
        "tenant_id": str(tenant.id),
        "tenant_name": tenant.name,
        "subscription_tier": tenant.subscription_tier,
        "is_trial": tenant.is_trial,
    }
```

This helps you:
- Filter errors by tenant
- Identify tenant-specific bugs
- Track which customers are affected
- Prioritize fixes based on customer value

### Anonymous Users

For applications with anonymous users:

```python
def _get_person() -> dict[str, Any]:
    user = get_current_user()

    if user.is_authenticated:
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
        }
    else:
        # Track anonymous users by session
        return {
            "id": f"anonymous_{get_session_id()}",
            "session_id": get_session_id(),
            "is_anonymous": True,
        }
```

## Customizing Metadata

### Replace Demo Data with Real Context

The demo code uses placeholder metadata:

```python
# Demo code
payload["data"]["custom"] = {
    "trace_id": uuid4().hex,
    "feature_flags": ["feature_1", "feature_2"],
}
```

Customize this for your application:

```python
def _get_custom_data() -> dict[str, Any]:
    """Get custom metadata for error tracking."""
    return {
        # Distributed tracing
        "trace_id": get_request_trace_id(),
        "request_id": get_request_id(),
        "correlation_id": get_correlation_id(),

        # Feature flags
        "feature_flags": get_user_feature_flags(),
        "experiments": get_active_experiments(),

        # Business context
        "session_id": get_session_id(),
        "user_role": get_user_role(),

        # Infrastructure
        "build_number": os.getenv("BUILD_NUMBER"),
        "deployment_id": os.getenv("DEPLOYMENT_ID"),
        "pod_name": os.getenv("HOSTNAME"),
        "region": os.getenv("AWS_REGION", "unknown"),
    }

# In payload handler
payload["data"]["custom"] = {
    **_get_custom_data(),
    **payload["data"].get("custom", {}),
}
```

### Request-Specific Metadata

For web applications, add request context:

```python
def _get_request_metadata() -> dict[str, Any]:
    """Get current HTTP request metadata."""
    request = get_current_request()  # Your framework's request object

    if request is None:
        return {}

    return {
        "url": request.url,
        "method": request.method,
        "path": request.path,
        "query_params": dict(request.query_params),
        "user_agent": request.headers.get("User-Agent"),
        "ip_address": get_client_ip(request),
        "referer": request.headers.get("Referer"),
    }

payload["data"]["custom"]["request"] = _get_request_metadata()
```

### Database Query Context

Track which database operations caused errors:

```python
def _get_database_context() -> dict[str, Any]:
    """Get active database transaction info."""
    return {
        "active_queries": get_active_query_count(),
        "last_query": get_last_executed_query(),
        "transaction_id": get_transaction_id(),
        "connection_pool_size": get_pool_size(),
    }
```

## Adjusting Severity Filtering

### Customize Which Errors to Send

The demo filters out non-error messages:

```python
# Demo code - only sends errors
if payload["data"]["level"] != "error":
    return False
```

Adjust based on your needs:

```python
# Send errors and critical only
if payload["data"]["level"] not in ["error", "critical"]:
    return False

# Send everything except debug
if payload["data"]["level"] == "debug":
    return False

# Send all levels (not recommended - uses quota quickly)
return True
```

### Filter by Error Type

Skip known non-critical errors:

```python
def _payload_handler(payload: dict, **_kw: Any) -> bool:
    # Filter by level
    if payload["data"]["level"] not in ["error", "critical"]:
        return False

    # Skip specific exception types
    exception_class = payload["data"]["body"].get("trace", {}).get("exception", {}).get("class")
    ignored_exceptions = ["KeyboardInterrupt", "SystemExit", "CancelledError"]

    if exception_class in ignored_exceptions:
        return False

    # Skip errors from specific modules
    frames = payload["data"]["body"].get("trace", {}).get("frames", [])
    if any("third_party_lib" in frame.get("filename", "") for frame in frames):
        return False

    return True
```

### Environment-Based Filtering

Send different errors based on environment:

```python
from src.config import settings

def _payload_handler(payload: dict, **_kw: Any) -> bool:
    if settings.environment == "local":
        # In local dev, only send critical errors
        return payload["data"]["level"] == "critical"

    elif settings.environment == "staging":
        # In staging, send errors and critical
        return payload["data"]["level"] in ["error", "critical"]

    else:  # production
        # In production, send everything except debug
        return payload["data"]["level"] != "debug"
```

## Web Framework Integration

### Flask Integration

```python
# src/rollbar.py
from flask import request, g
import rollbar
from src.config import settings

def setup_rollbar(app):
    """Initialize Rollbar for Flask application."""
    rollbar.init(
        access_token=settings.rollbar_access_token,
        environment=settings.environment,
        code_version=settings.code_version,
    )
    rollbar.events.add_payload_handler(_payload_handler)

    # Register error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        rollbar.report_exc_info()
        return "Internal Server Error", 500

    # Before request - store request context
    @app.before_request
    def before_request():
        g.trace_id = uuid4().hex

def _payload_handler(payload: dict, **_kw: Any) -> bool:
    if payload["data"]["level"] != "error":
        return False

    # Add Flask request context
    from flask import request, g

    payload["data"]["person"] = _get_person_from_flask()
    payload["data"]["custom"] = {
        "trace_id": getattr(g, "trace_id", None),
        "url": request.url,
        "method": request.method,
        "endpoint": request.endpoint,
        **payload["data"].get("custom", {}),
    }

    return True

def _get_person_from_flask() -> dict:
    from flask_login import current_user

    if current_user.is_authenticated:
        return {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
        }
    return {}
```

### FastAPI Integration

```python
# src/rollbar.py
from fastapi import Request
from contextvars import ContextVar
import rollbar
from src.config import settings

# Context variable to store request info
_request_context: ContextVar[dict] = ContextVar("request_context", default={})

def setup_rollbar():
    """Initialize Rollbar for FastAPI application."""
    rollbar.init(
        access_token=settings.rollbar_access_token,
        environment=settings.environment,
        code_version=settings.code_version,
    )
    rollbar.events.add_payload_handler(_payload_handler)

# Middleware
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

class RollbarMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Store request context
        _request_context.set({
            "trace_id": uuid4().hex,
            "url": str(request.url),
            "method": request.method,
            "path": request.url.path,
        })

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            rollbar.report_exc_info()
            raise

# Add middleware to app
app = FastAPI()
app.add_middleware(RollbarMiddleware)

def _payload_handler(payload: dict, **_kw: Any) -> bool:
    if payload["data"]["level"] != "error":
        return False

    # Get request context from context variable
    ctx = _request_context.get()

    payload["data"]["custom"] = {
        **ctx,
        **payload["data"].get("custom", {}),
    }

    payload["data"]["person"] = _get_person_from_fastapi()

    return True

def _get_person_from_fastapi() -> dict:
    # Implement based on your auth system
    # Could use contextvars or dependency injection
    return {}
```

### Django Integration

```python
# settings.py
MIDDLEWARE = [
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
    # ... other middleware
]

ROLLBAR = {
    'access_token': os.getenv('ROLLBAR_ACCESS_TOKEN'),
    'environment': os.getenv('ENVIRONMENT', 'production'),
    'code_version': os.getenv('CODE_VERSION', 'unknown'),
    'root': BASE_DIR,
    'exception_level_filters': [
        (Http404, 'warning'),
    ]
}

# Custom payload handler
import rollbar

def custom_payload_handler(payload, **kw):
    # Add Django-specific context
    request = kw.get('request')

    if request:
        payload['data']['custom'] = {
            'user_id': request.user.id if request.user.is_authenticated else None,
            'session_key': request.session.session_key,
            'path': request.path,
        }

        if request.user.is_authenticated:
            payload['data']['person'] = {
                'id': str(request.user.id),
                'username': request.user.username,
                'email': request.user.email,
            }

    return payload

rollbar.events.add_payload_handler(custom_payload_handler)
```

## Adding Request/Response Data

For web applications, capture HTTP request and response details:

```python
def _payload_handler(payload: dict, **_kw: Any) -> bool:
    if payload["data"]["level"] != "error":
        return False

    # Add request data
    payload["data"]["request"] = {
        "url": request.url,
        "method": request.method,
        "headers": _sanitize_headers(dict(request.headers)),
        "query_string": str(request.query_params),
        "POST": _sanitize_body(request.form),
        "user_ip": get_client_ip(request),
    }

    return True

def _sanitize_headers(headers: dict) -> dict:
    """Remove sensitive headers."""
    sensitive = ["authorization", "cookie", "x-api-key"]
    return {
        k: v if k.lower() not in sensitive else "[REDACTED]"
        for k, v in headers.items()
    }

def _sanitize_body(body: dict) -> dict:
    """Remove sensitive form fields."""
    sensitive = ["password", "token", "credit_card", "ssn"]
    return {
        k: v if k.lower() not in sensitive else "[REDACTED]"
        for k, v in body.items()
    }
```

## Real-World Example: Complete Integration

Here's a complete example for a FastAPI application:

```python
# src/rollbar.py
from typing import Any
from uuid import uuid4
from contextvars import ContextVar

import rollbar
from fastapi import Request

from src.config import settings
from src.auth import get_current_user
from src.features import get_feature_flags

# Context variables
_request_context: ContextVar[dict] = ContextVar("request_context", default={})

def setup_rollbar() -> None:
    """Initialize Rollbar with custom payload enrichment."""
    rollbar.init(
        access_token=settings.rollbar_access_token,
        environment=settings.environment,
        code_version=settings.code_version,
    )
    rollbar.events.add_payload_handler(_payload_handler)

def store_request_context(request: Request) -> str:
    """Store request context for error reporting. Returns trace_id."""
    trace_id = uuid4().hex

    _request_context.set({
        "trace_id": trace_id,
        "url": str(request.url),
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    })

    return trace_id

def _payload_handler(payload: dict, **_kw: Any) -> bool:
    """Enrich error payloads before sending to Rollbar."""

    # Filter: only send errors, not info/warnings
    if payload["data"]["level"] != "error":
        return False

    # Add person/user tracking
    payload["data"]["person"] = _get_person()

    # Add custom metadata
    ctx = _request_context.get()
    payload["data"]["custom"] = {
        **ctx,
        "feature_flags": get_feature_flags(),
        **payload["data"].get("custom", {}),
    }

    # Add framework identifier
    payload["data"]["framework"] = f"FastAPI {fastapi.__version__}"

    return True

def _get_person() -> dict[str, Any]:
    """Get current user information."""
    try:
        user = get_current_user()
        if user and user.is_authenticated:
            return {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "tenant_id": user.tenant_id,
            }
    except Exception:
        pass  # Don't fail error reporting if we can't get user

    return {}
```

## Testing Your Customization

After customizing, test that errors are properly enriched:

```python
# Test script
from src.rollbar import setup_rollbar

setup_rollbar()

# Trigger a test error
rollbar.report_message("Customization test", level="error", extra_data={
    "test_type": "customization_check"
})

# Trigger an exception
try:
    raise ValueError("Testing custom error enrichment")
except Exception:
    rollbar.report_exc_info()
```

Check your Rollbar dashboard to verify:
- ✅ Person data is populated correctly
- ✅ Custom metadata appears in the Custom section
- ✅ Request context is included (for web apps)
- ✅ Framework identifier is set
- ✅ All expected fields are present

## Best Practices

1. **Start simple** - Begin with basic customization and add complexity as needed
2. **Test thoroughly** - Verify enriched data appears correctly in Rollbar
3. **Don't block** - Keep payload handlers fast; avoid external API calls
4. **Sanitize sensitive data** - Never send passwords, tokens, or PII
5. **Use context variables** - Store request context for access in payload handlers
6. **Handle errors gracefully** - Don't let enrichment logic crash error reporting
7. **Document custom fields** - Keep track of what each custom field means

## Next Steps

- Review the [Code Walkthrough](code-walkthrough.md) to understand the integration structure
- Check the [Troubleshooting Guide](troubleshooting.md) if you encounter issues
- Read [Rollbar's API documentation](https://docs.rollbar.com/docs/items-json) for advanced customization
- Explore [Rollbar integrations](https://docs.rollbar.com/docs/integrations) for Slack, PagerDuty, Jira, etc.

---

Customize the integration to fit your application's specific needs and start tracking errors effectively!
