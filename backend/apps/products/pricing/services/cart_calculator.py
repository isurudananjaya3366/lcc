"""
Cart-level price calculation that combines tiered/volume pricing
with tax calculations for complete line-item and cart totals.
"""

from decimal import Decimal

from .bulk_pricing import BulkPricingService
from .tax_calculator import TaxCalculator


class CartPriceCalculator:
    """
    Combines tiered pricing + tax into a single cart-oriented API.

    Usage::

        calc = CartPriceCalculator()
        line = calc.calculate_line_item(product, quantity=10)
        cart = calc.calculate_cart(lines)
    """

    def __init__(self):
        self.bulk_service = BulkPricingService()
        self.tax_calc = TaxCalculator()

    # ── Single line-item ───────────────────────────────────────

    def calculate_line_item(
        self,
        product,
        quantity: int,
        *,
        variant=None,
        customer_type: str = "retail",
    ) -> dict:
        """
        Full calculation for one cart line.

        Returns dict with ``subtotal``, ``tax_amount``, ``total``,
        ``unit_price``, ``tier_info``, and ``tax_info``.
        """
        # 1. Resolve base price
        base_price = self._resolve_base_price(product, variant, customer_type)

        # 2. Tier calculation
        tier_result = self.bulk_service.calculate_cart_line(
            product, quantity, base_price, variant=variant
        )

        # 3. Tax calculation
        tax_info = self._calculate_tax(product, tier_result["total"])

        return {
            "product_id": str(product.pk),
            "variant_id": str(variant.pk) if variant else None,
            "quantity": quantity,
            "base_unit_price": base_price,
            "effective_unit_price": tier_result["unit_price"],
            "subtotal": tier_result["total"],
            "tax_amount": tax_info["tax_amount"],
            "total": tier_result["total"] + tax_info["tax_amount"],
            "tier_info": {
                "applied": tier_result["tier_applied"],
                "type": tier_result["tier_type"],
                "savings": tier_result["savings"],
                "discount_pct": tier_result["discount_pct"],
                "breakdown": tier_result["breakdown"],
            },
            "tax_info": tax_info,
        }

    # ── Full cart ──────────────────────────────────────────────

    def calculate_cart(self, lines: list[dict]) -> dict:
        """
        Calculate totals for a list of cart lines.

        Each entry in *lines* must be a dict with ``product``, ``quantity``,
        and optionally ``variant`` and ``customer_type``.
        """
        results = []
        subtotal = Decimal("0")
        tax_total = Decimal("0")
        total_savings = Decimal("0")

        for line in lines:
            item = self.calculate_line_item(
                product=line["product"],
                quantity=line["quantity"],
                variant=line.get("variant"),
                customer_type=line.get("customer_type", "retail"),
            )
            results.append(item)
            subtotal += item["subtotal"]
            tax_total += item["tax_amount"]
            total_savings += item["tier_info"]["savings"]

        return {
            "lines": results,
            "subtotal": subtotal,
            "tax_total": tax_total,
            "grand_total": subtotal + tax_total,
            "total_savings": total_savings,
            "line_count": len(results),
        }

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _resolve_base_price(product, variant, customer_type: str) -> Decimal:
        """Get the base price from the product or variant."""
        try:
            if variant:
                from ..models.variant_price import VariantPrice

                vp = VariantPrice.objects.filter(variant=variant).first()
                if vp:
                    return vp.get_effective_price()
            pp = getattr(product, "product_price", None)
            if pp:
                if customer_type == "wholesale" and pp.wholesale_price:
                    return pp.wholesale_price
                return pp.get_current_price()
        except Exception:
            pass
        return Decimal("0")

    def _calculate_tax(self, product, subtotal: Decimal) -> dict:
        """Resolve tax for a product's subtotal."""
        pp = getattr(product, "product_price", None)
        if not pp or not pp.is_taxable or not pp.tax_class:
            return {
                "tax_rate": Decimal("0"),
                "tax_amount": Decimal("0"),
                "is_taxable": False,
                "is_inclusive": False,
            }

        rate = pp.tax_class.rate
        is_inclusive = pp.is_tax_inclusive

        if is_inclusive:
            tax_amount = self.tax_calc.extract_tax_from_inclusive_price(subtotal, rate)
        else:
            tax_amount = self.tax_calc.calculate_tax_amount(subtotal, rate)

        return {
            "tax_rate": rate,
            "tax_amount": tax_amount,
            "is_taxable": True,
            "is_inclusive": is_inclusive,
            "tax_class": pp.tax_class.name,
        }
