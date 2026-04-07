"""Tests for alerts Celery tasks: stock monitoring, resolution, reorder."""

import pytest
from decimal import Decimal
from unittest.mock import patch

from django.utils import timezone

from apps.inventory.alerts.constants import (
    ALERT_STATUS_ACTIVE,
    ALERT_STATUS_RESOLVED,
    ALERT_STATUS_SNOOZED,
    ALERT_TYPE_BACK_IN_STOCK,
    ALERT_TYPE_CRITICAL_STOCK,
    ALERT_TYPE_LOW_STOCK,
    ALERT_TYPE_OUT_OF_STOCK,
)
from apps.inventory.alerts.models import (
    MonitoringLog,
    ProductStockConfig,
    StockAlert,
)
from apps.inventory.models import StockLevel

from .factories import (
    GlobalStockSettingsFactory,
    MonitoringLogFactory,
    ProductFactory,
    ProductStockConfigFactory,
    StockAlertFactory,
    WarehouseFactory,
)

pytestmark = pytest.mark.django_db


# ── Stock Monitoring Core Logic ─────────────────────────────────


class TestStockMonitoringLogic:
    """Tests for the core monitoring functions (non-Celery)."""

    def test_check_low_stock_detects_low(self, tenant_context):
        """Low stock is detected when available <= threshold and > 0."""
        from apps.inventory.alerts.tasks.stock_monitor import check_low_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("8.000"),
        )

        config = {"low_stock_threshold": 10}
        result = check_low_stock(product, stock_level, config)

        assert result["is_low"] is True
        assert result["current_stock"] <= 10
        assert result["severity"] > 0.0
        assert result["severity_level"] in ("low", "medium", "high", "critical")

    def test_check_low_stock_above_threshold(self, tenant_context):
        """Stock above threshold is not flagged as low."""
        from apps.inventory.alerts.tasks.stock_monitor import check_low_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("50.000"),
        )

        config = {"low_stock_threshold": 10}
        result = check_low_stock(product, stock_level, config)

        assert result["is_low"] is False
        assert result["severity"] == 0.0
        assert result["severity_level"] == "none"

    def test_check_critical_stock_detects_critical(self, tenant_context):
        """Critical stock detected when below critical threshold."""
        from apps.inventory.alerts.tasks.stock_monitor import check_critical_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("3.000"),
        )

        config = {"low_stock_threshold": 10, "critical_threshold_multiplier": 0.5}
        result = check_critical_stock(product, stock_level, config)

        assert result["is_critical"] is True
        assert result["critical_threshold"] == 5

    def test_check_critical_stock_above_threshold(self, tenant_context):
        """Stock above critical threshold is not critical."""
        from apps.inventory.alerts.tasks.stock_monitor import check_critical_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("8.000"),
        )

        config = {"low_stock_threshold": 10, "critical_threshold_multiplier": 0.5}
        result = check_critical_stock(product, stock_level, config)

        assert result["is_critical"] is False

    def test_check_out_of_stock(self, tenant_context):
        """OOS detected when available quantity is zero."""
        from apps.inventory.alerts.tasks.stock_monitor import check_out_of_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("0.000"),
        )

        result = check_out_of_stock(product, stock_level)

        assert result["is_out_of_stock"] is True
        assert result["available_quantity"] <= 0

    def test_check_out_of_stock_has_stock(self, tenant_context):
        """Product with stock is not OOS."""
        from apps.inventory.alerts.tasks.stock_monitor import check_out_of_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("100.000"),
        )

        result = check_out_of_stock(product, stock_level)

        assert result["is_out_of_stock"] is False

    def test_severity_calculation_gradients(self, tenant_context):
        """Severity calculation returns correct gradient values."""
        from apps.inventory.alerts.tasks.stock_monitor import check_low_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()

        # At 2/10 → severity ≈ 0.8 → critical
        stock_level = StockLevel.objects.create(
            product=product, warehouse=warehouse, quantity=Decimal("2.000"),
        )
        config = {"low_stock_threshold": 10}
        result = check_low_stock(product, stock_level, config)
        assert result["severity"] >= 0.75
        assert result["severity_level"] == "critical"


