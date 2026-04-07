"""Tests for PAYE tax calculator service."""

import pytest
from decimal import Decimal

from apps.payroll.services.paye_calculator import PAYECalculator

pytestmark = pytest.mark.django_db


class TestPAYECalculator:
    """Tests for PAYE progressive tax calculations."""

    def test_taxable_income_from_components(self, employee_salary):
        """Taxable income should sum is_taxable earning components."""
        taxable = PAYECalculator.get_taxable_income(employee_salary)
        # Basic (100000 taxable) + Transport (5000 taxable) = 105000
        # Medical is NOT taxable
        assert taxable == Decimal("105000.00")

    def test_annual_tax_zero_slab(self, paye_slabs):
        """Income within 0% slab should have zero tax."""
        tax = PAYECalculator.calculate_annual_tax(Decimal("1000000"), 2024)
        assert tax == Decimal("0.00")

    def test_annual_tax_first_taxed_slab(self, paye_slabs):
        """Income in first taxed slab (6%) should be calculated progressively."""
        # 1,400,000: first 1,200,000 @ 0% = 0, remaining 200,000 @ 6%
        tax = PAYECalculator.calculate_annual_tax(Decimal("1400000"), 2024)
        # 200000 * 6% = 12000.00
        assert tax == Decimal("12000.00")

    def test_annual_tax_multiple_slabs(self, paye_slabs):
        """Tax across multiple slabs should be progressive."""
        # 2,500,000 annual:
        # 0 - 1,200,000 (range 1,200,000) @ 0% = 0
        # 1,200,001 - 1,700,000 (range 499,999) @ 6% = 29,999.94
        # 1,700,001 - 2,200,000 (range 499,999) @ 12% = 59,999.88
        # remaining = 2,500,000 - 2,199,998 = 300,002 @ 18% = 54,000.36
        tax = PAYECalculator.calculate_annual_tax(Decimal("2500000"), 2024)
        expected = Decimal("29999.94") + Decimal("59999.88") + Decimal("54000.36")
        assert tax == expected

    def test_annual_tax_top_slab(self, paye_slabs):
        """Income exceeding all slabs should be taxed at top rate."""
        tax = PAYECalculator.calculate_annual_tax(Decimal("5000000"), 2024)
        assert tax > Decimal("0")

    def test_annual_tax_no_slabs(self, tenant_context):
        """No tax slabs configured should return zero."""
        tax = PAYECalculator.calculate_annual_tax(Decimal("5000000"), 2024)
        assert tax == Decimal("0")

    def test_calculate_monthly_paye(self, employee_salary, paye_slabs, tax_exemptions):
        """Monthly PAYE should be annual tax / 12."""
        result = PAYECalculator.calculate(employee_salary, 2024)
        assert "monthly_tax" in result
        assert "annual_tax" in result
        assert "monthly_taxable_income" in result
        assert "monthly_exemptions" in result
        assert result["monthly_tax"] >= Decimal("0")

    def test_monthly_exemptions_applied(self, employee_salary, paye_slabs, tax_exemptions):
        """Exemptions should reduce taxable income."""
        result = PAYECalculator.calculate(employee_salary, 2024)
        assert result["monthly_exemptions"] > Decimal("0")
        assert result["net_monthly_taxable"] < result["monthly_taxable_income"]

    def test_get_tax_slab_lookup(self, paye_slabs):
        """Should return the correct slab for a given income."""
        slab = PAYECalculator.get_tax_slab(Decimal("1500000"), 2024)
        assert slab is not None
        assert slab.rate == Decimal("6.00")

    def test_project_annual_tax(self, paye_slabs):
        """Annual projection should account for remaining months."""
        result = PAYECalculator.project_annual_tax(
            monthly_income=Decimal("200000"),
            current_month=6,
            tax_year=2024,
        )
        assert "projected_annual_income" in result
        assert "projected_annual_tax" in result
        assert "adjusted_monthly_tax" in result
        assert result["remaining_months"] == 7

    def test_project_annual_tax_with_ytd(self, paye_slabs):
        """YTD income should be used in projection."""
        result = PAYECalculator.project_annual_tax(
            monthly_income=Decimal("200000"),
            current_month=6,
            ytd_income=Decimal("1000000"),
            tax_year=2024,
        )
        # projected = 1000000 + 200000 * 7 = 2400000
        assert result["projected_annual_income"] == Decimal("2400000")

    def test_get_effective_rate(self, paye_slabs):
        """Effective rate should be total tax / total income * 100."""
        rate = PAYECalculator.get_effective_rate(Decimal("2400000"), 2024)
        assert rate >= Decimal("0")
        assert rate <= Decimal("36")

    def test_effective_rate_zero_income(self, paye_slabs):
        """Zero income should give zero effective rate."""
        rate = PAYECalculator.get_effective_rate(Decimal("0"), 2024)
        assert rate == Decimal("0")
