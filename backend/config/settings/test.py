"""
LankaCommerce Cloud - Test Settings

Optimised for fast test execution.

Usage:
    DJANGO_ENV=test python manage.py test
    DJANGO_ENV=test pytest
"""

from config.settings.base import *  # noqa: F401, F403


# ════════════════════════════════════════════════════════════════════════
# CORE
# ════════════════════════════════════════════════════════════════════════

DEBUG = False  # Match production behaviour

SECRET_KEY = "django-insecure-test-key-for-ci-only"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver", ".testserver"]


# ════════════════════════════════════════════════════════════════════════
# DATABASE
# ════════════════════════════════════════════════════════════════════════
# SQLite in-memory for speed.  Switch to PostgreSQL if testing PG-specific
# features (e.g. django-tenants, JSONField lookups, full-text search).

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# ════════════════════════════════════════════════════════════════════════
# PASSWORD HASHING — fast (insecure, tests only)
# ════════════════════════════════════════════════════════════════════════

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# ════════════════════════════════════════════════════════════════════════
# EMAIL — in-memory
# ════════════════════════════════════════════════════════════════════════
# Sent emails are stored in django.core.mail.outbox for assertions.

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

DEFAULT_FROM_EMAIL = "test@localhost"

EMAIL_SUBJECT_PREFIX = "[LCC Test] "


# ════════════════════════════════════════════════════════════════════════
# CACHING — local memory
# ════════════════════════════════════════════════════════════════════════

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "lcc-test",
    },
    "sessions": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "lcc-test-sessions",
    },
    "ratelimit": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "lcc-test-ratelimit",
    },
}


# ════════════════════════════════════════════════════════════════════════
# MISC OPTIMISATIONS
# ════════════════════════════════════════════════════════════════════════

# Reduce logging noise during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}

# Disable debug toolbar and extensions in tests
INSTALLED_APPS = [  # noqa: F405
    app
    for app in INSTALLED_APPS  # noqa: F405
    if app not in ("debug_toolbar", "django_extensions")
]

MIDDLEWARE = [  # noqa: F405
    mw
    for mw in MIDDLEWARE  # noqa: F405
    if mw != "debug_toolbar.middleware.DebugToolbarMiddleware"
]
