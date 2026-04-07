"""
Alert resolution and maintenance Celery tasks.

Tasks 41-42 (Celery wrappers), plus snooze expiration
and monitoring log cleanup tasks.
"""

import logging

from celery import shared_task
from django.utils import timezone

from apps.inventory.alerts.constants import ALERT_STATUS_ACTIVE

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def auto_resolve_alerts_task(self):
    """
    Celery task to auto-resolve alerts across all products.

    Iterates active alerts and resolves those where stock
    has improved above thresholds.
    """
    from apps.inventory.alerts.models import StockAlert
    from apps.inventory.alerts.tasks.stock_monitor import (
        auto_resolve_alerts,
    )
    from apps.inventory.stock.models.stock_level import StockLevel

    try:
        active_alerts = StockAlert.objects.get_active()

        # Get unique product/warehouse combinations from active alerts
        product_warehouse_pairs = (
            active_alerts.values_list("product_id", "warehouse_id")
            .distinct()
        )

        resolved_total = 0
        for product_id, warehouse_id in product_warehouse_pairs:
            try:
                stock_level = StockLevel.objects.filter(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                ).first()

                if stock_level:
                    from apps.products.models import Product

                    product = Product.objects.get(id=product_id)
                    resolved = auto_resolve_alerts(product, stock_level)
                    resolved_total += resolved
            except Exception:
                logger.exception(
                    "Error resolving alerts for product %s", product_id
                )

        logger.info("Auto-resolve task completed: %d alerts resolved", resolved_total)
        return {"resolved": resolved_total}

    except Exception as exc:
        logger.exception("Auto-resolve alerts task failed")
        raise self.retry(exc=exc)


@shared_task
def check_expired_snoozes():
    """
    Reactivate alerts whose snooze period has expired.

    Runs every 5 minutes via Celery Beat.
    """
    from apps.inventory.alerts.models import StockAlert

    expired = StockAlert.objects.get_snoozed_expired()
    count = 0

    for alert in expired:
        alert.unsnooze()
        count += 1
        logger.info(
            "Reactivated snoozed alert %s for %s",
            alert.id,
            alert.product.name,
        )

    if count:
        logger.info("Reactivated %d expired snoozed alerts", count)

    return {"reactivated": count}


@shared_task
def cleanup_old_monitoring_logs(retention_days=30):
    """
    Delete monitoring logs older than the retention period.

    Runs daily to keep the monitoring log table manageable.
    """
    from apps.inventory.alerts.models import MonitoringLog

    deleted = MonitoringLog.objects.cleanup_old_logs(retention_days)

    if deleted:
        logger.info("Cleaned up %d old monitoring logs", deleted)

    return {"deleted": deleted}
