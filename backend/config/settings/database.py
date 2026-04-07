"""
LankaCommerce Cloud - Database Configuration

Centralized database settings for django-tenants multi-tenancy.

This module defines:
    - TENANT_MODEL and TENANT_DOMAIN_MODEL references
    - DATABASE_ROUTERS for schema-aware synchronization
    - Domain and schema settings (naming, auto-create/drop)
    - Multi-tenancy related settings (schema limits, cloning, etc.)

Imported by base.py to ensure these settings are available
across all environments (local, production, test).

The actual DATABASES dict (connection credentials, engine, host, port)
remains in each environment file (local.py, production.py, test.py)
because connection details differ per environment.
"""

from config.env import env  # Centralized env loader


# ════════════════════════════════════════════════════════════════════════
# TENANT MODEL SETTINGS
# ════════════════════════════════════════════════════════════════════════
# These point to the models that implement TenantMixin and DomainMixin
# from django-tenants. The models live in apps/tenants/models.py.
#
# TENANT_MODEL: The model that represents a tenant (organization).
#   Each tenant maps to a PostgreSQL schema.
#
# TENANT_DOMAIN_MODEL: The model that maps domains/subdomains to tenants.
#   django-tenants uses this to resolve the current tenant from the
#   incoming request hostname.

TENANT_MODEL = "tenants.Tenant"

TENANT_DOMAIN_MODEL = "tenants.Domain"


# ════════════════════════════════════════════════════════════════════════
# DATABASE ROUTERS
# ════════════════════════════════════════════════════════════════════════
# Routers are evaluated in order. The first non-None return value wins.
#
# LCCDatabaseRouter (SubPhase-07, Task 04-05):
#   Custom router extending django-tenants' TenantSyncRouter.
#   Inherits allow_migrate (migration routing to correct schema) and
#   adds allow_relation (cross-schema relation prevention).
#
# django_tenants.routers.TenantSyncRouter:
#   Required by django-tenants AppConfig.ready() validation.
#   django-tenants performs a string-based check to ensure this router
#   is present in DATABASE_ROUTERS. LCCDatabaseRouter extends it, so
#   the actual routing logic is handled by our custom class first.
#   TenantSyncRouter is listed second as a framework requirement.
#
# Legacy reference (pre-SubPhase-07):
#   1. TenantRouter (allow_relation only)
#   2. TenantSyncRouter (allow_migrate only)

DATABASE_ROUTERS = [
    "apps.tenants.routers.LCCDatabaseRouter",
    "django_tenants.routers.TenantSyncRouter",
]


# ════════════════════════════════════════════════════════════════════════
# MULTI-TENANCY PERFORMANCE SETTINGS
# ════════════════════════════════════════════════════════════════════════
# TENANT_LIMIT_SET_CALLS: When True, django-tenants reduces the number
#   of SET search_path calls to PostgreSQL, improving performance.
#   The search_path is only set when switching tenants, not on every query.

TENANT_LIMIT_SET_CALLS = True


# ════════════════════════════════════════════════════════════════════════
# PUBLIC SCHEMA SETTINGS
# ════════════════════════════════════════════════════════════════════════
# PUBLIC_SCHEMA_NAME: The PostgreSQL schema name used for shared/public
#   data. Default is 'public'. All SHARED_APPS tables live here.
#
# SHOW_PUBLIC_IF_NO_TENANT_FOUND: When False, a 404 is returned if the
#   request hostname does not match any tenant domain. When True, the
#   public schema is used as fallback.

PUBLIC_SCHEMA_NAME = "public"

SHOW_PUBLIC_IF_NO_TENANT_FOUND = False


