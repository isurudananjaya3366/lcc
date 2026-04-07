# Naming Conventions

> Table, field, and schema naming rules for LankaCommerce Cloud database objects.

---

## Overview

Consistent naming ensures readability, prevents conflicts across schemas, and aligns with Django and PostgreSQL conventions. All LankaCommerce Cloud database objects follow these rules.

---

## Table Naming

### Django Convention

Django auto-generates table names from the app label and model name using the pattern:

    <app_label>_<modelname>

All names are lowercase with underscores. Examples:

| App Label | Model Name       | Table Name                |
| --------- | ---------------- | ------------------------- |
| tenants   | Tenant           | tenants_tenant            |
| tenants   | Domain           | tenants_domain            |
| platform  | SubscriptionPlan | platform_subscriptionplan |
| platform  | PlatformSetting  | platform_platformsetting  |
| platform  | FeatureFlag      | platform_featureflag      |
| products  | Product          | products_product          |
| sales     | SalesOrder       | sales_salesorder          |

### Custom Table Names

If a model needs a custom table name, use the Meta.db_table attribute. Custom names must:

- Use lowercase with underscores (snake_case)
- Include the app prefix to avoid conflicts
- Be no longer than 63 characters (PostgreSQL limit)

### Third-Party Tables

Third-party packages use their own prefixes:

| Package                     | Prefix                 | Example                          |
| --------------------------- | ---------------------- | -------------------------------- |
| django.contrib.auth         | auth\_                 | auth_user, auth_group            |
| django.contrib.contenttypes | django\_               | django_content_type              |
| django.contrib.sessions     | django\_               | django_session                   |
| django.contrib.admin        | django\_               | django_admin_log                 |
| django_celery_beat          | django*celery_beat*    | django_celery_beat_periodictask  |
| django_celery_results       | django*celery_results* | django_celery_results_taskresult |

---

## Field Naming

### General Rules

- Use snake_case for all field names
- Use descriptive names that convey purpose
- Suffix boolean fields with is* or has* (e.g. is_active, has_permissions)
- Suffix date fields with \_on or \_at or \_until (e.g. created_on, updated_at, paid_until)
- Suffix foreign keys with \_id (Django auto-adds this for FK columns)

### Common Field Patterns

| Pattern    | Usage                        | Example                        |
| ---------- | ---------------------------- | ------------------------------ |
| name       | Human-readable identifier    | tenant.name, plan.name         |
| slug       | URL-safe identifier          | tenant.slug, plan.slug         |
| status     | Lifecycle state with choices | tenant.status, order.status    |
| is_active  | Boolean active flag          | user.is_active, flag.is_active |
| created_on | Auto-set creation timestamp  | tenant.created_on              |
| updated_on | Auto-set update timestamp    | tenant.updated_on              |
| settings   | JSON configuration blob      | tenant.settings                |

### Foreign Key Fields

Django names FK columns as field_name_id in the database. In model definitions, use the related model name in lowercase:

| Model Field  | Database Column | Related Model    |
| ------------ | --------------- | ---------------- |
| tenant       | tenant_id       | Tenant           |
| plan         | plan_id         | SubscriptionPlan |
| user         | user_id         | User             |
| content_type | content_type_id | ContentType      |

---

## Schema Naming

### Public Schema

The shared public schema uses the PostgreSQL default name:

    public

All SHARED_APPS tables reside here.

### Tenant Schemas

Tenant schemas use the prefix configured in TENANT_SCHEMA_PREFIX:

    tenant_<slug_with_underscores>

Examples:

| Slug           | Schema Name           |
| -------------- | --------------------- |
| acme-trading   | tenant_acme_trading   |
| best-shop      | tenant_best_shop      |
| test-isolation | tenant_test_isolation |

Schema name rules:

- Maximum 63 characters (PostgreSQL limit)
- Hyphens in slugs are converted to underscores
- The prefix tenant\_ is mandatory for all business schemas
- Reserved names (public, pg_catalog, information_schema, pg_toast) are prohibited for tenant slugs

---

## Index Naming

Django auto-generates index names. Custom indexes should follow this pattern:

    <table>_<column(s)>_<type>

Where type is one of: idx (B-tree), uniq (unique), gin (GIN), gist (GiST).

Examples:

| Index Purpose        | Name Pattern                |
| -------------------- | --------------------------- |
| Single column B-tree | tenants_tenant_status_idx   |
| Composite B-tree     | sales_order_tenant_date_idx |
| Unique constraint    | platform_setting_key_uniq   |
| GIN (JSON)           | tenants_tenant_settings_gin |

---

## Constraint Naming

### Foreign Keys

Django generates FK constraint names automatically. Custom constraints should follow:

    <table>_<column>_fk_<referenced_table>

### Check Constraints

    <table>_<column>_check

### Unique Constraints

    <table>_<columns>_uniq

---

## Migration File Naming

Django auto-generates migration files with sequential numbering:

    <number>_<description>.py

Examples:

- 0001_initial.py
- 0002_add_status_field.py
- 0003_alter_tenant_settings.py

Custom migration descriptions should be lowercase with underscores and describe the change concisely.

---

## App Label Rules

App labels must be unique across the entire project. LankaCommerce Cloud uses these conventions:

| Category      | App Label    | Django Name       |
| ------------- | ------------ | ----------------- |
| Multi-Tenancy | tenants      | apps.tenants      |
| Platform      | platform     | apps.platform     |
| Core          | core         | apps.core         |
| Users         | users        | apps.users        |
| Products      | products     | apps.products     |
| Inventory     | inventory    | apps.inventory    |
| Sales         | sales        | apps.sales        |
| Customers     | customers    | apps.customers    |
| Vendors       | vendors      | apps.vendors      |
| HR            | hr           | apps.hr           |
| Accounting    | accounting   | apps.accounting   |
| Reports       | reports      | apps.reports      |
| Webstore      | webstore     | apps.webstore     |
| Integrations  | integrations | apps.integrations |

---

## Related Documentation

- [Public Schema ERD](public-schema-erd.md) — Entity relationships in the public schema
- [App Classification](app-classification.md) — SHARED_APPS vs TENANT_APPS
- [Tenant Settings](tenant-settings.md) — Schema prefix and naming configuration
