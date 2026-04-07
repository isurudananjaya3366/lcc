# Tenant and Domain Models

> Model reference for the Tenant and Domain models that power LankaCommerce Cloud's multi-tenancy.

---

## Overview

LankaCommerce Cloud uses two models in the tenants app to manage multi-tenancy:

- **Tenant** — Represents a business organization. Each tenant maps to a dedicated PostgreSQL schema.
- **Domain** — Maps hostnames and subdomains to tenants for request routing.

Both models live in the public schema (via SHARED_APPS) so django-tenants can look them up before routing to a tenant schema. They are defined in backend/apps/tenants/models.py.

---

## Tenant Model

The Tenant model extends django-tenants' TenantMixin.

### Fields

| Field       | Type           | Source      | Description                                                              |
| ----------- | -------------- | ----------- | ------------------------------------------------------------------------ |
| id          | BigAutoField   | Django      | Auto-incrementing primary key                                            |
| schema_name | CharField(63)  | TenantMixin | PostgreSQL schema name (e.g. 'public', 'tenant_acme'). Unique, auto-set. |
| name        | CharField(255) | LCC         | Human-readable business name                                             |
| slug        | SlugField(63)  | LCC         | URL-safe identifier for subdomains and schema naming. Unique.            |
| paid_until  | DateField      | LCC         | Subscription expiry date. Null means unlimited access.                   |
| on_trial    | BooleanField   | LCC         | Whether the tenant is on a trial period. Default: True.                  |
| status      | CharField(20)  | LCC         | Lifecycle state: active, suspended, or archived. Indexed for queries.    |
| settings    | JSONField      | LCC         | Per-tenant configuration (currency, timezone, date_format, language).    |
| created_on  | DateTimeField  | LCC         | Auto-set when the tenant is created.                                     |
| updated_on  | DateTimeField  | LCC         | Auto-set when the tenant is updated.                                     |

### Status Choices

| Value     | Label     | Meaning                                               |
| --------- | --------- | ----------------------------------------------------- |
| active    | Active    | Fully operational tenant                              |
| suspended | Suspended | Temporarily disabled (e.g. payment overdue)           |
| archived  | Archived  | Permanently deactivated, data retained for compliance |

### Properties

| Property     | Returns | Description                                   |
| ------------ | ------- | --------------------------------------------- |
| is_active    | bool    | True when status is active                    |
| is_suspended | bool    | True when status is suspended                 |
| is_archived  | bool    | True when status is archived                  |
| is_paid      | bool    | True when paid_until is null or in the future |
| is_public    | bool    | True when schema_name is 'public'             |

### Methods

| Method                         | Returns | Description                                            |
| ------------------------------ | ------- | ------------------------------------------------------ |
| get_setting(key, default=None) | any     | Returns a per-tenant setting, falling back to defaults |

### Schema Name Generation

When a Tenant is saved:

1. If schema_name is empty and slug is set, schema_name is auto-generated
2. Pattern: TENANT_SCHEMA_PREFIX + slug with hyphens replaced by underscores
3. Example: slug 'acme-trading' becomes schema_name 'tenant_acme_trading'
4. The public tenant has schema_name 'public' and is set manually

### Validation Rules

1. Slug must match the pattern: lowercase letters, digits, and hyphens only, starting with a letter or digit
2. Slug cannot be a reserved PostgreSQL name (public, pg_catalog, information_schema, pg_toast)
3. Generated schema_name must not exceed 63 characters (PostgreSQL limit)

### Meta Configuration

| Option              | Value    | Rationale                                                |
| ------------------- | -------- | -------------------------------------------------------- |
| verbose_name        | Tenant   | Clear singular name in admin and error messages          |
| verbose_name_plural | Tenants  | Correct pluralization for admin list views               |
| ordering            | ['name'] | Alphabetical by business name for predictable list order |

### Indexes

| Field       | Index Type | Reason                                                    |
| ----------- | ---------- | --------------------------------------------------------- |
| schema_name | Unique     | From TenantMixin — each schema maps to exactly one tenant |
| slug        | Unique     | Each tenant has a unique URL-safe identifier              |
| status      | B-tree     | Explicit db_index=True for filtering by lifecycle state   |

---

## Domain Model

The Domain model extends django-tenants' DomainMixin.

### Fields

