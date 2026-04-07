"""
Django admin configuration for the Inventory application.

Imports admin registrations from submodules so Django's autodiscovery
picks them up.
"""

from apps.inventory.stock.admin import StockLevelAdmin  # noqa: F401
from apps.inventory.stock.admin import StockMovementAdmin  # noqa: F401
from apps.inventory.warehouses.admin import BarcodeScanAdmin  # noqa: F401
from apps.inventory.warehouses.admin import DefaultWarehouseConfigAdmin  # noqa: F401
from apps.inventory.warehouses.admin import POSWarehouseMappingAdmin  # noqa: F401
from apps.inventory.warehouses.admin import StorageLocationAdmin  # noqa: F401
from apps.inventory.warehouses.admin import TransferRouteAdmin  # noqa: F401
from apps.inventory.warehouses.admin import WarehouseAdmin  # noqa: F401
from apps.inventory.warehouses.admin import WarehouseCapacityAdmin  # noqa: F401
from apps.inventory.warehouses.admin import WarehouseZoneAdmin  # noqa: F401

# Stock alerts & configuration
from apps.inventory.alerts.admin import CategoryStockConfigAdmin  # noqa: F401
from apps.inventory.alerts.admin import GlobalStockSettingsAdmin  # noqa: F401
from apps.inventory.alerts.admin import MonitoringLogAdmin  # noqa: F401
from apps.inventory.alerts.admin import ProductStockConfigAdmin  # noqa: F401
from apps.inventory.alerts.admin import StockAlertAdmin  # noqa: F401
from apps.inventory.alerts.admin import ReorderSuggestionAdmin  # noqa: F401
