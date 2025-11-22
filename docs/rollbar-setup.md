# Rollbar Setup Guide

This guide walks you through setting up a Rollbar account and obtaining the access token needed for this project.

## Overview

Rollbar is a real-time error monitoring and tracking service that helps you identify, debug, and resolve errors in your applications. This tutorial demonstrates how to integrate Rollbar with Python and enrich error reports with custom metadata.

## Step 1: Create a Rollbar Account

1. Visit [rollbar.com](https://rollbar.com)
2. Click **Sign Up** or **Get Started**
3. Choose your signup method:
   - Sign up with GitHub, Google, or email
   - Follow the account creation prompts
4. Verify your email if required

**Free tier:** Rollbar offers a free tier that's perfect for learning and small projects. You get:

- 5,000 events per month
- 30-day data retention
- Unlimited projects
- Basic integrations

## Step 2: Create a Project

After signing up, you'll be prompted to create your first project:

1. **Project name:** Enter a name (e.g., "Rollbar Tutorial" or "Python Integration Demo")
2. **Platform:** Select **Python** from the platform list
3. **Framework:** You can select "Other" or skip this for now
4. Click **Continue** or **Create Project**

Rollbar will generate a project and show you initial setup instructions.

## Step 3: Get Your Access Token

Access tokens authenticate your application with Rollbar. Different token types have different permissions.

### Finding Your Access Tokens

1. In your Rollbar project, click on **Settings** (gear icon) in the left sidebar
2. Navigate to **Project Access Tokens**
3. You'll see several token types listed

### Understanding Token Types

Rollbar provides different tokens for different use cases:

- **post_server_item** - For server-side applications (recommended for this tutorial)

  - Can post errors from backend applications
  - Cannot read data from Rollbar
  - Most secure for production backends

- **post_client_item** - For client-side applications (also works for this tutorial)

  - Can post errors from client applications
  - Safe to expose in frontend code
  - Cannot read sensitive data

- **read** - Read-only access (not needed for this tutorial)

  - Query Rollbar data via API
  - Cannot post new errors

- **write** - Full write access (not recommended for general use)
  - Can modify settings and data
  - Too permissive for regular error reporting

### Copying Your Token

1. Locate the **post_server_item** token (recommended) or **post_client_item** token
2. Click the **Copy** icon or select the token text
3. Save this token - you'll need it for configuration

**Example token format:**

```
abc123def456789012345678901234567890abcd
```

## Step 4: Configure the Application

Add your token to the application's configuration:

1. Open your `.env` file in the `app` directory
2. Add your token:
   ```bash
   ROLLBAR_ACCESS_TOKEN=your_token_here
   ```
3. Save the file

For more details on configuration options, see the [Configuration Guide](configuration.md).

## Step 5: Test the Integration

Run the demo application to test your Rollbar integration:

```bash
cd app
poetry run python -m src.main
```

If configured correctly, you should see:

1. Console output indicating Rollbar is initialized
2. An info message (will be filtered)
3. An exception being reported

## Step 6: View Errors in the Dashboard

After running the demo, check your Rollbar dashboard:

### Items Tab

1. Navigate to the **Items** tab in your Rollbar project
2. You should see a new error: **AttributeError: 'NoneType' object has no attribute 'hello'**
3. Click on the error to see details

### Error Details

The error detail page shows:

**Overview Section:**

- Error title and message
- Stack trace with file names and line numbers
- When the error occurred
- How many times it occurred

**Custom Data Section:**

- `trace_id` - Unique identifier for this error
- `feature_flags` - Array of enabled features
- `foo_key` - Custom nested data
- `base_model_custom` - Serialized Pydantic model

**Person Section:**

- User ID: `1234` (from the demo code)
- Tenant: `tenant_name` (custom field)

**Environment Section:**

- Environment: Shows your configured environment (e.g., "local")
- Code version: Your git commit hash or configured version
- Platform: Python version and OS information

**Framework:**

- Shows "oreore_framework 1.0" (custom identifier from the demo)

### People Tab

1. Click the **People** tab in the left sidebar
2. You'll see user ID `1234` listed
3. Click on the user to see all errors affecting them

This demonstrates how Rollbar tracks which users are experiencing errors.

### Occurrences Tab

1. In the error detail page, click the **Occurrences** tab
2. Shows individual occurrences of this error
3. Each occurrence includes all the custom metadata

## Understanding the Dashboard

### Key Dashboard Features

**Items**

- List of all unique errors in your project
- Grouped by error type and message
- Shows occurrence count and last seen time

**People**

- Users affected by errors
- Requires `person` data in error payloads (covered in this tutorial)
- Helps identify user-specific issues

**Deployments**

- Track which code versions introduced errors
- Requires `code_version` configuration (auto-detected from git)
- View error trends across deployments

**Settings**

- Project configuration
- Access tokens
- Integrations
- Alert rules

### Filtering Errors

Use filters to narrow down errors:

- **Environment:** Filter by development, staging, production, etc.
- **Level:** Filter by error, warning, info, etc.
- **Status:** Filter by active, resolved, muted, etc.
- **Time range:** View errors from specific time periods

## Best Practices

### Token Security

1. **Never commit tokens to git** - Always use `.env` files (already in `.gitignore`)
2. **Use different tokens per environment** - Separate tokens for dev, staging, production
3. **Rotate tokens periodically** - Generate new tokens and update configuration
4. **Limit token scope** - Use post_server_item or post_client_item, not full write access

### Project Organization

1. **One project per application** - Don't mix multiple apps in one project
2. **Use environments** - Separate local, staging, production within one project
3. **Consistent naming** - Use clear, descriptive project names
4. **Document token usage** - Keep track of which tokens are used where

### Error Management

1. **Set up alerts** - Get notified about critical errors (Slack, email, PagerDuty)
2. **Create rules** - Auto-ignore known non-critical errors
3. **Resolve errors** - Mark errors as resolved when fixed
4. **Add comments** - Document investigation notes on errors
5. **Use deployments** - Track when errors were introduced and resolved

## Next Steps

Now that you have Rollbar set up:

1. Review the [Code Walkthrough](code-walkthrough.md) to understand how the integration works
2. Explore the [Customization Guide](customization.md) to adapt it for your application
3. Check the [Configuration Guide](configuration.md) for advanced configuration options
4. Set up integrations in Rollbar:
   - Slack notifications for errors
   - GitHub integration for linking errors to commits
   - Jira integration for bug tracking

## Troubleshooting

### Can't find access tokens

- Make sure you're in the correct project
- Click **Settings** → **Project Access Tokens**
- If tokens are missing, you may not have admin permissions

### Invalid access token error

- Verify you copied the entire token (no spaces or line breaks)
- Check you're using the correct token for your project
- Ensure the token hasn't been revoked

### Errors not appearing in dashboard

- Check that your internet connection is working
- Verify the token is correctly set in `.env`
- Look for error messages in the console output
- Check that errors are at "error" level (info/warning messages are filtered)

### Multiple projects showing errors

- Ensure you're viewing the correct project
- Check that you're using the right token in `.env`
- Verify CODE_VERSION or ENVIRONMENT to distinguish sources

## Additional Resources

- [Rollbar Documentation](https://docs.rollbar.com/)
- [Rollbar Python SDK](https://docs.rollbar.com/docs/python)
- [Access Tokens Guide](https://docs.rollbar.com/docs/access-tokens)
- [Person Tracking](https://docs.rollbar.com/docs/person-tracking)
- [Payload Structure](https://docs.rollbar.com/docs/items-json)
- [Rollbar Support](https://rollbar.com/support/)

---

Once you've completed this setup, you're ready to explore the error monitoring capabilities demonstrated in this tutorial!
