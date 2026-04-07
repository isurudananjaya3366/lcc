# Error Handling & Fallback

> LankaCommerce Cloud - Error Handling Documentation
> SubPhase-06, Group-E (Tasks 55-68)

---

## Overview

LankaCommerce Cloud provides comprehensive error handling for tenant
resolution failures. When a request cannot be matched to an active
tenant, the middleware returns clear, consistent error responses
rather than generic server errors.

Five error scenarios are handled:

1. Tenant not found (HTTP 404) — no tenant matches the request.
2. Tenant suspended (HTTP 403) — tenant exists but is suspended.
3. Tenant expired (HTTP 403) — tenant subscription has expired.
4. Public fallback — certain paths bypass tenant resolution.
5. Resolution errors — all failures are logged and tracked.

---

## Tenant Not Found Handler (Task 55)

When tenant resolution fails (no matching hostname, subdomain, header,
or custom domain), the tenant_not_found() handler provides a consistent
fallback response.

### Behaviour

- Logs the failure at WARNING level with hostname, path, and method.
- Returns an HTTP 404 response.
- API requests receive JSON: {"error": "tenant_not_found", "detail": ...}
- Browser requests receive rendered HTML from the 404 template.
- No internal tenant details are leaked in the response.

### When It Triggers

- Subdomain does not match any tenant.
- Custom domain is not registered or not verified.
- Header-based identifier does not match any tenant.
- All resolution strategies return None.

### Logging

Every not-found event is logged for audit purposes:

    ErrorHandler: tenant not found for hostname='example.com'
    path='/api/v1/products/' method='GET' (Task 55)

---

## 404 Response (Task 56)

The 404 response uses a consistent format across API and browser
requests.

### API Response (JSON)

Status: 404 Not Found

Response body:

    {"error": "tenant_not_found", "detail": "No tenant found for this domain."}

### Browser Response (HTML)

Status: 404 Not Found

Rendered from the template configured in TENANT_404_TEMPLATE
(default: tenants/404_tenant_not_found.html).

### Fallback

If the HTML template is not found, a plain text response is returned:

    "Tenant not found." (text/plain, 404)

---

## Custom 404 Template (Task 57)

A custom HTML template is provided for browser-based 404 responses.

### Template Path

    apps/tenants/templates/tenants/404_tenant_not_found.html

### Template Context

- hostname: The requested hostname that could not be resolved.

### Customisation

To override the template:

1. Set TENANT_404_TEMPLATE in Django settings to a custom path.
2. Place your template in a directory included in TEMPLATES DIRS.
3. The template receives the hostname variable for display.

### Design

The template shows:

- A prominent 404 status code.
- A "Tenant Not Found" heading.
- A message including the hostname.
- A link to return home.

---

## Public Tenant Fallback (Task 58)

Certain URL paths must be accessible without tenant resolution. These
paths always use the public PostgreSQL schema, bypassing the tenant
resolution chain entirely.

### Rationale

- Authentication endpoints must work before a tenant is identified
  (the user may be logging in for the first time).
- Tenant registration is a public operation (creating a new tenant).
- Subscription plans are public information.
- Health checks and metrics must always be reachable for monitoring.

### Behaviour

When a request path matches PUBLIC_SCHEMA_PATHS:

- is_public_path() returns True.
- Tenant resolution is skipped.
- The public schema is activated.
- The request proceeds to the view.

### Security

- Keep the public path list minimal to reduce attack surface.
- Public paths have no tenant-level access control.
- Authentication is still enforced by DRF permission classes.

---

## Public Schema Paths (Task 59)

The public schema paths are configured in Django settings.

### Default Paths

- /api/v1/auth/ — Authentication (login, token refresh, logout).
- /api/v1/register/ — Tenant registration (new sign-up flow).
- /api/v1/plans/ — Subscription plans (public pricing page).
- /health/ — Health check endpoint (infrastructure monitoring).
- /metrics/ — Prometheus metrics endpoint (observability).

### Settings Location

All public paths are defined in:

    config/settings/base.py

Setting name: PUBLIC_SCHEMA_PATHS

### Adding New Paths