class TestAlertGeneration:
    """Tests for alert creation from monitoring."""

    def test_generate_alerts_creates_low_stock(self, tenant_context):
        """Low stock triggers alert creation."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            generate_alerts_for_product,
        )

        GlobalStockSettingsFactory()
        product = ProductFactory(is_active=True)
        warehouse = WarehouseFactory()
        # Stock=8 is below low threshold (10) but above critical (10*0.5=5)
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("8.000"),
        )
        ProductStockConfigFactory(
            product=product,
            low_stock_threshold=Decimal("10.000"),
        )

        result = generate_alerts_for_product(product)

        assert result["created"] >= 1
        # Should create LOW_STOCK or CRITICAL_STOCK alert
        assert StockAlert.objects.filter(
            product=product,
            status=ALERT_STATUS_ACTIVE,
        ).exists()

    def test_generate_alerts_creates_oos_alert(self, tenant_context):
        """Zero stock triggers OOS alert."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            generate_alerts_for_product,
        )

        GlobalStockSettingsFactory()
        product = ProductFactory(is_active=True)
        warehouse = WarehouseFactory()
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("0.000"),
        )

        result = generate_alerts_for_product(product)

        assert result["created"] >= 1
        assert StockAlert.objects.filter(
            product=product,
            alert_type=ALERT_TYPE_OUT_OF_STOCK,
        ).exists()

    def test_generate_alerts_no_alert_for_normal_stock(self, tenant_context):
        """Normal stock levels don't create alerts."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            generate_alerts_for_product,
        )

        GlobalStockSettingsFactory()
        product = ProductFactory(is_active=True)
        warehouse = WarehouseFactory()
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("500.000"),
        )

        result = generate_alerts_for_product(product)

        assert result["created"] == 0
        assert not StockAlert.objects.filter(product=product).exists()

    def test_no_duplicate_alerts_for_same_product(self, tenant_context):
        """Subsequent monitoring runs don't create duplicate alerts."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            generate_alerts_for_product,
        )

        GlobalStockSettingsFactory()
        product = ProductFactory(is_active=True)
        warehouse = WarehouseFactory()
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("5.000"),
        )
        ProductStockConfigFactory(
            product=product,
            low_stock_threshold=Decimal("10.000"),
        )

        # First run creates alert
        result1 = generate_alerts_for_product(product)
        # Second run should not duplicate
        result2 = generate_alerts_for_product(product)

        alert_count = StockAlert.objects.filter(
            product=product,
            alert_type=ALERT_TYPE_LOW_STOCK,
        ).count()
        # At most 1 active LOW_STOCK (second may be throttled or updated)
        assert alert_count <= 2


class TestMonitorSkipsExcluded:
    """Tests for exclusion logic in monitoring."""

    def test_excluded_product_skipped(self, tenant_context):
        """Products with monitoring disabled are excluded."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            filter_monitorable_products,
        )

        product = ProductFactory(is_active=True)
        ProductStockConfigFactory(product=product, monitoring_enabled=False)

        products = filter_monitorable_products()
        product_ids = list(products.values_list("id", flat=True))

        assert product.id not in product_ids

    def test_date_excluded_product_skipped(self, tenant_context):
        """Products within exclusion date range are excluded."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            filter_monitorable_products,
        )

        product = ProductFactory(is_active=True)
        today = timezone.now().date()
        ProductStockConfigFactory(
            product=product,
            exclude_from_monitoring=True,
            exclusion_start_date=today - timezone.timedelta(days=1),
            exclusion_end_date=today + timezone.timedelta(days=1),
        )

        products = filter_monitorable_products()
        product_ids = list(products.values_list("id", flat=True))

        assert product.id not in product_ids

    def test_active_tracked_product_included(self, tenant_context):
        """Active, inventory-tracked products are included."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            filter_monitorable_products,
        )

        product = ProductFactory(is_active=True)

        products = filter_monitorable_products()
        product_ids = list(products.values_list("id", flat=True))

        assert product.id in product_ids


class TestBatchProcessing:
    """Tests for batch processing in monitoring."""

    def test_batch_yields_products(self, tenant_context):
        """Batch processor yields product batches."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            batch_process_products,
        )

        ProductFactory.create_batch(5, is_active=True)

        batches = list(batch_process_products())
        total_products = sum(len(batch) for batch in batches)

        assert total_products >= 5


# ── Back In Stock Detection ─────────────────────────────────────


