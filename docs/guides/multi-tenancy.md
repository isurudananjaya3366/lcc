# Multi-Tenancy Guide

> Tenant provisioning, schema isolation, and multi-tenant operations for LankaCommerce Cloud.

**Navigation:** [Getting Started](getting-started.md) · [Database Guide](database.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud uses **schema-based multi-tenancy** powered by `django-tenants`. Each tenant gets a dedicated PostgreSQL schema, ensuring complete data isolation while sharing the same database instance.

> Multi-tenancy is implemented in **Phase 2** of the project. This guide documents the architecture and planned operations.

---

## Architecture

### Schema Isolation Model

| Schema             | Contents                                               | Managed By    |
| ------------------ | ------------------------------------------------------ | ------------- |
| **public**         | Shared tables — tenants, domains, plans                | `SHARED_APPS` |
| **tenant\_<slug>** | Tenant-specific tables — products, orders, users, etc. | `TENANT_APPS` |

Each tenant's data lives in its own PostgreSQL schema, making it impossible for one tenant to access another's data at the database level.

### App Classification

| Category        | Setting       | Examples                                                          |
| --------------- | ------------- | ----------------------------------------------------------------- |
| **Shared Apps** | `SHARED_APPS` | `tenants`, `django.contrib.admin`, `django.contrib.auth`          |
| **Tenant Apps** | `TENANT_APPS` | `products`, `inventory`, `sales`, `customers`, `hr`, `accounting` |

Apps in `SHARED_APPS` have their tables in the `public` schema only. Apps in `TENANT_APPS` have their tables replicated in every tenant schema.

---

## Tenant Models

### Tenant Model

The `Tenant` model (in `apps.tenants`) stores tenant metadata:

| Field         | Type     | Description                     |
| ------------- | -------- | ------------------------------- |
| `schema_name` | string   | PostgreSQL schema name (unique) |
| `name`        | string   | Display name of the business    |
| `slug`        | string   | URL-safe identifier             |
| `is_active`   | boolean  | Whether the tenant is active    |
| `created_at`  | datetime | When the tenant was created     |

### Domain Model

The `Domain` model maps hostnames to tenants:

| Field        | Type        | Description                              |
| ------------ | ----------- | ---------------------------------------- |
| `domain`     | string      | Hostname (e.g., `acme.lankacommerce.lk`) |
| `tenant`     | FK → Tenant | The owning tenant                        |
| `is_primary` | boolean     | Whether this is the primary domain       |

---

## Tenant Lifecycle

### 1. Provisioning a New Tenant

When a new business signs up:

1. Create a `Tenant` record with a unique `schema_name`
2. Create a `Domain` record mapping the subdomain to the tenant
3. Run migrations for the new schema: `python manage.py migrate_schemas --tenant`
4. Optionally seed the tenant with default data (categories, roles, etc.)
5. Create the tenant admin user

### 2. Accessing a Tenant

The tenant is identified by the incoming request's hostname:

| Request URL                 | Tenant Resolved |
| --------------------------- | --------------- |
| `acme.lankacommerce.lk`     | acme            |
| `bestshop.lankacommerce.lk` | bestshop        |
| `lankacommerce.lk`          | public (shared) |

The `TenantMainMiddleware` (from `django-tenants`) inspects the `Host` header and sets the PostgreSQL `search_path` to the corresponding schema.

### 3. Deactivating a Tenant

1. Set `is_active = False` on the Tenant record
2. The middleware will reject requests for inactive tenants
3. The schema and data are preserved for potential reactivation

### 4. Deleting a Tenant

1. Deactivate the tenant first
2. Export the tenant's data for archival
3. Drop the PostgreSQL schema: `DROP SCHEMA tenant_<slug> CASCADE;`
4. Delete the Tenant and Domain records

---

## Database Operations

### Running Migrations

| Scope                              | Command                                                        |
| ---------------------------------- | -------------------------------------------------------------- |
| All schemas (shared + all tenants) | `python manage.py migrate_schemas`                             |
| Shared schema only                 | `python manage.py migrate_schemas --shared`                    |
| Tenant schemas only                | `python manage.py migrate_schemas --tenant`                    |
| Specific tenant                    | `python manage.py tenant_command migrate --schema=tenant_acme` |

### Running Management Commands per Tenant

1. Run a command for a specific tenant: `python manage.py tenant_command <command> --schema=<schema_name>`
2. Run a command for all tenants: `python manage.py tenant_command <command> --all`

### Creating a Tenant Shell

1. Open a Django shell scoped to a tenant: `python manage.py tenant_command shell --schema=tenant_acme`

---

## Request Context

Within any view or serializer, the current tenant is available via:

| Access Method            | Description                       |
| ------------------------ | --------------------------------- |
| `request.tenant`         | The current Tenant object         |
| `connection.schema_name` | The active PostgreSQL schema name |
| `connection.tenant`      | Same as `request.tenant`          |

All ORM queries are automatically scoped to the current tenant's schema — no manual filtering is required.

---

## Data Isolation Rules

| Rule                                 | Description                                                         |
| ------------------------------------ | ------------------------------------------------------------------- |
| No cross-tenant queries              | The ORM only sees the current tenant's schema                       |
| Shared data is read-only for tenants | Tenants cannot modify shared tables                                 |
| Superusers bypass isolation          | Admin users can access the public schema                            |
| Background tasks must set context    | Celery tasks must explicitly set the tenant schema before executing |

### Celery Task Context

Background tasks run outside the request cycle and do not have automatic tenant context. Each task must set the schema explicitly:

1. Accept the `schema_name` as a task argument
2. Set the schema at the start of the task
3. Reset the schema when the task completes

---

## Best Practices

| Practice               | Recommendation                                            |
| ---------------------- | --------------------------------------------------------- |
| Schema naming          | Use `tenant_<slug>` format for consistency                |
| Migration testing      | Test migrations against both shared and tenant schemas    |
| Performance monitoring | Monitor per-tenant query counts and response times        |
| Backup strategy        | Back up the entire database (all schemas) regularly       |
| Data export            | Provide tenants with a data export feature for compliance |
| Resource limits        | Implement per-tenant quotas (storage, API calls, users)   |

---

## Related Documentation

- [Database Guide](database.md) — Migrations, seeding, and backups
- [Backend Apps Guide](../backend/apps.md) — App structure and tenant classification
- [Backend Models Guide](../backend/models.md) — TenantAwareMixin and base models
- [Getting Started](getting-started.md) — Quick onboarding overview
- [Docs Index](../index.md) — Documentation hub
