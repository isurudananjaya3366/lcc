# App Classification — SHARED vs TENANT

> How LankaCommerce Cloud classifies Django apps for multi-tenant schema isolation.

---

## Overview

django-tenants requires every Django app to be classified as **shared** (public schema), **tenant** (per-tenant schema), or **both**. This classification determines which database tables are created in the public schema versus replicated in each tenant schema.

LankaCommerce Cloud defines these lists in backend/config/settings/database.py as SHARED_APPS, TENANT_APPS, and INSTALLED_APPS.

---

## Classification Table

| App                         | SHARED | TENANT | Category             | Reason                                                                         |
| --------------------------- | ------ | ------ | -------------------- | ------------------------------------------------------------------------------ |
| django_tenants              | Yes    | No     | Multi-tenancy core   | Schema management, middleware hooks, signals — must be first                   |
| django.contrib.admin        | Yes    | No     | Django framework     | Single admin interface with schema-switching                                   |
| django.contrib.auth         | Yes    | Yes    | Django framework     | Public schema for superusers, tenant schema for per-tenant users               |
| django.contrib.contenttypes | Yes    | Yes    | Django framework     | Public schema for shared content types, tenant schema for per-tenant isolation |
| django.contrib.sessions     | Yes    | No     | Django framework     | Session storage is global, not per-tenant                                      |
| django.contrib.messages     | Yes    | No     | Django framework     | Flash messages framework, tenant-agnostic                                      |
| django.contrib.staticfiles  | Yes    | No     | Django framework     | Static file serving via WhiteNoise, global                                     |
| apps.tenants                | Yes    | No     | LankaCommerce shared | Tenant and Domain models — must be in public schema for routing                |
| apps.core                   | Yes    | No     | LankaCommerce shared | Core utilities, base models, shared helpers                                    |
| apps.users                  | Yes    | No     | LankaCommerce shared | User profiles and management — shared user registry                            |
| rest_framework              | Yes    | No     | Third-party infra    | DRF — API framework configuration is global                                    |
| django_filters              | Yes    | No     | Third-party infra    | Query filtering — configuration is global                                      |
| rest_framework_simplejwt    | Yes    | No     | Third-party infra    | JWT auth — token handling is global                                            |
| drf_spectacular             | Yes    | No     | Third-party infra    | OpenAPI docs — schema generation is global                                     |
| corsheaders                 | Yes    | No     | Third-party infra    | CORS handling — middleware is global                                           |
| channels                    | Yes    | No     | Third-party infra    | Django Channels/WebSocket — global routing                                     |
| django_celery_beat          | Yes    | No     | Third-party infra    | Celery beat scheduler — shared task schedule                                   |
| django_celery_results       | Yes    | No     | Third-party infra    | Celery results backend — shared result storage                                 |
| apps.products               | No     | Yes    | Business module      | Product catalog — tenant-specific SKUs and pricing                             |
| apps.inventory              | No     | Yes    | Business module      | Stock and warehouse — tenant-specific stock levels                             |
| apps.vendors                | No     | Yes    | Business module      | Supplier management — tenant-specific vendors                                  |
| apps.sales                  | No     | Yes    | Business module      | Orders, invoicing, POS — tenant-specific transactions                          |
| apps.customers              | No     | Yes    | Business module      | Customer CRM — tenant-specific customer records                                |
| apps.hr                     | No     | Yes    | Business module      | Human resources — tenant-specific employees and payroll                        |
| apps.accounting             | No     | Yes    | Business module      | Accounting and finance — tenant-specific ledgers                               |
| apps.reports                | No     | Yes    | Business module      | Reports and analytics — tenant-specific report data                            |
| apps.webstore               | No     | Yes    | Business module      | E-commerce storefront — tenant-specific store content                          |
| apps.integrations           | No     | Yes    | Business module      | Third-party integrations — tenant-specific API keys                            |

---

## Inclusion Criteria

### When to put an app in SHARED_APPS

An app belongs in SHARED_APPS if any of these apply:

1. It manages multi-tenancy infrastructure (django_tenants, apps.tenants)
2. It provides framework plumbing needed globally (contenttypes, sessions, messages, staticfiles)
3. It provides a single administrative interface (admin)
4. It manages cross-tenant authentication or authorization (auth)
5. It provides tenant-agnostic middleware or URL routing (corsheaders)
6. It provides API infrastructure used across all tenants (DRF, Spectacular, etc.)

### When to put an app in TENANT_APPS

An app belongs in TENANT_APPS if any of these apply:

1. Its database tables store business data that must be isolated per tenant
2. It provides per-tenant content types or permissions (contenttypes, auth)
3. Its models reference tenant-specific foreign keys
4. Data leakage would occur if tables were shared across tenants

### Apps in both lists

Some apps appear in both SHARED_APPS and TENANT_APPS:

- **django.contrib.contenttypes** — Needed in public schema for shared content type resolution, and in each tenant schema for per-tenant GenericForeignKey and permission resolution
- **django.contrib.auth** — Needed in public schema for superuser management, and in each tenant schema for per-tenant users, groups, and permissions

---

## INSTALLED_APPS Construction

INSTALLED_APPS is built automatically from SHARED_APPS and TENANT_APPS:

    INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

This ensures:

1. All SHARED_APPS appear first (django_tenants at index 0)
2. TENANT_APPS that are not already in SHARED_APPS are appended
3. No duplicates — apps like contenttypes and auth appear only once

---

## Ordering Rules

1. **django_tenants must be first** — It registers signals and middleware hooks that other apps depend on during Django startup
2. **contenttypes must be first in TENANT_APPS** — Per-tenant content type tables must exist before auth Permission tables (which have a foreign key to ContentType)
3. **auth must follow contenttypes in TENANT_APPS** — The Permission model depends on ContentType
4. **Shared apps always precede tenant-only apps in INSTALLED_APPS** — Guaranteed by the combination formula

---

## Counts

| List           | Count | Description                                                         |
| -------------- | ----- | ------------------------------------------------------------------- |
| SHARED_APPS    | 18    | 1 multi-tenancy + 6 Django + 3 LankaCommerce + 8 third-party        |
| TENANT_APPS    | 12    | 2 Django (contenttypes, auth) + 10 business modules                 |
| INSTALLED_APPS | 28    | 18 shared + 10 unique tenant-only (2 overlapping apps deduplicated) |

---

## Adding a New App

When adding a new Django app to LankaCommerce Cloud:

1. Determine if the app stores tenant-specific business data or provides shared infrastructure
2. Add it to SHARED_APPS, TENANT_APPS, or both in backend/config/settings/database.py
3. INSTALLED_APPS is rebuilt automatically — do not edit it directly
4. The old DJANGO_APPS, THIRD_PARTY_APPS, and LOCAL_APPS lists in base.py are kept as reference only and are not used for INSTALLED_APPS construction
5. Run migrate_schemas to create tables in the appropriate schemas

---

## Related Documentation

- [Tenant Settings Reference](tenant-settings.md) — All django-tenants configuration settings
- [Schema Naming and Multi-Tenancy Layout](schema-naming.md) — Tenant schema naming conventions
- [Multi-Tenancy Guide](../guides/multi-tenancy.md) — Tenant provisioning and operations
- [PgBouncer Connection Pooling](pgbouncer.md) — Connection pooling for multi-tenant workloads
- [ADR-0004: Per-Tenant Authentication](../adr/0004-per-tenant-authentication.md) — Why auth is per-tenant