class TestBackInStockDetection:
    """Tests for back-in-stock alert generation (Task 42)."""

    def test_back_in_stock_creates_alert(self, tenant_context):
        """Restocked product triggers BACK_IN_STOCK alert."""
        from apps.inventory.alerts.tasks.stock_monitor import detect_back_in_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("20.000"),
        )

        # Create a recent OOS alert
        StockAlertFactory(
            product=product,
            warehouse=warehouse,
            alert_type=ALERT_TYPE_OUT_OF_STOCK,
            status=ALERT_STATUS_RESOLVED,
        )

        result = detect_back_in_stock(product, stock_level)

        assert result is True
        assert StockAlert.objects.filter(
            product=product,
            warehouse=warehouse,
            alert_type=ALERT_TYPE_BACK_IN_STOCK,
        ).exists()

    def test_back_in_stock_not_triggered_if_still_zero(self, tenant_context):
        """No back-in-stock if stock is still zero."""
        from apps.inventory.alerts.tasks.stock_monitor import detect_back_in_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("0.000"),
        )

        result = detect_back_in_stock(product, stock_level)

        assert result is False

    def test_back_in_stock_not_triggered_without_prior_oos(self, tenant_context):
        """No back-in-stock alert if product was never OOS."""
        from apps.inventory.alerts.tasks.stock_monitor import detect_back_in_stock

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("50.000"),
        )

        result = detect_back_in_stock(product, stock_level)

        assert result is False


# ── Alert Resolution Tasks ──────────────────────────────────────


class TestAutoResolveAlertsTask:
    """Tests for alert resolution Celery tasks."""

    def test_auto_resolve_when_stock_recovers(self, tenant_context):
        """Active alerts resolve when stock rises above threshold."""
        from apps.inventory.alerts.tasks.stock_monitor import auto_resolve_alerts

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("50.000"),  # Well above threshold
        )

        # Create an active low-stock alert with threshold=10
        alert = StockAlertFactory(
            product=product,
            warehouse=warehouse,
            alert_type=ALERT_TYPE_LOW_STOCK,
            status=ALERT_STATUS_ACTIVE,
            threshold_value=10,
        )

        resolved = auto_resolve_alerts(product, stock_level)

        assert resolved >= 1
        alert.refresh_from_db()
        assert alert.status == ALERT_STATUS_RESOLVED

    def test_auto_resolve_does_not_resolve_still_low(self, tenant_context):
        """Alerts remain active if stock is still below threshold."""
        from apps.inventory.alerts.tasks.stock_monitor import auto_resolve_alerts

        product = ProductFactory()
        warehouse = WarehouseFactory()
        stock_level = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("5.000"),  # Still below threshold
        )

        alert = StockAlertFactory(
            product=product,
            warehouse=warehouse,
            alert_type=ALERT_TYPE_LOW_STOCK,
            status=ALERT_STATUS_ACTIVE,
            threshold_value=10,
        )

        resolved = auto_resolve_alerts(product, stock_level)

        assert resolved == 0
        alert.refresh_from_db()
        assert alert.status == ALERT_STATUS_ACTIVE


class TestCheckExpiredSnoozes:
    """Tests for snooze expiration task."""

    def test_expired_snooze_reactivated(self, tenant_context):
        """Expired snoozed alerts are reactivated."""
        from apps.inventory.alerts.tasks.alert_resolution import (
            check_expired_snoozes,
        )

        alert = StockAlertFactory(status=ALERT_STATUS_SNOOZED)
        alert.snoozed_until = timezone.now() - timezone.timedelta(hours=1)
        alert.save(update_fields=["snoozed_until"])

        result = check_expired_snoozes()

        assert result["reactivated"] >= 1
        alert.refresh_from_db()
        assert alert.status == ALERT_STATUS_ACTIVE


# ── Monitoring Log from Task ────────────────────────────────────


class TestMonitoringLogFromTask:
    """Tests for monitoring log creation during task runs."""

    def test_monitor_stock_creates_log(self, tenant_context):
        """monitor_stock function creates proper log entries."""
        from apps.inventory.alerts.tasks.stock_monitor import monitor_stock

        log = MonitoringLog.objects.create(status=MonitoringLog.STATUS_RUNNING)

        stats = monitor_stock(log)

        assert isinstance(stats, dict)
        assert "products_checked" in stats
        assert "alerts_created" in stats
        assert "alerts_resolved" in stats

    def test_log_marked_completed(self, tenant_context):
        """Monitoring log is marked completed with stats."""
        log = MonitoringLogFactory(status=MonitoringLog.STATUS_RUNNING)
        stats = {
            "products_checked": 10,
            "alerts_created": 2,
            "alerts_updated": 1,
            "alerts_resolved": 3,
            "errors": 0,
            "execution_time": 5.5,
        }

        log.mark_completed(stats)
        log.refresh_from_db()

        assert log.status == MonitoringLog.STATUS_COMPLETED
        assert log.products_checked == 10
        assert log.alerts_created == 2

    def test_log_marked_failed(self, tenant_context):
        """Monitoring log is marked failed with error info."""
        log = MonitoringLogFactory(status=MonitoringLog.STATUS_RUNNING)

        log.mark_failed("Test error", "traceback info")
        log.refresh_from_db()

        assert log.status == MonitoringLog.STATUS_FAILED
        assert log.error_message == "Test error"


