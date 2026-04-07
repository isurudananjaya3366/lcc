"""
LankaCommerce Cloud - Base Settings

Core Django settings shared across all environments (local, production, test).
Environment-specific overrides are in their respective files:
    - local.py      → Development
    - production.py → Production
    - test.py       → Testing

Generated initially by 'django-admin startproject' using Django 5.2.11,
then restructured into a modular settings package.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/
"""

import os  # noqa: F401
from pathlib import Path

from config.env import BASE_DIR, env  # Centralized env loader


# ── Future imports (uncomment when packages are installed) ──────────────
# import dj_database_url                        # database URL parsing


# ════════════════════════════════════════════════════════════════════════
# PATH CONFIGURATION
# ════════════════════════════════════════════════════════════════════════
# BASE_DIR is imported from config.env and points to backend/


# ════════════════════════════════════════════════════════════════════════
# SECURITY — SECRET KEY / DEBUG / HOSTS
# ════════════════════════════════════════════════════════════════════════
# These use the centralized env loader from config.env.
# Defaults are defined there; override via .env or system env vars.

SECRET_KEY = env("DJANGO_SECRET_KEY")

DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS")


# ════════════════════════════════════════════════════════════════════════
# APPLICATION DEFINITION  (Task 20)
# ════════════════════════════════════════════════════════════════════════
# NOTE: INSTALLED_APPS is now defined in database.py using the
# django-tenants pattern: SHARED_APPS + unique TENANT_APPS.
#
# The lists below are kept as reference for which apps are installed,
# but they are NO LONGER used to build INSTALLED_APPS. Any new app
# must be added to SHARED_APPS or TENANT_APPS in database.py.
#
# See: backend/config/settings/database.py

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS: list[str] = [
    "django_tenants",                    # Multi-tenancy (Phase 2)
    "channels",                          # Django Channels (WebSocket)
    "rest_framework",                    # Django REST Framework
    "django_filters",                    # Query filtering
    "rest_framework_simplejwt",          # JWT authentication
    "drf_spectacular",                   # OpenAPI documentation
    "drf_spectacular_sidecar",            # Self-hosted Swagger/ReDoc assets
    "corsheaders",                       # CORS handling
    "django_celery_beat",                # Periodic task scheduling
    "django_celery_results",             # Task result storage
]

LOCAL_APPS: list[str] = [
    # Core Framework
    "apps.core",                         # Core utilities (Phase 3)
    "apps.tenants",                      # Tenant models (Phase 2)
    "apps.users",                        # User management (Phase 3)

    # Business Modules - Phase 4
    "apps.products",                     # Product catalog
    "apps.inventory",                    # Stock & warehouse
    "apps.vendors",                      # Supplier management

    # Business Modules - Phase 5
    "apps.sales",                        # Orders, invoicing, POS
    "apps.customers",                    # Customer CRM

    # Advanced Modules - Phase 6
    "apps.hr",                           # Human resources
    "apps.accounting",                   # Accounting & finance
    "apps.reports",                      # Reports & analytics

    # Platform Apps
    "apps.webstore",                     # E-commerce storefront
    "apps.integrations",                 # Third-party integrations
]

# INSTALLED_APPS is defined in database.py via SHARED_APPS + TENANT_APPS.
# The import happens via: from config.settings.database import *


# ════════════════════════════════════════════════════════════════════════
# MIDDLEWARE  (Task 21)
# ════════════════════════════════════════════════════════════════════════
# Order is critical — security first, then session, auth, etc.

