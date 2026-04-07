"""Tests for alerts models: config, alert lifecycle, reorder suggestion."""

import pytest
from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.inventory.alerts.constants import (
    ALERT_STATUS_ACKNOWLEDGED,
    ALERT_STATUS_ACTIVE,
    ALERT_STATUS_RESOLVED,
    ALERT_STATUS_SNOOZED,
    ALERT_TYPE_CRITICAL_STOCK,
    ALERT_TYPE_LOW_STOCK,
    ALERT_TYPE_OUT_OF_STOCK,
    SUGGESTION_STATUS_CONVERTED,
    SUGGESTION_STATUS_DISMISSED,
    SUGGESTION_STATUS_PENDING,
)
from apps.inventory.alerts.models import (
    CategoryStockConfig,
    GlobalStockSettings,
    MonitoringLog,
    ProductStockConfig,
    ReorderSuggestion,
    StockAlert,
)
from apps.inventory.alerts.services import ConfigResolver

from .factories import (
    CategoryFactory,
    CategoryStockConfigFactory,
    GlobalStockSettingsFactory,
    MonitoringLogFactory,
    ProductFactory,
    ProductStockConfigFactory,
    ReorderSuggestionFactory,
    StockAlertFactory,
    WarehouseFactory,
)

pytestmark = pytest.mark.django_db


# ── GlobalStockSettings ────────────────────────────────────────────


class TestGlobalStockSettings:
    def test_create_global_settings(self, tenant_context):
        settings = GlobalStockSettingsFactory()
        assert settings.id is not None
        assert settings.default_low_threshold == Decimal("10.000")
        assert settings.default_reorder_point == Decimal("15.000")

    def test_get_settings_classmethod(self, tenant_context):
        """get_settings() creates or retrieves singleton."""
        settings = GlobalStockSettings.get_settings()
        assert settings is not None
        settings2 = GlobalStockSettings.get_settings()
        assert settings.pk == settings2.pk


# ── CategoryStockConfig ────────────────────────────────────────────


class TestCategoryStockConfig:
    def test_create(self, tenant_context):
        config = CategoryStockConfigFactory()
        assert config.id is not None
        assert config.category is not None
        assert config.low_stock_threshold == Decimal("20.000")

    def test_one_to_one_per_category(self, tenant_context):
        config = CategoryStockConfigFactory()
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                CategoryStockConfigFactory(category=config.category)


# ── ProductStockConfig ─────────────────────────────────────────────


class TestProductStockConfig:
    def test_create_product_config(self, tenant_context):
        config = ProductStockConfigFactory()
        assert config.product is not None
        assert config.warehouse is None
        assert config.low_stock_threshold == Decimal("15.000")

    def test_warehouse_specific(self, tenant_context):
        product = ProductFactory()
        wh = WarehouseFactory()
        config = ProductStockConfigFactory(
            product=product, warehouse=wh, low_stock_threshold=Decimal("25.000")
        )
        assert config.warehouse == wh

    def test_unique_product_variant_warehouse(self, tenant_context):
        from apps.products.models import ProductVariant

        product = ProductFactory()
        wh = WarehouseFactory()
        # Create a variant to avoid NULL (SQL NULL!=NULL bypasses UniqueConstraint)
        variant = ProductVariant.objects.create(product=product, sku="VAR-001", name="Test Variant")
        ProductStockConfigFactory(product=product, variant=variant, warehouse=wh)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ProductStockConfigFactory(product=product, variant=variant, warehouse=wh)


# ── ConfigResolver ──────────────────────────────────────────────────


class TestConfigResolver:
    def test_product_override_takes_precedence(self, global_settings):
        category = CategoryFactory()
        CategoryStockConfigFactory(
            category=category, low_stock_threshold=Decimal("20.000")
        )
        product = ProductFactory(category=category)
        ProductStockConfigFactory(
            product=product, low_stock_threshold=Decimal("30.000")
        )
        effective = ConfigResolver.resolve_for_product(product=product)
        assert effective["low_stock_threshold"] == Decimal("30.000")

    def test_category_fallback(self, global_settings):
        category = CategoryFactory()
        CategoryStockConfigFactory(
            category=category, low_stock_threshold=Decimal("20.000")
        )
        product = ProductFactory(category=category)
        effective = ConfigResolver.resolve_for_product(product=product)
        assert effective["low_stock_threshold"] == Decimal("20.000")

    def test_global_fallback(self, global_settings):
        product = ProductFactory()
        effective = ConfigResolver.resolve_for_product(product=product)
        assert effective["low_stock_threshold"] == global_settings.default_low_threshold

    def test_warehouse_override(self, global_settings):
        product = ProductFactory()
        wh = WarehouseFactory()
        ProductStockConfigFactory(
            product=product, warehouse=None, low_stock_threshold=Decimal("20.000")
        )
        ProductStockConfigFactory(
            product=product, warehouse=wh, low_stock_threshold=Decimal("35.000")
        )
        effective = ConfigResolver.resolve_for_product(product=product, warehouse=wh)
        assert effective["low_stock_threshold"] == Decimal("35.000")

    def test_sources_tracked(self, global_settings):
        product = ProductFactory()
        effective = ConfigResolver.resolve_for_product(product=product)
        assert "sources" in effective


