# Tenant Middleware Flow

> **Phase:** 02 - Database Architecture & Multi-Tenancy
> **SubPhase:** 06 - Tenant Middleware Configuration
> **Group:** A - Middleware Foundation
> **Document:** Architecture Reference

---

## Overview

Every HTTP request to LankaCommerce Cloud passes through `LCCTenantMiddleware`
before any view, session, or authentication middleware runs. The middleware
resolves the active tenant from the request's `Host` header, activates the
corresponding PostgreSQL schema, and injects convenience attributes onto the
request object for downstream use.

---

## Request Lifecycle

### Step 1: Host Extraction

Django receives the HTTP request. `LCCTenantMiddleware.__call__()` is invoked
first because it occupies position 0 in the `MIDDLEWARE` list. The middleware
reads the `Host` header from the request (e.g. `acme.lcc.example.com`).

### Step 2: Domain Lookup

`TenantMainMiddleware.process_request()` (the parent class) queries the
`tenants_domain` table in the **public schema** to find a `Domain` record
whose `domain` field matches the extracted hostname.

If no matching domain is found, the parent raises `Http404` (or redirects to
the fallback URL if `SHOW_PUBLIC_IF_NO_TENANT_FOUND = True` in settings).

### Step 3: Tenant Resolution

The parent class retrieves the `Tenant` instance linked to the matched
`Domain` record. All `Tenant` and `Domain` records live in the public schema
and are shared across all tenants.

### Step 4: Schema Activation

`connection.set_tenant(tenant)` is called on the PostgreSQL connection for the
current thread. This sets the `search_path` to the tenant's private schema
(e.g. `tenant_acme`), routing all subsequent ORM queries to that schema.
After activation:

- `django.db.connection.tenant` holds the `Tenant` instance.
- `django.db.connection.schema_name` holds the schema name string.

### Step 5: Request Attribute Injection

`LCCTenantMiddleware.process_request()` reads the two connection attributes
set in Step 4 and injects them directly onto the request object:

| Attribute             | Type                    | Source                   |
| --------------------- | ----------------------- | ------------------------ |
| `request.tenant`      | `Tenant` model instance | `connection.tenant`      |
| `request.schema_name` | `str`                   | `connection.schema_name` |

Views and downstream middleware can read these attributes without importing
any django-tenants internals.

### Step 6: Downstream Processing

With the schema activated, Django's middleware chain continues:
`SecurityMiddleware`, `SessionMiddleware`, `AuthenticationMiddleware`, and
finally the view resolver all execute inside the tenant's schema context. All
ORM queries automatically target the correct tenant schema.

### Step 7: Response and Schema Deactivation

After `get_response(request)` returns, `TenantMainMiddleware` deactivates the
tenant schema and resets `search_path` to the public schema, ensuring the
PostgreSQL connection is clean for the next request.

---

## Key Attributes

### `request.tenant`

Set by `LCCTenantMiddleware.process_request()`. Holds the active `Tenant`
model instance for the current request. Is `None` for requests that do not
resolve to a private tenant (e.g. admin on the public schema).

Access pattern:

    tenant = request.tenant  # inside any view or middleware

Utility helper:

    from apps.tenants.utils import get_tenant_from_request
    tenant = get_tenant_from_request(request)  # safe, returns None if absent

### `request.schema_name`

Set by `LCCTenantMiddleware.process_request()`. Holds the PostgreSQL schema
name string (e.g. `"tenant_acme"`) for the current request. Is `None` when
no tenant is resolved. Is `"public"` when the request targets the public
schema directly.

Access pattern:

    schema = request.schema_name  # inside any view or middleware

Utility helper:

    from apps.tenants.utils import get_schema_from_request
    schema = get_schema_from_request(request)  # safe, returns None if absent

---

## Non-Request Context (Background Tasks)

For code that runs outside the HTTP request lifecycle (Celery tasks, management
commands, signal handlers), use the thread-local context accessor functions:

| Function                     | Purpose                                                 |
| ---------------------------- | ------------------------------------------------------- |
| `get_current_tenant()`       | Read the active tenant from thread-local or connection  |
| `set_current_tenant(tenant)` | Activate a tenant on the DB connection and thread-local |
| `tenant_context(tenant)`     | Context manager: activate on enter, restore on exit     |

These functions are defined in `apps.tenants.utils.tenant_context` and
exported from `apps.tenants.utils`.

### Background Task Pattern

A Celery task that processes data for a specific tenant uses
`tenant_context()` to safely scope all ORM queries:

    from apps.tenants.utils import tenant_context
    from apps.tenants.models import Tenant

    @shared_task
    def process_tenant_report(tenant_id):
        tenant = Tenant.objects.get(id=tenant_id)
        with tenant_context(tenant):
            # All queries here run in tenant's schema
            ...

### Multi-Tenant Iteration Pattern

A management command that iterates over all tenants:

    from apps.tenants.utils import set_current_tenant
    from apps.tenants.models import Tenant

    for tenant in Tenant.objects.exclude(schema_name="public"):
        set_current_tenant(tenant)
        run_per_tenant_task()
    set_current_tenant(None)  # reset to public when done

---

## Middleware Order

`LCCTenantMiddleware` must be position 0 in `settings.MIDDLEWARE`. If it is
placed after `SecurityMiddleware` or `SessionMiddleware`, those middlewares
would execute before the schema is activated, potentially querying the wrong
schema or missing tenant-specific data.

Current order (defined in `config/settings/base.py`):

| Position | Middleware                                                | Purpose                   |
| -------- | --------------------------------------------------------- | ------------------------- |
| 0        | `apps.tenants.middleware.LCCTenantMiddleware`             | Schema activation (FIRST) |
| 1        | `django.middleware.security.SecurityMiddleware`           | HTTPS, HSTS               |
| 2        | `whitenoise.middleware.WhiteNoiseMiddleware`              | Static file serving       |
| 3        | `corsheaders.middleware.CorsMiddleware`                   | CORS headers              |
| 4        | `django.contrib.sessions.middleware.SessionMiddleware`    | Session handling          |
| 5        | `django.middleware.common.CommonMiddleware`               | URL normalization         |
| 6        | `django.middleware.csrf.CsrfViewMiddleware`               | CSRF protection           |
| 7        | `django.contrib.auth.middleware.AuthenticationMiddleware` | User auth                 |
| 8        | `django.contrib.messages.middleware.MessageMiddleware`    | Flash messages            |
| 9        | `django.middleware.clickjacking.XFrameOptionsMiddleware`  | Clickjacking              |

---

## Related Files

| File                                           | Description                                |
| ---------------------------------------------- | ------------------------------------------ |
| `apps/tenants/middleware/tenant_middleware.py` | `LCCTenantMiddleware` implementation       |
| `apps/tenants/middleware/__init__.py`          | Middleware package exports                 |
| `apps/tenants/utils/middleware_utils.py`       | Request-level tenant helper functions      |
| `apps/tenants/utils/tenant_context.py`         | Thread-local context manager and accessors |
| `apps/tenants/utils/__init__.py`               | Utils package — exports all helpers        |
| `config/settings/base.py`                      | MIDDLEWARE list definition                 |

---

## Error Handling

If no `Domain` matches the request hostname:

- `TenantMainMiddleware` raises `Http404` by default.
- `LCCTenantMiddleware` logs a warning before the exception propagates.
- If `SHOW_PUBLIC_IF_NO_TENANT_FOUND = True` in settings, the request falls
  through to the public schema instead of returning 404.

Group B (Subdomain Resolution) and Group C (Custom Domain Resolution) define
additional resolution strategies that extend this base flow.
