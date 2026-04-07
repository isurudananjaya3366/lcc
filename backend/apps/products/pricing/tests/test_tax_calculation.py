"""
Task 82 — TaxCalculator service tests.

All TaxCalculator core methods are pure math (static / classmethod),
so most tests run without a database.
"""

from decimal import Decimal

import pytest

from apps.products.pricing.services.tax_calculator import TaxCalculator


class TestTaxCalculatorBasic:
    """Core tax calculation methods — all static, no DB needed."""

    def setup_method(self):
        self.calc = TaxCalculator()

    def test_calculate_tax_amount(self):
        result = TaxCalculator.calculate_tax_amount(Decimal("1000.00"), Decimal("15.00"))
        assert result == Decimal("150.00")

    def test_calculate_tax_amount_zero_rate(self):
        result = TaxCalculator.calculate_tax_amount(Decimal("1000.00"), Decimal("0"))
        assert result == Decimal("0.00")

    def test_calculate_price_with_tax(self):
        result = TaxCalculator.calculate_price_with_tax(
            Decimal("1000.00"), Decimal("15.00")
        )
        assert result == Decimal("1150.00")

    def test_calculate_price_without_tax(self):
        result = TaxCalculator.calculate_price_without_tax(
            Decimal("1150.00"), Decimal("15.00")
        )
        assert result == Decimal("1000.00")

    def test_extract_tax_from_inclusive_price(self):
        result = TaxCalculator.extract_tax_from_inclusive_price(
            Decimal("1150.00"), Decimal("15.00")
        )
        assert result == Decimal("150.00")

    def test_round_trip_exclusive_to_inclusive(self):
        base = Decimal("1000.00")
        rate = Decimal("15.00")
        inclusive = TaxCalculator.calculate_price_with_tax(base, rate)
        extracted_base = TaxCalculator.calculate_price_without_tax(inclusive, rate)
        assert extracted_base == base


class TestTaxCalculatorConversion:
    """Inclusive ↔ exclusive conversion — returns tuples."""

    def test_convert_inclusive_to_exclusive(self):
        calc = TaxCalculator()
        base, tax = calc.convert_inclusive_to_exclusive(
            Decimal("1150.00"), Decimal("15.00")
        )
        assert base == Decimal("1000.00")
        assert tax == Decimal("150.00")

    def test_convert_exclusive_to_inclusive(self):
        calc = TaxCalculator()
        total, tax = calc.convert_exclusive_to_inclusive(
            Decimal("1000.00"), Decimal("15.00")
        )
        assert total == Decimal("1150.00")
        assert tax == Decimal("150.00")


class TestTaxCalculatorCompound:
    """Compound tax with multiple layers — returns (cumulative_total, taxes)."""

    def test_calculate_compound_tax_single_layer(self):
        calc = TaxCalculator()
        layers = [{"name": "VAT", "rate": Decimal("15.00")}]
        cumulative, taxes = calc.calculate_compound_tax(Decimal("1000.00"), layers)
        # cumulative = base + tax = 1000 + 150 = 1150
        assert cumulative == Decimal("1150.00")
        assert len(taxes) == 1
        assert taxes[0]["amount"] == Decimal("150.00")

    def test_calculate_compound_tax_two_layers(self):
        calc = TaxCalculator()
        layers = [
            {"name": "VAT", "rate": Decimal("15.00")},
            {"name": "NBT", "rate": Decimal("2.00")},
        ]
        cumulative, taxes = calc.calculate_compound_tax(Decimal("1000.00"), layers)
        # Layer 1: 1000 * 15% = 150 → cumulative 1150
        # Layer 2: 1150 * 2% = 23 → cumulative 1173
        assert cumulative == Decimal("1173.00")
        assert len(taxes) == 2

    def test_calculate_effective_compound_rate(self):
        # Static method taking list of rate Decimals
        effective = TaxCalculator.calculate_effective_compound_rate(
            [Decimal("15.00"), Decimal("2.00")]
        )
        # (1.15)(1.02) - 1 = 0.173 → 17.30%
        assert effective == Decimal("17.30")


class TestTaxCalculatorValidation:
    """Tax validation helpers — static method with positional args."""

    def test_validate_tax_calculation_valid(self):
        # validate_tax_calculation(base, tax, total) → True or raises
        result = TaxCalculator.validate_tax_calculation(
            Decimal("1000.00"), Decimal("150.00"), Decimal("1150.00")
        )
        assert result is True

    def test_validate_tax_calculation_invalid(self):
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            TaxCalculator.validate_tax_calculation(
                Decimal("1000.00"), Decimal("200.00"), Decimal("1150.00")
            )


class TestTaxCalculatorEdgeCases:
    """Edge cases and boundary conditions."""

    def test_zero_price(self):
        result = TaxCalculator.calculate_tax_amount(Decimal("0"), Decimal("15.00"))
        assert result == Decimal("0.00")

    def test_very_large_price(self):
        result = TaxCalculator.calculate_tax_amount(
            Decimal("999999999.99"), Decimal("15.00")
        )
        assert result > Decimal("0")

    def test_fractional_rate(self):
        result = TaxCalculator.calculate_tax_amount(
            Decimal("100.00"), Decimal("7.50")
        )
        assert result == Decimal("7.50")

    def test_rounding_consistency(self):
        calc = TaxCalculator()
        price = Decimal("333.33")
        rate = Decimal("15.00")
        tax = TaxCalculator.calculate_tax_amount(price, rate)
        rounded = calc.round_price(tax)
        assert rounded == rounded.quantize(Decimal("0.01"))
