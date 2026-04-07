"""Test factories for alerts module."""

import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from faker import Faker

from apps.products.models import Category, Product
from apps.inventory.models import Warehouse
from apps.inventory.alerts.models import (
    CategoryStockConfig,
    GlobalStockSettings,
    MonitoringLog,
    ProductStockConfig,
    ReorderSuggestion,
    StockAlert,
)
from apps.inventory.alerts.constants import (
    ALERT_STATUS_ACTIVE,
    ALERT_TYPE_LOW_STOCK,
    SUGGESTION_STATUS_PENDING,
    URGENCY_MEDIUM,
)

fake = Faker()


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    sku = factory.Sequence(lambda n: f"SKU-{n:05d}")
    category = factory.SubFactory(CategoryFactory)


class WarehouseFactory(DjangoModelFactory):
    class Meta:
        model = Warehouse

    name = factory.Sequence(lambda n: f"Warehouse {n}")
    code = factory.Sequence(lambda n: f"WH-{n:03d}")


class GlobalStockSettingsFactory(DjangoModelFactory):
    class Meta:
        model = GlobalStockSettings
        django_get_or_create = ()

    default_low_threshold = Decimal("10.000")
    default_reorder_point = Decimal("15.000")
    default_reorder_qty = Decimal("50.000")
    enable_auto_reorder = False


class CategoryStockConfigFactory(DjangoModelFactory):
    class Meta:
        model = CategoryStockConfig

    category = factory.SubFactory(CategoryFactory)
    low_stock_threshold = Decimal("20.000")
    reorder_point = Decimal("50.000")
    reorder_quantity = Decimal("200.000")


class ProductStockConfigFactory(DjangoModelFactory):
    class Meta:
        model = ProductStockConfig

    product = factory.SubFactory(ProductFactory)
    warehouse = None
    low_stock_threshold = Decimal("15.000")
    reorder_point = Decimal("40.000")
    reorder_quantity = Decimal("150.000")


class StockAlertFactory(DjangoModelFactory):
    class Meta:
        model = StockAlert

    product = factory.SubFactory(ProductFactory)
    warehouse = factory.SubFactory(WarehouseFactory)
    alert_type = ALERT_TYPE_LOW_STOCK
    status = ALERT_STATUS_ACTIVE
    priority = 5
    threshold_value = 20
    current_stock = 15
    message = factory.LazyAttribute(
        lambda o: f"{o.product.name} is below threshold"
    )


class ReorderSuggestionFactory(DjangoModelFactory):
    class Meta:
        model = ReorderSuggestion

    product = factory.SubFactory(ProductFactory)
    warehouse = factory.SubFactory(WarehouseFactory)
    suggested_qty = Decimal("200.000")
    current_stock = Decimal("25.000")
    urgency = URGENCY_MEDIUM
    status = SUGGESTION_STATUS_PENDING
    daily_velocity = Decimal("5.000")
    days_until_stockout = Decimal("5.00")
    estimated_cost = Decimal("10000.00")
    unit_cost = Decimal("50.00")


class MonitoringLogFactory(DjangoModelFactory):
    class Meta:
        model = MonitoringLog

    status = MonitoringLog.STATUS_COMPLETED
    products_checked = 100
    alerts_created = 5
    alerts_updated = 2
    alerts_resolved = 1
    errors_encountered = 0
    execution_time = Decimal("3.50")
