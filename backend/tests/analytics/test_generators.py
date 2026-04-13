"""Tests for analytics report generators."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.analytics.generators.base import BaseReportGenerator

pytestmark = pytest.mark.django_db


# ── BaseReportGenerator ──────────────────────────────────────────


class TestBaseReportGenerator:
    """Tests for common generator utilities."""

    def test_get_filter_value(self, tenant_context):
        class Stub(BaseReportGenerator):
            REPORT_TYPE = "TEST"
            def get_base_queryset(self): return None
            def generate(self): return {}

        gen = Stub(filter_parameters={"key": "value"})
        assert gen.get_filter_value("key") == "value"
        assert gen.get_filter_value("missing", "default") == "default"

    def test_calculate_totals(self, tenant_context):
        class Stub(BaseReportGenerator):
            REPORT_TYPE = "TEST"
            def get_base_queryset(self): return None
            def generate(self): return {}

        gen = Stub()
        data = [
            {"amount": 100, "qty": 3, "rank": 1},
            {"amount": 200, "qty": 5, "rank": 2},
        ]
        totals = gen.calculate_totals(data)
        assert totals["amount"] == 300
        assert totals["qty"] == 8
        assert totals["row_count"] == 2
        # rank should be excluded
        assert "rank" not in totals

    def test_build_response_structure(self, tenant_context):
        class Stub(BaseReportGenerator):
            REPORT_TYPE = "TEST"
            def get_base_queryset(self): return None
            def generate(self): return {}

        gen = Stub(filter_parameters={"date_range": {"start_date": "2024-01-01", "end_date": "2024-12-31"}})
        gen.start_timer()
        data = [{"value": 42}]
        resp = gen.build_response(data)
        assert resp["report_type"] == "TEST"
        assert resp["data"] == data
        assert resp["row_count"] == 1
        assert "generated_at" in resp
        assert "metadata" in resp

    def test_get_report_title(self, tenant_context):
        class Stub(BaseReportGenerator):
            REPORT_TYPE = "SALES_BY_PRODUCT"
            def get_base_queryset(self): return None
            def generate(self): return {}

        gen = Stub(filter_parameters={"date_range": {"start_date": "2024-01-01", "end_date": "2024-12-31"}})
        title = gen.get_report_title()
        assert "Sales By Product" in title
        assert "2024-01-01" in title

    def test_to_csv_output(self, tenant_context):
        class Stub(BaseReportGenerator):
            REPORT_TYPE = "TEST"
            def get_base_queryset(self): return None
            def generate(self): return {}

        gen = Stub()
        data = {"data": [{"name": "Product A", "qty": 10}]}
        csv_str = gen.to_csv(data)
        assert "name" in csv_str
        assert "Product A" in csv_str


# ── Sales Generators ─────────────────────────────────────────────


class TestSalesByProductReport:
    """Tests for SalesByProductReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.sales.by_product import SalesByProductReport

        gen = SalesByProductReport()
        result = gen.generate()
        assert result["report_type"] == "SALES_BY_PRODUCT"
        assert result["data"] == []
        assert result["row_count"] == 0

    def test_generate_with_date_filter(self, tenant_context):
        from apps.analytics.generators.sales.by_product import SalesByProductReport

        gen = SalesByProductReport(
            filter_parameters={
                "date_range": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                }
            }
        )
        result = gen.generate()
        assert result["report_type"] == "SALES_BY_PRODUCT"
        assert isinstance(result["data"], list)


class TestSalesByCustomerReport:
    """Tests for SalesByCustomerReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.sales.by_customer import SalesByCustomerReport

        gen = SalesByCustomerReport()
        result = gen.generate()
        assert result["report_type"] == "SALES_BY_CUSTOMER"
        assert result["data"] == []

    def test_generate_with_filters(self, tenant_context):
        from apps.analytics.generators.sales.by_customer import SalesByCustomerReport

        gen = SalesByCustomerReport(
            filter_parameters={
                "date_range": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-30",
                }
            }
        )
        result = gen.generate()
        assert "totals" in result


class TestSalesByPeriodReport:
    """Tests for SalesByPeriodReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.sales.by_period import SalesByPeriodReport

        gen = SalesByPeriodReport()
        result = gen.generate()
        assert result["report_type"] == "SALES_BY_PERIOD"

    def test_grouping_options(self, tenant_context):
        from apps.analytics.generators.sales.by_period import SalesByPeriodReport

        for grouping in ("daily", "weekly", "monthly", "quarterly", "yearly"):
            gen = SalesByPeriodReport(
                filter_parameters={"grouping": grouping}
            )
            result = gen.generate()
            assert result["report_type"] == "SALES_BY_PERIOD"


