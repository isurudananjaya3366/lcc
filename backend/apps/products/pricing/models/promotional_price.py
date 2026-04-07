"""
PromotionalPrice model – rule-based discounts with conditions.

Supports percentage-off, fixed-off, and fixed-price discount types
with optional minimum quantity / order value conditions.
"""

from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.models import BaseModel

from ..fields import PriceField
from ..utils import format_lkr


class PromotionalPrice(BaseModel):
    """
    Condition-based promotional discount that can target
    specific products and/or categories.
    """

    class DiscountType(models.TextChoices):
        PERCENTAGE_OFF = "PERCENTAGE_OFF", "Percentage Off"
        FIXED_OFF = "FIXED_OFF", "Fixed Amount Off"
        FIXED_PRICE = "FIXED_PRICE", "Fixed Price"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    # Targeting
    products = models.ManyToManyField(
        "products.Product", blank=True, related_name="promotional_prices"
    )
    categories = models.ManyToManyField(
        "products.Category", blank=True, related_name="promotional_prices"
    )

    # Conditions
    min_quantity = models.PositiveIntegerField(null=True, blank=True)
    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Cap for percentage-based discounts.",
    )

    priority = models.IntegerField(default=0)
    is_stackable = models.BooleanField(default=False, help_text="Can combine with other promotions.")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promotions_created",
    )

    class Meta:
        db_table = "pricing_promotional"
        ordering = ["-priority", "-start_datetime"]
        indexes = [
            models.Index(fields=["start_datetime", "end_datetime"], name="idx_promo_dates"),
            models.Index(fields=["is_active", "priority"], name="idx_promo_active_prio"),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(end_datetime__gt=F("start_datetime")),
                name="promo_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_discount_type_display()})"

    # ── Properties ─────────────────────────────────────────────

    @property
    def is_currently_active(self) -> bool:
        now = timezone.now()
        return self.is_active and self.start_datetime <= now <= self.end_datetime

    # ── Targeting ──────────────────────────────────────────────

    def applies_to_product(self, product) -> bool:
        """Does this promo apply to *product*?"""
        # No targeting = applies to all
        has_products = self.products.exists()
        has_categories = self.categories.exists()
        if not has_products and not has_categories:
            return True
        if has_products and self.products.filter(pk=product.pk).exists():
            return True
        if has_categories:
            product_cats = set()
            if hasattr(product, "category_id") and product.category_id:
                product_cats.add(product.category_id)
            if hasattr(product, "categories"):
                product_cats.update(product.categories.values_list("pk", flat=True))
            if self.categories.filter(pk__in=product_cats).exists():
                return True
        return False

    # ── Condition checking ─────────────────────────────────────

    def check_conditions(self, product, customer=None, quantity=1, order_value=None):
        """
        Evaluate all conditions. Returns PromotionalConditionResult.
        """
        if not self.is_currently_active:
            return PromotionalConditionResult(False, "Promotion is not active.")
        if not self.applies_to_product(product):
            return PromotionalConditionResult(False, "Product not eligible for this promotion.")
        if self.min_quantity and quantity < self.min_quantity:
            return PromotionalConditionResult(False, f"Minimum quantity {self.min_quantity} not met.")
        if self.min_order_value and order_value is not None:
            if order_value < self.min_order_value:
                return PromotionalConditionResult(
                    False, f"Minimum order value {format_lkr(self.min_order_value)} not met."
                )
        return PromotionalConditionResult(True, "All conditions met.")

    def get_conditions_display(self) -> list[str]:
        conditions = []
        if self.min_quantity:
            conditions.append(f"Buy {self.min_quantity}+ items")
        if self.min_order_value:
            conditions.append(f"Min order: {format_lkr(self.min_order_value)}")
        if self.max_discount_amount:
            conditions.append(f"Max discount: {format_lkr(self.max_discount_amount)}")
        if self.products.exists():
            conditions.append(f"For {self.products.count()} specific product(s)")
        if self.categories.exists():
            conditions.append(f"For {self.categories.count()} category(ies)")
        return conditions

    # ── Calculation ────────────────────────────────────────────

    def calculate_discounted_price(self, original_price: Decimal, quantity: int = 1) -> Decimal | None:
        """
        Apply the discount. Returns the discounted unit price, or None
        if conditions are not met.
        """
        if self.min_quantity and quantity < self.min_quantity:
            return None

        if self.discount_type == self.DiscountType.PERCENTAGE_OFF:
            discount = original_price * (self.discount_value / Decimal("100"))
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
            return max(Decimal("0"), original_price - discount)

        if self.discount_type == self.DiscountType.FIXED_OFF:
            return max(Decimal("0"), original_price - self.discount_value)

        if self.discount_type == self.DiscountType.FIXED_PRICE:
            return self.discount_value

        return None

    # ── Validation ─────────────────────────────────────────────

    def clean(self):
        super().clean()
        errors = {}
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                errors["end_datetime"] = "End must be after start."
        if self.discount_type == self.DiscountType.PERCENTAGE_OFF:
            if self.discount_value is not None and not (0 <= self.discount_value <= 100):
                errors["discount_value"] = "Percentage must be between 0 and 100."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)


@dataclass
class PromotionalConditionResult:
    is_met: bool
    reason: str

    def __bool__(self):
        return self.is_met