1. Add the path prefix to PUBLIC_SCHEMA_PATHS in settings.
2. Ensure the endpoint handles requests without tenant context.
3. Restart the application server.

### Path Matching

Prefix matching is used (startswith). For example, /api/v1/auth/
matches /api/v1/auth/login/ and /api/v1/auth/token/refresh/.

---

## Suspended Tenant Handling (Task 60)

When a resolved tenant is in suspended state, the middleware blocks
access with an HTTP 403 Forbidden response.

### Detection

is_tenant_suspended(tenant) checks:

1. The tenant's status field (if present) for value "suspended".
2. Falls back to False if no status field exists.

### Behaviour

- Logs the suspension at WARNING level with tenant name, path, method.
- Returns HTTP 403 Forbidden.
- API requests receive JSON: {"error": "tenant_suspended", "detail": ...}
- Browser requests receive rendered HTML from the suspended template.
- Tenant data remains intact but inaccessible.

### Reactivation

When a tenant is reactivated (status changed from "suspended" to
"active"), access is immediately restored on the next request.

---

## Suspended Response (Task 61)

The suspended response provides a clear message to users.

### API Response (JSON)

Status: 403 Forbidden

Response body:

    {"error": "tenant_suspended", "detail": "This account has been suspended. Please contact support for assistance."}

### Browser Response (HTML)

Status: 403 Forbidden

Rendered from the template configured in TENANT_SUSPENDED_TEMPLATE
(default: tenants/suspended.html).

### Template Path

    apps/tenants/templates/tenants/suspended.html

### Template Context

- tenant_name: The name of the suspended tenant.

### Design

The template shows:

- A prominent 403 status code.
- An "Account Suspended" heading.
- A message asking the user to contact support.
- A link to email support.

---

## Settings Reference

### Error Handling Settings

- PUBLIC_SCHEMA_PATHS: URL path prefixes using public schema.
  Default: ["/api/v1/auth/", "/api/v1/register/", "/api/v1/plans/",
  "/health/", "/metrics/"]

- TENANT_404_TEMPLATE: Template for tenant not found pages.
  Default: "tenants/404_tenant_not_found.html"

- TENANT_SUSPENDED_TEMPLATE: Template for suspended tenant pages.
  Default: "tenants/suspended.html"

### Settings Location

    config/settings/base.py

---

## Error Handler Module

The error handler lives in:

    apps.tenants.middleware.error_handler

### Key Functions

- tenant_not_found(request, hostname): HTTP 404 for missing tenants.
- tenant_suspended(request, tenant): HTTP 403 for suspended tenants.
- tenant_expired(request, tenant): HTTP 403 for expired subscriptions.
- is_public_path(path): Check if path uses public schema.
- is_tenant_suspended(tenant): Check if tenant is suspended.
- is_tenant_expired(tenant): Check if subscription is expired.
- is_within_grace_period(tenant): Check if expired tenant is in grace period.
- get_tenant_status(tenant): Return normalised tenant status.
- get_public_schema_paths(): Return configured public paths.
- log_resolution_error(error_type, request, ...): Log resolution errors.
- get_error_metrics(): Return error metrics counters.
- reset_error_metrics(): Reset error metrics counters.

### Constants

- TENANT_STATUS_ACTIVE: "active"
- TENANT_STATUS_SUSPENDED: "suspended"
- TENANT_STATUS_EXPIRED: "expired"
- DEFAULT_404_TEMPLATE: "tenants/404_tenant_not_found.html"
- DEFAULT_SUSPENDED_TEMPLATE: "tenants/suspended.html"
- DEFAULT_EXPIRED_TEMPLATE: "tenants/expired.html"
- DEFAULT_GRACE_PERIOD_DAYS: 7

---

## Suspended Template (Task 62)

The suspended tenant template is documented here.

### Template Path

    apps/tenants/templates/tenants/suspended.html

### Template Content

- 403 status code display.
- "Account Suspended" heading.
- Message: "This account has been suspended. Please contact support."
- Link to contact support via email.
- Responsive design with system font stack.

### Customisation

Override via TENANT_SUSPENDED_TEMPLATE setting.