MIDDLEWARE = [
    # ── Task 08-09 (SubPhase-06): Tenant middleware — MUST be first ──
    # Resolves the active tenant from the request hostname, activates the
    # tenant's PostgreSQL schema, and injects request.tenant /
    # request.schema_name before any other middleware runs.
    # Must precede SecurityMiddleware so all downstream code runs inside
    # the correct schema context.
    "apps.tenants.middleware.LCCTenantMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # "django_tenants.middleware.main.TenantMainMiddleware",   # replaced above
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # ── LankaCommerce custom middleware (Phase 3) ──
    "apps.core.middleware.request_logging.RequestLoggingMiddleware",
    "apps.core.middleware.security.SecurityHeadersMiddleware",
    "apps.core.middleware.sentry.SentryContextMiddleware",
    "apps.core.middleware.timezone.TimezoneMiddleware",
    # "apps.core.middleware.rate_limiting.RateLimitingMiddleware",  # Enable when needed
    # "apps.platform.middleware.feature_flags.FeatureFlagMiddleware",  # Phase 3
]


# ════════════════════════════════════════════════════════════════════════
# URL CONFIGURATION
# ════════════════════════════════════════════════════════════════════════

ROOT_URLCONF = "config.urls"


# ════════════════════════════════════════════════════════════════════════
# TEMPLATES  (Task 22)
# ════════════════════════════════════════════════════════════════════════

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ════════════════════════════════════════════════════════════════════════
# WSGI / ASGI
# ════════════════════════════════════════════════════════════════════════

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ════════════════════════════════════════════════════════════════════════
# DJANGO REST FRAMEWORK  (Task 36)
# ════════════════════════════════════════════════════════════════════════

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "EXCEPTION_HANDLER": "apps.core.exceptions.handlers.custom_exception_handler",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
}


# ════════════════════════════════════════════════════════════════════════
# CORS  (Task 39)
# ════════════════════════════════════════════════════════════════════════
# Defaults: restrictive.  local.py opens up for development.

CORS_ALLOW_ALL_ORIGINS = False  # Overridden in local.py
CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS")
CORS_ALLOWED_ORIGINS: list[str] = env.list("CORS_ALLOWED_ORIGINS")


# ════════════════════════════════════════════════════════════════════════
# SIMPLE JWT  (Task 42)
# ════════════════════════════════════════════════════════════════════════

from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES"),
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS"),
    ),
    "ROTATE_REFRESH_TOKENS": env.bool("JWT_ROTATE_REFRESH_TOKENS"),
    "BLACKLIST_AFTER_ROTATION": env.bool("JWT_BLACKLIST_AFTER_ROTATION"),
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}


# ════════════════════════════════════════════════════════════════════════
# API DOCUMENTATION — drf-spectacular  (SP11)
# ════════════════════════════════════════════════════════════════════════
from config.settings.api_docs import *  # noqa: E402, F401, F403


# ════════════════════════════════════════════════════════════════════════
# CELERY  (Tasks 44-46)
# ════════════════════════════════════════════════════════════════════════

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = env("TIME_ZONE")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Task execution safeguards
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60        # 30 minutes hard kill
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60   # 25 minutes graceful timeout

# ── Retry Policies (SP08 Tasks 67-73) ──────────────────────────────
CELERY_TASK_DEFAULT_RETRY_DELAY = 60       # 60 seconds before first retry
CELERY_TASK_MAX_RETRIES = 3                # Max 3 retries per task
CELERY_TASK_RETRY_BACKOFF = True           # Exponential backoff
CELERY_TASK_RETRY_BACKOFF_MAX = 600        # Max 10 minutes between retries
CELERY_TASK_RETRY_JITTER = True            # Add jitter to avoid thundering herd

# ── Task Queues (SP08 Tasks 74-78) ─────────────────────────────────
from kombu import Exchange, Queue  # noqa: E402

default_exchange = Exchange("default", type="direct")

CELERY_TASK_QUEUES = (
    Queue("high_priority", default_exchange, routing_key="high"),
    Queue("default", default_exchange, routing_key="default"),
    Queue("low_priority", default_exchange, routing_key="low"),
)

CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_DEFAULT_EXCHANGE = "default"
CELERY_TASK_DEFAULT_ROUTING_KEY = "default"

