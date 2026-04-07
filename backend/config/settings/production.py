"""
LankaCommerce Cloud - Production Settings

Strict security settings for production deployment.
All secrets are read from environment variables — nothing is hardcoded.

Required environment variables:
    DJANGO_SECRET_KEY       - Cryptographic signing key
    DJANGO_ALLOWED_HOSTS    - Comma-separated domain list
    DATABASE_URL            - PostgreSQL connection string
    REDIS_URL               - Redis connection string
    SENTRY_DSN              - (optional) Sentry error tracking
"""

import os  # noqa: F401

from config.env import env  # noqa: F401
from config.settings.base import *  # noqa: F401, F403


# ════════════════════════════════════════════════════════════════════════
# SECURITY  (Task 32)
# ════════════════════════════════════════════════════════════════════════

DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# ── HTTPS ──────────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── HSTS (HTTP Strict Transport Security) ─────────────────────────────
SECURE_HSTS_SECONDS = 31536000              # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ── Cookies ────────────────────────────────────────────────────────────
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# ── Security headers ──────────────────────────────────────────────────
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# ── CSRF trusted origins ──────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=[],
)

# ── CORS (Cross-Origin Resource Sharing) ──────────────────────────────
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS")


# ════════════════════════════════════════════════════════════════════════
# DATABASE  (Task 33 — Updated for PgBouncer in Phase 2)
# ════════════════════════════════════════════════════════════════════════
# Driver: psycopg v3 (psycopg[binary] 3.3.2) — the modern async-capable
# PostgreSQL adapter. Replaces the legacy psycopg2-binary.
#
# In production, all application traffic routes through PgBouncer for
# connection pooling. PgBouncer uses transaction pooling mode.
#
# CONN_MAX_AGE must be 0 with transaction pooling — persistent
# connections would leak tenant search_path between requests.
#
# DISABLE_SERVER_SIDE_CURSORS must be True because PgBouncer does not
# support server-side cursors in transaction pooling mode.
#
# Multi-Tenancy: django-tenants 3.10.0 installed and verified
# compatible with Django 5.2.x. ENGINE is now set to
# django_tenants.postgresql_backend for multi-tenant schema support.

DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django_tenants.postgresql_backend"),
        "NAME": env("DB_NAME", default="lankacommerce"),
        "USER": env("DB_USER", default="lcc_user"),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default="pgbouncer"),
        "PORT": env.int("DB_PORT", default=6432),
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": True,
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "OPTIONS": {
            "sslmode": env("DB_SSLMODE", default="require"),
        },
    }
}

# If dj-database-url is installed, uncomment to parse DATABASE_URL:
# import dj_database_url
# DATABASES["default"] = dj_database_url.config(
#     default=os.environ.get("DATABASE_URL"),
#     conn_max_age=60,
#     conn_health_checks=True,
#     ssl_require=True,
# )


# ════════════════════════════════════════════════════════════════════════
# CACHING — Redis  (Task 34)
# ════════════════════════════════════════════════════════════════════════

REDIS_URL = env("REDIS_URL")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 300,                          # 5 minutes
        "KEY_PREFIX": "lcc",
        "VERSION": 1,
        "OPTIONS": {
            # "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# ── Session via cache (faster than database) ──────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ── Celery broker ─────────────────────────────────────────────────────
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")


# ── Channel Layers (Redis-backed) ────────────────────────────────────
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL")],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}


# ════════════════════════════════════════════════════════════════════════
# EMAIL  (Production SMTP)
# ════════════════════════════════════════════════════════════════════════

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@lankacommerce.lk")
EMAIL_SUBJECT_PREFIX = "[LCC] "


# ════════════════════════════════════════════════════════════════════════
# STATIC FILES — WhiteNoise (or Nginx)
# ════════════════════════════════════════════════════════════════════════

# Uncomment when whitenoise is installed:
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# Insert "whitenoise.middleware.WhiteNoiseMiddleware" after SecurityMiddleware


# ════════════════════════════════════════════════════════════════════════
# S3 PRODUCTION STORAGE (SP10 Group C — Task 46)
# ════════════════════════════════════════════════════════════════════════
# In production the STORAGE_BACKEND env-var should be "s3".
# storage.py already validates credentials when STORAGE_BACKEND=s3 and
# wires up TenantS3Storage as the default backend automatically.
#
# This block emits a loud warning if production is running on local
# filesystem storage — it should never happen in a real deployment.

if STORAGE_BACKEND == "local":  # noqa: F405 (imported via base *)
    import warnings

    warnings.warn(
        "STORAGE_BACKEND is 'local' in production settings. "
        "Set STORAGE_BACKEND=s3 and provide AWS credentials for production.",
        stacklevel=1,
    )


# ════════════════════════════════════════════════════════════════════════
# ERROR TRACKING — Sentry (optional)
# ════════════════════════════════════════════════════════════════════════

SENTRY_DSN = env("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk  # noqa: E402
    from sentry_sdk.integrations.django import DjangoIntegration  # noqa: E402

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=env("SENTRY_ENVIRONMENT"),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE"),
        send_default_pii=False,
    )


# ════════════════════════════════════════════════════════════════════════
# LOGGING
# ════════════════════════════════════════════════════════════════════════

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
