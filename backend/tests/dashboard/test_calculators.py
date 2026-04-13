"""Tests for dashboard KPI calculators."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from apps.dashboard.calculators.base import BaseKPICalculator
from apps.dashboard.calculators.financial import FinancialKPICalculator
from apps.dashboard.calculators.hr import HRKPICalculator
from apps.dashboard.calculators.inventory import InventoryKPICalculator
from apps.dashboard.calculators.sales import SalesKPICalculator


class TestBaseKPICalculator:
    """Tests for the BaseKPICalculator."""

    def test_format_result(self):
        calc = SalesKPICalculator()
        result = calc.format_result(value=100, label="Test KPI")
        assert result["value"] == 100
        assert result["label"] == "Test KPI"
        assert result["format_type"] == "number"

    def test_format_result_with_change(self):
        calc = SalesKPICalculator()
        result = calc.format_result(value=100, label="Test", change=15.5)
        assert result["change"] == 15.5

    def test_format_result_with_extra(self):
        calc = SalesKPICalculator()
        result = calc.format_result(
            value=100, label="Test", extra={"detail": "info"}
        )
        assert result["extra"]["detail"] == "info"

    def test_calculate_change_positive(self):
        calc = SalesKPICalculator()
        change = calc.calculate_change(120, 100)
        assert change["change_percent"] == 20.0
        assert change["trend"] == "up"

    def test_calculate_change_negative(self):
        calc = SalesKPICalculator()
        change = calc.calculate_change(80, 100)
        assert change["change_percent"] == -20.0
        assert change["trend"] == "down"

    def test_calculate_change_zero_previous(self):
        calc = SalesKPICalculator()
        change = calc.calculate_change(100, 0)
        assert change["change_percent"] == Decimal("0.00")
        assert change["trend"] == "up"

    def test_get_date_range_returns_tuple(self):
        calc = SalesKPICalculator()
        start, end = calc.get_date_range("month")
        assert start is not None
        assert end is not None
        assert start <= end


class TestSalesKPICalculator:
    """Tests for SalesKPICalculator."""

    def test_unknown_kpi_code(self):
        calc = SalesKPICalculator()
        result = calc.calculate("nonexistent_kpi")
        assert "error" in result

    @pytest.mark.django_db
    def test_todays_sales_empty(self, tenant_context):
        calc = SalesKPICalculator()
        result = calc.calculate("todays_sales")
        assert "value" in result
        assert result["value"] == 0 or isinstance(result["value"], (int, float, Decimal))

    @pytest.mark.django_db
    def test_monthly_sales_empty(self, tenant_context):
        calc = SalesKPICalculator()
        result = calc.calculate("monthly_sales")
        assert "value" in result

    @pytest.mark.django_db
    def test_average_order_value_empty(self, tenant_context):
        calc = SalesKPICalculator()
        result = calc.calculate("average_order_value")
        assert "value" in result

    @pytest.mark.django_db
    def test_orders_count_empty(self, tenant_context):
        calc = SalesKPICalculator()
        result = calc.calculate("orders_count")
        assert "value" in result
        assert result["value"] == 0


class TestInventoryKPICalculator:
    """Tests for InventoryKPICalculator."""

    def test_unknown_kpi_code(self):
        calc = InventoryKPICalculator()
        result = calc.calculate("nonexistent_kpi")
        assert "error" in result

    @pytest.mark.django_db
    def test_stock_value_empty(self, tenant_context):
        calc = InventoryKPICalculator()
        result = calc.calculate("stock_value")
        assert "value" in result

    @pytest.mark.django_db
    def test_low_stock_items_empty(self, tenant_context):
        calc = InventoryKPICalculator()
        result = calc.calculate("low_stock_items")
        assert "value" in result

    @pytest.mark.django_db
    def test_out_of_stock_empty(self, tenant_context):
        calc = InventoryKPICalculator()
        result = calc.calculate("out_of_stock")
        assert "value" in result


class TestFinancialKPICalculator:
    """Tests for FinancialKPICalculator."""

    def test_unknown_kpi_code(self):
        calc = FinancialKPICalculator()
        result = calc.calculate("nonexistent_kpi")
        assert "error" in result

    @pytest.mark.django_db
    def test_revenue_empty(self, tenant_context):
        calc = FinancialKPICalculator()
        result = calc.calculate("revenue")
        assert "value" in result

    @pytest.mark.django_db
    def test_expenses_empty(self, tenant_context):
        calc = FinancialKPICalculator()
        result = calc.calculate("expenses")
        assert "value" in result

    @pytest.mark.django_db
    def test_net_income_empty(self, tenant_context):
        calc = FinancialKPICalculator()
        result = calc.calculate("net_income")
        assert "value" in result

    @pytest.mark.django_db
    def test_accounts_receivable_empty(self, tenant_context):
        calc = FinancialKPICalculator()
        result = calc.calculate("accounts_receivable")
        assert "value" in result


class TestHRKPICalculator:
    """Tests for HRKPICalculator."""

    def test_unknown_kpi_code(self):
        calc = HRKPICalculator()
        result = calc.calculate("nonexistent_kpi")
        assert "error" in result

    @pytest.mark.django_db
    def test_total_employees_empty(self, tenant_context):
        calc = HRKPICalculator()
        result = calc.calculate("total_employees")
        assert "value" in result
        assert result["value"] == 0

    @pytest.mark.django_db
    def test_new_hires_empty(self, tenant_context):
        calc = HRKPICalculator()
        result = calc.calculate("new_hires")
        assert "value" in result
        assert result["value"] == 0

    @pytest.mark.django_db
    def test_turnover_rate_empty(self, tenant_context):
        calc = HRKPICalculator()
        result = calc.calculate("turnover_rate")
        assert "value" in result

    @pytest.mark.django_db
    def test_attendance_rate_empty(self, tenant_context):
        calc = HRKPICalculator()
        result = calc.calculate("attendance_rate")
        assert "value" in result

    @pytest.mark.django_db
    def test_pending_leave_requests_empty(self, tenant_context):
        calc = HRKPICalculator()
        result = calc.calculate("pending_leave_requests")
        assert "value" in result
        assert result["value"] == 0

    @pytest.mark.django_db
    def test_payroll_cost_empty(self, tenant_context):
        calc = HRKPICalculator()
        result = calc.calculate("payroll_cost")
        assert "value" in result

    @pytest.mark.django_db
    def test_department_headcount_empty(self, tenant_context):
        calc = HRKPICalculator()
        result = calc.calculate("department_headcount")
        assert "value" in result
        assert result["value"] == 0