# ════════════════════════════════════════════════════════════════════════
# TENANT DOMAIN SETTINGS
# ════════════════════════════════════════════════════════════════════════
# How domains map to tenants in LankaCommerce Cloud:
#
# Domain-based routing (using TenantMainMiddleware):
#   - Public tenant:  lankacommerce.lk     → schema: public
#   - Tenant 1:       acme.lankacommerce.lk → schema: tenant_acme
#   - Tenant 2:       best.lankacommerce.lk → schema: tenant_best
#
# Each tenant can have multiple domains. One domain must be marked
# as is_primary=True. The Domain model (TENANT_DOMAIN_MODEL) stores
# the mapping between hostnames and tenant schemas.
#
# In development, localhost subdomains (e.g. acme.localhost) are used.
# In production, wildcard DNS (*.lankacommerce.lk) routes all subdomains
# to the same server, where TenantMainMiddleware resolves the tenant.
#
# BASE_TENANT_DOMAIN: The base domain used for constructing tenant URLs.
#   This is NOT a django-tenants setting — it's a LankaCommerce custom
#   setting used by our tenant provisioning logic to auto-generate
#   subdomain URLs (e.g. <slug>.BASE_TENANT_DOMAIN).

BASE_TENANT_DOMAIN = env(
    "BASE_TENANT_DOMAIN",
    default="localhost",
)


# ════════════════════════════════════════════════════════════════════════
# TENANT SCHEMA SETTINGS
# ════════════════════════════════════════════════════════════════════════
# Schema naming convention: tenant_<slug>
#   - Public tenant schema: 'public' (set by PUBLIC_SCHEMA_NAME above)
#   - Tenant schemas: 'tenant_acme', 'tenant_best', etc.
#
# The schema_name field on the Tenant model stores the PostgreSQL schema
# name. Our Tenant model will enforce the 'tenant_' prefix via validation
# (implemented in Phase 2 SubPhase 3 when models are built).
#
# TENANT_SCHEMA_PREFIX: Custom LankaCommerce setting used by our tenant
#   provisioning code to generate schema names: {prefix}{slug}.
#   Not a django-tenants built-in.

TENANT_SCHEMA_PREFIX = "tenant_"

# AUTO_CREATE_SCHEMA: When True, saving a new Tenant model instance
#   automatically creates the corresponding PostgreSQL schema and runs
#   all TENANT_APPS migrations in it. This is the standard flow for
#   tenant provisioning.
#   Default is True. Can be overridden per-instance via the model's
#   auto_create_schema attribute.

AUTO_CREATE_SCHEMA = True

# AUTO_DROP_SCHEMA: When True, deleting a Tenant model instance
#   automatically drops the PostgreSQL schema and ALL its data.
#   SAFETY: This MUST remain False in production. Schema deletion
#   should only happen through explicit admin action with proper
#   backup procedures. Use manage.py delete_tenant for controlled removal.

AUTO_DROP_SCHEMA = False

# TENANT_CREATION_FAKES_MIGRATIONS: When True and TENANT_BASE_SCHEMA is
#   set, new tenant schemas are created by cloning the base schema
#   instead of running migrations from scratch. This dramatically speeds
#   up tenant creation for large migration sets.
#   Default is False — migrations run normally for each new tenant.

TENANT_CREATION_FAKES_MIGRATIONS = False

# TENANT_BASE_SCHEMA: The name of a pre-migrated 'template' schema
#   that new tenants are cloned from (when TENANT_CREATION_FAKES_MIGRATIONS
#   is True). Set to None to disable cloning.
#   To set up: python manage.py migrate_schemas --schema=template_tenant

TENANT_BASE_SCHEMA = None


# ════════════════════════════════════════════════════════════════════════
# TENANT-AWARE FILE STORAGE
# ════════════════════════════════════════════════════════════════════════
# Media files (user uploads) are partitioned per tenant to ensure
# data isolation. Each tenant's files are stored in a subdirectory
# named after their schema_name.
#
# Storage layout:
#   MEDIA_ROOT/
#     public/              ← Public tenant media
#     tenant_acme/         ← Acme Corp media
#     tenant_best/         ← Best Trading media
#
# django-tenants provides TenantFileSystemStorage which automatically
# prepends the current tenant's schema_name to media paths.
#
# MULTITENANT_RELATIVE_MEDIA_ROOT: Template for tenant media subdirectory.
#   '%s' is replaced with the tenant's schema_name at runtime.
#
# Static files (CSS, JS) are NOT tenant-specific — they are served
# globally by WhiteNoise from STATIC_ROOT. The STORAGES["staticfiles"]
# backend remains whitenoise.storage.CompressedManifestStaticFilesStorage
# in base.py. Only media files need tenant partitioning.