CELERY_TASK_ROUTES = {
    "apps.core.tasks.email_tasks.*": {"queue": "default"},
    "apps.core.tasks.notification_tasks.*": {"queue": "default"},
    "apps.core.tasks.report_tasks.*": {"queue": "low_priority"},
    "apps.core.tasks.scheduled_tasks.*": {"queue": "low_priority"},
    "apps.inventory.alerts.tasks.*": {"queue": "default"},
}

# ── Beat Schedule (periodic tasks) ─────────────────────────────────
from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    "daily-sales-report": {
        "task": "apps.core.tasks.scheduled_tasks.daily_sales_report_task",
        "schedule": crontab(hour=6, minute=0),
    },
    "check-low-stock": {
        "task": "apps.core.tasks.scheduled_tasks.check_low_stock_task",
        "schedule": crontab(hour="*/4", minute=0),
    },
    "cleanup-sessions": {
        "task": "apps.core.tasks.scheduled_tasks.cleanup_old_sessions_task",
        "schedule": crontab(hour=0, minute=0),
    },
    "cleanup-tokens": {
        "task": "apps.core.tasks.scheduled_tasks.cleanup_expired_tokens_task",
        "schedule": crontab(hour=2, minute=0),
    },
    # ── SP10 Stock Alert Tasks (Task 43) ────────────────────────
    "run-stock-monitoring": {
        "task": "apps.inventory.alerts.tasks.stock_monitor.run_stock_monitoring",
        "schedule": crontab(minute=0),  # Every hour
    },
    "auto-resolve-alerts": {
        "task": "apps.inventory.alerts.tasks.alert_resolution.auto_resolve_alerts_task",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "check-expired-snoozes": {
        "task": "apps.inventory.alerts.tasks.alert_resolution.check_expired_snoozes",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "cleanup-monitoring-logs": {
        "task": "apps.inventory.alerts.tasks.alert_resolution.cleanup_old_monitoring_logs",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    # ── SP04 Leave Management Accrual Tasks ─────────────────────
    "year-end-leave-accrual": {
        "task": "apps.leave.tasks.accrual_tasks.year_end_accrual",
        "schedule": crontab(month_of_year=12, day_of_month=31, hour=23, minute=59),
    },
    "daily-leave-expiry-check": {
        "task": "apps.leave.tasks.accrual_tasks.daily_leave_expiry_check",
        "schedule": crontab(hour=0, minute=30),
    },
    # ── SP06 Payroll Period Auto-Creation ────────────────────────
    "auto-create-payroll-periods": {
        "task": "payroll.auto_create_payroll_periods",
        "schedule": crontab(hour=2, minute=30),  # Daily at 2:30 AM
        "options": {"expires": 3600},
    },
}


# ════════════════════════════════════════════════════════════════════════
# CHANNEL LAYERS  (Task 70)
# ════════════════════════════════════════════════════════════════════════
# Redis-backed channel layer for WebSocket message routing.
# Each environment file may override with different backends.
# Redis database allocation: 0=Celery, 1=Cache, 2=Channels, 15=Testing

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL")],
        },
    },
}


# ════════════════════════════════════════════════════════════════════════
# CACHING — Redis  (SP09)
# ════════════════════════════════════════════════════════════════════════
from config.settings.cache import *  # noqa: E402, F401, F403

# ════════════════════════════════════════════════════════════════════════
# FILE STORAGE — Local / S3  (SP10)
# ════════════════════════════════════════════════════════════════════════
from config.settings.storage import *  # noqa: E402, F401, F403  (SP10)


# ════════════════════════════════════════════════════════════════════════
# DATABASE  (Task 23 — Configured in Phase 2)
# ════════════════════════════════════════════════════════════════════════
# Database credentials are NEVER stored here.
# Each environment file (local.py, production.py, test.py) overrides
# DATABASES with its own connection configuration.
#
# Multi-tenancy settings (TENANT_MODEL, TENANT_DOMAIN_MODEL,
# DATABASE_ROUTERS) are centralized in config/settings/database.py.

