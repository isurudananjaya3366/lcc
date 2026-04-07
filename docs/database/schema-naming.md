# Schema Naming & Multi-Tenancy Layout

> PostgreSQL schema naming conventions, public schema baseline, and tenant search path behaviour for LankaCommerce Cloud.

---

## Table of Contents

- [Schema Naming Convention](#schema-naming-convention)
- [Public Schema Baseline](#public-schema-baseline)
- [Tenant Schema Contents](#tenant-schema-contents)
- [Search Path Behaviour](#search-path-behaviour)
- [Privilege Access Boundaries](#privilege-access-boundaries)
- [Schema Template Validation](#schema-template-validation)

---

## Schema Naming Convention

Every tenant receives a dedicated PostgreSQL schema. Schemas follow the `tenant_<slug>` pattern where `<slug>` is the tenant's URL-safe identifier.

### Naming Pattern

| Component  | Rule                                                                |
| ---------- | ------------------------------------------------------------------- |
| Prefix     | `tenant_` (literal, always lowercase)                               |
| Slug       | Lowercase alphanumeric with hyphens, derived from the tenant domain |
| Separator  | Hyphens converted to underscores for PostgreSQL compatibility       |
| Max length | 63 characters total (PostgreSQL identifier limit)                   |

### Examples

| Tenant Domain                 | Schema Name         |
| ----------------------------- | ------------------- |
| acme.lankacommerce.lk         | tenant_acme         |
| island-foods.lankacommerce.lk | tenant_island_foods |
| colombo-mart.lankacommerce.lk | tenant_colombo_mart |
| 123-store.lankacommerce.lk    | tenant_123_store    |

### Constraints

- Slug must start with a letter or digit
- Only lowercase letters, digits, and underscores after the `tenant_` prefix
- No consecutive underscores
- Reserved names: `public`, `pg_catalog`, `information_schema`, `pg_toast` are never used as tenant slugs
- The `public` schema is shared and is never a tenant schema

---

## Public Schema Baseline

The `public` schema holds data shared across all tenants. It is managed by django-tenants and contains tables from `SHARED_APPS`.

### Public Schema Tables

| Category           | Tables                                                                      | Purpose                            |
| ------------------ | --------------------------------------------------------------------------- | ---------------------------------- |
| Tenant registry    | `tenants_tenant`, `tenants_domain`                                          | Tenant metadata and domain routing |
| User accounts      | `users_user`, `users_userprofile`                                           | Authentication and user data       |
| Subscription plans | `tenants_plan` (future)                                                     | Billing and feature gating         |
| Django system      | `django_migrations`, `django_content_type`, `auth_permission`, `auth_group` | Framework internals                |
| Admin              | `django_admin_log`                                                          | Audit trail for admin actions      |
| Sessions           | `django_session`                                                            | Server-side session storage        |

### Separation Rules

| Rule                        | Description                                                                                                         |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Tenant data never in public | Products, orders, inventory, customers, vendors, HR, and accounting tables live exclusively in tenant schemas       |
| Shared data never in tenant | Tenant registry, user accounts, and subscription plans live exclusively in the public schema                        |
| Extensions are global       | PostgreSQL extensions (uuid-ossp, hstore, pg_trgm) are installed at the database level and available to all schemas |
| Migrations are split        | `SHARED_APPS` migrate against the public schema; `TENANT_APPS` migrate against every tenant schema                  |

---

## Tenant Schema Contents

Each `tenant_<slug>` schema contains tables from `TENANT_APPS`. When a new tenant is provisioned, django-tenants runs `migrate_schemas` to create these tables inside the tenant's schema.

### Tenant Schema Tables

| App          | Key Tables                                     | Purpose                  |
| ------------ | ---------------------------------------------- | ------------------------ |
| products     | `products_product`, `products_category`        | Product catalogue        |
| inventory    | `inventory_stock`, `inventory_warehouse`       | Stock management         |
| sales        | `sales_order`, `sales_orderitem`               | Sales orders and POS     |
| customers    | `customers_customer`                           | Customer records         |
| vendors      | `vendors_vendor`                               | Supplier records         |
| hr           | `hr_employee`, `hr_department`                 | Human resources          |
| accounting   | `accounting_account`, `accounting_transaction` | Financial records        |
| webstore     | `webstore_storefront`                          | E-commerce storefront    |
| reports      | `reports_report`                               | Reporting metadata       |
| integrations | `integrations_provider`                        | Third-party integrations |

---

## Search Path Behaviour

PostgreSQL's `search_path` determines which schema is queried when a table name is used without a schema qualifier. django-tenants manages this automatically via middleware.

### Request Flow

1. HTTP request arrives with a `Host` header (e.g., `acme.lankacommerce.lk`)
2. `TenantMainMiddleware` looks up the domain in the `tenants_domain` table (public schema)
3. The middleware sets `search_path` to `tenant_acme, public`
4. All subsequent ORM queries resolve tables from the tenant schema first, falling back to public
5. At the end of the request, the `search_path` is reset

### Search Path Order

| Position | Schema          | Purpose                                         |
| -------- | --------------- | ----------------------------------------------- |
| 1st      | `tenant_<slug>` | Tenant-specific tables (products, orders, etc.) |
| 2nd      | `public`        | Shared tables (users, tenants, Django system)   |

### Key Rules

- The tenant schema is always first — tenant tables shadow any identically-named public tables
- The public schema is always included so that shared models (users, tenants) are accessible
- Celery tasks must explicitly set the tenant context before accessing tenant data
- Management commands that operate across tenants use `tenant_command` or iterate with `all_tenants`

### Middleware Configuration

The middleware is configured in Django settings:

| Setting             | Value                                                                 |
| ------------------- | --------------------------------------------------------------------- |
| MIDDLEWARE entry    | `django_tenants.middleware.main.TenantMainMiddleware` (first in list) |
| TENANT_MODEL        | `tenants.Tenant`                                                      |
| TENANT_DOMAIN_MODEL | `tenants.Domain`                                                      |
| DATABASE_ROUTERS    | `django_tenants.routers.TenantSyncRouter`                             |

---

## Privilege Access Boundaries

Schema privileges enforce tenant isolation at the database level, preventing cross-tenant data access even if application logic is bypassed.

### Role Model

| Role     | Type          | Purpose                                                      |
| -------- | ------------- | ------------------------------------------------------------ |
| postgres | Superuser     | Database owner, creates schemas and runs init scripts        |
| lcc_user | Application   | Django application user, full CRUD on public and tenant data |
| PUBLIC   | Default group | No access (explicitly revoked from public schema)            |

### Public Schema Privileges

| Privilege                 | Granted To | Method                               |
| ------------------------- | ---------- | ------------------------------------ |
| ALL ON SCHEMA public      | lcc_user   | Explicit GRANT in 03-privileges.sql  |
| ALL ON TABLES (future)    | lcc_user   | DEFAULT PRIVILEGES for postgres role |
| ALL ON SEQUENCES (future) | lcc_user   | DEFAULT PRIVILEGES for postgres role |
| ALL ON FUNCTIONS (future) | lcc_user   | DEFAULT PRIVILEGES for postgres role |
| USAGE ON TYPES (future)   | lcc_user   | DEFAULT PRIVILEGES for postgres role |
| All permissions           | PUBLIC     | Revoked — no anonymous schema access |

### Tenant Schema Privileges

When a tenant schema is created via `create_tenant_schema()` or django-tenants:

| Privilege                 | Granted To | Method                                                |
| ------------------------- | ---------- | ----------------------------------------------------- |
| ALL ON SCHEMA             | lcc_user   | Explicit grant in `create_tenant_schema()` function   |
| ALL ON TABLES (future)    | lcc_user   | DEFAULT PRIVILEGES in function + global postgres role |
| ALL ON SEQUENCES (future) | lcc_user   | DEFAULT PRIVILEGES in function + global postgres role |
| ALL ON FUNCTIONS (future) | lcc_user   | DEFAULT PRIVILEGES via global postgres role defaults  |
| USAGE ON TYPES (future)   | lcc_user   | DEFAULT PRIVILEGES via global postgres role defaults  |

### Isolation Guarantees

| Guarantee                             | Enforcement Layer                                        |
| ------------------------------------- | -------------------------------------------------------- |
| Tenant cannot access other tenants    | search_path set per-request by django-tenants middleware |
| PUBLIC role has no schema access      | REVOKE ALL ON SCHEMA public FROM PUBLIC                  |
| Only lcc_user and postgres can create | Explicit CREATE grant, all others excluded               |
| System catalogs are read-only         | USAGE grant on information_schema and pg_catalog only    |
| Extension functions shared safely     | Public schema in search_path provides extension access   |

### Privilege Inheritance

Privileges are established at three levels to ensure complete coverage:

| Level                    | File                    | Scope                                           |
| ------------------------ | ----------------------- | ----------------------------------------------- |
| Database-wide defaults   | 03-privileges.sql       | Global defaults for any object postgres creates |
| Schema-specific defaults | 02-schema-functions.sql | Per-schema defaults set during creation         |
| Object-level grants      | 01-init.sql             | Explicit grants on existing objects             |

---

When a new tenant is created, django-tenants provisions the schema by:

1. Creating the PostgreSQL schema (`CREATE SCHEMA tenant_<slug>`)
2. Setting `search_path` to the new schema
3. Running all `TENANT_APPS` migrations inside the new schema
4. Creating default data via post-save signals (if configured)

### Validation Record

| Check                  | Status        | Details                                         |
| ---------------------- | ------------- | ----------------------------------------------- |
| Schema naming pattern  | ✅ Verified   | `tenant_<slug>` format enforced by Tenant model |
| Public schema contents | ✅ Documented | SHARED_APPS tables listed above                 |
| Tenant schema contents | ✅ Documented | TENANT_APPS tables listed above                 |
| search_path order      | ✅ Documented | Tenant-first, public-second                     |
| Extension availability | ✅ Verified   | uuid-ossp, hstore, pg_trgm in all schemas       |
| Naming constraints     | ✅ Documented | Max 63 chars, lowercase, underscores            |

**Validation Date:** 2026-02-15
**Reviewer:** AI Agent (GitHub Copilot)

---

## Related Documentation

- [Multi-Tenancy Guide](../guides/multi-tenancy.md) — Tenant provisioning and operations
- [ADR-0002: Multi-Tenancy Approach](../adr/0002-multi-tenancy-approach.md) — Decision rationale
- [Models Guide](../backend/models.md) — Base model patterns
- [Database Guide](../guides/database.md) — Migrations and maintenance
