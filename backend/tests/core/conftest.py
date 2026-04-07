"""
LankaCommerce Cloud – Core test fixtures (SP08 Task 79).

Reusable Celery & cache-related fixtures for ``tests/core/`` test modules.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest


# ════════════════════════════════════════════════════════════════════════
# Celery fixtures
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def celery_eager_mode(settings):
    """Ensure Celery tasks execute synchronously during the test."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    return settings


@pytest.fixture()
def mock_celery_app():
    """Return a lightweight mock of the Celery application."""
    app = MagicMock()
    app.conf = MagicMock()
    app.control = MagicMock()
    app.AsyncResult = MagicMock()
    return app


@pytest.fixture()
def mock_task():
    """Return a mock Celery task object with common attributes pre-set."""
    task = MagicMock()
    task.name = "tests.mock_task"
    task.request = MagicMock()
    task.request.id = "test-task-id-0001"
    task.request.retries = 0
    task.max_retries = 3
    task.default_retry_delay = 60
    return task


@pytest.fixture()
def base_task():
    """Instantiate a real :class:`BaseTask` for white-box testing."""
    from apps.core.tasks.base import BaseTask

    task = BaseTask()
    task.name = "fixture.base_task"
    task._start_time = 0
    return task


@pytest.fixture()
def tenant_aware_task():
    """Instantiate a real :class:`TenantAwareTask`."""
    from apps.core.tasks.base import TenantAwareTask

    task = TenantAwareTask()
    task.name = "fixture.tenant_aware_task"
    task._start_time = 0
    return task


@pytest.fixture()
def mock_tenant():
    """Return a mock tenant with schema_name and name attributes."""
    tenant = MagicMock()
    tenant.schema_name = "test_tenant"
    tenant.name = "Test Tenant"
    tenant.pk = 1
    return tenant


# ════════════════════════════════════════════════════════════════════════
# Cache fixtures
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def mock_cache():
    """Patch ``django.core.cache.cache`` and return the mock."""
    with patch("django.core.cache.cache") as _mock:
        _mock.get.return_value = None
        _mock.set.return_value = True
        _mock.delete.return_value = True
        _mock.clear.return_value = None
        yield _mock


@pytest.fixture()
def mock_redis():
    """Patch the low-level Redis client returned by ``get_redis_connection``."""
    with patch("django_redis.get_redis_connection") as _mock:
        conn = MagicMock()
        conn.scan_iter.return_value = iter([])
        conn.pipeline.return_value.__enter__ = MagicMock(return_value=conn)
        conn.pipeline.return_value.__exit__ = MagicMock(return_value=False)
        _mock.return_value = conn
        yield conn


# ════════════════════════════════════════════════════════════════════════
# Logging helpers
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def task_logger(caplog):
    """Capture Celery-related log output at DEBUG level."""
    with caplog.at_level(logging.DEBUG, logger="apps.core.tasks"):
        yield caplog
