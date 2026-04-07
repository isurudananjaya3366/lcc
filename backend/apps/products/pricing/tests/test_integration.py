"""
Task 86 — Integration tests for the pricing calculation pipeline.

Tests the interplay between BulkPricingService, TaxCalculator,
and CartPriceCalculator using in-memory stubs.
"""

from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.products.pricing.services.tax_calculator import TaxCalculator
from apps.products.pricing.services.bulk_pricing import BulkPricingService
from apps.products.pricing.services.cart_calculator import CartPriceCalculator

from .factories import make_product
from .test_tiered_pricing import _TierStub, _make_tiers


# =========================================================================
# Tax + Tiered pricing combined
# =========================================================================

class TestTieredPricingWithTax:
    """Verify tiered unit price → subtotal → tax → total pipeline."""

    def test_tiered_price_then_tax(self):
        svc = BulkPricingService()
        tiers = _make_tiers()  # tier 2 = 10-49 @ 90
        result = svc.calculate_tiered_price(
            tiers, 20, Decimal("100.00"), tier_type="all_units"
        )
        subtotal = result["total"]  # 1800.00
        assert subtotal == Decimal("1800.00")

        tax = TaxCalculator.calculate_tax_amount(subtotal, Decimal("15.00"))
        assert tax == Decimal("270.00")
        assert subtotal + tax == Decimal("2070.00")


class TestCartPriceCalculatorPipeline:
    """End-to-end cart calculation with mocked ORM lookups.

    _resolve_base_price and _calculate_tax access reverse FK descriptors
    that require a live DB connection.  We mock them so the pipeline
    arithmetic (tiered-price → tax → totals) is exercised without a DB.
    """

    @staticmethod
    def _tax_side_effect(product, subtotal):
        """Return 15 % exclusive tax info for any product."""
        rate = Decimal("15.00")
        return {
            "tax_rate": rate,
            "tax_amount": TaxCalculator.calculate_tax_amount(subtotal, rate),
            "is_taxable": True,
            "is_inclusive": False,
            "tax_class": "Standard VAT",
        }

    def test_single_line_no_tiers(self):
        product = make_product(name="Widget")
        calc = CartPriceCalculator()

        with (
            patch.object(
                CartPriceCalculator,
                "_resolve_base_price",
                return_value=Decimal("1000.00"),
            ),
            patch.object(
                CartPriceCalculator,
                "_calculate_tax",
                side_effect=self._tax_side_effect,
            ),
            patch(
                "apps.products.pricing.models.tiered_pricing.TieredPricing"
            ) as MockTP,
        ):
            MockTP.get_all_tiers.return_value = []

            line = calc.calculate_line_item(product, 2)
            assert line["quantity"] == 2
            assert line["base_unit_price"] == Decimal("1000.00")
            assert line["subtotal"] == Decimal("2000.00")
            assert line["tax_amount"] == Decimal("300.00")
            assert line["total"] == Decimal("2300.00")

    def test_cart_aggregation(self):
        product1 = make_product(name="Widget-A")
        product2 = make_product(name="Widget-B")
        price_map = {product1.pk: Decimal("500.00"), product2.pk: Decimal("1000.00")}

        calc = CartPriceCalculator()

        with (
            patch.object(
                CartPriceCalculator,
                "_resolve_base_price",
                side_effect=lambda prod, var, ct: price_map[prod.pk],
            ),
            patch.object(
                CartPriceCalculator,
                "_calculate_tax",
                side_effect=self._tax_side_effect,
            ),
            patch(
                "apps.products.pricing.models.tiered_pricing.TieredPricing"
            ) as MockTP,
        ):
            MockTP.get_all_tiers.return_value = []

            result = calc.calculate_cart(
                [
                    {"product": product1, "quantity": 3},
                    {"product": product2, "quantity": 1},
                ]
            )
            assert result["line_count"] == 2
            # 500*3=1500 + 1000*1=1000 = 2500 subtotal
            assert result["subtotal"] == Decimal("2500.00")
            assert result["tax_total"] == Decimal("375.00")
            assert result["grand_total"] == Decimal("2875.00")


# =========================================================================
# Tax conversion round-trip
# =========================================================================

class TestTaxConversionRoundTrip:
    """Ensure inclusive ↔ exclusive conversions are lossless."""

    @pytest.mark.parametrize(
        "price,rate",
        [
            (Decimal("100.00"), Decimal("15.00")),
            (Decimal("999.99"), Decimal("7.50")),
            (Decimal("1.00"), Decimal("0.01")),
        ],
    )
    def test_exclusive_to_inclusive_and_back(self, price, rate):
        calc = TaxCalculator()
        total, tax = calc.convert_exclusive_to_inclusive(price, rate)
        base, _ = calc.convert_inclusive_to_exclusive(total, rate)
        assert base == price


# =========================================================================
# Compound tax integration
# =========================================================================

class TestCompoundTaxIntegration:
    """Compound tax layers applied to a tiered-pricing subtotal."""

    def test_compound_on_tiered_subtotal(self):
        svc = BulkPricingService()
        tiers = _make_tiers()
        tiered = svc.calculate_tiered_price(
            tiers, 50, Decimal("100.00"), tier_type="all_units"
        )
        subtotal = tiered["total"]  # 4000.00

        calc = TaxCalculator()
        layers = [
            {"name": "VAT", "rate": Decimal("15.00")},
            {"name": "NBT", "rate": Decimal("2.00")},
        ]
        cumulative_total, taxes = calc.calculate_compound_tax(subtotal, layers)
        # VAT: 4000*15% = 600 → 4600, NBT: 4600*2% = 92 → 4692
        assert cumulative_total == Decimal("4692.00")
        total_tax = sum(t["amount"] for t in taxes)
        assert total_tax == Decimal("692.00")
        assert len(taxes) == 2


# =========================================================================
# Utils integration
# =========================================================================

class TestUtilsIntegration:
    """Currency formatting with calculated values."""

    def test_format_lkr(self):
        from apps.products.pricing.utils import format_lkr

        assert format_lkr(Decimal("1500.00")) == "₨ 1,500.00"

    def test_format_lkr_zero(self):
        from apps.products.pricing.utils import format_lkr

        assert format_lkr(Decimal("0")) == "₨ 0.00"

    def test_parse_lkr(self):
        from apps.products.pricing.utils import parse_lkr

        result = parse_lkr("₨ 1,500.00")
        assert result == Decimal("1500.00")
