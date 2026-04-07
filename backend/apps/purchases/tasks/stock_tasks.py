"""
Celery tasks for stock updates after goods receiving.
"""

import logging

try:
    from celery import shared_task
except ImportError:
    # Fallback decorator when Celery is not installed
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        if args and callable(args[0]):
            return args[0]
        return decorator

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_stock_update(self, grn_id):
    """
    Process stock updates for a completed goods receipt.

    Args:
        grn_id: UUID string of the GoodsReceipt.
    """
    try:
        from apps.purchases.services.receiving_service import ReceivingService
        results = ReceivingService.add_to_stock(grn_id)
        logger.info("Stock update processed for GRN %s: %d items", grn_id, len(results))
        return results
    except Exception as exc:
        logger.error("Stock update failed for GRN %s: %s", grn_id, exc)
        try:
            self.retry(exc=exc)
        except AttributeError:
            raise


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_po_line_quantities_task(self, po_line_id):
    """
    Re-aggregate received quantities for a PO line item.

    Args:
        po_line_id: UUID string of the POLineItem.
    """
    try:
        from apps.purchases.models.po_line_item import POLineItem
        from apps.purchases.services.receiving_service import ReceivingService

        po_line = POLineItem.objects.get(pk=po_line_id)
        ReceivingService.update_po_line_quantities(po_line)
        logger.info("PO line quantities updated for %s", po_line_id)
    except Exception as exc:
        logger.error("PO line update failed for %s: %s", po_line_id, exc)
        try:
            self.retry(exc=exc)
        except AttributeError:
            raise