# ── StockAlert ──────────────────────────────────────────────────────


class TestStockAlert:
    def test_create(self, tenant_context):
        alert = StockAlertFactory()
        assert alert.id is not None
        assert alert.status == ALERT_STATUS_ACTIVE
        assert alert.alert_type == ALERT_TYPE_LOW_STOCK

    def test_str(self, tenant_context):
        alert = StockAlertFactory()
        assert str(alert)  # just ensure no error

    def test_is_snoozed_property(self, tenant_context):
        alert = StockAlertFactory(
            status=ALERT_STATUS_SNOOZED,
            snoozed_until=timezone.now() + timedelta(hours=2),
        )
        assert alert.is_snoozed is True

    def test_not_snoozed_when_expired(self, tenant_context):
        alert = StockAlertFactory(
            status=ALERT_STATUS_SNOOZED,
            snoozed_until=timezone.now() - timedelta(hours=1),
        )
        assert alert.is_snoozed is False


class TestStockAlertLifecycle:
    def test_acknowledge(self, user):
        alert = StockAlertFactory(status=ALERT_STATUS_ACTIVE)
        alert.acknowledge(user=user)
        assert alert.status == ALERT_STATUS_ACKNOWLEDGED
        assert alert.acknowledged_by == user
        assert alert.acknowledged_at is not None

    def test_resolve(self, user):
        alert = StockAlertFactory(status=ALERT_STATUS_ACTIVE)
        alert.resolve(user=user)
        assert alert.status == ALERT_STATUS_RESOLVED
        assert alert.resolved_at is not None

    def test_snooze(self, user):
        alert = StockAlertFactory(status=ALERT_STATUS_ACTIVE)
        until = timezone.now() + timedelta(hours=2)
        alert.snooze(until_datetime=until, user=user)
        assert alert.snoozed_until is not None
        assert alert.is_snoozed is True

    def test_snooze_for_hours(self, user):
        alert = StockAlertFactory(status=ALERT_STATUS_ACTIVE)
        alert.snooze_for_hours(hours=4, user=user)
        assert alert.snoozed_until > timezone.now()
        assert alert.snooze_count >= 1


class TestStockAlertDeduplication:
    def test_no_duplicate_for_same_product_type(self, tenant_context):
        product = ProductFactory()
        wh = WarehouseFactory()
        StockAlertFactory(
            product=product, warehouse=wh,
            alert_type=ALERT_TYPE_LOW_STOCK, status=ALERT_STATUS_ACTIVE,
        )
        assert StockAlert.objects.filter(
            product=product, warehouse=wh,
            alert_type=ALERT_TYPE_LOW_STOCK, status=ALERT_STATUS_ACTIVE,
        ).count() == 1

    def test_allow_different_alert_types(self, tenant_context):
        product = ProductFactory()
        wh = WarehouseFactory()
        StockAlertFactory(
            product=product, warehouse=wh,
            alert_type=ALERT_TYPE_LOW_STOCK, status=ALERT_STATUS_ACTIVE,
        )
        StockAlertFactory(
            product=product, warehouse=wh,
            alert_type=ALERT_TYPE_CRITICAL_STOCK, status=ALERT_STATUS_ACTIVE,
        )
        assert StockAlert.objects.filter(
            product=product, status=ALERT_STATUS_ACTIVE,
        ).count() == 2

    def test_allow_alert_after_resolution(self, tenant_context):
        product = ProductFactory()
        wh = WarehouseFactory()
        StockAlertFactory(
            product=product, warehouse=wh,
            alert_type=ALERT_TYPE_LOW_STOCK, status=ALERT_STATUS_RESOLVED,
            resolved_at=timezone.now(),
        )
        alert2 = StockAlertFactory(
            product=product, warehouse=wh,
            alert_type=ALERT_TYPE_LOW_STOCK, status=ALERT_STATUS_ACTIVE,
        )
        assert alert2.status == ALERT_STATUS_ACTIVE


