"""
LankaCommerce Cloud - Base Celery Task Classes.

Provides abstract base tasks with structured logging, error handling,
and multi-tenant schema switching.

Classes:
    BaseTask        — Abstract base with lifecycle logging hooks.
    TenantAwareTask — Extends BaseTask to set the tenant schema before
                      task body execution and to propagate tenant_id
                      through apply_async.
"""

import logging
import time

import celery
from django.db import connection

logger = logging.getLogger(__name__)


class BaseTask(celery.Task):
    """Abstract base task with lifecycle logging.

    All project tasks should inherit from this class (directly or via
    ``TenantAwareTask``) to get consistent logging on success, failure,
    and retry events.
    """

    abstract = True

    # ── Lifecycle hooks ─────────────────────────────────────────────

    def on_success(self, retval, task_id, args, kwargs):
        """Log successful task completion with elapsed time."""
        elapsed = self._get_elapsed(task_id)
        logger.info(
            "Task %s[%s] succeeded in %.2fs | result=%s",
            self.name,
            task_id,
            elapsed,
            retval,
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failure with exception details."""
        logger.error(
            "Task %s[%s] failed: %s\n%s",
            self.name,
            task_id,
            exc,
            einfo,
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log retry attempts."""
        logger.warning(
            "Task %s[%s] retrying due to: %s",
            self.name,
            task_id,
            exc,
        )

    # ── Helpers ─────────────────────────────────────────────────────

    def before_start(self, task_id, args, kwargs):
        """Record start timestamp for duration tracking."""
        self._start_time = time.monotonic()

    def _get_elapsed(self, task_id) -> float:
        """Return elapsed seconds since ``before_start``."""
        start = getattr(self, "_start_time", None)
        if start is None:
            return 0.0
        return time.monotonic() - start


class TenantAwareTask(BaseTask):
    """Abstract task that activates a tenant schema before execution.

    Tasks using this base **must** receive ``tenant_id`` as a keyword
    argument.  The ``__call__`` method resolves the tenant from the DB
    and switches the connection's search_path to the tenant's schema
    via ``django.db.connection.set_tenant()``.

    Usage::

        @shared_task(bind=True, base=TenantAwareTask)
        def my_task(self, *, tenant_id: int, **kwargs):
            # Inside here the DB connection targets the tenant schema.
            ...
    """

    abstract = True

    def __call__(self, *args, **kwargs):
        """Set the tenant schema before running the task body."""
        tenant_id = kwargs.get("tenant_id")
        if tenant_id is None:
            logger.error(
                "TenantAwareTask %s called without tenant_id", self.name
            )
            raise ValueError(
                f"TenantAwareTask {self.name} requires 'tenant_id' in kwargs."
            )

        # Import here to avoid circular imports at module load time.
        from apps.tenants.models import Tenant

        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            logger.error("Tenant with id=%s does not exist", tenant_id)
            raise

        # django-tenants exposes set_tenant on the connection wrapper.
        connection.set_tenant(tenant)
        logger.debug(
            "Task %s: activated schema '%s' for tenant %s",
            self.name,
            tenant.schema_name,
            tenant_id,
        )

        return super().__call__(*args, **kwargs)

    def apply_async(self, args=None, kwargs=None, **options):
        """Ensure ``tenant_id`` is forwarded when dispatching."""
        kwargs = kwargs or {}
        if "tenant_id" not in kwargs:
            # Try to inherit tenant_id from the current connection.
            current_tenant = getattr(connection, "tenant", None)
            if current_tenant is not None:
                kwargs["tenant_id"] = current_tenant.pk
        return super().apply_async(args=args, kwargs=kwargs, **options)
