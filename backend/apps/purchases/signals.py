"""
Purchase Order signal handlers.

Auto-recalculates PO totals when line items change.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.purchases.models.po_line_item import POLineItem


@receiver(post_save, sender=POLineItem)
def recalculate_po_on_line_save(sender, instance, **kwargs):
    """Recalculate PO totals when a line item is saved."""
    from apps.purchases.services.calculation_service import POCalculationService

    update_fields = kwargs.get("update_fields")
    # Skip if only tax_amount/line_total were updated (avoids recursion)
    if update_fields and set(update_fields) <= {"tax_amount", "line_total"}:
        return

    try:
        po = instance.purchase_order
    except Exception:
        return

    POCalculationService.recalculate_po(po)


@receiver(post_delete, sender=POLineItem)
def recalculate_po_on_line_delete(sender, instance, **kwargs):
    """Recalculate PO totals when a line item is deleted."""
    from apps.purchases.services.calculation_service import POCalculationService
    from apps.purchases.models.purchase_order import PurchaseOrder

    try:
        po = PurchaseOrder.objects.get(pk=instance.purchase_order_id)
    except PurchaseOrder.DoesNotExist:
        return

    POCalculationService.recalculate_po(po)
