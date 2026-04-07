# Debugging Guide

> Debugging practices, logging, tracing, and tooling for LankaCommerce Cloud.

**Navigation:** [Testing](testing.md) · [Troubleshooting](troubleshooting.md) · [Docs Index](../index.md)

---

## Overview

This guide covers debugging techniques for both the Django backend and the Next.js frontend, including logging configuration, interactive debugging, and useful development tools.

---

## Backend Debugging

### Django Debug Toolbar

Django Debug Toolbar is available in local development for inspecting SQL queries, templates, cache hits, and more.

1. Ensure `debug_toolbar` is uncommented in `INSTALLED_APPS` (in `config/settings/local.py`)
2. Ensure `DebugToolbarMiddleware` is uncommented in `MIDDLEWARE`
3. Start the development server: `python manage.py runserver`
4. The debug toolbar panel appears on the right side of HTML pages

### Logging

Django logging is configured in `config/settings/base.py` (production) and can be overridden per environment.

| Log Level  | When to Use                                        |
| ---------- | -------------------------------------------------- |
| `DEBUG`    | Detailed diagnostic information (development only) |
| `INFO`     | General operational events (requests, task starts) |
| `WARNING`  | Unexpected but recoverable situations              |
| `ERROR`    | Failures that need attention                       |
| `CRITICAL` | System-level failures requiring immediate action   |

To add logging in your code:

1. Import the logger: `import logging` then `logger = logging.getLogger(__name__)`
2. Log at the appropriate level: `logger.info("Processing order %s", order_id)`
3. In development, logs appear in the terminal running the Django server

### Interactive Debugging

| Method            | Description                                                                             |
| ----------------- | --------------------------------------------------------------------------------------- |
| Django Shell      | Run `python manage.py shell` to interactively test queries and logic                    |
| Django Shell Plus | Run `python manage.py shell_plus` (requires django-extensions) for auto-imported models |
| pdb / breakpoint  | Add `breakpoint()` in your code to pause execution and inspect state                    |
| ipdb              | Install `ipdb` for an enhanced interactive debugger with tab completion                 |

### Inspecting API Requests

1. Visit `http://localhost:8000/api/docs/` to use Swagger UI for testing endpoints interactively
2. Check the terminal output for request logs and SQL queries
3. Use Django Debug Toolbar's SQL panel to inspect query performance

### Celery Task Debugging

| Tool        | URL / Command                          | Purpose                                       |
| ----------- | -------------------------------------- | --------------------------------------------- |
| Flower      | `http://localhost:5555/`               | Monitor task execution, retries, and failures |
| Worker logs | `docker compose logs -f celery-worker` | Real-time task execution logs                 |
| Beat logs   | `docker compose logs -f celery-beat`   | Scheduled task dispatch logs                  |

To debug a specific Celery task:

1. Run the task synchronously for testing: call the function directly instead of using `.delay()`
2. Check Flower for task status, arguments, and return values
3. Inspect worker logs for exception tracebacks

---

## Frontend Debugging

### Browser DevTools

| Tab            | Purpose                                                |
| -------------- | ------------------------------------------------------ |
| Console        | View `console.log` output, errors, and warnings        |
| Network        | Inspect API requests, response payloads, and timing    |
| Sources        | Set breakpoints and step through JavaScript/TypeScript |
| Application    | Inspect localStorage, cookies, and service workers     |
| React DevTools | Inspect component tree, props, state, and hooks        |

### React DevTools

1. Install the React Developer Tools browser extension
2. Open DevTools and switch to the Components or Profiler tab
3. Inspect component hierarchy, props, and state
4. Use the Profiler to identify rendering performance bottlenecks

### Zustand DevTools

Zustand stores with the `devtools` middleware integrate with Redux DevTools:

1. Install the Redux DevTools browser extension
2. Open DevTools and switch to the Redux tab
3. Inspect store state changes, actions, and diffs over time

### Next.js Debugging

| Feature               | Description                                                    |
| --------------------- | -------------------------------------------------------------- |
| Error overlay         | Development server shows a full error overlay with stack trace |
| Server component logs | Check the terminal running `pnpm dev` for server-side logs     |
| Client component logs | Check the browser console for client-side logs                 |
| Source maps           | Enabled by default in development for accurate stack traces    |

### VS Code Debugging

1. Open the Run and Debug panel in VS Code (Ctrl+Shift+D)
2. Select the appropriate launch configuration (backend or frontend)
3. Set breakpoints by clicking in the gutter next to line numbers
4. Start debugging with F5
5. Use the Debug Console to evaluate expressions at breakpoints

---

## Database Debugging

| Task                    | Command / Approach                                       |
| ----------------------- | -------------------------------------------------------- |
| Inspect SQL queries     | Enable Django Debug Toolbar's SQL panel                  |
| Log all queries         | Set `django.db.backends` logger to `DEBUG` level         |
| Check slow queries      | Use PostgreSQL's `pg_stat_statements` extension          |
| Connect to database     | Run `docker compose exec db psql -U postgres -d lcc-dev` |
| View table structure    | In psql: `\d <table_name>`                               |
| View active connections | In psql: `SELECT * FROM pg_stat_activity;`               |

---

## Common Debugging Scenarios

| Scenario                    | Approach                                                           |
| --------------------------- | ------------------------------------------------------------------ |
| API returns 500             | Check the Django server terminal for the full traceback            |
| API returns unexpected data | Use Swagger UI to test the endpoint, then check the serializer     |
| Frontend shows stale data   | Check React Query cache in DevTools, verify invalidation logic     |
| Celery task not executing   | Check Flower for task status, verify the worker is running         |
| Database migration fails    | Read the full error message, check for conflicting migrations      |
| CORS errors in browser      | Verify `CORS_ALLOWED_ORIGINS` in settings matches the frontend URL |

---

## Related Documentation

- [Testing Guide](testing.md) — Test execution and coverage
- [Troubleshooting Guide](troubleshooting.md) — Common issues and resolutions
- [Development Setup](development-setup.md) — Environment setup
- [Docs Index](../index.md) — Documentation hub
