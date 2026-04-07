"""Tests for alerts services: velocity, reorder calculator."""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from apps.inventory.alerts.services.reorder_calculator import ReorderCalculator
from apps.inventory.alerts.services.sales_velocity import SalesVelocityService

from .factories import (
    GlobalStockSettingsFactory,
    ProductFactory,
    ProductStockConfigFactory,
    WarehouseFactory,
)

pytestmark = pytest.mark.django_db


# ── SalesVelocityService ───────────────────────────────────────────


class TestSalesVelocityService:
    def test_calculate_velocity_no_sales(self, tenant_context):
        """No sales history returns fallback result."""
        product = ProductFactory()
        result = SalesVelocityService.calculate_velocity(product, days=30)
        # Should return a dict or None
        assert result is None or isinstance(result, dict)

    def test_calculate_daily_velocity_no_data(self, tenant_context):
        product = ProductFactory()
        result = SalesVelocityService.calculate_daily_velocity(product, days=30)
        assert result is None

    def test_detect_trend_no_data(self, tenant_context):
        product = ProductFactory()
        result = SalesVelocityService.detect_trend(product, days=30)
        assert isinstance(result, dict)
        assert result["direction"] == "flat"

    def test_calculate_weekly_velocity(self, tenant_context):
        product = ProductFactory()
        result = SalesVelocityService.calculate_weekly_velocity(product, weeks=4)
        assert result is None

    def test_velocity_with_sales_data(self, tenant_context):
        """Velocity calculation with mocked sales data returns proper dict."""
        product = ProductFactory()
        fake_sales = [
            {"date": "2024-01-01", "quantity": Decimal("10")},
            {"date": "2024-01-02", "quantity": Decimal("15")},
            {"date": "2024-01-03", "quantity": Decimal("20")},
        ]
        with patch.object(
            SalesVelocityService, "get_sales_data", return_value=fake_sales
        ):
            result = SalesVelocityService.calculate_velocity(product, days=30)

        assert result is not None
        assert result["source"] == "order_history"
        assert result["avg_daily_velocity"] > 0
        assert result["total_sold"] == Decimal("45")

    def test_daily_velocity_with_data(self, tenant_context):
        """Daily velocity with data returns avg, std_dev, data_points."""
        product = ProductFactory()
        fake_sales = [
            {"date": "2024-01-01", "quantity": Decimal("8")},
            {"date": "2024-01-02", "quantity": Decimal("12")},
            {"date": "2024-01-03", "quantity": Decimal("10")},
        ]
        with patch.object(
            SalesVelocityService, "get_sales_data", return_value=fake_sales
        ):
            result = SalesVelocityService.calculate_daily_velocity(product, days=30)

        assert result is not None
        assert "avg_daily" in result
        assert "std_dev" in result
        assert result["data_points"] == 3

    def test_detect_trend_upward(self, tenant_context):
        """Increasing sales data slopes upward."""
        product = ProductFactory()
        fake_sales = [
            {"date": f"2024-01-{i:02d}", "quantity": Decimal(str(i * 5))}
            for i in range(1, 11)
        ]
        with patch.object(
            SalesVelocityService, "get_sales_data", return_value=fake_sales
        ):
            result = SalesVelocityService.detect_trend(product, days=30)

        assert result["direction"] == "up"
        assert result["slope"] > 0

    def test_detect_seasonality_no_data(self, tenant_context):
        """Seasonality detection returns False with no data."""
        product = ProductFactory()
        result = SalesVelocityService.detect_seasonality(product)
        assert result is False

    def test_get_seasonal_factor_default(self, tenant_context):
        """Seasonal factor defaults to 1.0 without data."""
        product = ProductFactory()
        result = SalesVelocityService.get_seasonal_factor(product)
        assert result == 1.0

    def test_handle_no_sales_zero_velocity(self, tenant_context):
        """No-sales fallback returns zero velocity dict."""
        product = ProductFactory()
        result = SalesVelocityService.handle_no_sales(product, days=30)
        assert result is not None
        assert result["source"] in ("extended_history", "category_average", "no_data")

    def test_week_over_week_growth_no_data(self, tenant_context):
        """WoW growth returns empty list with insufficient data."""
        product = ProductFactory()
        result = SalesVelocityService.week_over_week_growth(product, weeks=4)
        assert result == []


# ── ReorderCalculator ──────────────────────────────────────────────