| Field      | Type           | Source      | Description                                                   |
| ---------- | -------------- | ----------- | ------------------------------------------------------------- |
| id         | BigAutoField   | Django      | Auto-incrementing primary key                                 |
| domain     | CharField(253) | DomainMixin | Hostname or subdomain (e.g. 'acme.lankacommerce.lk'). Unique. |
| tenant     | ForeignKey     | DomainMixin | Foreign key to the Tenant model. related_name='domains'.      |
| is_primary | BooleanField   | DomainMixin | Whether this is the primary domain. Default: True.            |

### Domain Routing

django-tenants uses the Domain table to resolve tenants from incoming requests:

1. TenantMainMiddleware reads the Host header from each request
2. It looks up the hostname in the Domain table
3. The matching domain's tenant is activated
4. PostgreSQL search_path is set to the tenant's schema_name

### Domain Examples

| Domain                | Tenant    | Schema      | Notes                |
| --------------------- | --------- | ----------- | -------------------- |
| localhost             | Public    | public      | Local development    |
| lankacommerce.lk      | Public    | public      | Production           |
| acme.lankacommerce.lk | Acme Corp | tenant_acme | Business tenant      |
| acme.localhost        | Acme Corp | tenant_acme | Local dev for tenant |

### Domain Rules

- Do not include port numbers in the domain field (use 'localhost', not 'localhost:8000')
- Do not include 'www' prefix (use 'lankacommerce.lk', not 'www.lankacommerce.lk')
- Each tenant must have at least one domain
- Only one domain per tenant should be marked as is_primary=True
- The primary domain is used for generating canonical URLs

### Meta Configuration

| Option              | Value      | Rationale                                         |
| ------------------- | ---------- | ------------------------------------------------- |
| verbose_name        | Domain     | Clear singular name in admin and error messages   |
| verbose_name_plural | Domains    | Correct pluralization for admin list views        |
| ordering            | ['domain'] | Alphabetical by domain for predictable list order |

### Indexes

| Field  | Index Type | Reason                                                    |
| ------ | ---------- | --------------------------------------------------------- |
| domain | Unique     | From DomainMixin — each domain maps to exactly one tenant |
| tenant | B-tree     | Foreign key index for efficient reverse lookups           |

---

## Admin Configuration

Both models are registered in Django admin (backend/apps/tenants/admin.py).

### TenantAdmin

- **List display:** name, slug, schema_name, status, on_trial, paid_until, created_on
- **Filters:** status, on_trial
- **Search:** name, slug, schema_name
- **Read-only:** schema_name (auto-generated), created_on, updated_on
- **Fieldsets:** Identity, Billing, Lifecycle, Configuration (collapsed), Timestamps (collapsed)

### DomainAdmin

- **List display:** domain, tenant, is_primary
- **Filters:** is_primary
- **Search:** domain, tenant name, tenant slug
- **Raw ID fields:** tenant (for performance with many tenants)

### Security Notes

- Only superusers and platform administrators should have access to tenant admin
- Tenant and Domain admin operates on the public schema only
- Business data is not accessible through this admin interface
- Schema creation is triggered by AUTO_CREATE_SCHEMA on Tenant.save()
- Schema deletion is controlled by AUTO_DROP_SCHEMA (must remain False in production)

---

## Settings References

| Setting              | Value           | Location                            |
| -------------------- | --------------- | ----------------------------------- |
| TENANT_MODEL         | tenants.Tenant  | backend/config/settings/database.py |
| TENANT_DOMAIN_MODEL  | tenants.Domain  | backend/config/settings/database.py |
| TENANT_SCHEMA_PREFIX | tenant\_        | backend/config/settings/database.py |
| AUTO_CREATE_SCHEMA   | True            | backend/config/settings/database.py |
| AUTO_DROP_SCHEMA     | False           | backend/config/settings/database.py |
| BASE_TENANT_DOMAIN   | localhost (dev) | .env.docker                         |

---

## Related Documentation

- [App Classification — SHARED vs TENANT](app-classification.md) — How apps are classified
- [Tenant Settings Reference](tenant-settings.md) — All django-tenants settings
- [Schema Naming and Multi-Tenancy Layout](schema-naming.md) — Schema naming conventions
- [ADR-0002: Multi-Tenancy Approach](../adr/0002-multi-tenancy-approach.md) — Why schema-based isolation
- [ADR-0004: Per-Tenant Authentication](../adr/0004-per-tenant-authentication.md) — Why auth is per-tenant
- [Multi-Tenancy Guide](../guides/multi-tenancy.md) — Operational guide for tenant management
