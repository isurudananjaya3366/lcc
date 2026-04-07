"""
Celery tasks for delivery reminders.
"""

import logging
from datetime import date, timedelta

try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        if args and callable(args[0]):
            return args[0]
        return decorator

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def delivery_reminder_task(self):
    """
    Check for POs with overdue expected delivery dates and notify.
    Uses POSettings.overdue_reminder_days for threshold.
    """
    try:
        from apps.purchases.constants import PO_STATUS_ACKNOWLEDGED, PO_STATUS_SENT
        from apps.purchases.models.purchase_order import PurchaseOrder

        # Get reminder threshold from settings
        reminder_days = 3
        try:
            from apps.purchases.models.po_settings import POSettings
            settings = POSettings.objects.first()
            if settings:
                reminder_days = settings.overdue_reminder_days
        except Exception:
            pass

        threshold_date = date.today() - timedelta(days=reminder_days)
        overdue_pos = PurchaseOrder.objects.filter(
            status__in=[PO_STATUS_SENT, PO_STATUS_ACKNOWLEDGED],
            expected_delivery_date__lt=date.today(),
        )
        overdue_list = list(overdue_pos.values_list("po_number", flat=True))
        if overdue_list:
            logger.warning("Overdue POs found: %s", ", ".join(overdue_list))

            # Send delivery reminders
            try:
                from apps.purchases.services.email_service import POEmailService
                for po in overdue_pos.select_related("vendor"):
                    vendor = po.vendor
                    email = getattr(vendor, "email", "") or getattr(vendor, "contact_email", "")
                    if email:
                        POEmailService.send_delivery_reminder(po.pk, email)
            except Exception as e:
                logger.error("Failed to send delivery reminders: %s", e)

        return overdue_list
    except Exception as exc:
        logger.error("Delivery reminder task failed: %s", exc)
        try:
            self.retry(exc=exc)
        except AttributeError:
            raise