class TestSalesByChannelReport:
    """Tests for SalesByChannelReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.sales.by_channel import SalesByChannelReport

        gen = SalesByChannelReport()
        result = gen.generate()
        assert result["report_type"] == "SALES_BY_CHANNEL"
        assert isinstance(result["data"], list)


class TestSalesByCashierReport:
    """Tests for SalesByCashierReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.sales.by_cashier import SalesByCashierReport

        gen = SalesByCashierReport()
        result = gen.generate()
        assert result["report_type"] == "SALES_BY_CASHIER"


# ── Inventory Generators ─────────────────────────────────────────


class TestStockLevelReport:
    """Tests for StockLevelReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.inventory.stock_level import StockLevelReport

        gen = StockLevelReport()
        result = gen.generate()
        assert result["report_type"] == "STOCK_LEVEL"
        assert result["data"] == []


class TestStockMovementReport:
    """Tests for StockMovementReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.inventory.stock_movement import (
            StockMovementReport,
        )

        gen = StockMovementReport()
        result = gen.generate()
        assert result["report_type"] == "STOCK_MOVEMENT"


class TestStockValuationReport:
    """Tests for StockValuationReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.inventory.stock_valuation import (
            StockValuationReport,
        )

        gen = StockValuationReport()
        result = gen.generate()
        assert result["report_type"] == "STOCK_VALUATION"


# ── Purchase Generators ──────────────────────────────────────────


class TestPurchaseByVendorReport:
    """Tests for PurchaseByVendorReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.purchase.by_vendor import PurchaseByVendorReport

        gen = PurchaseByVendorReport()
        result = gen.generate()
        assert result["report_type"] == "PURCHASE_VENDOR"


class TestPurchaseByCategoryReport:
    """Tests for PurchaseByCategoryReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.purchase.by_category import (
            PurchaseByCategoryReport,
        )

        gen = PurchaseByCategoryReport()
        result = gen.generate()
        assert result["report_type"] == "PURCHASE_CATEGORY"


class TestVendorPerformanceReport:
    """Tests for VendorPerformanceReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.purchase.vendor_performance import (
            VendorPerformanceReport,
        )

        gen = VendorPerformanceReport()
        result = gen.generate()
        assert result["report_type"] == "VENDOR_PERFORMANCE"


# ── Customer Generators ──────────────────────────────────────────


class TestCustomerAcquisitionReport:
    """Tests for CustomerAcquisitionReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.customer.acquisition import (
            CustomerAcquisitionReport,
        )

        gen = CustomerAcquisitionReport()
        result = gen.generate()
        assert result["report_type"] == "CUSTOMER_ACQUISITION"
        assert result["totals"]["total_new_customers"] == 0


class TestCustomerRetentionReport:
    """Tests for CustomerRetentionReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.customer.retention import CustomerRetentionReport

        gen = CustomerRetentionReport()
        result = gen.generate()
        assert result["report_type"] == "CUSTOMER_RETENTION"
        assert result["totals"]["total_customers"] == 0


class TestCustomerLifetimeValueReport:
    """Tests for CustomerLifetimeValueReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.customer.lifetime_value import (
            CustomerLifetimeValueReport,
        )

        gen = CustomerLifetimeValueReport()
        result = gen.generate()
        assert result["report_type"] == "CUSTOMER_LIFETIME_VALUE"
        assert result["data"] == []


# ── Staff Generators ─────────────────────────────────────────────


class TestAttendanceReport:
    """Tests for AttendanceReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.staff.attendance import AttendanceReport

        gen = AttendanceReport()
        result = gen.generate()
        assert result["report_type"] == "STAFF_ATTENDANCE"
        assert result["totals"]["total_employees"] == 0


class TestLeaveReport:
    """Tests for LeaveReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.staff.leave import LeaveReport

        gen = LeaveReport()
        result = gen.generate()
        assert result["report_type"] == "STAFF_LEAVE"
        assert result["totals"]["total_employees"] == 0


class TestOvertimeReport:
    """Tests for OvertimeReport generator."""

    def test_generate_empty(self, tenant_context):
        from apps.analytics.generators.staff.overtime import OvertimeReport

        gen = OvertimeReport()
        result = gen.generate()
        assert result["report_type"] == "STAFF_OVERTIME"
        assert result["totals"]["total_employees"] == 0