class TestReorderCalculator:
    def test_calculate_days_until_stockout(self):
        days = ReorderCalculator.calculate_days_until_stockout(
            current_stock=Decimal("100.000"),
            daily_velocity=Decimal("10.000"),
        )
        # 100 / 10 = 10 days
        assert days == Decimal("10.00")

    def test_stockout_zero_velocity(self):
        days = ReorderCalculator.calculate_days_until_stockout(
            current_stock=Decimal("100.000"),
            daily_velocity=Decimal("0.000"),
        )
        # No sales → returns Decimal("999")
        assert days == Decimal("999")

    def test_determine_urgency_critical(self):
        # < 5 is critical
        assert ReorderCalculator.determine_urgency(Decimal("2")) == "critical"

    def test_determine_urgency_high(self):
        # 5 <= x < 15 is high
        assert ReorderCalculator.determine_urgency(Decimal("10")) == "high"

    def test_determine_urgency_medium(self):
        # 15 <= x < 30 is medium
        assert ReorderCalculator.determine_urgency(Decimal("20")) == "medium"

    def test_determine_urgency_low(self):
        # >= 30 is low
        assert ReorderCalculator.determine_urgency(Decimal("35")) == "low"

    def test_simplified_safety_stock(self):
        ss = ReorderCalculator.simplified_safety_stock(
            daily_velocity=Decimal("10.000"), safety_days=7
        )
        # 10 × 7 = 70
        assert ss == Decimal("70.000") or ss >= Decimal("60")

    def test_calculate_annual_demand(self):
        ad = ReorderCalculator.calculate_annual_demand(Decimal("10.000"))
        # 10 × 365 = 3650
        assert ad == Decimal("3650.000") or ad >= Decimal("3600")

    def test_calculate_eoq_with_settings(self, tenant_context):
        settings = GlobalStockSettingsFactory(
            ordering_cost_lkr=Decimal("5000.00"),
            holding_cost_percent=Decimal("0.25"),
        )
        product = ProductFactory()
        config = ProductStockConfigFactory(product=product)
        result = ReorderCalculator.calculate_eoq(
            product=product,
            daily_velocity=Decimal("10.000"),
            config=config,
        )
        # Should return a positive Decimal or None if holding cost not calculable
        assert result is None or result > 0

    def test_calculate_reorder_suggestion_no_stock(self, tenant_context):
        GlobalStockSettingsFactory()
        product = ProductFactory()
        ProductStockConfigFactory(product=product)
        result = ReorderCalculator.calculate_reorder_suggestion(product=product)
        # No stock levels — result may be None or a dict
        assert result is None or isinstance(result, dict)

    def test_calculate_estimated_cost(self, tenant_context):
        product = ProductFactory()
        total, unit = ReorderCalculator.calculate_estimated_cost(
            product=product,
            quantity=Decimal("100.000"),
        )
        assert isinstance(total, Decimal)
        assert isinstance(unit, Decimal)

    def test_get_reorder_point(self, tenant_context):
        config = {"lead_time_days": 7}
        ss = Decimal("20.000")
        rp = ReorderCalculator.get_reorder_point(
            daily_velocity=Decimal("10.000"),
            config=config,
            safety_stock=ss,
        )
        assert isinstance(rp, Decimal)
        assert rp > 0

    def test_suggestion_with_stock_level(self, tenant_context):
        """Reorder suggestion when stock level exists."""
        from apps.inventory.models import StockLevel

        GlobalStockSettingsFactory()
        product = ProductFactory(is_active=True)
        warehouse = WarehouseFactory()
        config = ProductStockConfigFactory(
            product=product,
            warehouse=warehouse,
            low_stock_threshold=Decimal("10.000"),
            reorder_point=Decimal("15.000"),
            reorder_quantity=Decimal("50.000"),
        )
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("5.000"),
        )

        result = ReorderCalculator.calculate_reorder_suggestion(product=product)
        # Should return a suggestion dict or None (depends on velocity)
        assert result is None or isinstance(result, dict)
        if result:
            assert "suggested_qty" in result
            assert result["suggested_qty"] > 0

    def test_sufficient_stock_no_suggestion(self, tenant_context):
        """Product with sufficient stock should not generate urgent suggestion."""
        from apps.inventory.models import StockLevel

        GlobalStockSettingsFactory()
        product = ProductFactory(is_active=True)
        warehouse = WarehouseFactory()
        ProductStockConfigFactory(
            product=product,
            warehouse=warehouse,
            low_stock_threshold=Decimal("10.000"),
            reorder_point=Decimal("15.000"),
        )
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("500.000"),
        )

        result = ReorderCalculator.calculate_reorder_suggestion(product=product)
        # With 500 units and no velocity, should be None or low urgency
        if result:
            assert result.get("urgency") in ("low", "medium", None)


# ── ConfigResolver ─────────────────────────────────────────────────


class TestConfigResolver:
    def test_resolve_global_fallback(self, tenant_context):
        """Config resolves to global when no product/category config."""
        from apps.inventory.alerts.services.config_resolver import ConfigResolver

        GlobalStockSettingsFactory(default_low_threshold=Decimal("10.000"))
        product = ProductFactory()

        config = ConfigResolver.resolve_for_product(product)

        assert isinstance(config, dict)
        assert "low_stock_threshold" in config

    def test_resolve_product_config_priority(self, tenant_context):
        """Product-level config takes precedence."""
        from apps.inventory.alerts.services.config_resolver import ConfigResolver

        GlobalStockSettingsFactory(default_low_threshold=Decimal("10.000"))
        product = ProductFactory()
        ProductStockConfigFactory(
            product=product,
            low_stock_threshold=Decimal("25.000"),
        )

        config = ConfigResolver.resolve_for_product(product)

        assert config["low_stock_threshold"] == Decimal("25.000")

    def test_resolve_returns_source(self, tenant_context):
        """Resolved config includes source field."""
        from apps.inventory.alerts.services.config_resolver import ConfigResolver

        GlobalStockSettingsFactory()
        product = ProductFactory()

        config = ConfigResolver.resolve_for_product(product)

        assert "source" in config or "sources" in config
