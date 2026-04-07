# Public Schema ERD

> Entity-Relationship Diagram and model reference for the LankaCommerce Cloud public (shared) schema.

---

## Overview

The public schema contains all platform-wide models that are shared across tenants. These models are defined in apps listed in SHARED_APPS and reside exclusively in the public PostgreSQL schema.

Django-tenants sets the search_path to include public for every tenant context, so shared data is always accessible.

---

## Entity Groups

### Multi-Tenancy Core (apps.tenants)

Manages tenant lifecycle, domain routing, and schema provisioning.

| Entity | Table          | Description                                   |
| ------ | -------------- | --------------------------------------------- |
| Tenant | tenants_tenant | Business organizations with dedicated schemas |
| Domain | tenants_domain | Hostname-to-tenant routing mappings           |

**Relationships:**

- Domain belongs to Tenant (many-to-one via tenant_id FK)
- Each Tenant can have multiple Domains but exactly one primary domain

### Platform Services (apps.platform)

Platform-wide configuration, subscription management, and operational data. Models are planned for subsequent SubPhase-03 tasks.

| Entity           | Table                     | Description                                   | Status  |
| ---------------- | ------------------------- | --------------------------------------------- | ------- |
| SubscriptionPlan | platform_subscriptionplan | Tenant subscription tiers and resource limits | Planned |
| PlatformSetting  | platform_platformsetting  | Global key-value configuration store          | Planned |
| FeatureFlag      | platform_featureflag      | Feature toggle system for tenants             | Planned |
| AuditLog         | platform_auditlog         | Platform-level audit trail                    | Planned |
| BillingRecord    | platform_billingrecord    | Tenant billing and invoice records            | Planned |

**Planned Relationships:**

- Tenant has one SubscriptionPlan (FK from Tenant or via junction)
- FeatureFlag may reference SubscriptionPlan (plan-specific toggles)
- AuditLog references Tenant (which tenant triggered the event)
- BillingRecord references Tenant and SubscriptionPlan

### User Management (apps.users)

User profiles and authentication in the shared schema.

| Entity | Table     | Description                                                                 |
| ------ | --------- | --------------------------------------------------------------------------- |
| User   | auth_user | Django's built-in User model (also in TENANT_APPS for per-schema isolation) |

### Django Framework

Standard Django tables that support the framework.

| Entity      | Table               | Description                                          |
| ----------- | ------------------- | ---------------------------------------------------- |
| ContentType | django_content_type | Model registry for permissions and generic relations |
| Permission  | auth_permission     | Permission definitions                               |
| Group       | auth_group          | Permission groups                                    |
| Session     | django_session      | Server-side session storage                          |
| AdminLog    | django_admin_log    | Admin action audit trail                             |
| Migration   | django_migrations   | Applied migration tracking                           |

### Third-Party Services

Background task and scheduling tables.

| Entity           | Table                               | Description                         |
| ---------------- | ----------------------------------- | ----------------------------------- |
| PeriodicTask     | django_celery_beat_periodictask     | Celery Beat scheduled tasks         |
| CrontabSchedule  | django_celery_beat_crontabschedule  | Cron-style schedule definitions     |
| IntervalSchedule | django_celery_beat_intervalschedule | Interval-based schedule definitions |
| SolarSchedule    | django_celery_beat_solarschedule    | Solar event-based schedules         |
| ClockedSchedule  | django_celery_beat_clockedschedule  | One-time clocked schedules          |
| PeriodicTasks    | django_celery_beat_periodictasks    | Schedule change tracking            |
| TaskResult       | django_celery_results_taskresult    | Celery task execution results       |
| GroupResult      | django_celery_results_groupresult   | Celery group execution results      |
| ChordCounter     | django_celery_results_chordcounter  | Celery chord callback tracking      |

---

## Entity Relationship Summary

The public schema ERD follows this hierarchy:

    Tenant (1) ──── (*) Domain
       │
       │ (planned)
       ├──── (1) SubscriptionPlan
       ├──── (*) AuditLog
       ├──── (*) BillingRecord
       └──── (*) FeatureFlag (via plan or direct)

    PlatformSetting (standalone key-value store)

---

## Schema Counts

| Category           | Current Tables | Planned Tables |
| ------------------ | -------------- | -------------- |
| Multi-Tenancy Core | 2              | 0              |
| Platform Services  | 0              | 5              |
| Django Auth/Admin  | 6              | 0              |
| Celery Beat        | 6              | 0              |
| Celery Results     | 3              | 0              |
| Django Framework   | 2              | 0              |
| **Total**          | **19**         | **5**          |

---

## Related Documentation

- [Tenant and Domain Models](tenant-models.md) — Detailed Tenant and Domain field reference
- [App Classification](app-classification.md) — SHARED_APPS vs TENANT_APPS breakdown
- [Database Routers](database-routers.md) — How routing prevents cross-schema relations
- [Tenant Settings](tenant-settings.md) — Multi-tenancy configuration reference
- [Naming Conventions](naming-conventions.md) — Table and field naming rules
