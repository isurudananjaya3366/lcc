"""
LankaCommerce Cloud - Celery Beat Scheduled Tasks.

Periodic tasks executed on a cron-like schedule via Celery Beat.
Tasks that iterate across tenants use ``BaseTask`` (not
``TenantAwareTask``) because they manage tenant context themselves.
"""

import logging

from celery import shared_task
from django.contrib.sessions.models import Session
from django.db import connection
from django.utils import timezone

from apps.core.tasks.base import BaseTask

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# Daily Sales Report
# ════════════════════════════════════════════════════════════════════════


@shared_task(
    bind=True,
    base=BaseTask,
    name="apps.core.tasks.scheduled_tasks.daily_sales_report_task",
)
def daily_sales_report_task(self):
    """
    Dispatch a daily-sales report generation task for every active tenant.

    Runs once a day (configured in ``CELERY_BEAT_SCHEDULE``).  For each
    active tenant it enqueues a ``generate_report_task`` with the
    ``daily_sales`` report type.
    """
    from apps.core.tasks.report_tasks import generate_report_task
    from apps.tenants.models import TENANT_STATUS_ACTIVE, Tenant

    tenants = Tenant.objects.filter(status=TENANT_STATUS_ACTIVE).exclude(
        schema_name="public",
    )
    count = 0
    for tenant in tenants.iterator():
        generate_report_task.apply_async(
            kwargs={
                "tenant_id": tenant.pk,
                "report_type": "daily_sales",
                "params": {"date": str(timezone.now().date())},
            },
        )
        count += 1

    logger.info(
        "daily_sales_report_task dispatched %d report(s) for active tenants.",
        count,
    )
    return {"dispatched": count}


# ════════════════════════════════════════════════════════════════════════
# Low Stock Check
# ════════════════════════════════════════════════════════════════════════


@shared_task(
    bind=True,
    base=BaseTask,
    name="apps.core.tasks.scheduled_tasks.check_low_stock_task",
)
def check_low_stock_task(self):
    """
    Check inventory for low-stock items across all active tenants.

    Stub implementation — the actual inventory query will be added when
    the inventory module's models are available.
    """
    from apps.tenants.models import TENANT_STATUS_ACTIVE, Tenant

    tenants = Tenant.objects.filter(status=TENANT_STATUS_ACTIVE).exclude(
        schema_name="public",
    )
    checked = 0
    for tenant in tenants.iterator():
        connection.set_tenant(tenant)
        # TODO: Query inventory models for items below reorder_level.
        logger.debug(
            "Low stock check for tenant '%s' (stub).", tenant.schema_name
        )
        checked += 1

    logger.info(
        "check_low_stock_task completed for %d tenant(s) (stub).", checked
    )
    return {"tenants_checked": checked}


# ════════════════════════════════════════════════════════════════════════
# Session Cleanup
# ════════════════════════════════════════════════════════════════════════


@shared_task(
    bind=True,
    base=BaseTask,
    name="apps.core.tasks.scheduled_tasks.cleanup_old_sessions_task",
)
def cleanup_old_sessions_task(self):
    """
    Delete expired Django sessions from the database.

    Equivalent to ``python manage.py clearsessions`` but executed
    asynchronously via Celery Beat.
    """
    now = timezone.now()
    expired = Session.objects.filter(expire_date__lt=now)
    count = expired.count()
    expired.delete()

    logger.info("cleanup_old_sessions_task removed %d expired session(s).", count)
    return {"deleted_sessions": count}


# ════════════════════════════════════════════════════════════════════════
# Token Cleanup
# ════════════════════════════════════════════════════════════════════════


@shared_task(
    bind=True,
    base=BaseTask,
    name="apps.core.tasks.scheduled_tasks.cleanup_expired_tokens_task",
)
def cleanup_expired_tokens_task(self):
    """
    Clean up expired authentication tokens.

    Stub — the exact token model depends on the auth strategy
    (``rest_framework_simplejwt`` outstanding tokens, DRF ``Token``,
    etc.).  Replace with the appropriate query once the auth module
    is finalised.
    """
    logger.info(
        "cleanup_expired_tokens_task executed (stub — no token model configured yet)."
    )
    return {"status": "stub"}


# ════════════════════════════════════════════════════════════════════════
# Database Backup
# ════════════════════════════════════════════════════════════════════════


@shared_task(
    bind=True,
    base=BaseTask,
    name="apps.core.tasks.scheduled_tasks.database_backup_task",
)
def database_backup_task(self):
    """
    Trigger a database backup.

    Stub — logs intent.  In production this will invoke ``pg_dump``
    (via the ``scripts/db-backup.sh`` helper) or an equivalent cloud
    snapshot mechanism.
    """
    logger.info(
        "database_backup_task triggered (stub — backup mechanism not yet wired)."
    )
    return {"status": "stub"}
