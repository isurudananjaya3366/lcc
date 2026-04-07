"""
ProductPrice model – core pricing for each product.

Covers base price, sale pricing with date ranges, wholesale pricing,
tax configuration, and profit margin calculations.
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel

from ..constants import DEFAULT_PRICE
from ..fields import PriceField


class ProductPrice(BaseModel):
    """
    One-to-one pricing record for a Product.

    Fields
    ------
    base_price : Decimal
        Default selling price (LKR).
    cost_price : Decimal | None
        Supplier / manufacturing cost.
    sale_price, sale_price_start, sale_price_end : sale window
    wholesale_price, minimum_wholesale_quantity : B2B pricing
    tax_class, is_taxable, is_tax_inclusive : tax configuration
    """

    # ── Relationships ──────────────────────────────────────────
    product = models.OneToOneField(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="price",
        verbose_name="Product",
        help_text="Product this pricing belongs to.",
    )
    tax_class = models.ForeignKey(
        "products.TaxClass",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="product_prices",
        verbose_name="Tax Class",
        help_text="Tax classification for this product.",
    )

    # ── Base pricing ───────────────────────────────────────────
    base_price = PriceField(
        verbose_name="Base Price",
        default=DEFAULT_PRICE,
        help_text="Default selling price in LKR.",
    )
    cost_price = PriceField(
        null=True,
        blank=True,
        verbose_name="Cost Price",
        help_text="Supplier or manufacturing cost in LKR.",
    )

    # ── Sale pricing ───────────────────────────────────────────
    sale_price = PriceField(
        null=True,
        blank=True,
        verbose_name="Sale Price",
        help_text="Promotional price during sale period.",
    )
    sale_price_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Sale Start Date",
        help_text="When the sale period begins.",
    )
    sale_price_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Sale End Date",
        help_text="When the sale period ends.",
    )

    # ── Wholesale pricing ──────────────────────────────────────
    wholesale_price = PriceField(
        null=True,
        blank=True,
        verbose_name="Wholesale Price",
        help_text="Discounted price for B2B / wholesale customers.",
    )
    minimum_wholesale_quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Minimum Wholesale Quantity",
        help_text="Minimum order quantity to qualify for wholesale price.",
    )

    # ── Tax configuration ──────────────────────────────────────
    is_taxable = models.BooleanField(
        default=True,
        verbose_name="Is Taxable",
        help_text="Whether this product is subject to tax.",
    )
    is_tax_inclusive = models.BooleanField(
        default=True,
        verbose_name="Tax Inclusive",
        help_text="Whether the stored price already includes tax.",
    )
    tax_exemption_reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Tax Exemption Reason",
        help_text="Documentation reason if product is tax-exempt.",
    )

    # ── Metadata ───────────────────────────────────────────────
    pricing_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Pricing Notes",
        help_text="Internal notes about pricing decisions.",
    )
    last_cost_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Cost Update",
        help_text="When the cost price was last changed.",
    )

    # ── Manager ────────────────────────────────────────────────
    from ..managers import ProductPriceManager

    objects = ProductPriceManager()

    class Meta:
        db_table = "pricing_product_price"
        verbose_name = "Product Price"
        verbose_name_plural = "Product Prices"
        ordering = ["product__name"]
        indexes = [
            models.Index(fields=["product"], name="idx_pp_product"),
            models.Index(fields=["is_taxable"], name="idx_pp_taxable"),
            models.Index(
                fields=["sale_price_start", "sale_price_end"],
                name="idx_pp_sale_dates",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(sale_price__isnull=True)
                | models.Q(sale_price__lt=models.F("base_price")),
                name="chk_sale_lt_base",
            ),
            models.CheckConstraint(
                check=models.Q(wholesale_price__isnull=True)
                | models.Q(wholesale_price__lt=models.F("base_price")),
                name="chk_wholesale_lt_base",
            ),
            models.CheckConstraint(
                check=models.Q(cost_price__isnull=True)
                | models.Q(cost_price__lte=models.F("base_price")),
                name="chk_cost_lte_base",
            ),
        ]
        permissions = [
            ("view_cost_price", "Can view cost prices"),
            ("manage_pricing", "Can manage all pricing"),
            ("create_promotions", "Can create promotional pricing"),
        ]

    # ── String representation ──────────────────────────────────
    def __str__(self):
        name = getattr(self.product, "name", "?") if hasattr(self, "product") else "?"
        from ..utils import format_lkr

        return f"{name} - {format_lkr(self.base_price)}"

    # ── Sale helpers ───────────────────────────────────────────
    @property
    def is_on_sale(self) -> bool:
        if not self.sale_price:
            return False
        now = timezone.now()
        if self.sale_price_start and now < self.sale_price_start:
            return False
        if self.sale_price_end and now > self.sale_price_end:
            return False
        return True

    def get_current_price(self) -> Decimal:
        """Return sale price if active, otherwise base price."""
        if self.is_on_sale:
            return self.sale_price
        return self.base_price

    @property
    def discount_amount(self) -> Decimal:
        if self.is_on_sale and self.sale_price:
            return self.base_price - self.sale_price
        return Decimal("0.00")

    @property
    def discount_percentage(self) -> Decimal:
        if self.is_on_sale and self.sale_price and self.base_price:
            return ((self.base_price - self.sale_price) / self.base_price * 100).quantize(Decimal("0.01"))
        return Decimal("0.00")

    # ── Wholesale helpers ──────────────────────────────────────
    @property
    def wholesale_discount_percentage(self) -> Decimal:
        if self.wholesale_price and self.base_price:
            return ((self.base_price - self.wholesale_price) / self.base_price * 100).quantize(Decimal("0.01"))
        return Decimal("0.00")

    def is_wholesale_eligible(self, quantity: int) -> bool:
        if not self.wholesale_price:
            return False
        return quantity >= self.minimum_wholesale_quantity

    def get_price_for_customer_type(self, customer_type: str) -> Decimal:
        if customer_type in ("wholesale", "b2b"):
            if self.wholesale_price:
                return self.wholesale_price
        return self.get_current_price()

    # ── Tax helpers ────────────────────────────────────────────
    def _tax_rate(self) -> Decimal:
        if self.tax_class:
            return self.tax_class.rate / Decimal("100")
        return Decimal("0")

    def _tax_rate_pct(self, customer=None) -> Decimal:
        """Percentage rate (e.g. 12) with SVAT awareness."""
        from ..services import TaxCalculator

        calc = TaxCalculator(tax_class=self.tax_class, customer=customer)
        return calc.get_effective_tax_rate()

    def _price_for_type(self, price_type: str = "base") -> Decimal | None:
        if price_type == "sale":
            return self.sale_price if self.is_on_sale else None
        if price_type == "wholesale":
            return self.wholesale_price
        return self.base_price

    def get_price_with_tax(self, customer=None, price_type: str = "base") -> Decimal:
        if not self.is_taxable:
            return self._price_for_type(price_type) or Decimal("0")
        price = self._price_for_type(price_type)
        if price is None:
            return Decimal("0")
        rate = self._tax_rate_pct(customer)
        if self.is_tax_inclusive:
            return price
        from ..services import TaxCalculator

        return TaxCalculator.calculate_price_with_tax(price, rate)

    def get_price_without_tax(self, customer=None, price_type: str = "base") -> Decimal:
        if not self.is_taxable:
            return self._price_for_type(price_type) or Decimal("0")
        price = self._price_for_type(price_type)
        if price is None:
            return Decimal("0")
        rate = self._tax_rate_pct(customer)
        if not self.is_tax_inclusive:
            return price
        from ..services import TaxCalculator

        return TaxCalculator.calculate_price_without_tax(price, rate)

    def get_tax_amount(self, price: Decimal | None = None, customer=None) -> Decimal:
        price = price or self.base_price
        rate = self._tax_rate_pct(customer)
        if self.is_tax_inclusive:
            from ..services import TaxCalculator

            return TaxCalculator.extract_tax_from_inclusive_price(price, rate)
        return (price * rate / Decimal("100")).quantize(Decimal("0.01"))

    def get_tax_breakdown(self, customer=None, price_type: str = "base") -> dict:
        """Return a complete tax breakdown dict for invoice display."""
        price = self._price_for_type(price_type)
        if price is None:
            return {
                "base_price": Decimal("0"),
                "tax_amount": Decimal("0"),
                "total_price": Decimal("0"),
                "tax_rate": Decimal("0"),
                "is_inclusive": self.is_tax_inclusive,
                "is_exempt": not self.is_taxable,
                "svat_applied": False,
            }
        from ..services import TaxCalculator

        calc = TaxCalculator(tax_class=self.tax_class, customer=customer)
        rate = calc.get_effective_tax_rate()
        svat = calc.is_svat_eligible(customer) if customer else False
        if not self.is_taxable:
            return {
                "base_price": price,
                "tax_amount": Decimal("0"),
                "total_price": price,
                "tax_rate": Decimal("0"),
                "is_inclusive": self.is_tax_inclusive,
                "is_exempt": True,
                "svat_applied": svat,
                "exemption_reason": self.tax_exemption_reason or "",
            }
        breakdown = calc.get_tax_breakdown(
            price, rate, is_inclusive=self.is_tax_inclusive, customer=customer
        )
        breakdown["is_exempt"] = False
        breakdown["svat_applied"] = svat
        return breakdown

    # ── Profit calculations ────────────────────────────────────
    @property
    def profit_margin(self) -> Decimal | None:
        if self.cost_price is None:
            return None
        if not self.base_price:
            return Decimal("0")
        return ((self.base_price - self.cost_price) / self.base_price * 100).quantize(Decimal("0.01"))

    @property
    def markup_percentage(self) -> Decimal | None:
        if not self.cost_price:
            return None
        return ((self.base_price - self.cost_price) / self.cost_price * 100).quantize(Decimal("0.01"))

    @property
    def profit_per_unit(self) -> Decimal | None:
        if self.cost_price is None:
            return None
        return self.base_price - self.cost_price

    @property
    def profit_amount(self) -> Decimal | None:
        return self.profit_per_unit

    @property
    def sale_profit_margin(self) -> Decimal | None:
        if not self.is_on_sale or self.cost_price is None or not self.sale_price:
            return None
        return ((self.sale_price - self.cost_price) / self.sale_price * 100).quantize(Decimal("0.01"))

    @property
    def wholesale_profit_margin(self) -> Decimal | None:
        if not self.wholesale_price or self.cost_price is None:
            return None
        return ((self.wholesale_price - self.cost_price) / self.wholesale_price * 100).quantize(Decimal("0.01"))

    def break_even_quantity(self, fixed_costs: Decimal) -> int | None:
        unit_profit = self.profit_per_unit
        if not unit_profit or unit_profit <= 0:
            return None
        import math

        return math.ceil(fixed_costs / unit_profit)

    def get_margin_for_price(self, selling_price: Decimal) -> Decimal | None:
        if self.cost_price is None or not selling_price:
            return None
        return ((selling_price - self.cost_price) / selling_price * 100).quantize(Decimal("0.01"))

    # ── Tax exemption helpers ─────────────────────────────────
    @property
    def is_exempt(self) -> bool:
        """True when product is explicitly not taxable."""
        return not self.is_taxable

    def get_tax_status(self) -> str:
        """Return 'taxable', 'zero_rated', or 'exempt'."""
        if not self.is_taxable:
            return "exempt"
        tc = getattr(self, "tax_class", None)
        if tc and tc.rate == 0:
            return "zero_rated"
        return "taxable"

    def get_exemption_display(self) -> str:
        """Human-readable exemption info."""
        if self.is_taxable:
            return "Taxable"
        return self.tax_exemption_reason or "Exempt (no reason given)"

    # ── Validation ─────────────────────────────────────────────
    def validate_profit_margin(self, minimum_margin: Decimal = Decimal("0")):
        margin = self.profit_margin
        if margin is not None and margin < minimum_margin:
            raise ValidationError(
                f"Profit margin {margin}% is below minimum {minimum_margin}%."
            )

    def validate_sale_price(self):
        if self.sale_price:
            if not self.sale_price_start or not self.sale_price_end:
                raise ValidationError("Sale price requires both start and end dates.")
            if self.sale_price >= self.base_price:
                raise ValidationError("Sale price must be less than base price.")
            if self.cost_price and self.sale_price < self.cost_price:
                raise ValidationError("Sale price must be at least equal to cost price.")

    def validate_wholesale_pricing(self):
        if self.wholesale_price:
            if self.wholesale_price >= self.base_price:
                raise ValidationError("Wholesale price must be less than base price.")
            if self.cost_price and self.wholesale_price < self.cost_price:
                raise ValidationError("Wholesale price must be at least equal to cost price.")

    def clean(self):
        super().clean()
        errors = {}
        if self.sale_price:
            if self.sale_price >= self.base_price:
                errors["sale_price"] = "Sale price must be less than base price."
            if self.sale_price_start and self.sale_price_end and self.sale_price_start >= self.sale_price_end:
                errors["sale_price_end"] = "Sale start must be before sale end."
        if self.wholesale_price and self.wholesale_price >= self.base_price:
            errors["wholesale_price"] = "Wholesale price must be less than base price."
        if self.cost_price and self.cost_price > self.base_price:
            errors["cost_price"] = "Cost price cannot exceed base price."
        if not self.is_taxable and not self.tax_exemption_reason:
            errors["tax_exemption_reason"] = "Tax exemption reason is required for non-taxable products."
        if errors:
            raise ValidationError(errors)