---

## Expired Subscription Handling (Task 63)

When a resolved tenant has an expired subscription, access is blocked
with an HTTP 403 response.

### Detection

is_tenant_expired(tenant) checks the tenant status field for "expired".

### Grace Period Policy

After expiration, tenants have a grace period (default 7 days) before
full access revocation. During the grace period:

- Read access may be allowed (implementation-specific).
- Write operations may be restricted.
- The grace period is calculated from expired_at or subscription_end.

Configuration: TENANT_GRACE_PERIOD_DAYS setting (default: 7).

### Grace Period Check

is_within_grace_period(tenant) determines if an expired tenant is
still within the grace window. If no expiration date field exists,
the grace period check returns False.

### Behaviour

- Logs the expiration at WARNING level with tenant name, path, method.
- Returns HTTP 403 Forbidden.
- API: JSON {"error": "tenant_expired", "detail": ...}
- Browser: Rendered HTML from the expired template.

---

## Expired Response (Task 64)

The expired response uses a consistent format.

### API Response (JSON)

Status: 403 Forbidden

Response body:

    {"error": "tenant_expired", "detail": "Your subscription has expired. Please renew your plan to continue."}

### Browser Response (HTML)

Status: 403 Forbidden

Rendered from TENANT_EXPIRED_TEMPLATE (default: tenants/expired.html).

### Fallback

If the template is not found, a plain text response is returned:

    "Your subscription has expired. Please renew your plan to continue." (text/plain, 403)

---

## Expired Template (Task 65)

A custom HTML template for expired subscription responses.

### Template Path

    apps/tenants/templates/tenants/expired.html

### Template Content

- 403 status code display (red).
- "Subscription Expired" heading.
- Message prompting plan renewal.
- Link to view plans.
- Link to contact support.
- Responsive design with system font stack.

### Customisation

Override via TENANT_EXPIRED_TEMPLATE setting.

---

## Resolution Error Logging (Task 66)

All tenant resolution errors are logged consistently using
structured log fields.

### Log Fields

- error_type: Category (not_found, suspended, expired).
- domain: The hostname/domain involved.
- path: The request URL path.
- method: The HTTP method.
- detail: Optional additional information.

### Log Level

WARNING level for all resolution errors.

### Log Format

    ErrorHandler: resolution_error type='not_found' domain='example.com'
    path='/api/v1/products/' method='GET' detail='...' (Task 66)

### Retention

Log entries follow the application log rotation policy. Structured
fields allow aggregation by domain and error type in log management
systems (ELK, Datadog, CloudWatch).

### Usage

Call log_resolution_error() for any tenant resolution failure:

    log_resolution_error("not_found", request, hostname="example.com")

The tenant_not_found(), tenant_suspended(), and tenant_expired()
handlers also call log_resolution_error() internally via the
metrics recording system.

---

## Error Metrics (Task 67)

In-memory counters track error occurrences for monitoring.

### Tracked Metrics

- Total error count across all types.
- Error counts grouped by error type (not_found, suspended, expired).
- Error counts grouped by domain and error type.

### Functions

- get_error_metrics(): Returns current counters as a dictionary.
- reset_error_metrics(): Clears all counters.

### Metrics Format

    {
        "total": 42,
        "by_type": {"tenant_not_found": 30, "tenant_suspended": 10, "tenant_expired": 2},
        "by_domain": {"bad.example.com": {"tenant_not_found": 5}}
    }

### Dashboards and Alerts

- Expose metrics via a health check or metrics endpoint.
- Alert on high error rates by domain (possible abuse).
- Track trends in expired/suspended tenant access attempts.
- Metrics reset on application restart; use external persistence
  for long-term tracking.

---

## Error Response Summary

| Situation        | HTTP Status | Response Type   | Template                  |
| ---------------- | ----------- | --------------- | ------------------------- |
| Tenant not found | 404         | JSON or HTML    | 404_tenant_not_found.html |
| Tenant suspended | 403         | JSON or HTML    | suspended.html            |
| Tenant expired   | 403         | JSON or HTML    | expired.html              |
| Public path      | N/A         | Normal response | N/A (public schema)       |

