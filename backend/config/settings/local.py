"""
LankaCommerce Cloud - Local Development Settings

Extends base settings with development-specific overrides:
    - DEBUG enabled with detailed error pages
    - PostgreSQL database (Docker or remote)
    - Console email backend
    - Debug toolbar + django-extensions

Usage:
    Set DJANGO_ENV=local (default) or run without setting it.
"""

import os  # noqa: F401

from config.env import env  # noqa: F401
from config.settings.base import *  # noqa: F401, F403

# ════════════════════════════════════════════════════════════════════════
# DEBUG SETTINGS  (Task 29)
# ════════════════════════════════════════════════════════════════════════

DEBUG = True

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-local-dev-key-do-not-use-in-production",
)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "0.0.0.0"],
)

# Required for django-debug-toolbar
INTERNAL_IPS = [
    "127.0.0.1",
    "10.0.2.2",  # Docker host (common)
]

# ── Development apps ──────────────────────────────────────────────────
INSTALLED_APPS += [  # noqa: F405
    # "debug_toolbar",          # Uncomment after pip install django-debug-toolbar
    # "django_extensions",      # Uncomment after pip install django-extensions
]

# ── Development middleware ─────────────────────────────────────────────
MIDDLEWARE += [  # noqa: F405
    # "debug_toolbar.middleware.DebugToolbarMiddleware",  # Uncomment with debug_toolbar
]


# ════════════════════════════════════════════════════════════════════════
# DATABASE  (Task 30 — Updated for PgBouncer in Phase 2)
# ════════════════════════════════════════════════════════════════════════
# Driver: psycopg v3 (psycopg[binary] 3.3.2) — the modern async-capable
# PostgreSQL adapter. Replaces the legacy psycopg2-binary.
#
# Application traffic routes through PgBouncer (port 6432) for
# connection pooling. PgBouncer uses transaction pooling mode, which
# is required for django-tenants search_path isolation.
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
        "PASSWORD": env("DB_PASSWORD", default="dev_password_change_me"),
        "HOST": env("DB_HOST", default="pgbouncer"),
        "PORT": env.int("DB_PORT", default=6432),
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": True,
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "OPTIONS": {
            "connect_timeout": 5,
        },
    }
}


# ════════════════════════════════════════════════════════════════════════
# EMAIL  (Task 31)
# ════════════════════════════════════════════════════════════════════════
# Console backend prints emails to terminal — simplest for development.
# Switch to MailHog (Docker) for full SMTP testing if needed.

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "noreply@localhost"

EMAIL_SUBJECT_PREFIX = "[LCC Dev] "

# ── MailHog alternative (uncomment to use MailHog in Docker) ──────────
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "mailhog"
# EMAIL_PORT = 1025


# ════════════════════════════════════════════════════════════════════════
# CORS (development — allow all origins)
# ════════════════════════════════════════════════════════════════════════

CORS_ALLOW_ALL_ORIGINS = False  # Must be False when CORS_ALLOW_CREDENTIALS=True; use CORS_ALLOWED_ORIGINS instead


# ════════════════════════════════════════════════════════════════════════
# CHANNEL LAYERS (development — in-memory, no Redis required)
# ════════════════════════════════════════════════════════════════════════

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
