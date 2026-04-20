"""
LankaCommerce Cloud - PostgreSQL Test Settings

Test settings that use the Docker PostgreSQL database instead of SQLite.
This is REQUIRED for any test that needs django-tenants DB operations
(schema creation, migrations, set_search_path, etc.).

Usage (inside Docker):
    DJANGO_SETTINGS_MODULE=config.settings.test_pg pytest tests/

Usage (from host via docker compose):
    docker compose run --rm --no-deps \
        -e DJANGO_SETTINGS_MODULE=config.settings.test_pg \
        --entrypoint "" backend bash -c \
        "pip install -q pytest pytest-django && python -m pytest tests/ --tb=short -q"

Why this file exists:
    config.settings.test uses SQLite in-memory for fast test execution.
    SQLite is incompatible with django-tenants because django-tenants
    calls connection.set_schema() which is a PostgreSQL-only operation
    (SET search_path TO ...). Any test marked @pytest.mark.django_db
    that triggers migrate_schemas will fail on SQLite.

    This file inherits from test.py but overrides DATABASES to use
    the Docker PostgreSQL 15-alpine instance (lcc-postgres container)
    with the lankacommerce_test database created by 01-init.sql.
"""

from config.settings.test import *  # noqa: F401, F403


# ════════════════════════════════════════════════════════════════════════
# CELERY — Eager mode for tests (SP08 Tasks 79-81)
# ════════════════════════════════════════════════════════════════════════
# Execute tasks synchronously in-process so tests don't need a running
# Celery worker or Redis broker.  Exceptions propagate immediately.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# ════════════════════════════════════════════════════════════════════════
# DATABASE — Docker PostgreSQL (django-tenants compatible)
# ════════════════════════════════════════════════════════════════════════
# Connects directly to the db container (port 5432) bypassing PgBouncer.
# This is intentional for tests: PgBouncer's transaction pooling can
# interfere with schema-level operations during test setup/teardown.
#
# CONN_MAX_AGE=0 ensures each request gets a fresh connection,
# preventing search_path leakage between test schemas.

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": "lankacommerce",
        "USER": "lcc_user",
        "PASSWORD": "dev_password_change_me",
        "HOST": "db",
        "PORT": 5432,
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": False,
        "TEST": {
            "NAME": "lankacommerce_test",
        },
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c search_path=public",
        },
    }
}