---

## Template Mappings (Task 68)

| Template File                     | Setting                   | Default                           | Use Case             |
| --------------------------------- | ------------------------- | --------------------------------- | -------------------- |
| tenants/404_tenant_not_found.html | TENANT_404_TEMPLATE       | tenants/404_tenant_not_found.html | Tenant not found     |
| tenants/suspended.html            | TENANT_SUSPENDED_TEMPLATE | tenants/suspended.html            | Suspended tenant     |
| tenants/expired.html              | TENANT_EXPIRED_TEMPLATE   | tenants/expired.html              | Expired subscription |

---

## Settings Reference

### Error Handling Settings

- PUBLIC_SCHEMA_PATHS: URL path prefixes using public schema.
  Default: ["/api/v1/auth/", "/api/v1/register/", "/api/v1/plans/",
  "/health/", "/metrics/"]

- TENANT_404_TEMPLATE: Template for tenant not found pages.
  Default: "tenants/404_tenant_not_found.html"

- TENANT_SUSPENDED_TEMPLATE: Template for suspended tenant pages.
  Default: "tenants/suspended.html"

- TENANT_EXPIRED_TEMPLATE: Template for expired subscription pages.
  Default: "tenants/expired.html"

- TENANT_GRACE_PERIOD_DAYS: Grace period in days after subscription
  expiration. Default: 7

### Settings Location

    config/settings/base.py

---

## Integration with Middleware

The error handler functions are called by the tenant middleware
resolution chain:

1. Middleware receives request.
2. is_public_path() checks for public schema bypass.
3. Resolver chain (subdomain, custom domain, header) runs.
4. If all resolvers return None: tenant_not_found() is called.
5. If tenant is suspended: tenant_suspended() is called.
6. If tenant is expired: tenant_expired() is called.
7. Otherwise: tenant schema is activated normally.

All error paths log the failure (Task 66) and record metrics (Task 67).

---

## Task Coverage Summary

| Task | Name                             | Status      |
| ---- | -------------------------------- | ----------- |
| 55   | Create Tenant Not Found Handler  | Implemented |
| 56   | Create 404 Response              | Implemented |
| 57   | Create Custom 404 Template       | Implemented |
| 58   | Configure Public Tenant Fallback | Implemented |
| 59   | Define Public Schema Paths       | Implemented |
| 60   | Handle Suspended Tenant          | Implemented |
| 61   | Create Suspended Response        | Implemented |
| 62   | Create Suspended Template        | Implemented |
| 63   | Handle Expired Subscription      | Implemented |
| 64   | Create Expired Response          | Implemented |
| 65   | Create Expired Template          | Implemented |
| 66   | Log Resolution Errors            | Implemented |
| 67   | Create Error Metrics             | Implemented |
| 68   | Document Error Handling          | Implemented |

---

## Testing (Tasks 76-82)

### Test Suite

The error handling module is covered by the following test files:

- tests/tenants/test_middleware.py: Unit tests (Tasks 69-75)
- tests/tenants/test_integration.py: Integration tests (Tasks 76-77)
- tests/tenants/test_performance.py: Performance benchmarks (Task 80)
- tests/tenants/conftest.py: Shared fixtures (Task 78)

### Integration Coverage (Task 76)

End-to-end tests verify that error handlers integrate correctly
with the resolution pipeline and that metrics are tracked
consistently when errors occur.

### Isolation Verification (Task 77)

Multi-tenant isolation tests confirm that error responses do not
leak tenant schema names, internal IDs, or other sensitive data.
Each error type (not found, suspended, expired) produces generic
messages without tenant-specific details.

### Performance (Task 80)

All error handling operations complete within the 5ms target:

- is_public_path check
- is_tenant_suspended check
- Error metric recording
- Error metrics retrieval

### Test Results (Task 81)

Full test results are documented at docs/backend/test-results.md.

### Related Documentation

- docs/backend/test-results.md: Complete test results and coverage
- docs/backend/custom-domain-setup.md: Custom domain resolution
- docs/backend/header-resolution.md: Header-based resolution
