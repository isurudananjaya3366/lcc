# Tenant Management Commands

Tenant management commands for LankaCommerce Cloud. These Django management
commands provide tenant lifecycle operations from the command line.

---

## Available Commands

### tenant_create

Creates a new tenant with its primary domain. The command automatically
generates the PostgreSQL schema name from the slug (with prefix tenant\_)
and runs all TENANT_APPS migrations in the new schema.

**Required Arguments**

| Argument | Description                                      |
| -------- | ------------------------------------------------ |
| --name   | Human-readable business name                     |
| --slug   | URL-safe identifier (lowercase, digits, hyphens) |

**Optional Arguments**

| Argument     | Default        | Description                                  |
| ------------ | -------------- | -------------------------------------------- |
| --domain     | slug.localhost | Primary domain for the tenant                |
| --paid-until | None           | Subscription expiry date (YYYY-MM-DD)        |
| --no-trial   | False          | Disable trial mode                           |
| --status     | active         | Initial status (active, suspended, archived) |

**Validation Rules**

- Slug must match the pattern: lowercase letters, digits, and hyphens only, starting with a letter or digit, no consecutive hyphens
- Slug must not be a reserved schema name (public, pg_catalog, information_schema, pg_toast)
- Generated schema name (tenant\_ + slug with hyphens as underscores) must not exceed 63 characters
- Slug must be unique across all tenants
- Domain must be unique across all domains

**What Happens on Creation**

1. Tenant record is created in the public schema (tenants_tenant table)
2. PostgreSQL schema is created (e.g. tenant_acme_trading)
3. All TENANT_APPS migrations are applied to the new schema
4. Primary domain record is created in the public schema (tenants_domain table)

**Usage via manage.py**

Run with Django manage.py:

    python manage.py tenant_create --name "Acme Trading" --slug "acme-trading"

With all options:

    python manage.py tenant_create --name "Best Shop" --slug "best-shop" --domain "best.lankacommerce.lk" --paid-until "2026-12-31" --status active --no-trial

**Usage via Makefile**

    make tenant-create name="Acme Trading" slug="acme-trading"

With optional domain:

    make tenant-create name="Best Shop" slug="best-shop" domain="best.lankacommerce.lk"

---

### tenant_list

Lists all tenants with their details and associated domains.

**Optional Arguments**

| Argument  | Description                                           |
| --------- | ----------------------------------------------------- |
| --status  | Filter by status (active, suspended, archived)        |
| --verbose | Show additional details (trial, paid_until, settings) |

**Output Fields**

| Field   | Description                                |
| ------- | ------------------------------------------ |
| ID      | Database primary key                       |
| Name    | Human-readable business name               |
| Schema  | PostgreSQL schema name                     |
| Slug    | URL-safe identifier                        |
| Status  | Lifecycle state                            |
| Domains | Associated domain names (\* marks primary) |
| Created | Creation timestamp                         |

**Verbose Mode Additional Fields**

| Field      | Description                       |
| ---------- | --------------------------------- |
| On Trial   | Whether tenant is on trial        |
| Paid Until | Subscription expiry date          |
| Public     | Whether this is the public tenant |
| Settings   | Per-tenant JSON configuration     |

**Usage via manage.py**

List all tenants:

    python manage.py tenant_list

List active tenants only:

    python manage.py tenant_list --status active

List with verbose details:

    python manage.py tenant_list --verbose

**Usage via Makefile**

    make tenant-list
    make tenant-list-verbose
    make tenant-list-active

---

## Makefile Targets

| Target                | Description                                  |
| --------------------- | -------------------------------------------- |
| tenant-list           | List all tenants                             |
| tenant-list-verbose   | List all tenants with verbose details        |
| tenant-list-active    | List only active tenants                     |
| tenant-create         | Create a new tenant (requires name and slug) |
| tenant-migrate-shared | Run shared schema migrations                 |
| tenant-migrate-tenant | Run tenant schema migrations                 |
| tenant-migrate-all    | Run all schema migrations                    |

---

## Migration Commands

django-tenants provides the migrate_schemas command that replaces Django's
standard migrate command for multi-tenant setups.

**Shared Migrations** apply to the public schema and affect SHARED_APPS only:

    python manage.py migrate_schemas --shared

**Tenant Migrations** apply to all tenant schemas and affect TENANT_APPS only:

    python manage.py migrate_schemas --tenant

**All Migrations** apply shared and tenant migrations in sequence:

    python manage.py migrate_schemas

---

## Related Documentation

- [Database Routers](../database/database-routers.md) — Router configuration and app classification
- [Tenant Settings](../database/tenant-settings.md) — Multi-tenancy settings reference
- [Database Routing](database-routing.md) — Routing mechanism overview
