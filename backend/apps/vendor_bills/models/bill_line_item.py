"""BillLineItem model for individual line items on a vendor bill."""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteMixin, TimestampMixin, UUIDMixin


class BillLineItem(UUIDMixin, TimestampMixin, models.Model):
    """Represents a single line item on a vendor bill."""

    # Core fields (Task 17)
    vendor_bill = models.ForeignKey(
        "vendor_bills.VendorBill",
        on_delete=models.CASCADE,
        related_name="line_items",
        help_text="The vendor bill this line item belongs to",
    )
    line_number = models.PositiveIntegerField(
        help_text="Line item sequence number",
    )

    # Product fields (Task 18)
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bill_line_items",
        help_text="Product reference (optional for non-catalog items)",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bill_line_items",
        help_text="Product variant reference (optional)",
    )
    vendor_sku = models.CharField(
        max_length=100,
        blank=True,
        help_text="Vendor's SKU/part number",
    )

    # Description (Task 19)
    item_description = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Description of the item (auto-populated from product or manual)",
    )

    # Quantity fields (Task 20)
    quantity = models.PositiveIntegerField(
        help_text="Billed quantity",
    )
    quantity_ordered = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity ordered from PO (for matching)",
    )
    quantity_received = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity received from GRN (for matching)",
    )

    # Pricing fields (Task 21)
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original unit price from PO",
    )
    billed_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Price on the vendor's bill",
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Tax rate as a percentage (0-100)",
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Computed tax amount for this line",
    )

    # Line total (Task 22)
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Computed: (quantity * billed_price) + tax_amount",
    )

    # PO Reference (Task 23)
    po_line = models.ForeignKey(
        "purchases.POLineItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bill_line_items",
        help_text="Matched PO line item",
    )

    # GRN Reference (Task 24)
    grn_line = models.ForeignKey(
        "purchases.GRNLineItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bill_line_items",
        help_text="Matched GRN line item",
    )

    class Meta:
        ordering = ["line_number"]
        unique_together = [("vendor_bill", "line_number")]
        verbose_name = "Bill Line Item"
        verbose_name_plural = "Bill Line Items"
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="billlineitem_qty_positive",
            ),
            models.CheckConstraint(
                check=models.Q(billed_price__gt=Decimal("0")),
                name="billlineitem_billed_price_positive",
            ),
            models.CheckConstraint(
                check=models.Q(tax_rate__gte=Decimal("0"), tax_rate__lte=Decimal("100")),
                name="billlineitem_tax_rate_range",
            ),
        ]

    def __str__(self):
        desc = self.item_description or str(self.product or "Item")
        return f"Line {self.line_number}: {desc}"

    def calculate_line_total(self):
        """Calculate the line total: (quantity * billed_price) + tax_amount."""
        base = Decimal(str(self.quantity)) * self.billed_price
        self.tax_amount = base * (self.tax_rate / Decimal("100"))
        self.line_total = base + self.tax_amount

    def save(self, *args, **kwargs):
        self.calculate_line_total()
        super().save(*args, **kwargs)
        # Trigger bill recalculation
        self.vendor_bill.recalculate_from_lines()

    @property
    def quantity_variance(self):
        """Variance between ordered and billed quantity."""
        if self.quantity_ordered is None:
            return None
        return self.quantity - self.quantity_ordered

    @property
    def price_variance(self):
        """Variance between PO unit price and billed price."""
        if self.unit_price is None:
            return None
        return self.billed_price - self.unit_price

    @property
    def is_3way_matched(self):
        """Check if this line has both PO and GRN references."""
        return self.po_line is not None and self.grn_line is not None

    def clean(self):
        """Validate line item data."""
        from django.core.exceptions import ValidationError

        if not self.product and not self.item_description:
            raise ValidationError(
                "Either a product or item description is required."
            )