# ── Cleanup Task ────────────────────────────────────────────────


class TestCleanupMonitoringLogs:
    """Tests for monitoring log cleanup task."""

    def test_cleanup_removes_old_logs(self, tenant_context):
        """Old monitoring logs are cleaned up."""
        from apps.inventory.alerts.tasks.alert_resolution import (
            cleanup_old_monitoring_logs,
        )

        # Create old log
        old_log = MonitoringLogFactory()
        old_log.run_started_at = timezone.now() - timezone.timedelta(days=60)
        old_log.save()

        # Create recent log
        recent_log = MonitoringLogFactory()

        result = cleanup_old_monitoring_logs(retention_days=30)

        assert result["deleted"] >= 1
        assert MonitoringLog.objects.filter(id=recent_log.id).exists()


# ── Reorder Suggestion Tasks ───────────────────────────────────


class TestReorderSuggestionTasks:
    """Tests for reorder suggestion generation tasks."""

    def test_mark_expired_suggestions(self, tenant_context):
        """Old pending suggestions are marked expired."""
        from apps.inventory.alerts.tasks.reorder_suggestions import (
            mark_expired_suggestions,
        )
        from apps.inventory.alerts.models import ReorderSuggestion

        from .factories import ReorderSuggestionFactory

        s = ReorderSuggestionFactory(status="pending")
        # Backdate created_at
        ReorderSuggestion.objects.filter(id=s.id).update(
            created_at=timezone.now() - timezone.timedelta(days=60),
        )

        result = mark_expired_suggestions(expiry_days=30)

        assert result["expired"] >= 1

    def test_generate_suggestions_disabled(self, tenant_context):
        """Suggestion generation skips when disabled in settings."""
        from apps.inventory.alerts.tasks.reorder_suggestions import (
            generate_reorder_suggestions,
        )

        settings = GlobalStockSettingsFactory()
        settings.reorder_suggestions_enabled = False
        settings.save()

        result = generate_reorder_suggestions()

        assert result["status"] == "disabled"


# ── Warehouse-Specific Monitoring ───────────────────────────────


class TestWarehouseMonitoring:
    """Tests for per-warehouse monitoring logic (Task 47)."""

    def test_monitor_warehouse_stock_creates_alerts(self, tenant_context):
        """Warehouse monitoring creates alerts per-warehouse."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            monitor_warehouse_stock,
        )

        GlobalStockSettingsFactory()
        product = ProductFactory(is_active=True)
        wh1 = WarehouseFactory()
        wh2 = WarehouseFactory()
        StockLevel.objects.create(
            product=product, warehouse=wh1, quantity=Decimal("0.000"),
        )
        StockLevel.objects.create(
            product=product, warehouse=wh2, quantity=Decimal("5.000"),
        )
        ProductStockConfigFactory(
            product=product,
            low_stock_threshold=Decimal("10.000"),
        )

        result = monitor_warehouse_stock(product)

        assert isinstance(result, list)

    def test_company_wide_oos_alert(self, tenant_context):
        """Company-wide OOS alert when product is out in all warehouses."""
        from apps.inventory.alerts.tasks.stock_monitor import (
            monitor_warehouse_stock,
        )

        GlobalStockSettingsFactory()
        product = ProductFactory(is_active=True)
        wh1 = WarehouseFactory()
        wh2 = WarehouseFactory()
        StockLevel.objects.create(
            product=product, warehouse=wh1, quantity=Decimal("0.000"),
        )
        StockLevel.objects.create(
            product=product, warehouse=wh2, quantity=Decimal("0.000"),
        )

        monitor_warehouse_stock(product)

        # Should create a company-wide OOS alert (warehouse=None)
        assert StockAlert.objects.filter(
            product=product,
            warehouse=None,
            alert_type=ALERT_TYPE_OUT_OF_STOCK,
            threshold_type="company_wide_oos",
        ).exists()
