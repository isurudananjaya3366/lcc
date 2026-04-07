"""
TieredPricing and VariantTieredPricing models.

Quantity-based price breaks for wholesale / volume purchases.
Supports both INCREMENTAL (graduated) and ALL_UNITS (single-tier)
calculation modes.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, F

from apps.core.models import BaseModel

from ..fields import PriceField
from ..utils import format_lkr

TIER_TYPE_CHOICES = [
    ("all_units", "All Units (one price for entire order)"),
    ("incremental", "Incremental (graduated, each tier separately)"),
]


class TieredPricing(BaseModel):
    """
    Quantity-based price break for a Product.

    Each tier specifies a [min_quantity … max_quantity] range and the
    per-unit price that applies.  ``max_quantity=None`` means unlimited.
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="tiered_prices",
        verbose_name="Product",
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Tier Name",
        help_text="Optional label, e.g. 'Wholesale', 'Bulk'.",
    )
    description = models.TextField(blank=True, default="")
    min_quantity = models.PositiveIntegerField(
        verbose_name="Min Quantity",
        help_text="Minimum order quantity for this tier.",
    )
    max_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Max Quantity",
        help_text="Maximum quantity. Leave blank for unlimited.",
    )
    tier_price = PriceField(
        verbose_name="Tier Price (per unit)",
        help_text="Per-unit price in LKR for this quantity range.",
    )
    tier_type = models.CharField(
        max_length=20,
        choices=TIER_TYPE_CHOICES,
        default="all_units",
        verbose_name="Tier Type",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        verbose_name="Discount %",
        help_text="Pre-calculated discount from base price.",
    )

    class Meta:
        db_table = "pricing_tiered_pricing"
        verbose_name = "Tiered Pricing"
        verbose_name_plural = "Tiered Pricing Rules"
        ordering = ["product", "min_quantity"]
        indexes = [
            models.Index(fields=["product", "min_quantity"], name="idx_tp_prod_min"),
            models.Index(fields=["product", "is_active"], name="idx_tp_prod_active"),
            models.Index(fields=["is_active", "min_quantity"], name="idx_tp_active_min"),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(min_quantity__gte=1),
                name="chk_tp_min_gte_1",
            ),
            models.CheckConstraint(
                check=Q(max_quantity__isnull=True) | Q(max_quantity__gt=F("min_quantity")),
                name="chk_tp_max_gt_min",
            ),
            models.CheckConstraint(
                check=Q(tier_price__gt=0),
                name="chk_tp_price_gt_0",
            ),
        ]
        permissions = [
            ("manage_tiered_pricing", "Can manage tiered pricing"),
            ("view_tier_reports", "Can view tier reports"),
        ]

    def __str__(self):
        product_name = getattr(self.product, "name", "?") if self.product_id else "?"
        return f"{product_name}: {self.get_tier_range()} at {format_lkr(self.tier_price)}"

    # ── Helpers ────────────────────────────────────────────────

    def get_tier_range(self) -> str:
        if self.max_quantity:
            return f"{self.min_quantity}-{self.max_quantity} units"
        return f"{self.min_quantity}+ units"

    def is_quantity_in_tier(self, quantity: int) -> bool:
        if quantity < self.min_quantity:
            return False
        if self.max_quantity and quantity > self.max_quantity:
            return False
        return True

    def get_discount_percentage(self, base_price: Decimal) -> Decimal:
        if not base_price:
            return Decimal("0")
        return ((base_price - self.tier_price) / base_price * 100).quantize(Decimal("0.01"))

    # ── Lookup ─────────────────────────────────────────────────

    @classmethod
    def get_tier_for_quantity(cls, product, quantity: int):
        """Return the matching active tier for a product + quantity, or None."""
        return (
            cls.objects.filter(
                product=product,
                is_active=True,
                min_quantity__lte=quantity,
            )
            .filter(Q(max_quantity__isnull=True) | Q(max_quantity__gte=quantity))
            .order_by("-min_quantity")
            .first()
        )

    @classmethod
    def get_price_for_quantity(cls, product, quantity: int) -> Decimal | None:
        tier = cls.get_tier_for_quantity(product, quantity)
        return tier.tier_price if tier else None

    @classmethod
    def get_all_tiers(cls, product):
        return cls.objects.filter(product=product, is_active=True).order_by("min_quantity")

    # ── Display helpers ────────────────────────────────────────

    @classmethod
    def get_tier_table(cls, product, base_price: Decimal | None = None) -> list[dict]:
        """Return list-of-dicts suitable for rendering a tier table."""
        tiers = cls.get_all_tiers(product)
        result = []
        for t in tiers:
            entry = {
                "name": t.name or t.get_tier_range(),
                "range": t.get_tier_range(),
                "price": t.tier_price,
                "formatted_price": format_lkr(t.tier_price),
                "tier_type": t.tier_type,
            }
            if base_price:
                entry["discount"] = t.get_discount_percentage(base_price)
                entry["savings"] = base_price - t.tier_price
            result.append(entry)
        return result

    def get_next_tier_info(self) -> dict | None:
        """Info about the next tier break (e.g. 'Buy 10 more to save …')."""
        next_tier = (
            TieredPricing.objects.filter(
                product=self.product,
                is_active=True,
                min_quantity__gt=(self.max_quantity or self.min_quantity),
            )
            .order_by("min_quantity")
            .first()
        )
        if not next_tier:
            return None
        return {
            "quantity_needed": next_tier.min_quantity,
            "price": next_tier.tier_price,
            "savings": self.tier_price - next_tier.tier_price,
        }

    # ── Copy / bulk ────────────────────────────────────────────

    @classmethod
    def has_tiered_pricing(cls, product) -> bool:
        """Return True if the product has at least one active tier."""
        return cls.objects.filter(product=product, is_active=True, is_deleted=False).exists()

    @classmethod
    def copy_tiers(cls, source_product, target_product):
        """Copy all active tiers from one product to another."""
        tiers = cls.get_all_tiers(source_product)
        created = []
        for t in tiers:
            new = cls(
                product=target_product,
                name=t.name,
                description=t.description,
                min_quantity=t.min_quantity,
                max_quantity=t.max_quantity,
                tier_price=t.tier_price,
                tier_type=t.tier_type,
                discount_percentage=t.discount_percentage,
            )
            new.save()
            created.append(new)
        return created

    @classmethod
    def copy_tiers_to_variant(cls, product, variant, overwrite: bool = False):
        """Copy product-level tiers to a variant's VariantTieredPricing."""
        from .tiered_pricing import VariantTieredPricing  # noqa: F811 - same module

        if overwrite:
            VariantTieredPricing.objects.filter(variant=variant).delete()
        tiers = cls.get_all_tiers(product)
        created = []
        for t in tiers:
            vt = VariantTieredPricing(
                variant=variant,
                name=t.name,
                min_quantity=t.min_quantity,
                max_quantity=t.max_quantity,
                tier_price=t.tier_price,
                tier_type=t.tier_type,
                discount_percentage=t.discount_percentage,
            )
            vt.save()
            created.append(vt)
        return created

    # ── Tier set validation ────────────────────────────────────

    @classmethod
    def validate_tier_set(cls, product) -> dict:
        """Validate all tiers for a product and return a report."""
        tiers = list(cls.get_all_tiers(product))
        errors = []
        warnings = []
        for i, t in enumerate(tiers):
            for j, other in enumerate(tiers):
                if i >= j:
                    continue
                if _ranges_overlap(t, other):
                    errors.append(f"Tier '{t.get_tier_range()}' overlaps with '{other.get_tier_range()}'")
        # Check for gaps
        for i in range(len(tiers) - 1):
            current_max = tiers[i].max_quantity
            next_min = tiers[i + 1].min_quantity
            if current_max and next_min > current_max + 1:
                warnings.append(f"Gap between {tiers[i].get_tier_range()} and {tiers[i+1].get_tier_range()}")
        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    # ── Validation ─────────────────────────────────────────────

    def clean(self):
        super().clean()
        errors = {}
        if self.min_quantity is not None and self.min_quantity < 1:
            errors["min_quantity"] = "Minimum quantity must be at least 1."
        if self.max_quantity is not None and self.min_quantity is not None:
            if self.max_quantity <= self.min_quantity:
                errors["max_quantity"] = "Maximum must be greater than minimum."
        if self.tier_price is not None and self.tier_price <= 0:
            errors["tier_price"] = "Tier price must be positive."
        # Overlap check
        if self.product_id:
            overlap = self._check_overlap()
            if overlap:
                errors["min_quantity"] = f"Quantity range overlaps with existing tier: {overlap.get_tier_range()}"
        if errors:
            raise ValidationError(errors)

    def _check_overlap(self):
        qs = TieredPricing.objects.filter(
            product=self.product, is_active=True
        ).exclude(pk=self.pk)
        for t in qs:
            if _ranges_overlap(self, t):
                return t
        return None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class VariantTieredPricing(BaseModel):
    """
    Variant-specific tiered pricing that overrides product-level tiers.

    When a variant has its own tiers the product's tiers are ignored
    for that variant.
    """

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="tiered_pricing",
        verbose_name="Variant",
    )
    name = models.CharField(max_length=100, blank=True, default="")
    min_quantity = models.PositiveIntegerField(verbose_name="Min Quantity")
    max_quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name="Max Quantity")
    tier_price = PriceField(verbose_name="Tier Price (per unit)")
    tier_type = models.CharField(
        max_length=20,
        choices=TIER_TYPE_CHOICES,
        default="all_units",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )

    class Meta:
        db_table = "pricing_variant_tiered"
        verbose_name = "Variant Tiered Pricing"
        verbose_name_plural = "Variant Tiered Pricings"
        ordering = ["variant", "min_quantity"]
        indexes = [
            models.Index(fields=["variant", "min_quantity"], name="idx_vtp_var_min"),
            models.Index(fields=["variant", "is_active"], name="idx_vtp_var_active"),
        ]
        constraints = [
            models.CheckConstraint(check=Q(min_quantity__gte=1), name="chk_vtp_min_gte_1"),
            models.CheckConstraint(
                check=Q(max_quantity__isnull=True) | Q(max_quantity__gt=F("min_quantity")),
                name="chk_vtp_max_gt_min",
            ),
        ]

    def __str__(self):
        sku = getattr(self.variant, "sku", "?") if self.variant_id else "?"
        rng = self.get_tier_range()
        return f"Variant {sku}: {rng} at {format_lkr(self.tier_price)}"

    def get_tier_range(self) -> str:
        if self.max_quantity:
            return f"{self.min_quantity}-{self.max_quantity} units"
        return f"{self.min_quantity}+ units"

    def is_quantity_in_tier(self, quantity: int) -> bool:
        if quantity < self.min_quantity:
            return False
        if self.max_quantity and quantity > self.max_quantity:
            return False
        return True

    @classmethod
    def get_tier_for_quantity(cls, variant, quantity: int):
        return (
            cls.objects.filter(
                variant=variant,
                is_active=True,
                min_quantity__lte=quantity,
            )
            .filter(Q(max_quantity__isnull=True) | Q(max_quantity__gte=quantity))
            .order_by("-min_quantity")
            .first()
        )

    @classmethod
    def get_tiers_or_inherit(cls, variant):
        """Return variant tiers if any, else fall back to product tiers."""
        variant_tiers = cls.objects.filter(variant=variant, is_active=True).order_by("min_quantity")
        if variant_tiers.exists():
            return variant_tiers
        return TieredPricing.objects.filter(product=variant.product, is_active=True).order_by("min_quantity")

    def clean(self):
        super().clean()
        errors = {}
        if self.min_quantity is not None and self.min_quantity < 1:
            errors["min_quantity"] = "Minimum quantity must be at least 1."
        if self.max_quantity is not None and self.min_quantity is not None:
            if self.max_quantity <= self.min_quantity:
                errors["max_quantity"] = "Maximum must be greater than minimum."
        if self.tier_price is not None and self.tier_price <= 0:
            errors["tier_price"] = "Tier price must be positive."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# ── Private helpers ────────────────────────────────────────────


def _ranges_overlap(a, b) -> bool:
    """Check whether two tier ranges overlap."""
    a_max = a.max_quantity if a.max_quantity else float("inf")
    b_max = b.max_quantity if b.max_quantity else float("inf")
    return a.min_quantity <= b_max and b.min_quantity <= a_max
