# Backend Applications

> Guide to the Django application modules in LankaCommerce Cloud.

**Navigation:** [Docs Index](../index.md) · [Backend README](../../backend/README.md) · [Models](models.md) · [API](api.md)

---

## Overview

The backend is organized as a collection of **Django apps** inside `backend/apps/`. Each app encapsulates a specific business domain with its own models, views, serializers, URLs, and tests. Shared utilities live in `apps/core/`.

Apps are implemented in phases, following the project roadmap:

| Phase    | Apps                       | Status                                       |
| -------- | -------------------------- | -------------------------------------------- |
| Phase 2  | tenants                    | Multi-tenancy foundation _(scaffolded)_      |
| Phase 3  | core, users                | Framework and authentication _(in progress)_ |
| Phase 4  | products, inventory, sales | ERP core modules _(scaffolded)_              |
| Phase 5  | customers, vendors         | Relationship management _(scaffolded)_       |
| Phase 6  | hr, accounting, reports    | Advanced modules _(scaffolded)_              |
| Platform | webstore, integrations     | E-commerce and third-party _(scaffolded)_    |

---

## App Directory

### core — Core Framework

The most developed app, providing shared infrastructure for all other modules.

**Responsibilities:**

- Health check endpoint for monitoring and readiness probes
- Base model classes and mixins (UUID primary keys, timestamps, soft delete)
- Management commands for database readiness, superuser creation, and demo data
- Template tags and shared utilities

**Key Components:**

- Health check view at `/health/`
- `wait_for_db` management command — ensures database is available before starting
- `create_default_superuser` — creates admin user from environment variables
- `seed_demo_data` — populates development database with sample data

---

### tenants — Multi-Tenancy

Manages tenant (business/store) isolation using PostgreSQL schema-based multi-tenancy via django-tenants.

**Responsibilities:**

- Tenant registration and lifecycle management
- Domain routing and tenant resolution
- Tenant-specific settings and configuration
- Billing and subscription management

**Planned Models:** Tenant, Domain, TenantSettings, TenantBilling

**Key Directories:**

- `middleware/` — Tenant resolution middleware
- `management/` — Tenant management commands
- `utils/` — Tenant utility functions

---

### users — User Management

Handles authentication, user profiles, and access control.

**Responsibilities:**

- Custom user model with email-based authentication
- User registration, login, and password management
- User profiles and preferences
- Login history and session tracking
- Phone number validation for Sri Lankan format (+94)

**Planned Models:** CustomUser, UserProfile, UserPreferences, LoginHistory

**Key Directories:**

- `api/` — Serializers, viewsets, and URL routing for user endpoints
- `managers/` — Custom user model managers
- `signals/` — Post-save signals for profile creation

---

### products — Product Management

Manages the product catalog, categories, and pricing.

**Responsibilities:**

- Product CRUD operations
- Category hierarchies and organization
- Pricing rules, discounts, and tax handling
- Product images and media

---

### inventory — Inventory Management

Tracks stock levels, warehouse locations, and inventory movements.

**Responsibilities:**

- Stock tracking and quantity management
- Warehouse and location management
- Stock transfer and adjustment records
- Low-stock alerts and reorder points

---

### sales — Sales Management

Handles POS transactions, orders, and receipts.

**Responsibilities:**

- Sales order creation and processing
- POS terminal transactions
- Receipt generation and printing
- Payment recording and reconciliation

---

### customers — Customer Management

Manages customer records and relationships.

**Responsibilities:**

- Customer registration and profiles
- Purchase history and loyalty tracking
- Customer segmentation and groups

---

### vendors — Vendor Management

Manages supplier relationships and procurement.

**Responsibilities:**

- Vendor registration and profiles
- Purchase orders and procurement workflows
- Vendor performance tracking

---

### hr — Human Resources

Handles employee management and payroll.

**Responsibilities:**

- Employee records and profiles
- Attendance tracking and leave management
- Payroll calculations and salary processing

---

### accounting — Accounting and Finance

Manages financial operations and reporting.

**Responsibilities:**

- Chart of accounts and journal entries
- Invoice generation and payment tracking
- Tax calculations and compliance
- Financial period management

---

### reports — Reports and Analytics

Provides analytics dashboards and data exports.

**Responsibilities:**

- Sales analytics and trend reports
- Inventory status reports
- Financial summaries and dashboards
- Data export in CSV, PDF, and Excel formats

---

### webstore — E-commerce Webstore

Powers the customer-facing online store.

**Responsibilities:**

- Product catalog browsing and search
- Shopping cart and checkout flow
- Order management and tracking
- Customer account self-service

---

### integrations — Third-Party Integrations

Connects to external services and local Sri Lankan platforms.

**Responsibilities:**

- PayHere payment gateway integration
- Courier service APIs (Domex, Koombiyo)
- SMS notification services
- Email delivery services

---

## App Structure Convention

Each app follows a consistent internal structure:

```
apps/<app_name>/
├── __init__.py
├── apps.py           # App configuration and metadata
├── models.py         # Database models (or models/ package)
├── admin.py          # Django admin registration
├── views.py          # View functions or viewsets (or api/ package)
├── serializers.py    # DRF serializers (or api/serializers.py)
├── urls.py           # URL patterns (or api/urls.py)
├── tasks.py          # Celery async tasks
├── signals.py        # Django signals
├── managers.py       # Custom model managers
├── permissions.py    # Custom DRF permissions
├── filters.py        # Django filter backends
├── utils.py          # App-specific utilities
└── tests/            # App-level unit tests
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    └── test_serializers.py
```

> Not all files are required in every app. Create them as needed during implementation.

---

## Configuration

Apps are registered in `config/settings/base.py` as `LOCAL_APPS`:

```python
LOCAL_APPS = [
    "apps.tenants",
    "apps.core",
    "apps.users",
    "apps.products",
    "apps.inventory",
    "apps.sales",
    "apps.customers",
    "apps.vendors",
    "apps.hr",
    "apps.accounting",
    "apps.reports",
    "apps.webstore",
    "apps.integrations",
]
```

When multi-tenancy is enabled (Phase 2), apps will be split into:

- **SHARED_APPS** — Tenant management, admin, auth (shared across all schemas)
- **TENANT_APPS** — Business modules (isolated per tenant schema)

---

## Related Documentation

- [Backend README](../../backend/README.md) — Setup and development guide
- [Models Documentation](models.md) — Base models and conventions
- [API Documentation](api.md) — API structure and conventions
- [Docs Index](../index.md) — Full documentation hub