from config.settings.database import *  # noqa: E402, F401, F403

DATABASES: dict = {}


# ════════════════════════════════════════════════════════════════════════
# AUTHENTICATION  (Task 24)
# ════════════════════════════════════════════════════════════════════════

# Custom user model — must be set before first migration.
# PlatformUser is the platform-level auth model in the public schema.
# Tenant-scoped users will be handled separately in the users app.
AUTH_USER_MODEL = "platform.PlatformUser"

# TENANT_MODEL and TENANT_DOMAIN_MODEL are imported from
# config/settings/database.py via the wildcard import above.

# Authentication backends — will be extended for JWT, social auth.
# EmailBackend enables authentication using email + password, which
# aligns with PlatformUser's USERNAME_FIELD = "email".
AUTHENTICATION_BACKENDS = [
    "apps.platform.backends.EmailBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ════════════════════════════════════════════════════════════════════════
# INTERNATIONALIZATION & LOCALIZATION  (Task 25)
# ════════════════════════════════════════════════════════════════════════
# Sri Lanka-first: Asia/Colombo (UTC+5:30), English primary, Sinhala & Tamil

LANGUAGE_CODE = "en"

TIME_ZONE = "Asia/Colombo"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Supported languages: English (primary), Sinhala, Tamil
LANGUAGES = [
    ("en", "English"),
    ("si", "Sinhala"),
    ("ta", "Tamil"),
]

# Translation file location
LOCALE_PATHS = [
    BASE_DIR / "locale",
]


# ════════════════════════════════════════════════════════════════════════
# STATIC FILES  (Task 26)
# ════════════════════════════════════════════════════════════════════════
# STATIC_URL and STATIC_ROOT are defined in config/settings/storage.py
# and imported via ``from config.settings.storage import *`` above.

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# STORAGES is defined in config/settings/storage.py (local or S3 mode).


# ════════════════════════════════════════════════════════════════════════
# MEDIA FILES  (Task 27)
# ════════════════════════════════════════════════════════════════════════
# MEDIA_URL and MEDIA_ROOT are defined in config/settings/storage.py.
# User-uploaded content (product images, documents, avatars, logos).
# Development: local filesystem.  Production: S3/cloud (overridden).

# Upload size limits (10 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024    # 10 MB


# ════════════════════════════════════════════════════════════════════════
# SECURITY DEFAULTS  (Task 28)
# ════════════════════════════════════════════════════════════════════════
# Conservative defaults for base.  local.py relaxes; production.py hardens.

# ── CSRF ───────────────────────────────────────────────────────────────
CSRF_COOKIE_SECURE = False           # True in production
CSRF_COOKIE_HTTPONLY = False          # True in production
CSRF_TRUSTED_ORIGINS: list[str] = [] # Overridden per environment

# ── Session ────────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = False        # True in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1209600         # 2 weeks (seconds)

# ── Security Headers ──────────────────────────────────────────────────
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# ── HTTPS / HSTS (disabled in base; enabled in production.py) ─────────
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False


# ════════════════════════════════════════════════════════════════════════
# DEFAULT PRIMARY KEY
# ════════════════════════════════════════════════════════════════════════

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ════════════════════════════════════════════════════════════════════════
# TENANT SUBDOMAIN CONFIGURATION  (SubPhase-06 Group-B Task 16)
# ════════════════════════════════════════════════════════════════════════
# Controls how LCCTenantMiddleware resolves tenant subdomains from the
# incoming request's Host header.
#
# TENANT_BASE_DOMAIN: The root domain shared by all tenants.
#   Production example: "lcc.example.com"
#   → acme.lcc.example.com  resolves to tenant "acme"
#   Development default: "localhost"
#   → acme.localhost resolves to tenant "acme"
#
# Override in local.py, staging.py, or production.py as needed.
# Also configurable via the TENANT_BASE_DOMAIN environment variable.

TENANT_BASE_DOMAIN: str = env("TENANT_BASE_DOMAIN", default="localhost")

# Subdomains reserved for platform/infrastructure use.
# Requests with these subdomains are never resolved to a tenant.
TENANT_RESERVED_SUBDOMAINS: list[str] = [
    "www",
    "api",
    "admin",
    "app",
    "static",
    "media",
    "mail",
    "smtp",
    "cdn",
    "docs",
    "help",
    "support",
    "status",
]

# Task 21: Development domains that bypass strict subdomain matching.
# Requests from these hosts use .localhost subdomain parsing rules.
# Port numbers are always stripped before matching (Task 22).
TENANT_DEV_DOMAINS: list[str] = [
    "localhost",
    "127.0.0.1",
]

# Task 24: Cache time-to-live for subdomain → Tenant lookups (in seconds).
# 300 = 5 minutes. Increase in production to reduce DB round-trips.
# Task 25: Cache is invalidated immediately on Domain post_save/post_delete.
TENANT_DOMAIN_CACHE_TTL: int = 300

# ---------------------------------------------------------------------------
# Header-Based Tenant Resolution (Group-D, Tasks 43-48)
# ---------------------------------------------------------------------------
# Used by HeaderResolver for API-only traffic where the client
# explicitly identifies the tenant via an HTTP header.
#
# TENANT_HEADER_NAME: Primary header carrying the tenant ID (UUID/PK).
#   Clients send: X-Tenant-ID: <tenant-pk-or-uuid>
#
# TENANT_SLUG_HEADER: Alternative header carrying the tenant slug.
#   Clients send: X-Tenant-Slug: <schema-name>
#   Used as a fallback when TENANT_HEADER_NAME is not present.
#
# TENANT_HEADER_PATHS: URL path prefixes where header resolution is active.
#   Only requests whose path starts with one of these prefixes will
#   have their tenant resolved via header. All other paths fall through
#   to subdomain or custom domain resolution.
#
# Security: Headers alone are NOT authentication. They only select the
# target tenant schema. API authentication (JWT, API key, etc.) must
# still be enforced by the DRF permission/authentication classes.

TENANT_HEADER_NAME: str = env("TENANT_HEADER_NAME", default="X-Tenant-ID")

TENANT_SLUG_HEADER: str = env("TENANT_SLUG_HEADER", default="X-Tenant-Slug")

TENANT_HEADER_PATHS: list[str] = [
    "/api/",
    "/mobile/",
    "/webhook/",
]

# ---------------------------------------------------------------------------
# Error Handling & Fallback (Group-E, Tasks 55-61)
# ---------------------------------------------------------------------------
# PUBLIC_SCHEMA_PATHS: URL path prefixes that always use the public schema.
# These paths bypass tenant resolution entirely, allowing access to
# shared endpoints regardless of the tenant context. Use cases:
# - Authentication (login, token refresh) before tenant is known.
# - Tenant registration (new tenant sign-up flow).
# - Subscription plan listing (public pricing page).
# - Health checks (infrastructure monitoring).
# - Prometheus metrics (observability).
#
# Security: Keep this list minimal. Every public path is accessible
# without tenant context, which means no tenant-level access control.

PUBLIC_SCHEMA_PATHS: list[str] = [
    "/api/v1/auth/",
    "/api/v1/register/",
    "/api/v1/plans/",
    "/health/",
    "/metrics/",
]

# Template paths for tenant error pages (overridable per environment).
TENANT_404_TEMPLATE: str = "tenants/404_tenant_not_found.html"
TENANT_SUSPENDED_TEMPLATE: str = "tenants/suspended.html"
TENANT_EXPIRED_TEMPLATE: str = "tenants/expired.html"

# Grace period (in days) for expired subscriptions (Task 63).
# After expiration, tenants have this many days before full revocation.
TENANT_GRACE_PERIOD_DAYS: int = 7
