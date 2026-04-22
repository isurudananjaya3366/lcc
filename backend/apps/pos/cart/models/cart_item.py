from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import BaseModel
from apps.pos.constants import DISCOUNT_TYPE_FIXED, DISCOUNT_TYPE_PERCENT

MAX_CART_ITEM_QUANTITY = Decimal("9999.999")


class POSCartItemManager(models.Manager):
    """Manager for POSCartItem."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_deleted=False)

    def for_cart(self, cart):
        return self.get_queryset().filter(cart=cart)


class POSCartItem(BaseModel):
    """
    Line item in a POS cart.

    Represents a product (or variant) added to the cart with
    quantity, pricing, discount, and tax information.
    """

    # ── Core References ───────────────────────────────────────────────────
    cart = models.ForeignKey(
        "pos.POSCart",
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="pos_cart_items",
        db_index=True,
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="pos_cart_items",
    )
    line_number = models.PositiveIntegerField(default=0)

    # ── Quantity ──────────────────────────────────────────────────────────
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal("1.000"),
        validators=[MinValueValidator(Decimal("0.001"))],
    )

    # ── Pricing ───────────────────────────────────────────────────────────
    original_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    # ── Line Discount ─────────────────────────────────────────────────────
    discount_type = models.CharField(
        max_length=10,
        choices=[
            (DISCOUNT_TYPE_PERCENT, "Percentage"),
            (DISCOUNT_TYPE_FIXED, "Fixed Amount"),
        ],
        null=True,
        blank=True,
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
    )
    discount_reason = models.CharField(max_length=200, blank=True, default="")
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    # ── Tax ───────────────────────────────────────────────────────────────
    is_taxable = models.BooleanField(default=True)
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )
    tax_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    # ── Managers ──────────────────────────────────────────────────────────
    objects = POSCartItemManager()
    all_with_deleted = models.Manager()

    class Meta:
        db_table = "pos_cart_item"
        verbose_name = "POS Cart Item"
        verbose_name_plural = "POS Cart Items"
        ordering = ["line_number", "created_on"]
        indexes = [
            models.Index(
                fields=["cart", "product"], name="idx_pos_cartitem_cart_prod"
            ),
            models.Index(
                fields=["cart", "line_number"],
                name="idx_pos_cartitem_cart_line",
            ),
        ]

    def __str__(self):
        qty = self.formatted_quantity
        return f"{qty}x {self.product_display}"

    def save(self, *args, **kwargs):
        self.calculate_line_total()
        super().save(*args, **kwargs)

    # ── Properties ────────────────────────────────────────────────────────
    @property
    def product_display(self):
        if self.variant:
            return f"{self.product.name} - {self.variant}"
        return self.product.name

    @property
    def is_variant_item(self):
        return self.variant_id is not None

    @property
    def formatted_quantity(self):
        return f"{self.quantity:g}"

    @property
    def has_discount(self):
        return (
            self.discount_type is not None
            and self.discount_value
            and self.discount_value > 0
        )

    @property
    def price_difference(self):
        return self.original_price - self.unit_price

    @property
    def total_discount_amount(self):
        return self.discount_amount * self.quantity

    @property
    def line_total_with_tax(self):
        return self.line_total + self.tax_amount

    @property
    def formatted_unit_price(self):
        return f"\u20A8 {self.unit_price:,.2f}"

    @property
    def formatted_line_total(self):
        return f"\u20A8 {self.line_total:,.2f}"

    @property
    def formatted_discount(self):
        """Format discount for display."""
        if not self.has_discount:
            return ""
        if self.discount_type == DISCOUNT_TYPE_PERCENT:
            return f"{self.discount_value}% (\u20A8 {self.discount_amount:,.2f})"
        return f"\u20A8 {self.discount_amount:,.2f}"

    @property
    def formatted_tax_rate(self):
        return f"{self.tax_rate}%"

    @property
    def formatted_tax_amount(self):
        return f"\u20A8 {self.tax_amount:,.2f}"

    # ── Pricing Methods ───────────────────────────────────────────────────
    def set_prices_from_product(self):
        """Copy price from the product or variant."""
        if self.variant and hasattr(self.variant, "price") and self.variant.price:
            price = self.variant.price
        elif hasattr(self.product, "base_price") and self.product.base_price:
            price = self.product.base_price
        elif hasattr(self.product, "selling_price") and self.product.selling_price:
            price = self.product.selling_price
        else:
            price = Decimal("0.00")
        self.original_price = price
        self.unit_price = price

    def calculate_line_total(self):
        """Calculate line total and tax from quantity and unit price."""
        self.line_total = (self.quantity * self.unit_price).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        self.calculate_tax()

    def calculate_tax(self):
        """Calculate tax amount from line total and tax rate."""
        if self.is_taxable and self.tax_rate > 0:
            self.tax_amount = (
                self.line_total * self.tax_rate / 100
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            self.tax_amount = Decimal("0.00")

    def set_tax_from_product(self):
        """Set tax rate from the product's tax class."""
        if hasattr(self.product, "tax_class") and self.product.tax_class:
            self.tax_rate = getattr(
                self.product.tax_class, "rate", Decimal("0.00")
            )
        else:
            self.tax_rate = Decimal("0.00")

    def calculate_discount_amount(self):
        """Calculate and return the discount amount without saving."""
        if not self.has_discount:
            return Decimal("0.00")
        if self.discount_type == DISCOUNT_TYPE_PERCENT:
            return (
                self.original_price * self.discount_value / 100
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif self.discount_type == DISCOUNT_TYPE_FIXED:
            return min(self.discount_value, self.original_price)
        return Decimal("0.00")

    def validate_stock_availability(self, quantity=None):
        """Check if requested quantity is available in stock."""
        qty = quantity if quantity is not None else self.quantity
        target = self.variant if self.variant else self.product
        if hasattr(target, "stock_quantity"):
            if target.stock_quantity < qty:
                raise ValidationError(
                    f"Insufficient stock. Available: {target.stock_quantity}, "
                    f"Requested: {qty}"
                )
        return True

    # ── Discount Methods ──────────────────────────────────────────────────
    def apply_discount(self, discount_type, discount_value, reason=None):
        """Apply a discount to this line item."""
        self.discount_type = discount_type
        self.discount_value = Decimal(str(discount_value))

        if discount_type == DISCOUNT_TYPE_PERCENT:
            if not (0 <= self.discount_value <= 100):
                raise ValidationError(
                    "Percentage discount must be between 0 and 100."
                )
            self.discount_amount = (
                self.original_price * self.discount_value / 100
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif discount_type == DISCOUNT_TYPE_FIXED:
            if self.discount_value > self.original_price:
                raise ValidationError(
                    "Fixed discount cannot exceed the original price."
                )
            self.discount_amount = self.discount_value
        else:
            self.discount_amount = Decimal("0.00")

        self.unit_price = self.original_price - self.discount_amount
        if reason:
            self.discount_reason = reason

        self.calculate_line_total()
        self.save()

    def remove_discount(self):
        """Remove discount and restore original price."""
        self.discount_type = None
        self.discount_value = Decimal("0.00")
        self.discount_amount = Decimal("0.00")
        self.discount_reason = ""
        self.unit_price = self.original_price
        self.calculate_line_total()
        self.save()
