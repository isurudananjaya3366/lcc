"""
Celery tasks for PO email notifications.
"""

import logging

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


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_po_email_task(self, po_id):
    """
    Send PO email asynchronously.

    Args:
        po_id: UUID string of the PurchaseOrder.
    """
    try:
        from apps.purchases.models.purchase_order import PurchaseOrder
        from apps.purchases.services.email_service import POEmailService

        po = PurchaseOrder.objects.select_related("vendor").get(pk=po_id)
        vendor = po.vendor
        email = getattr(vendor, "email", "") or getattr(vendor, "contact_email", "")
        if email:
            POEmailService.send_po_email(po_id, email)
            logger.info("PO email sent for %s to %s", po.po_number, email)
        else:
            logger.warning("No email address found for vendor %s", vendor)
    except Exception as exc:
        logger.error("PO email failed for %s: %s", po_id, exc)
        try:
            self.retry(exc=exc)
        except AttributeError:
            raise


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_acknowledgment_reminders(self):
    """
    Send reminders to vendors who haven't acknowledged their POs.
    """
    try:
        from apps.purchases.services.email_service import POEmailService
        results = POEmailService.send_acknowledgment_reminder()
        logger.info("Acknowledgment reminders sent: %d", len(results))
        return results
    except Exception as exc:
        logger.error("Acknowledgment reminders failed: %s", exc)
        try:
            self.retry(exc=exc)
        except AttributeError:
            raise
