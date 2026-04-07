# Tenant Settings Reference

> LankaCommerce Cloud — Multi-Tenancy Configuration

---

## Overview

LankaCommerce Cloud uses django-tenants 3.10.0 for PostgreSQL schema-based
multi-tenancy. Each tenant (organization) gets an isolated PostgreSQL schema
while sharing a single database instance.

All tenant-related settings are centralized in:

    backend/config/settings/database.py

This module is wildcard-imported into base.py, making settings available
across all environments (local, production, test).

---

## Settings Reference

### Tenant Model Settings

| Setting             | Value          | Purpose                        |
| ------------------- | -------------- | ------------------------------ |
| TENANT_MODEL        | tenants.Tenant | Model implementing TenantMixin |
| TENANT_DOMAIN_MODEL | tenants.Domain | Model implementing DomainMixin |

Both models live in apps/tenants/models.py. The Tenant model stores
schema_name and tenant metadata. The Domain model maps hostnames to tenants.

### Database Engine

| Setting          | Value                                    | Purpose                                 |
| ---------------- | ---------------------------------------- | --------------------------------------- |
| ENGINE           | django_tenants.postgresql_backend        | Multi-tenant aware DB backend           |
| DATABASE_ROUTERS | TenantRouter, TenantSyncRouter (2 total) | Relation prevention + migration routing |

The engine extends the standard PostgreSQL backend to manage search_path
switching per request. TenantRouter (apps.tenants.routers.TenantRouter)
prevents cross-schema foreign key relations. TenantSyncRouter ensures
SHARED_APPS migrate to the public schema and TENANT_APPS migrate to
each tenant schema. See database-routers.md for full details.

### Public Schema Settings

| Setting                        | Value  | Purpose                                         |
| ------------------------------ | ------ | ----------------------------------------------- |
| PUBLIC_SCHEMA_NAME             | public | PostgreSQL schema for shared data               |
| SHOW_PUBLIC_IF_NO_TENANT_FOUND | False  | Returns 404 if hostname does not match a tenant |

The public schema contains tables for all SHARED_APPS including tenant
metadata, authentication, and the admin interface.

### Domain Settings

| Setting            | Value                            | Purpose                               |
| ------------------ | -------------------------------- | ------------------------------------- |
| BASE_TENANT_DOMAIN | localhost (configurable via env) | Base domain for tenant URL generation |

Domain routing pattern:

- Development: acme.localhost, best.localhost
- Production: acme.lankacommerce.lk, best.lankacommerce.lk

TenantMainMiddleware resolves the current tenant from the request hostname
by looking up the Domain model.

### Schema Settings

| Setting                          | Value    | Purpose                             |
| -------------------------------- | -------- | ----------------------------------- |
| TENANT_SCHEMA_PREFIX             | tenant\_ | Prefix for tenant schema names      |
| AUTO_CREATE_SCHEMA               | True     | Auto-create schema on Tenant.save() |
| AUTO_DROP_SCHEMA                 | False    | Do NOT auto-delete schemas (safety) |
| TENANT_CREATION_FAKES_MIGRATIONS | False    | Run full migrations per tenant      |
| TENANT_BASE_SCHEMA               | None     | No template schema cloning          |

Schema naming convention:

- Public tenant: schema = public
- Business tenants: schema = tenant\_{slug} (e.g. tenant_acme, tenant_best)

The TENANT_SCHEMA_PREFIX is a custom LankaCommerce setting used by tenant
provisioning logic to auto-generate schema names.

### Performance Settings

| Setting                | Value | Purpose                       |
| ---------------------- | ----- | ----------------------------- |
| TENANT_LIMIT_SET_CALLS | True  | Reduces SET search_path calls |

When enabled, the search_path is only updated when switching between
tenants, not on every database query.

### Storage Settings

| Setting                         | Value                                                | Purpose                       |
| ------------------------------- | ---------------------------------------------------- | ----------------------------- |
| STORAGES["default"]["BACKEND"]  | django_tenants.files.storage.TenantFileSystemStorage | Tenant-aware media storage    |
| MULTITENANT_RELATIVE_MEDIA_ROOT | %s                                                   | Media subdirectory per tenant |

Media file layout:

    MEDIA_ROOT/
      public/              <- Public tenant uploads
      tenant_acme/         <- Acme Corp uploads
      tenant_best/         <- Best Trading uploads

Static files are NOT tenant-specific. They are served globally by WhiteNoise.

### App Classification

| Setting        | Purpose                                |
| -------------- | -------------------------------------- |
| SHARED_APPS    | Apps synced to the public schema only  |
| TENANT_APPS    | Apps synced to each tenant schema      |
| INSTALLED_APPS | Derived from SHARED_APPS + TENANT_APPS |

Currently configured as placeholders. Full classification is completed
in Group-C of SubPhase-02.

---

## Environment Variables

| Variable            | Default                           | Description                 |
| ------------------- | --------------------------------- | --------------------------- |
| DB_ENGINE           | django_tenants.postgresql_backend | Database engine             |
| BASE_TENANT_DOMAIN  | localhost                         | Base domain for tenant URLs |
| PUBLIC_SCHEMA_NAME  | public                            | Public schema name          |
| TENANT_MODEL        | tenants.Tenant                    | Tenant model reference      |
| TENANT_DOMAIN_MODEL | tenants.Domain                    | Domain model reference      |

---

## Safety Rules

1. AUTO_DROP_SCHEMA must remain False in production
2. Schema deletion should only occur via manage.py delete_tenant
3. Always back up before any schema operations
4. The public schema should never be dropped

---

## Related Documentation

- [Database Routers](database-routers.md) — Router configuration and routing rules
- [Schema Naming](schema-naming.md) — Schema naming conventions
- [PgBouncer](pgbouncer.md) — Connection pooling configuration
- [Backup Procedures](backup-procedures.md) — Database backup and restore
- [Performance Tuning](performance-tuning.md) — Database optimization

---

## Configuration File

All settings are in backend/config/settings/database.py, which is
imported by base.py via wildcard import.

Database credentials (HOST, PORT, PASSWORD) are in environment-specific
settings files (local.py, production.py) and are NOT in database.py.
