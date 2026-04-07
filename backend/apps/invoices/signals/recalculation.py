"""
Invoice recalculation signals.

Auto-recalculate invoice totals when line items are created, updated, or deleted.
"""

import logging

from django.db.models.signals import post_save, post_delete

logger = logging.getLogger(__name__)

_RECALCULATING = set()


def _recalculate_invoice(sender, instance, **kwargs):
    """Recalculate parent invoice totals on line item change."""
    invoice_id = instance.invoice_id
    if invoice_id in _RECALCULATING:
        return
    _RECALCULATING.add(invoice_id)
    try:
        from apps.invoices.services.calculation_service import InvoiceCalculationService
        InvoiceCalculationService.recalculate_invoice(invoice_id)
    except Exception:
        logger.exception("Failed to recalculate invoice %s", invoice_id)
    finally:
        _RECALCULATING.discard(invoice_id)


def connect_signals():
    """Connect invoice recalculation signals."""
    from apps.invoices.models.invoice_line_item import InvoiceLineItem

    post_save.connect(
        _recalculate_invoice,
        sender=InvoiceLineItem,
        dispatch_uid="invoice_line_item_post_save_recalc",
    )
    post_delete.connect(
        _recalculate_invoice,
        sender=InvoiceLineItem,
        dispatch_uid="invoice_line_item_post_delete_recalc",
    )
