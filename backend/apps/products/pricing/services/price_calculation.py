"""
PriceCalculationService – unified price resolution for products and variants.

Delegates to TaxCalculator for tax math and provides a single entry-point
for all price queries across the pricing system.
"""

from __future__ import annotations

from decimal import Decimal

from .tax_calculator import TaxCalculator, _round


class PriceCalculationService:
    """
    Facade that resolves the final price for a ProductPrice or VariantPrice,
    including tax, sale, and wholesale logic.
    """

    def __init__(self, customer=None):
        self.customer = customer
        self._calc = TaxCalculator(customer=customer)

    # ── ProductPrice helpers ───────────────────────────────────

    def get_product_price(
        self, product_price, price_type: str = "base", include_tax: bool = True
    ) -> Decimal:
        """
        Resolve the final price for a ``ProductPrice`` instance.

        Parameters
        ----------
        price_type : 'base', 'sale', 'wholesale'
        include_tax : whether to return the tax-inclusive amount
        """
        raw = self._raw_price(product_price, price_type)
        if raw is None:
            return Decimal("0.00")
        if not include_tax:
            if product_price.is_tax_inclusive:
                return self._calc.get_base_from_inclusive(
                    raw, self._rate(product_price)
                )
            return raw
        # include_tax
        if product_price.is_tax_inclusive:
            return raw
        return self._calc.calculate_price_with_tax(raw, self._rate(product_price))

    def get_product_breakdown(self, product_price, price_type: str = "base") -> dict:
        """Full tax breakdown for a ProductPrice."""
        raw = self._raw_price(product_price, price_type)
        if raw is None:
            return {"base_price": Decimal("0"), "tax_amount": Decimal("0"), "total_price": Decimal("0")}
        rate = self._rate(product_price)
        return self._calc.get_tax_breakdown(
            raw, rate, is_inclusive=product_price.is_tax_inclusive, customer=self.customer
        )

    # ── VariantPrice helpers ───────────────────────────────────

    def get_variant_price(
        self, variant_price, price_type: str = "base", include_tax: bool = True
    ) -> Decimal:
        """
        Resolve the final price for a ``VariantPrice``, respecting
        ``use_product_price`` inheritance.
        """
        pp = variant_price._product_price()
        if variant_price.use_product_price and pp:
            return self.get_product_price(pp, price_type, include_tax)
        # Variant has its own prices
        raw = self._variant_raw(variant_price, price_type)
        if raw is None:
            return Decimal("0.00")
        rate = self._rate(pp) if pp else Decimal("0")
        if not include_tax:
            return raw
        return self._calc.calculate_price_with_tax(raw, rate)

    def get_variant_breakdown(self, variant_price, price_type: str = "base") -> dict:
        pp = variant_price._product_price()
        if variant_price.use_product_price and pp:
            return self.get_product_breakdown(pp, price_type)
        raw = self._variant_raw(variant_price, price_type)
        if raw is None:
            return {"base_price": Decimal("0"), "tax_amount": Decimal("0"), "total_price": Decimal("0")}
        rate = self._rate(pp) if pp else Decimal("0")
        return self._calc.get_tax_breakdown(raw, rate, is_inclusive=False, customer=self.customer)

    # ── Extended API (Tasks 31-32) ────────────────────────────

    def calculate_final_price(self, price_obj) -> Decimal:
        """Orchestration: return the customer-appropriate final price."""
        from ..models.variant_price import VariantPrice

        if isinstance(price_obj, VariantPrice):
            return self.get_variant_price(price_obj)
        return self.get_product_price(price_obj)

    def get_complete_breakdown(self, price_obj) -> dict:
        """Full breakdown including tax, margins, and source."""
        from ..models.variant_price import VariantPrice

        if isinstance(price_obj, VariantPrice):
            bd = self.get_variant_breakdown(price_obj)
            bd["pricing_source"] = price_obj.get_pricing_source()
            return bd
        bd = self.get_product_breakdown(price_obj)
        bd["pricing_source"] = "product"
        return bd

    def calculate_for_quantity(self, price_obj, quantity: int) -> Decimal:
        """Final price × quantity."""
        return _round(self.calculate_final_price(price_obj) * quantity)

    def get_customer_specific_price(self, product_price) -> Decimal:
        """Return the best price for the current customer."""
        ctype = getattr(self.customer, "customer_type", "retail") if self.customer else "retail"
        return self.get_product_price(
            product_price, price_type="wholesale" if ctype in ("wholesale", "b2b") else "base"
        )

    def calculate_margin(self, price_obj, cost_price: Decimal | None = None) -> dict:
        """Return margin metrics for a price object."""
        final = self.calculate_final_price(price_obj)
        cost = cost_price or getattr(price_obj, "cost_price", None) or Decimal("0")
        margin_pct = (
            ((final - cost) / final * 100).quantize(Decimal("0.01"))
            if final
            else Decimal("0")
        )
        return {
            "final_price": final,
            "cost_price": cost,
            "profit": final - cost,
            "margin_pct": margin_pct,
        }

    def format_for_display(self, price_obj) -> dict:
        """Return formatted pricing for UI consumption."""
        from ..utils import format_lkr

        final = self.calculate_final_price(price_obj)
        cost = getattr(price_obj, "cost_price", None)
        return {
            "price": format_lkr(final),
            "cost": format_lkr(cost) if cost else None,
            "is_on_sale": getattr(price_obj, "is_on_sale", False),
        }

    def bulk_calculate(self, price_objects: list) -> list:
        """Calculate final prices for a list of price objects."""
        return [
            {
                "obj": obj,
                "final_price": self.calculate_final_price(obj),
            }
            for obj in price_objects
        ]

    # ── Variant comparison helpers (Task 32) ───────────────────

    def get_variant_price_difference(self, variant_price) -> Decimal | None:
        """Delta between variant final price and product final price."""
        pp = variant_price._product_price()
        if not pp:
            return None
        variant_final = self.get_variant_price(variant_price)
        product_final = self.get_product_price(pp)
        return variant_final - product_final

    # ── Internals ──────────────────────────────────────────────

    @staticmethod
    def _raw_price(product_price, price_type: str) -> Decimal | None:
        if price_type == "sale":
            return product_price.sale_price if product_price.is_on_sale else None
        if price_type == "wholesale":
            return product_price.wholesale_price
        return product_price.base_price

    @staticmethod
    def _variant_raw(variant_price, price_type: str) -> Decimal | None:
        if price_type == "sale":
            return variant_price.sale_price
        if price_type == "wholesale":
            return variant_price.wholesale_price
        return variant_price.base_price

    def _rate(self, product_price) -> Decimal:
        if product_price is None:
            return Decimal("0")
        if not product_price.is_taxable:
            return Decimal("0")
        tc = product_price.tax_class
        return self._calc.get_effective_tax_rate(tc, self.customer)
