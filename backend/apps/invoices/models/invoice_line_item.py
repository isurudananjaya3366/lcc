"""
Invoice line item model.

Individual line items on an invoice, supporting both product references
and custom/service descriptions.
"""

from decimal import Decimal

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.invoices.constants import DiscountType


PRICE_MAX_DIGITS = 15
PRICE_DECIMAL_PLACES = 2


class InvoiceLineItem(UUIDMixin, TimestampMixin, models.Model):
    """
    Line item on an invoice.

    Represents an individual product, service, or charge on an invoice.
    Supports product FK references for inventory tracking and custom
    descriptions for service/ad-hoc items.
    """

    # ── Parent Invoice ──────────────────────────────────────────────
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.CASCADE,
        related_name="line_items",
        db_index=True,
        help_text="Invoice this line item belongs to",
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Display position/order of line item",
    )

    # ── Product References (Optional) ───────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="invoice_line_items",
        db_index=True,
        help_text="Product reference (optional for custom items)",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="invoice_line_items",
        db_index=True,
        help_text="Product variant reference (if applicable)",
    )
    product_snapshot = models.JSONField(
        default=dict, blank=True,
        help_text="Product data snapshot at time of invoice",
    )

    # ── Description Fields ──────────────────────────────────────────
    description = models.TextField(
        blank=True, default="",
        help_text="Line item description",
    )
    sku = models.CharField(
        max_length=100, blank=True, default="",
        help_text="SKU at time of invoice",
    )

    # ── Quantity ────────────────────────────────────────────────────
    quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        default=Decimal("1.000"),
        help_text="Quantity of items",
    )
    unit_of_measure = models.CharField(
        max_length=50, blank=True, default="unit",
        help_text="Unit of measure (e.g., unit, kg, hour)",
    )

    # ── Pricing ─────────────────────────────────────────────────────
    unit_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Unit price",
    )
    original_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Original price before any adjustments",
    )

    # ── Discount ────────────────────────────────────────────────────
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        blank=True, default="",
        help_text="Discount type for this line",
    )
    discount_value = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Discount value (percentage or fixed amount)",
    )
    discount_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Calculated discount amount",
    )

    # ── Tax ─────────────────────────────────────────────────────────
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
        help_text="Tax rate percentage (e.g., 12.00 for 12% VAT)",
    )
    tax_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Calculated tax amount",
    )
    is_taxable = models.BooleanField(
        default=True,
        help_text="Whether this line item is taxable",
    )
    tax_code = models.CharField(
        max_length=50, blank=True, default="",
        help_text="Tax category code (e.g., STANDARD_RATE, EXEMPT)",
    )
    tax_description = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Tax description (e.g., 'VAT 12%')",
    )

    # ── HSN/SAC Code ────────────────────────────────────────────────
    hsn_code = models.CharField(
        max_length=20, blank=True, default="",
        help_text="HSN/SAC code for product classification",
    )
    hsn_description = models.CharField(
        max_length=200, blank=True, default="",
        help_text="Description of HSN/SAC category",
    )

    # ── Line Total ──────────────────────────────────────────────────
    line_total = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Line total (qty × price - discount + tax)",
    )

    class Meta:
        ordering = ["position"]
        verbose_name = "Invoice Line Item"
        verbose_name_plural = "Invoice Line Items"
        indexes = [
            models.Index(fields=["invoice", "position"], name="inv_line_inv_pos_idx"),
        ]

    def __str__(self):
        desc = self.description or "Item"
        return f"Line {self.position}: {desc} × {self.quantity}"

    def recalculate(self):
        """Recalculate discount, tax, and line total."""
        line_subtotal = self.quantity * self.unit_price

        # Calculate discount
        if self.discount_type == DiscountType.PERCENTAGE and self.discount_value:
            self.discount_amount = line_subtotal * (self.discount_value / Decimal("100"))
        elif self.discount_type == DiscountType.FIXED and self.discount_value:
            self.discount_amount = min(self.discount_value, line_subtotal)
        else:
            self.discount_amount = Decimal("0.00")

        taxable_amount = line_subtotal - self.discount_amount

        # Calculate tax
        if self.is_taxable and self.tax_rate > 0:
            self.tax_amount = (taxable_amount * self.tax_rate / Decimal("100")).quantize(
                Decimal("0.01")
            )
        else:
            self.tax_amount = Decimal("0.00")

        self.line_total = taxable_amount + self.tax_amount
