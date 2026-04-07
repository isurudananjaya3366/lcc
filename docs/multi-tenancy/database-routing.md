# Database Routing — Multi-Tenancy Guide

> How LankaCommerce Cloud routes queries and migrations across schemas.

---

## How It Works

LankaCommerce Cloud uses PostgreSQL schema-based multi-tenancy via
django-tenants. Each tenant gets a dedicated schema (e.g. tenant_acme)
while shared data lives in the public schema.

Database routing ensures:

- Shared apps migrate to and query the public schema only
- Tenant apps migrate to and query individual tenant schemas
- Cross-schema foreign key relations are prevented

---

## Routing Mechanism

### Query Routing (search_path)

django-tenants uses PostgreSQL's search_path to route queries:

1. A request arrives at the server
2. TenantMainMiddleware resolves the tenant from the hostname
3. The middleware sets search_path to the tenant's schema
4. All subsequent queries in that request use the tenant's schema
5. No router-level query routing is needed

### Migration Routing (TenantSyncRouter)

TenantSyncRouter routes migrations during manage.py migrate_schemas:

1. For the public schema: only SHARED_APPS migrations run
2. For each tenant schema: only TENANT_APPS migrations run
3. Dual apps (contenttypes, auth) migrate to both schemas

### Relation Prevention (TenantRouter)

TenantRouter prevents cross-schema foreign key declarations:

1. Relations within the same schema classification: allowed
2. Relations involving dual apps: allowed
3. Shared-only to tenant-only relations: blocked

---

## Router Stack

Routers are evaluated in order in DATABASE_ROUTERS:

| Priority | Router           | Implements     | Purpose                 |
| -------- | ---------------- | -------------- | ----------------------- |
| 1        | TenantRouter     | allow_relation | Cross-schema prevention |
| 2        | TenantSyncRouter | allow_migrate  | Migration routing       |

TenantRouter is first so relation checks happen before migration routing.
Both routers return None for methods they do not implement, allowing
Django to fall through to the next router.

---

## App Classification Summary

| Category    | Count | Schema     | Examples                              |
| ----------- | ----- | ---------- | ------------------------------------- |
| Shared-only | 16    | public     | tenants, core, users, rest_framework  |
| Tenant-only | 10    | tenant\_\* | products, sales, inventory, customers |
| Dual        | 2     | both       | contenttypes, auth                    |

The classification is defined in SHARED_APPS and TENANT_APPS in
backend/config/settings/database.py.

---

## Test Coverage

Router behavior is covered by tests in
backend/tests/tenants/test_routers.py with 31 test cases across
5 test classes:

| Class                     | Tests | Covers                                |
| ------------------------- | ----- | ------------------------------------- |
| TestGetAppClassification  | 5     | App classification logic              |
| TestAllowRelation         | 11    | Relation allow/block rules            |
| TestDeferredMethods       | 5     | None returns for deferred methods     |
| TestDatabaseRoutersConfig | 4     | Settings configuration                |
| TestEdgeCases             | 6     | Unknown apps, empty hints, edge cases |

---

## Key Files

| File                                  | Purpose                              |
| ------------------------------------- | ------------------------------------ |
| backend/config/settings/database.py   | DATABASE_ROUTERS, SHARED/TENANT_APPS |
| backend/apps/tenants/routers.py       | TenantRouter implementation          |
| backend/tests/tenants/test_routers.py | Router test suite                    |

---

## Related Documentation

- [Database Routers Reference](../database/database-routers.md) — Detailed router configuration
- [Tenant Settings](../database/tenant-settings.md) — All multi-tenancy settings
- [App Classification](../database/app-classification.md) — SHARED vs TENANT lists
- [Schema Naming](../database/schema-naming.md) — Schema naming conventions
- [Tenant Models](../database/tenant-models.md) — Tenant and Domain model reference
