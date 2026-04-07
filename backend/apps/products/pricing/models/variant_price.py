"""
VariantPrice model – per-variant price overrides.

When ``use_product_price`` is True the variant inherits prices from
the parent product's ProductPrice record.  When overridden, the variant
may carry its own base / sale / wholesale / cost prices, or apply a
percentage / fixed adjustment to the parent price.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel

from ..constants import ADJUSTMENT_TYPE_CHOICES
from ..fields import PriceField


class VariantPrice(BaseModel):
    """
    One-to-one pricing override for a ProductVariant.
    """

    # ── Relationships ──────────────────────────────────────────
    variant = models.OneToOneField(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="price",
        verbose_name="Variant",
        help_text="Variant this pricing belongs to.",
    )

    # ── Override toggle ────────────────────────────────────────
    use_product_price = models.BooleanField(
        default=True,
        verbose_name="Use Product Price",
        help_text="When True, inherit prices from the parent product.",
    )

    # ── Per-variant price overrides ────────────────────────────
    base_price = PriceField(
        null=True,
        blank=True,
        verbose_name="Base Price Override",
        help_text="Overridden base price for this variant.",
    )
    sale_price = PriceField(
        null=True,
        blank=True,
        verbose_name="Sale Price Override",
        help_text="Overridden sale price for this variant.",
    )
    sale_price_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Sale Start Override",
    )
    sale_price_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Sale End Override",
    )
    wholesale_price = PriceField(
        null=True,
        blank=True,
        verbose_name="Wholesale Price Override",
        help_text="Overridden wholesale price for this variant.",
    )
    cost_price = PriceField(
        null=True,
        blank=True,
        verbose_name="Cost Price Override",
        help_text="Overridden cost price for this variant.",
    )

    # ── Adjustment logic ───────────────────────────────────────
    price_adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Adjustment Type",
        help_text="Fixed amount or percentage adjustment on parent price.",
    )
    price_adjustment_value = PriceField(
        null=True,
        blank=True,
        verbose_name="Adjustment Value",
        help_text="Amount or percentage to add/subtract from parent price.",
    )

    class Meta:
        db_table = "pricing_variant_price"
        verbose_name = "Variant Price"
        verbose_name_plural = "Variant Prices"
        ordering = ["variant"]
        indexes = [
            models.Index(fields=["variant"], name="idx_vp_variant"),
            models.Index(fields=["use_product_price"], name="idx_vp_useproduct"),
        ]

    # ── String representation ──────────────────────────────────
    def __str__(self):
        sku = getattr(self.variant, "sku", "?") if hasattr(self, "variant") else "?"
        from ..utils import format_lkr

        return f"Variant {sku} - {format_lkr(self.get_effective_price())}"

    # ── Product price accessor ─────────────────────────────────
    def _product_price(self):
        """Lookup the parent product's ProductPrice record."""
        return getattr(self.variant.product, "price", None) if self.variant_id else None

    # ── Override helpers ───────────────────────────────────────
    def get_base_price(self) -> Decimal:
        if not self.use_product_price and self.base_price is not None:
            return self.base_price
        pp = self._product_price()
        return pp.base_price if pp else Decimal("0.00")

    def get_sale_price(self) -> Decimal | None:
        if not self.use_product_price and self.sale_price is not None:
            return self.sale_price
        pp = self._product_price()
        return pp.sale_price if pp else None

    def get_wholesale_price(self) -> Decimal | None:
        if not self.use_product_price and self.wholesale_price is not None:
            return self.wholesale_price
        pp = self._product_price()
        return pp.wholesale_price if pp else None

    def get_cost_price(self) -> Decimal | None:
        if not self.use_product_price and self.cost_price is not None:
            return self.cost_price
        pp = self._product_price()
        return pp.cost_price if pp else None

    def apply_price_adjustment(self, price: Decimal) -> Decimal:
        if not self.price_adjustment_type or self.price_adjustment_value is None:
            return price
        if self.price_adjustment_type == "fixed":
            return (price + self.price_adjustment_value).quantize(Decimal("0.01"))
        if self.price_adjustment_type == "percentage":
            adjustment = (price * self.price_adjustment_value / Decimal("100")).quantize(Decimal("0.01"))
            return price + adjustment
        return price

    def get_effective_price(self) -> Decimal:
        base = self.get_base_price()
        adjusted = self.apply_price_adjustment(base)
        sale = self.get_sale_price()
        if sale is not None:
            from django.utils import timezone

            now = timezone.now()
            start = self.sale_price_start if not self.use_product_price else None
            end = self.sale_price_end if not self.use_product_price else None
            # If using product price, delegate is_on_sale to the product.
            if self.use_product_price:
                pp = self._product_price()
                if pp and pp.is_on_sale:
                    return sale
            else:
                active = True
                if start and now < start:
                    active = False
                if end and now > end:
                    active = False
                if active:
                    return sale
        return adjusted

    @property
    def is_on_sale(self) -> bool:
        sale = self.get_sale_price()
        if sale is None:
            return False
        if self.use_product_price:
            pp = self._product_price()
            return pp.is_on_sale if pp else False
        from django.utils import timezone

        now = timezone.now()
        if self.sale_price_start and now < self.sale_price_start:
            return False
        if self.sale_price_end and now > self.sale_price_end:
            return False
        return True

    @property
    def has_price_override(self) -> bool:
        return not self.use_product_price

    def get_pricing_source(self) -> str:
        if self.use_product_price:
            return "product"
        return "variant"

    # ── Tax helpers (delegate to parent product) ─────────────

    def get_price_with_tax(self, customer=None, price_type: str = "base") -> Decimal:
        """Return variant price including tax, delegating tax info to product."""
        price = self.get_effective_price()
        pp = self._product_price()
        if not pp or not pp.is_taxable:
            return price
        from ..services.tax_calculator import TaxCalculator

        rate = TaxCalculator.get_effective_tax_rate(pp.tax_class, customer)
        if pp.is_tax_inclusive:
            return price
        return TaxCalculator.calculate_price_with_tax(price, rate)

    def get_price_without_tax(self, price_type: str = "base") -> Decimal:
        """Return variant price excluding tax."""
        price = self.get_effective_price()
        pp = self._product_price()
        if not pp or not pp.is_taxable:
            return price
        if not pp.is_tax_inclusive:
            return price
        from ..services.tax_calculator import TaxCalculator

        rate = pp.tax_class.rate if pp.tax_class else Decimal("0")
        base, _ = TaxCalculator().convert_inclusive_to_exclusive(price, rate)
        return base

    def get_tax_breakdown(self, customer=None) -> dict:
        """Return tax breakdown for this variant, using parent product's tax config."""
        price = self.get_effective_price()
        pp = self._product_price()
        if not pp or not pp.is_taxable:
            return {
                "base_price": price,
                "tax_amount": Decimal("0"),
                "total_price": price,
                "tax_rate": Decimal("0"),
                "is_inclusive": False,
                "is_exempt": True,
                "svat_applied": False,
            }
        from ..services.tax_calculator import TaxCalculator

        rate = TaxCalculator.get_effective_tax_rate(pp.tax_class, customer)
        if pp.is_tax_inclusive:
            tax = TaxCalculator.extract_tax_from_inclusive_price(price, rate)
            base = price - tax
        else:
            base = price
            tax = TaxCalculator.calculate_tax_amount(price, rate)
        svat = TaxCalculator.is_svat_eligible(customer) if customer else False
        return {
            "base_price": base,
            "tax_amount": Decimal("0") if svat else tax,
            "total_price": base if svat else base + tax,
            "tax_rate": Decimal("0") if svat else rate,
            "is_inclusive": pp.is_tax_inclusive,
            "is_exempt": False,
            "svat_applied": svat,
        }

    # ── Margin calculations ────────────────────────────────────

    @property
    def profit_margin(self) -> Decimal | None:
        """Profit margin % for this variant's effective price vs cost."""
        price = self.get_effective_price()
        cost = self.get_cost_price()
        if not price or not cost or price == 0:
            return None
        return ((price - cost) / price * 100).quantize(Decimal("0.01"))

    def variant_vs_product_margin(self) -> dict | None:
        """Compare this variant's margin with the parent product's margin."""
        pp = self._product_price()
        if not pp:
            return None
        variant_margin = self.profit_margin
        product_margin = pp.profit_margin
        if variant_margin is None or product_margin is None:
            return None
        return {
            "variant_margin": variant_margin,
            "product_margin": product_margin,
            "difference": variant_margin - product_margin,
        }

    def get_margin_comparison(self) -> dict | None:
        """Alias for variant_vs_product_margin."""
        return self.variant_vs_product_margin()

    # ── Validation ─────────────────────────────────────────────
    def clean(self):
        super().clean()
        errors = {}
        if not self.use_product_price:
            if self.base_price is None:
                errors["base_price"] = "Base price is required when not using product price."
            if self.sale_price is not None and self.base_price and self.sale_price >= self.base_price:
                errors["sale_price"] = "Sale price must be less than base price."
        if errors:
            raise ValidationError(errors)
