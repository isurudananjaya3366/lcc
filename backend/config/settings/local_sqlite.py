"""
LankaCommerce Cloud - Local SQLite Development Settings

Lightweight settings for local development WITHOUT Docker or PostgreSQL.
Uses SQLite for quick iteration, model development, and admin browsing.

Limitations (vs. full PostgreSQL/Docker setup):
    - No multi-tenancy (django-tenants disabled — requires PostgreSQL schemas)
    - No tenant middleware — all requests serve the "default" database
    - No Celery/Redis — background tasks run synchronously
    - No PgBouncer connection pooling
    - JSONField lookups have limited support in SQLite

Usage:
    # Option 1: Set environment variable
    set DJANGO_SETTINGS_MODULE=config.settings.local_sqlite
    python manage.py runserver

    # Option 2: Pass directly
    python manage.py runserver --settings=config.settings.local_sqlite

    # Run migrations first
    python manage.py migrate --settings=config.settings.local_sqlite

    # Create superuser
    python manage.py createsuperuser --settings=config.settings.local_sqlite

Migration to PostgreSQL:
    When ready for full multi-tenancy, switch to config.settings.local
    (requires Docker Compose with PostgreSQL + PgBouncer). All models
    and migrations remain compatible — only the database engine changes.
"""

from pathlib import Path

from config.env import BASE_DIR, env


# ════════════════════════════════════════════════════════════════════════
# CORE
# ════════════════════════════════════════════════════════════════════════

DEBUG = True

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-sqlite-local-dev-key-do-not-use-in-production",
)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "0.0.0.0"],
)

INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ════════════════════════════════════════════════════════════════════════
# DATABASE — SQLite (local file)
# ════════════════════════════════════════════════════════════════════════

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# No database routers — single SQLite database, no schema routing
DATABASE_ROUTERS: list[str] = []


# ════════════════════════════════════════════════════════════════════════
# INSTALLED_APPS — Flat list (no SHARED_APPS / TENANT_APPS split)
# ════════════════════════════════════════════════════════════════════════
# django_tenants and apps.tenants are EXCLUDED because django-tenants
# requires PostgreSQL schemas. All other apps work fine with SQLite.

INSTALLED_APPS: list[str] = [
    # ── Django Framework ────────────────────────────────────────────
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ── LankaCommerce Apps ──────────────────────────────────────────
    "apps.core",
    "apps.users",
    "apps.platform",
    "apps.products",
    "apps.inventory",
    "apps.vendors",
    "apps.sales",
    "apps.customers",
    "apps.orders",
    "apps.hr",
    "apps.accounting",
    "apps.reports",
    "apps.webstore",
    "apps.integrations",
    # ── Third-Party ─────────────────────────────────────────────────
    "rest_framework",
    "django_filters",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
]

# AUTH_USER_MODEL — same as full PostgreSQL setup
AUTH_USER_MODEL = "platform.PlatformUser"


# ════════════════════════════════════════════════════════════════════════
# MIDDLEWARE — No tenant middleware
# ════════════════════════════════════════════════════════════════════════

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # ── LankaCommerce custom middleware ──
    "apps.core.middleware.request_logging.RequestLoggingMiddleware",
    "apps.core.middleware.security.SecurityHeadersMiddleware",
    "apps.core.middleware.timezone.TimezoneMiddleware",
]


# ════════════════════════════════════════════════════════════════════════
# TEMPLATES
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
# DJANGO REST FRAMEWORK
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
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
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
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
}


# ════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ════════════════════════════════════════════════════════════════════════

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ════════════════════════════════════════════════════════════════════════
# INTERNATIONALISATION
# ════════════════════════════════════════════════════════════════════════

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Colombo"
USE_I18N = True
USE_TZ = True


# ════════════════════════════════════════════════════════════════════════
# STATIC & MEDIA FILES
# ════════════════════════════════════════════════════════════════════════

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"


# ════════════════════════════════════════════════════════════════════════
# CORS (Development — allow all origins)
# ════════════════════════════════════════════════════════════════════════

CORS_ALLOW_ALL_ORIGINS = True


# ════════════════════════════════════════════════════════════════════════
# EMAIL — Console backend for development
# ════════════════════════════════════════════════════════════════════════

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ════════════════════════════════════════════════════════════════════════
# LOGGING — minimal for development
# ════════════════════════════════════════════════════════════════════════

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "apps": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