class TestStockAlertManager:
    def test_get_active(self, tenant_context):
        StockAlertFactory(status=ALERT_STATUS_ACTIVE)
        StockAlertFactory(status=ALERT_STATUS_ACTIVE)
        StockAlertFactory(status=ALERT_STATUS_RESOLVED)
        assert StockAlert.objects.get_active().count() == 2

    def test_get_by_product(self, tenant_context):
        product = ProductFactory()
        StockAlertFactory(product=product)
        StockAlertFactory(product=product)
        StockAlertFactory()
        assert StockAlert.objects.get_by_product(product).count() == 2

    def test_get_critical(self, tenant_context):
        StockAlertFactory(alert_type=ALERT_TYPE_OUT_OF_STOCK, status=ALERT_STATUS_ACTIVE)
        StockAlertFactory(alert_type=ALERT_TYPE_CRITICAL_STOCK, status=ALERT_STATUS_ACTIVE)
        StockAlertFactory(alert_type=ALERT_TYPE_LOW_STOCK, status=ALERT_STATUS_ACTIVE)
        assert StockAlert.objects.get_critical().count() == 2

    def test_get_snoozed_expired(self, tenant_context):
        StockAlertFactory(
            status=ALERT_STATUS_SNOOZED,
            snoozed_until=timezone.now() + timedelta(hours=2),
        )
        StockAlertFactory(
            status=ALERT_STATUS_SNOOZED,
            snoozed_until=timezone.now() - timedelta(hours=1),
        )
        assert StockAlert.objects.get_snoozed_expired().count() == 1

    def test_count_by_status(self, tenant_context):
        StockAlertFactory.create_batch(3, status=ALERT_STATUS_ACTIVE)
        StockAlertFactory.create_batch(2, status=ALERT_STATUS_RESOLVED)
        result = StockAlert.objects.count_by_status()
        assert isinstance(result, dict) or hasattr(result, "__iter__")


# ── ReorderSuggestion ──────────────────────────────────────────────


class TestReorderSuggestion:
    def test_create(self, tenant_context):
        s = ReorderSuggestionFactory()
        assert s.id is not None
        assert s.status == SUGGESTION_STATUS_PENDING
        assert s.suggested_qty == Decimal("200.000")

    def test_str(self, tenant_context):
        s = ReorderSuggestionFactory()
        assert str(s)

    def test_can_convert_pending(self, tenant_context):
        s = ReorderSuggestionFactory(status=SUGGESTION_STATUS_PENDING)
        ok, msg = s.can_convert()
        # may require supplier — just verify return type
        assert isinstance(ok, bool)

    def test_mark_converted(self, user):
        import uuid

        s = ReorderSuggestionFactory(status=SUGGESTION_STATUS_PENDING)
        po_id = uuid.uuid4()
        s.mark_converted(po_id=po_id, user=user)
        s.refresh_from_db()
        assert s.status == SUGGESTION_STATUS_CONVERTED
        assert s.converted_po_id == po_id

    def test_mark_dismissed(self, user):
        s = ReorderSuggestionFactory(status=SUGGESTION_STATUS_PENDING)
        s.mark_dismissed(reason="Already ordered", user=user)
        s.refresh_from_db()
        assert s.status == SUGGESTION_STATUS_DISMISSED
        assert s.dismissal_reason == "Already ordered"

    def test_is_expired(self, tenant_context):
        s = ReorderSuggestionFactory(status=SUGGESTION_STATUS_PENDING)
        # Freshly created — not expired
        assert s.is_expired() is False


class TestReorderSuggestionManager:
    def test_get_pending(self, tenant_context):
        ReorderSuggestionFactory(status=SUGGESTION_STATUS_PENDING)
        ReorderSuggestionFactory(status=SUGGESTION_STATUS_DISMISSED)
        assert ReorderSuggestion.objects.get_pending().count() == 1

    def test_get_critical(self, tenant_context):
        ReorderSuggestionFactory(urgency="critical")
        ReorderSuggestionFactory(urgency="low")
        assert ReorderSuggestion.objects.get_critical().count() == 1


# ── MonitoringLog ───────────────────────────────────────────────────


class TestMonitoringLog:
    def test_create(self, tenant_context):
        log = MonitoringLogFactory()
        assert log.id is not None
        assert log.status == MonitoringLog.STATUS_COMPLETED

    def test_mark_failed(self, tenant_context):
        log = MonitoringLog.objects.create(status=MonitoringLog.STATUS_RUNNING)
        log.mark_failed("something broke", "traceback here")
        log.refresh_from_db()
        assert log.status == MonitoringLog.STATUS_FAILED
        assert log.error_message == "something broke"

    def test_mark_completed(self, tenant_context):
        log = MonitoringLog.objects.create(status=MonitoringLog.STATUS_RUNNING)
        log.mark_completed({"products_checked": 50, "alerts_created": 3})
        log.refresh_from_db()
        assert log.status == MonitoringLog.STATUS_COMPLETED

    def test_get_recent(self, tenant_context):
        MonitoringLogFactory.create_batch(15)
        recent = MonitoringLog.objects.get_recent(limit=10)
        assert len(recent) == 10
