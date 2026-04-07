"""
Price breakdown serializer – read-only composite view of pricing.
"""

from decimal import Decimal

from rest_framework import serializers

from ..utils import format_lkr


class PriceBreakdownSerializer(serializers.Serializer):
    """Read-only serializer for detailed price breakdown."""

    item_type = serializers.CharField(read_only=True)
    item_id = serializers.CharField(read_only=True)
    item_name = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)

    base_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    base_price_formatted = serializers.CharField(read_only=True)
    effective_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    effective_price_formatted = serializers.CharField(read_only=True)
    price_type = serializers.CharField(read_only=True)
    price_reason = serializers.CharField(read_only=True)

    has_discount = serializers.BooleanField(read_only=True)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_amount_formatted = serializers.CharField(read_only=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax_amount_formatted = serializers.CharField(read_only=True)
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    subtotal_formatted = serializers.CharField(read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_formatted = serializers.CharField(read_only=True)

    tiered_pricing = serializers.DictField(read_only=True, required=False, allow_null=True)
    savings_summary = serializers.DictField(read_only=True)

    @classmethod
    def build_breakdown(cls, product, quantity=1, *, variant=None, customer=None):
        """Build breakdown dict from a product/variant."""
        from ..services.price_resolution import PriceResolutionService
        from ..services.tax_calculator import TaxCalculator
        from ..services.bulk_pricing import BulkPricingService

        resolution = PriceResolutionService.get_effective_price(
            variant or product, customer=customer, quantity=quantity
        )
        effective = resolution["price"]
        base = resolution["original_price"]
        subtotal = effective * quantity

        # Tax
        tax_rate = Decimal("0")
        tax_amount = Decimal("0")
        pp = getattr(product, "product_price", None)
        if pp and pp.is_taxable and pp.tax_class:
            tax_rate = pp.tax_class.rate
            calc = TaxCalculator()
            if pp.is_tax_inclusive:
                tax_amount = calc.extract_tax_from_inclusive_price(subtotal, tax_rate)
            else:
                tax_amount = calc.calculate_tax_amount(subtotal, tax_rate)

        # Tiered
        tiered = None
        from ..models.tiered_pricing import TieredPricing
        tiers = TieredPricing.get_all_tiers(product)
        if tiers.exists():
            svc = BulkPricingService()
            tiered = svc.calculate_tiered_price(tiers, quantity, base)

        discount_amt = resolution["discount_amount"]

        return {
            "item_type": "variant" if variant else "product",
            "item_id": str((variant or product).pk),
            "item_name": getattr(variant, "sku", getattr(product, "name", "?")),
            "quantity": quantity,
            "base_price": base,
            "base_price_formatted": format_lkr(base),
            "effective_price": effective,
            "effective_price_formatted": format_lkr(effective),
            "price_type": resolution["price_type"].upper(),
            "price_reason": resolution["reason"],
            "has_discount": discount_amt > 0,
            "discount_amount": discount_amt,
            "discount_amount_formatted": format_lkr(discount_amt),
            "discount_percentage": resolution["discount_percentage"],
            "tax_amount": tax_amount,
            "tax_amount_formatted": format_lkr(tax_amount),
            "tax_rate": tax_rate,
            "subtotal": subtotal,
            "subtotal_formatted": format_lkr(subtotal),
            "total": subtotal + tax_amount,
            "total_formatted": format_lkr(subtotal + tax_amount),
            "tiered_pricing": tiered,
            "savings_summary": {
                "amount": str(discount_amt * quantity),
                "amount_formatted": format_lkr(discount_amt * quantity),
                "percentage": str(resolution["discount_percentage"]),
            },
        }
