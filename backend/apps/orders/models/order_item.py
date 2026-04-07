"""
OrderLineItem model for the orders application.

Defines the OrderLineItem model which stores individual line items
within a customer order. Each line item links to a product/variant,
records the ordered/fulfilled/returned quantities, and captures
pricing snapshots.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.orders.constants import DiscountType, OrderLineItemStatus


PRICE_MAX_DIGITS = 12
PRICE_DECIMAL_PLACES = 2
QUANTITY_MAX_DIGITS = 12
QUANTITY_DECIMAL_PLACES = 3


class OrderLineItem(UUIDMixin, TimestampMixin, models.Model):
    """
    Line item within a customer order.

    Each line item represents a single product entry, capturing
    the product reference, quantities (ordered/fulfilled/returned),
    pricing snapshot, and fulfillment status.
    """

    # ── Order FK ────────────────────────────────────────────────────
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="line_items",
        verbose_name="Order",
    )

    # ── Position ────────────────────────────────────────────────────
    position = models.IntegerField(default=0)

    # ── Product References (Task 20) ────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_line_items",
        verbose_name="Product",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_line_items",
        verbose_name="Product Variant",
    )

    # ── Description Snapshot (Task 21) ──────────────────────────────
    item_name = models.CharField(max_length=255, blank=True, default="")
    item_sku = models.CharField(max_length=100, blank=True, default="")
    item_description = models.TextField(blank=True, default="")
    item_category = models.CharField(max_length=255, blank=True, default="")
    item_image_url = models.URLField(max_length=500, blank=True, default="")

    # ── Quantities (Task 22) ────────────────────────────────────────
    quantity_ordered = models.DecimalField(
        max_digits=QUANTITY_MAX_DIGITS,
        decimal_places=QUANTITY_DECIMAL_PLACES,
        default=1,
        validators=[MinValueValidator(Decimal("0.001"))],
    )
    quantity_fulfilled = models.DecimalField(
        max_digits=QUANTITY_MAX_DIGITS,
        decimal_places=QUANTITY_DECIMAL_PLACES,
        default=0,
    )
    quantity_returned = models.DecimalField(
        max_digits=QUANTITY_MAX_DIGITS,
        decimal_places=QUANTITY_DECIMAL_PLACES,
        default=0,
    )
    quantity_cancelled = models.DecimalField(
        max_digits=QUANTITY_MAX_DIGITS,
        decimal_places=QUANTITY_DECIMAL_PLACES,
        default=0,
    )

    # ── Pricing (Task 23) ──────────────────────────────────────────
    unit_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
    )
    original_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
    )
    cost_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
    )
    currency = models.CharField(max_length=3, default="LKR")

    # ── Discount (Task 24) ─────────────────────────────────────────
    discount_type = models.CharField(
        max_length=20, choices=DiscountType.choices, blank=True, default=""
    )
    discount_value = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    discount_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    discount_reason = models.CharField(max_length=255, blank=True, default="")

    # ── Tax (Task 25) ──────────────────────────────────────────────
    is_taxable = models.BooleanField(default=True)
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    tax_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    tax_code = models.CharField(max_length=50, blank=True, default="")

    # ── Line Total (Task 26) ───────────────────────────────────────
    line_total = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )

    # ── Status & Fulfillment (Task 27) ─────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=OrderLineItemStatus.choices,
        default=OrderLineItemStatus.PENDING,
    )
    allocated_at = models.DateTimeField(null=True, blank=True)
    picked_at = models.DateTimeField(null=True, blank=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # ── Warehouse References (Task 28) ─────────────────────────────
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_line_items",
    )
    location = models.ForeignKey(
        "inventory.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_line_items",
    )
    picker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="picked_order_items",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "orders_orderlineitem"
        verbose_name = "Order Line Item"
        verbose_name_plural = "Order Line Items"
        ordering = ["position", "created_on"]
        indexes = [
            models.Index(
                fields=["order", "product"], name="idx_orderline_order_product"
            ),
            models.Index(
                fields=["order", "position"], name="idx_orderline_order_pos"
            ),
            models.Index(
                fields=["status"], name="idx_orderline_status"
            ),
        ]

    def __str__(self):
        name = self.item_name or (str(self.product) if self.product_id else "Item")
        return f"{self.quantity_ordered}x {name}"

    def recalculate(self):
        """Recalculate line totals from pricing fields."""
        subtotal = self.quantity_ordered * self.unit_price
        # Apply discount
        if self.discount_type == DiscountType.PERCENTAGE and self.discount_value:
            self.discount_amount = (
                subtotal * self.discount_value / Decimal("100")
            ).quantize(Decimal("0.01"))
        elif self.discount_type == DiscountType.FIXED and self.discount_value:
            self.discount_amount = min(self.discount_value, subtotal)
        else:
            self.discount_amount = Decimal("0")
        after_discount = subtotal - self.discount_amount
        # Apply tax
        if self.is_taxable and self.tax_rate:
            self.tax_amount = (
                after_discount * self.tax_rate / Decimal("100")
            ).quantize(Decimal("0.01"))
        else:
            self.tax_amount = Decimal("0")
        self.line_total = after_discount + self.tax_amount

    def snapshot_from_product(self):
        """Populate snapshot fields from the linked product/variant."""
        product = self.variant or self.product
        if not product:
            return
        self.item_name = getattr(product, "name", "") or ""
        self.item_sku = getattr(product, "sku", "") or ""
        self.item_description = getattr(product, "description", "") or ""
        if hasattr(product, "category") and product.category:
            self.item_category = str(product.category)

    @property
    def subtotal(self):
        """quantity_ordered × unit_price before discounts and tax."""
        return self.quantity_ordered * self.unit_price

    @property
    def quantity_remaining(self):
        """Quantity not yet fulfilled."""
        return self.quantity_ordered - self.quantity_fulfilled

    @property
    def is_fully_fulfilled(self):
        return self.quantity_fulfilled >= self.quantity_ordered

    @property
    def product_display(self):
        if self.item_name:
            return self.item_name
        if self.variant_id:
            return str(self.variant)
        if self.product_id:
            return str(self.product)
        return "Custom Item"

    def save(self, *args, **kwargs):
        # Auto-set position if not set
        if not self.position and self.order_id:
            max_pos = OrderLineItem.objects.filter(order=self.order).aggregate(
                m=models.Max("position")
            )["m"]
            self.position = (max_pos or 0) + 1
        super().save(*args, **kwargs)
