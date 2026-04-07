"""
QuoteLineItem model for individual line items within a quote.

Tasks 19-28, 36: Line item model with product references, pricing,
discounts, tax, totals, ordering, and price snapshotting.
"""

from contextlib import contextmanager
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone


class QuoteLineItem(models.Model):
    """Individual line item within a quote."""

    # ── UOM Choices ──────────────────────────────────────────────
    UOM_CHOICES = [
        ("unit", "Unit"),
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("m", "Meter"),
        ("cm", "Centimeter"),
        ("sqm", "Square Meter"),
        ("hour", "Hour"),
        ("day", "Day"),
        ("month", "Month"),
    ]

    # ── Discount Choices ─────────────────────────────────────────
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"
    DISCOUNT_TYPE_CHOICES = [
        ("PERCENTAGE", "Percentage"),
        ("FIXED", "Fixed Amount"),
    ]

    # ── Core References ──────────────────────────────────────────
    quote = models.ForeignKey(
        "quotes.Quote",
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    position = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Display order of line item",
    )

    # ── Product References ───────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="quote_line_items",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="quote_line_items",
    )
    product_name = models.CharField(
        max_length=255,
        help_text="Product name snapshot at time of quote creation",
    )

    # ── Custom Item Fields ───────────────────────────────────────
    custom_description = models.TextField(
        blank=True,
        help_text="Custom description for non-product items",
    )
    custom_sku = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom SKU for non-product items",
    )

    # ── Quantity Fields ──────────────────────────────────────────
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("1.000"),
        validators=[MinValueValidator(Decimal("0.001"))],
        help_text="Quantity of items",
    )
    unit_of_measure = models.CharField(
        max_length=50,
        default="unit",
        help_text="Unit of measure (unit, kg, hour, sqm, etc.)",
    )

    # ── Pricing Fields ───────────────────────────────────────────
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Price per unit (LKR)",
    )
    original_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Original price before discounts",
    )
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost price for margin calculation",
    )

    # ── Discount Fields ──────────────────────────────────────────
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Type of discount applied",
    )
    discount_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Discount percentage or fixed amount",
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        help_text="Calculated discount amount in LKR",
    )

    # ── Tax Fields ───────────────────────────────────────────────
    is_taxable = models.BooleanField(
        default=True,
        help_text="Whether this item is subject to tax",
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Tax rate percentage (e.g., 15 for 15% VAT)",
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        help_text="Calculated tax amount in LKR",
    )

    # ── Total Field ──────────────────────────────────────────────
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        help_text="Total for this line (quantity × price - discount + tax)",
    )

    # ── Notes ────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes or instructions for this line item",
    )

    # ── Price Snapshot Tracking ──────────────────────────────────
    price_snapshot_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When product prices were captured",
    )

    # ── Timestamps ───────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotes_quotelineitem"
        ordering = ["position", "created_at"]
        verbose_name = "Quote Line Item"
        verbose_name_plural = "Quote Line Items"
        indexes = [
            models.Index(
                fields=["quote", "position"],
                name="idx_qli_quote_position",
            ),
        ]

    def __str__(self):
        name = self.product_name or "Item"
        qty = self.quantity.normalize()
        return f"Quote {self.quote.quote_number} - {name} (Qty: {qty})"

    # ── Properties ───────────────────────────────────────────────

    @property
    def is_product_based(self):
        return self.product_id is not None

    @property
    def is_custom_item(self):
        return self.product_id is None

    @property
    def get_subtotal(self):
        return self.quantity * self.unit_price

    @property
    def get_taxable_amount(self):
        return (self.quantity * self.unit_price) - self.discount_amount

    @property
    def get_tax_percentage(self):
        return f"{self.tax_rate.normalize()}%"

    @property
    def get_margin(self):
        if self.cost_price is None:
            return None
        return self.unit_price - self.cost_price

    @property
    def get_margin_percentage(self):
        if self.cost_price is None or self.cost_price == 0:
            return None
        return ((self.unit_price - self.cost_price) / self.cost_price) * 100

    @property
    def get_discounted_price(self):
        if self.quantity == 0:
            return self.unit_price
        return self.unit_price - (self.discount_amount / self.quantity)

    @property
    def get_line_subtotal_with_discount(self):
        return (self.quantity * self.unit_price) - self.discount_amount

    @property
    def has_discount(self):
        return self.discount_amount > 0

    @property
    def has_notes(self):
        return bool(self.notes and self.notes.strip())

    @property
    def get_line_total_formatted(self):
        return f"₨ {self.line_total:,.2f}"

    @property
    def breakdown(self):
        return {
            "subtotal": self.get_subtotal,
            "discount_amount": self.discount_amount,
            "taxable_amount": self.get_taxable_amount,
            "tax_amount": self.tax_amount,
            "line_total": self.line_total,
        }

    # ── Description / SKU helpers ────────────────────────────────

    def get_description(self):
        if self.product_id is not None:
            return getattr(self.product, "description", "") or ""
        return self.custom_description or ""

    def get_sku(self):
        if self.variant_id is not None:
            return getattr(self.variant, "sku", "") or ""
        if self.product_id is not None:
            return getattr(self.product, "sku", "") or ""
        return self.custom_sku or ""

    def get_display_name(self):
        return self.product_name or ""

    def get_quantity_display(self):
        qty = self.quantity.normalize()
        return f"{qty} {self.unit_of_measure}"

    def get_notes_preview(self, length=50):
        if not self.notes:
            return ""
        if len(self.notes) <= length:
            return self.notes
        return self.notes[:length] + "..."

    # ── Calculation Methods ──────────────────────────────────────

    def calculate_discount_amount(self):
        subtotal = self.quantity * self.unit_price
        if self.discount_type == self.PERCENTAGE:
            self.discount_amount = subtotal * (self.discount_value / Decimal("100"))
        elif self.discount_type == self.FIXED:
            self.discount_amount = self.discount_value
        else:
            self.discount_amount = Decimal("0.00")
        return self.discount_amount

    def calculate_tax_amount(self):
        taxable_base = (self.quantity * self.unit_price) - self.discount_amount
        if self.is_taxable and self.tax_rate > 0:
            self.tax_amount = taxable_base * (self.tax_rate / Decimal("100"))
        else:
            self.tax_amount = Decimal("0.00")
        return self.tax_amount

    def calculate_line_total(self):
        self.line_total = (
            (self.quantity * self.unit_price) - self.discount_amount + self.tax_amount
        )
        return self.line_total

    def recalculate(self):
        """Recalculate all computed fields in memory (does NOT save)."""
        self.calculate_discount_amount()
        self.calculate_tax_amount()
        self.calculate_line_total()
        return self

    # ── Price Snapshotting ───────────────────────────────────────

    def snapshot_from_product(self, product, variant=None):
        """Snapshot current product prices into line item fields."""
        self.product = product
        self.variant = variant
        self.product_name = product.name

        self.unit_price = getattr(product, "selling_price", None) or Decimal("0.00")
        self.original_price = self.unit_price
        self.cost_price = getattr(product, "cost_price", None)

        # Tax from product's tax_class if available
        tax_class = getattr(product, "tax_class", None)
        if tax_class:
            self.tax_rate = getattr(tax_class, "rate", Decimal("0.00")) or Decimal(
                "0.00"
            )
            self.is_taxable = True
        else:
            self.tax_rate = Decimal("0.00")
            self.is_taxable = False

        if not self.price_snapshot_at:
            self.price_snapshot_at = timezone.now()

        return self

    @classmethod
    def create_from_product(cls, quote, product, quantity, variant=None):
        """Create a line item from a product with price snapshot."""
        item = cls(quote=quote, quantity=quantity)
        item.snapshot_from_product(product, variant)
        item.save()
        return item

    def has_price_changed(self):
        """Check if the product's current price differs from snapshot."""
        if not self.product_id:
            return False
        current = getattr(self.product, "selling_price", None) or Decimal("0.00")
        return current != self.unit_price

    def get_price_difference(self):
        """Return difference between current product price and snapshot."""
        if not self.product_id:
            return None
        current = getattr(self.product, "selling_price", None) or Decimal("0.00")
        return current - self.unit_price

    def default_tax_from_product(self, product):
        """Set tax fields from product's tax_class."""
        tax_class = getattr(product, "tax_class", None)
        if tax_class:
            self.tax_rate = getattr(tax_class, "rate", Decimal("0.00")) or Decimal(
                "0.00"
            )
            self.is_taxable = True
        else:
            self.tax_rate = Decimal("0.00")
            self.is_taxable = False

    # ── Ordering Methods ─────────────────────────────────────────

    def auto_position(self):
        """Set position to next available value for this quote."""
        max_pos = (
            QuoteLineItem.objects.filter(quote=self.quote)
            .aggregate(max_pos=models.Max("position"))
            .get("max_pos")
        )
        self.position = (max_pos or 0) + 1

    def move_up(self):
        """Swap position with the previous item."""
        prev = self.get_previous_item()
        if prev:
            with transaction.atomic():
                prev.position, self.position = self.position, prev.position
                prev.save(update_fields=["position"])
                self.save(update_fields=["position"])

    def move_down(self):
        """Swap position with the next item."""
        nxt = self.get_next_item()
        if nxt:
            with transaction.atomic():
                nxt.position, self.position = self.position, nxt.position
                nxt.save(update_fields=["position"])
                self.save(update_fields=["position"])

    def move_to_position(self, target_position):
        """Move this item to a specific position, reordering others."""
        with transaction.atomic():
            items = list(
                QuoteLineItem.objects.filter(quote=self.quote)
                .exclude(pk=self.pk)
                .order_by("position")
            )
            items.insert(target_position, self)
            for idx, item in enumerate(items):
                item.position = idx
            QuoteLineItem.objects.bulk_update(items, ["position"])

    @classmethod
    def reorder_quote_items(cls, quote, item_ids):
        """Bulk reorder items from a list of IDs."""
        with transaction.atomic():
            for idx, item_id in enumerate(item_ids):
                cls.objects.filter(pk=item_id, quote=quote).update(position=idx)

    def get_previous_item(self):
        return (
            QuoteLineItem.objects.filter(quote=self.quote, position__lt=self.position)
            .order_by("-position")
            .first()
        )

    def get_next_item(self):
        return (
            QuoteLineItem.objects.filter(quote=self.quote, position__gt=self.position)
            .order_by("position")
            .first()
        )

    # ── Validation ───────────────────────────────────────────────

    def clean(self):
        errors = {}

        # Variant must belong to product
        if self.variant_id and not self.product_id:
            errors["variant"] = "Product must be set when variant is specified."
        if self.variant_id and self.product_id:
            if self.variant.product_id != self.product_id:
                errors["variant"] = "Variant must belong to the selected product."

        # Custom items require description
        if self.product_id is None and not self.custom_description:
            errors["custom_description"] = "Custom items require a description."

        # Pricing validation
        if self.unit_price < 0:
            errors["unit_price"] = "Unit price cannot be negative."
        if self.cost_price is not None and self.cost_price < 0:
            errors["cost_price"] = "Cost price cannot be negative."

        # Discount validation
        if self.discount_type and self.discount_value <= 0:
            errors["discount_value"] = "Discount value must be positive."
        if self.discount_type == self.PERCENTAGE and self.discount_value > 100:
            errors["discount_value"] = "Percentage discount cannot exceed 100%."

        if errors:
            raise ValidationError(errors)

    # ── Save Override ────────────────────────────────────────────

    def save(self, *args, **kwargs):
        # Auto-position for new items
        if self.pk is None and self.position == 0:
            self.auto_position()

        # Recalculate computed fields
        self.calculate_discount_amount()
        self.calculate_tax_amount()
        self.calculate_line_total()

        super().save(*args, **kwargs)
