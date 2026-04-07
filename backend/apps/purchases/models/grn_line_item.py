"""
GRNLineItem model for the purchases application.

Tracks individual line items received on a goods receipt note.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.purchases.constants import (
    CONDITION_CHOICES,
    DEFAULT_CONDITION,
)


class GRNLineItem(UUIDMixin, TimestampMixin, models.Model):
    """Line item on a goods receipt note."""

    goods_receipt = models.ForeignKey(
        "purchases.GoodsReceipt",
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    po_line = models.ForeignKey(
        "purchases.POLineItem",
        on_delete=models.PROTECT,
        related_name="grn_line_items",
    )
    line_number = models.PositiveIntegerField(
        default=0,
        help_text="Line item sequence number within the GRN",
    )
    quantity_received = models.PositiveIntegerField(
        help_text="Quantity accepted in this receipt",
    )
    quantity_rejected = models.PositiveIntegerField(
        default=0,
        help_text="Quantity rejected in this receipt",
    )
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default=DEFAULT_CONDITION,
    )
    rejection_reason = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    # Quality fields (Task 58)
    quality_notes = models.TextField(
        blank=True,
        default="",
        help_text="Quality inspection notes",
    )
    requires_followup = models.BooleanField(
        default=False,
        help_text="Whether this item requires follow-up action",
    )

    # Receiving location (Task 57)
    receiving_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grn_line_items",
        help_text="Warehouse where items were received into",
    )
    receiving_location = models.ForeignKey(
        "inventory.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grn_line_items",
        help_text="Storage location where items were placed",
    )

    class Meta:
        verbose_name = "GRN Line Item"
        verbose_name_plural = "GRN Line Items"
        ordering = ["line_number", "po_line"]

    def __str__(self):
        return (
            f"GRN {self.goods_receipt} - "
            f"{self.po_line.product_name}: {self.quantity_received} received"
        )

    @property
    def quantity_accepted(self):
        """Quantity accepted = received - rejected."""
        return self.quantity_received - self.quantity_rejected
