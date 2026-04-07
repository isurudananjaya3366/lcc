"""Tests for EPF and ETF calculator services."""

import pytest
from decimal import Decimal

from apps.payroll.services.epf_calculator import EPFCalculator
from apps.payroll.services.etf_calculator import ETFCalculator

pytestmark = pytest.mark.django_db


class TestEPFCalculator:
    """Tests for EPF contribution calculations."""

    def test_epf_base_from_applicable_components(self, employee_salary, basic_component):
        """EPF base should include only is_epf_applicable earning components."""
        epf_base = EPFCalculator.get_epf_base(employee_salary)
        # Basic (100000) is EPF applicable; transport and medical are not
        assert epf_base == Decimal("100000.00")

    def test_calculate_employee_contribution(self, employee_salary, epf_settings):
        """Employee EPF should be 8% of EPF base."""
        result = EPFCalculator.calculate(employee_salary, epf_settings)
        # 8% of 100000 = 8000
        assert result["employee_contribution"] == Decimal("8000.00")

    def test_calculate_employer_contribution(self, employee_salary, epf_settings):
        """Employer EPF should be 12% of EPF base."""
        result = EPFCalculator.calculate(employee_salary, epf_settings)
        # 12% of 100000 = 12000
        assert result["employer_contribution"] == Decimal("12000.00")

    def test_calculate_returns_epf_base(self, employee_salary, epf_settings):
        """Result should contain the EPF base amount."""
        result = EPFCalculator.calculate(employee_salary, epf_settings)
        assert result["epf_base"] == Decimal("100000.00")

    def test_calculate_no_settings_returns_zeros(self, employee_salary):
        """Without active EPF settings, all contributions should be zero."""
        result = EPFCalculator.calculate(employee_salary, settings=None)
        assert result["employee_contribution"] == Decimal("0")
        assert result["employer_contribution"] == Decimal("0")
        assert result["epf_base"] == Decimal("0")

    def test_calculate_employee_epf_convenience(self, epf_settings):
        """Convenience method for employee EPF."""
        result = EPFCalculator.calculate_employee_epf(Decimal("200000"), epf_settings)
        assert result == Decimal("16000.00")

    def test_calculate_employer_epf_convenience(self, epf_settings):
        """Convenience method for employer EPF."""
        result = EPFCalculator.calculate_employer_epf(Decimal("200000"), epf_settings)
        assert result == Decimal("24000.00")

    def test_calculate_total_epf(self, epf_settings):
        """Total EPF should be employee + employer contributions."""
        result = EPFCalculator.calculate_total_epf(Decimal("200000"), epf_settings)
        # 8% + 12% = 20% of 200000 = 40000
        assert result == Decimal("40000.00")

    def test_ceiling_applied_when_configured(self, employee_salary, tenant_context):
        """EPF ceiling should cap contributions."""
        from apps.payroll.models import EPFSettings

        settings = EPFSettings.objects.create(
            employee_rate=Decimal("8.00"),
            employer_rate=Decimal("12.00"),
            max_contribution_ceiling=Decimal("5000.00"),
            is_active=True,
        )
        result = EPFCalculator.calculate(employee_salary, settings)
        assert result["employee_contribution"] <= Decimal("5000.00")
        assert result["employer_contribution"] <= Decimal("5000.00")


class TestETFCalculator:
    """Tests for ETF contribution calculations."""

    def test_etf_employer_contribution(self, employee_salary, etf_settings):
        """ETF employer contribution should be 3% of ETF base."""
        result = ETFCalculator.calculate(employee_salary, etf_settings)
        # 3% of 100000 = 3000
        assert result["employer_contribution"] == Decimal("3000.00")

    def test_etf_base_matches_epf_base(self, employee_salary, etf_settings):
        """ETF base should be same as EPF base."""
        result = ETFCalculator.calculate(employee_salary, etf_settings)
        epf_base = EPFCalculator.get_epf_base(employee_salary)
        assert result["etf_base"] == epf_base

    def test_etf_no_settings_returns_zeros(self, employee_salary):
        """Without active ETF settings, all contributions zero."""
        result = ETFCalculator.calculate(employee_salary, settings=None)
        assert result["employer_contribution"] == Decimal("0")
        assert result["etf_base"] == Decimal("0")
