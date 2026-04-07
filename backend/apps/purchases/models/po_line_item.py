"""
POLineItem model for the purchases application.

Defines purchase order line items with product linking, quantities,
pricing, discounts, taxes, and receiving tracking.
"""

from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.purchases.constants import (
    DEFAULT_LINE_STATUS,
    LINE_STATUS_CHOICES,
)


class POLineItem(UUIDMixin, TimestampMixin, models.Model):
    """
    Individual line item within a purchase order.

    Tracks product details, quantities (ordered/received/rejected/cancelled),
    pricing with discounts and tax, and receiving status.
    """

    # ── Parent Relationship ─────────────────────────────────────────
    purchase_order = models.ForeignKey(
        "purchases.PurchaseOrder",
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    line_number = models.PositiveIntegerField(default=1)

    # ── Product Fields (Task 20) ────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="po_line_items",
        blank=True,
        null=True,
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="po_line_items",
        blank=True,
        null=True,
    )
    vendor_sku = models.CharField(max_length=100, blank=True, default="")
    product_name = models.CharField(max_length=255)

    # ── Description Fields (Task 21) ───────────────────────────────
    item_description = models.TextField(blank=True, default="")
    is_service = models.BooleanField(default=False)

    # ── Quantity Fields (Task 22) ───────────────────────────────────
    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    quantity_rejected = models.PositiveIntegerField(default=0)
    quantity_cancelled = models.PositiveIntegerField(default=0)

    # ── Pricing Fields (Task 23) ────────────────────────────────────
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    tax_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    # ── Total Field (Task 24) ──────────────────────────────────────
    line_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    # ── Status Field (Task 25) ─────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=LINE_STATUS_CHOICES,
        default=DEFAULT_LINE_STATUS,
    )

    # ── Expected Date (Task 26) ────────────────────────────────────
    expected_delivery_date = models.DateField(blank=True, null=True)

    # ── Warehouse (Task 27) ────────────────────────────────────────
    receiving_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        related_name="po_line_items",
        blank=True,
        null=True,
        db_index=True,
    )
    receiving_location = models.ForeignKey(
        "inventory.StorageLocation",
        on_delete=models.SET_NULL,
        related_name="po_line_items",
        blank=True,
        null=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "PO Line Item"
        verbose_name_plural = "PO Line Items"
        ordering = ["line_number"]
        unique_together = [("purchase_order", "line_number")]
        indexes = [
            models.Index(fields=["status"], name="idx_poli_status"),
            models.Index(fields=["product"], name="idx_poli_product"),
        ]

    def __str__(self):
        po_num = self.purchase_order.po_number if self.purchase_order_id else "?"
        return f"{po_num} Line {self.line_number}"

    def clean(self):
        super().clean()
        if self.receiving_location_id and self.receiving_warehouse_id:
            if self.receiving_location.warehouse_id != self.receiving_warehouse_id:
                raise ValidationError(
                    "Storage location must belong to the receiving warehouse."
                )

    @property
    def quantity_pending(self):
        """Remaining quantity to receive."""
        return self.quantity_ordered - self.quantity_received - self.quantity_cancelled

    def calculate_total(self):
        """Calculate line total from pricing fields."""
        TWO = Decimal("0.01")
        base = self.unit_price * self.quantity_ordered

        if self.discount_percentage > 0:
            discount = base * (self.discount_percentage / Decimal("100"))
        else:
            discount = self.discount_amount * self.quantity_ordered

        subtotal = base - discount
        self.tax_amount = (subtotal * (self.tax_rate / Decimal("100"))).quantize(
            TWO, rounding=ROUND_HALF_UP
        )
        self.line_total = (subtotal + self.tax_amount).quantize(
            TWO, rounding=ROUND_HALF_UP
        )
        return self.line_total

    def save(self, *args, **kwargs):
        self.calculate_total()
        super().save(*args, **kwargs)