MULTITENANT_RELATIVE_MEDIA_ROOT = "%s"


# ════════════════════════════════════════════════════════════════════════
# SHARED & TENANT APP CLASSIFICATION
# ════════════════════════════════════════════════════════════════════════
#
# SHARED_APPS CRITERIA (how to decide if an app belongs here):
# ────────────────────────────────────────────────────────────
# An app should be in SHARED_APPS if any of the following apply:
#   1. It manages multi-tenancy infrastructure (django_tenants, tenants)
#   2. It provides framework plumbing needed globally (contenttypes,
#      sessions, messages, staticfiles)
#   3. It provides a single administrative interface (admin)
#   4. It manages cross-tenant authentication/authorization (auth)
#   5. It provides tenant-agnostic middleware or URL routing (corsheaders)
#   6. It provides API infrastructure used across all tenants (DRF, etc.)
#
# An app should NOT be in SHARED_APPS if:
#   - Its data is specific to a single tenant (products, sales, inventory)
#   - It would cause data leakage if tables were shared across tenants
#
# ORDERING RULES:
# ────────────────
#   1. django_tenants MUST be first — it registers signals and middleware
#      hooks that other apps depend on during startup.
#   2. Django's contenttypes MUST appear in SHARED_APPS because
#      django-tenants uses it for content type resolution in the public
#      schema. It also appears in TENANT_APPS for per-tenant content
#      type isolation (required by django-tenants).
#   3. Django's auth MUST appear in SHARED_APPS for the public schema
#      user management. It also appears in TENANT_APPS for per-tenant
#      user isolation (LankaCommerce uses per-tenant users).
#   4. apps.tenants stores Tenant and Domain models — these MUST be in
#      the public schema so django-tenants can look up tenants before
#      routing to a tenant schema.
#   5. Third-party apps that are tenant-agnostic infrastructure
#      (corsheaders, rest_framework, etc.) belong in SHARED_APPS.
#      Their configuration applies globally, not per-tenant.

SHARED_APPS: list[str] = [
    # ── Multi-Tenancy Core (MUST be first) ──────────────────────────
    "django_tenants",                    # Schema management & middleware
    # ── Django Framework (public schema) ────────────────────────────
    "django.contrib.admin",              # Admin interface (shared, uses schema switching)
    "django.contrib.auth",               # Authentication (also in TENANT_APPS for per-tenant users)
    "django.contrib.contenttypes",       # Content types (also in TENANT_APPS for isolation)
    "django.contrib.sessions",           # Session storage (global, not per-tenant)
    "django.contrib.messages",           # Flash messages framework
    "django.contrib.staticfiles",        # Static file serving (global via WhiteNoise)
    # ── LankaCommerce Shared Apps ───────────────────────────────────
    "apps.tenants",                      # Tenant & Domain models (must be in public schema)
    "apps.core",                         # Core utilities, base models, shared helpers
    "apps.users",                        # User profiles & management (shared user registry)
    "apps.platform",                     # Platform services (plans, settings, flags, audit, billing)
    # ── Third-Party Infrastructure (tenant-agnostic) ────────────────
    "rest_framework",                    # DRF — API framework (config is global)
    "django_filters",                    # Query filtering (config is global)
    "rest_framework_simplejwt",          # JWT auth (token handling is global)
    "drf_spectacular",                   # OpenAPI docs (schema generation is global)
    "drf_spectacular_sidecar",            # Self-hosted Swagger/ReDoc assets
    "corsheaders",                       # CORS handling (middleware is global)
    "channels",                          # Django Channels / WebSocket (global routing)
    "django_celery_beat",                # Celery beat scheduler (shared task schedule)
    "django_celery_results",             # Celery results backend (shared result storage)
    "mptt",                              # MPTT — Hierarchical tree structure for categories
]

