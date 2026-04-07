"""Signals for the Vendor Bills application."""

from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.vendor_bills.models.bill_line_item import BillLineItem


@receiver(post_delete, sender=BillLineItem)
def recalculate_bill_on_line_delete(sender, instance, **kwargs):
    """Recalculate the parent bill totals when a line item is deleted."""
    bill = instance.vendor_bill
    if bill is not None:
        bill.recalculate_from_lines()
