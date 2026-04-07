"""
FulfillmentLineItem model for tracking individual items in a fulfillment (Task 54).
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class FulfillmentLineItem(UUIDMixin, TimestampMixin, models.Model):
    """
    Tracks an individual line item within a fulfillment.

    Links to both the Fulfillment and the OrderLineItem to track
    how many units of each order item are being fulfilled.
    """

    fulfillment = models.ForeignKey(
        "orders.Fulfillment",
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    order_line_item = models.ForeignKey(
        "orders.OrderLineItem",
        on_delete=models.CASCADE,
        related_name="fulfillment_items",
    )

    # ── Quantity ────────────────────────────────────────────────────
    quantity = models.DecimalField(
        max_digits=12, decimal_places=3, default=0,
        help_text="Quantity being fulfilled in this shipment.",
    )

    # ── Warehouse Details ───────────────────────────────────────────
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fulfillment_line_items",
    )
    bin_location = models.CharField(max_length=100, blank=True, default="")
    serial_number = models.CharField(max_length=100, blank=True, default="")
    batch_number = models.CharField(max_length=100, blank=True, default="")

    # ── Workflow Timestamps ─────────────────────────────────────────
    picked_at = models.DateTimeField(null=True, blank=True)
    picked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="picked_fulfillment_items",
    )
    packed_at = models.DateTimeField(null=True, blank=True)
    packed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packed_fulfillment_items",
    )

    # ── QC / Inspection ─────────────────────────────────────────────
    qc_passed = models.BooleanField(null=True, blank=True)
    qc_notes = models.TextField(blank=True, default="")
    inspected_at = models.DateTimeField(null=True, blank=True)
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspected_fulfillment_items",
    )

    # ── Condition / Damage ─────────────────────────────────────────
    condition = models.CharField(
        max_length=20, blank=True, default="good",
        choices=[
            ("good", "Good"),
            ("damaged", "Damaged"),
            ("defective", "Defective"),
        ],
    )
    damage_notes = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "orders_fulfillmentlineitem"
        verbose_name = "Fulfillment Line Item"
        verbose_name_plural = "Fulfillment Line Items"
        unique_together = [("fulfillment", "order_line_item")]
        ordering = ["order_line_item__position"]

    def __str__(self):
        return (
            f"{self.quantity}x "
            f"{self.order_line_item.item_name or 'Item'} "
            f"in {self.fulfillment.fulfillment_number}"
        )

    def get_product(self):
        """Return the product associated with this line item."""
        return self.order_line_item.product

    def is_fully_fulfilled(self):
        """Whether this fulfillment item's parent order line is fully fulfilled."""
        return self.order_line_item.is_fully_fulfilled

    def get_remaining_quantity(self):
        """Remaining quantity on the parent order line item."""
        return self.order_line_item.quantity_remaining
