# ADR-0002: Multi-Tenancy Approach

> **Status:** Accepted  
> **Date:** 2025-01-01  
> **Authors:** LankaCommerce Cloud Team

---

## Context

LankaCommerce Cloud is a SaaS platform serving multiple Sri Lankan SMEs from a single deployment. Each business (tenant) must have complete data isolation — one tenant must never see or modify another tenant's products, orders, customers, or financial data.

The team evaluated three common multi-tenancy approaches for Django and PostgreSQL:

| Approach                         | Description                                                             |
| -------------------------------- | ----------------------------------------------------------------------- |
| Shared schema with tenant column | All tenants share the same tables; a `tenant_id` column filters data    |
| Schema-based isolation           | Each tenant gets a dedicated PostgreSQL schema within the same database |
| Database-per-tenant              | Each tenant gets a completely separate database                         |

Key requirements included:

- Strong data isolation for compliance and trust
- Reasonable operational complexity for a small team
- Efficient resource usage (not one database per tenant)
- Compatibility with Django ORM and existing third-party apps
- Ability to run migrations across all tenants reliably

---

## Decision

We will use **schema-based multi-tenancy** powered by `django-tenants`. Each tenant gets a dedicated PostgreSQL schema, while shared data (tenant registry, plans, domains) lives in the `public` schema.

| Schema          | Contents                                          | Apps          |
| --------------- | ------------------------------------------------- | ------------- |
| `public`        | Tenant records, domains, plans, admin users       | `SHARED_APPS` |
| `tenant_<slug>` | Products, orders, customers, HR, accounting, etc. | `TENANT_APPS` |

Tenant resolution is handled by `TenantMainMiddleware`, which inspects the `Host` header of each request and sets the PostgreSQL `search_path` to the corresponding schema.

---

## Consequences

### Positive

- Complete data isolation at the database level — no risk of cross-tenant data leaks through ORM mistakes
- Each tenant's schema is structurally identical, simplifying migrations
- PostgreSQL handles schema-level indexing and query optimization independently per tenant
- `django-tenants` is a mature, well-maintained library with good documentation
- Backup and restore can be done per-schema or for the entire database
- Future compliance requirements (data residency, GDPR) are easier to address per-schema

### Negative

- Schema count grows linearly with tenant count — may require management at scale (hundreds of tenants)
- Migrations must run across all schemas, which takes longer as tenant count grows
- Background tasks (Celery) must explicitly set the schema context before executing
- Some Django third-party apps may not be schema-aware out of the box
- Database connection pooling (PgBouncer) requires careful configuration with schema switching

### Neutral

- PostgreSQL's schema mechanism is a standard feature and does not require extensions
- Migration tooling (`migrate_schemas`) is provided by `django-tenants`
- The approach is between full isolation (database-per-tenant) and shared tables, balancing security and efficiency

---

## Alternatives Considered

| Alternative                           | Reason for Rejection                                                                                                     |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Shared schema with `tenant_id` column | Weaker isolation — a missing filter could expose another tenant's data; every query must include the tenant filter       |
| Database-per-tenant                   | Too resource-intensive for the expected tenant count; each database requires its own connection pool and backup strategy |
| Row-level security (RLS)              | PostgreSQL RLS adds isolation but is harder to manage, test, and debug with Django ORM; `django-tenants` is more mature  |

---

## References

- [django-tenants documentation](https://django-tenants.readthedocs.io/)
- [Multi-Tenancy Guide](../guides/multi-tenancy.md) — Operational guide for tenant management
- [Backend Apps Guide](../backend/apps.md) — SHARED_APPS and TENANT_APPS classification