# TENANT_APPS CRITERIA (how to decide if an app belongs here):
# ────────────────────────────────────────────────────────────
# An app should be in TENANT_APPS if any of the following apply:
#   1. Its database tables store business data that must be isolated
#      per tenant (products, sales, inventory, customers, etc.)
#   2. It provides per-tenant content types or permissions (contenttypes,
#      auth) — these also appear in SHARED_APPS for the public schema
#   3. Its models reference tenant-specific foreign keys
#   4. Data leakage would occur if tables were shared across tenants
#
# An app should NOT be in TENANT_APPS if:
#   - It only provides middleware, URL routing, or config (corsheaders)
#   - It manages multi-tenancy infrastructure itself (django_tenants)
#   - Its tables must exist in the public schema for routing (tenants)
#
# ORDERING RULES:
# ────────────────
#   1. django.contrib.contenttypes MUST be first — django-tenants
#      requires per-tenant content type tables for GenericForeignKey
#      and permission resolution within each tenant schema.
#   2. django.contrib.auth MUST follow contenttypes — the auth
#      Permission model has a FK to ContentType, so contenttypes
#      tables must exist first. Per-tenant auth enables isolated
#      user accounts, groups, and permissions per tenant.
#   3. LankaCommerce business modules follow in dependency order:
#      core utilities first, then domain modules.

TENANT_APPS: list[str] = [
    # ── Django Framework (per-tenant isolation) ─────────────────────
    "django.contrib.contenttypes",       # Per-tenant content types (MUST be first)
    "django.contrib.auth",               # Per-tenant users, groups, permissions
    # ── LankaCommerce Business Modules (per-tenant data) ────────────
    "apps.products",                     # Product catalog — tenant-specific SKUs & pricing
    "apps.products.pricing",             # Product pricing — price types, history & tax config
    "apps.attributes",                   # Product attributes — tenant-specific attribute definitions
    "apps.inventory",                    # Stock & warehouse — tenant-specific stock levels
    "apps.vendors",                      # Supplier management — tenant-specific vendors
    "apps.purchases",                    # Purchase orders — tenant-specific procurement
    "apps.sales",                        # Orders, invoicing, POS — tenant-specific transactions
    "apps.customers",                    # Customer CRM — tenant-specific customer records
    "apps.orders",                       # Order management — tenant-specific order records
    "apps.hr",                           # Human resources — tenant-specific employees & payroll
    "apps.accounting",                   # Accounting & finance — tenant-specific ledgers
    "apps.reports",                      # Reports & analytics — tenant-specific report data
    "apps.webstore",                     # E-commerce storefront — tenant-specific store content
    "apps.integrations",                 # Third-party integrations — tenant-specific API keys
    "apps.pos",                          # Point of Sale — tenant-specific POS terminals & sessions
    "apps.quotes",                       # Quote management — tenant-specific quotations
    "apps.invoices",                     # Invoice system — tenant-specific invoices & credit/debit notes
    "apps.payments",                     # Payment recording — tenant-specific payment transactions
    "apps.credit",                       # Credit & loyalty — tenant-specific credit accounts & loyalty
    "apps.vendor_bills",                 # Vendor bills & payments — tenant-specific bill management
    "apps.employees",                    # Employee management — tenant-specific employee records
    "apps.organization",                 # Organization structure — departments & designations
    "apps.attendance",                   # Attendance tracking — shifts, schedules, clock in/out
    "apps.leave",                        # Leave management — leave types, policies, applications
    "apps.payroll",                      # Payroll — salary components, templates, EPF/ETF/PAYE
    "apps.payslip",                      # Payslip generation — PDF payslips, distribution, tracking
]


# ════════════════════════════════════════════════════════════════════════
# INSTALLED_APPS — Combined App Registry
# ════════════════════════════════════════════════════════════════════════
# django-tenants requires INSTALLED_APPS to be built from SHARED_APPS
# and TENANT_APPS so it knows which tables belong in the public schema
# vs. tenant schemas.
#
# The combination rule ensures:
#   1. All SHARED_APPS appear first (django_tenants at index 0)
#   2. TENANT_APPS that are NOT already in SHARED_APPS are appended
#   3. No duplicates — apps like contenttypes and auth appear in both
#      SHARED_APPS and TENANT_APPS, but only once in INSTALLED_APPS
#
# This replaces the previous DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# pattern that was defined in base.py.

INSTALLED_APPS: list[str] = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]
