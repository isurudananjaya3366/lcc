"""
Warehouse API URL routing.

Registers all warehouse ViewSets with DRF DefaultRouter.

URL structure:
    /api/v1/warehouse/warehouses/
    /api/v1/warehouse/warehouses/{id}/
    /api/v1/warehouse/warehouses/{id}/set_default/
    /api/v1/warehouse/warehouses/{id}/dashboard/
    /api/v1/warehouse/warehouses/{id}/capacity/
    /api/v1/warehouse/locations/
    /api/v1/warehouse/locations/{id}/
    /api/v1/warehouse/locations/{id}/children/
    /api/v1/warehouse/locations/{id}/ancestors/
    /api/v1/warehouse/locations/{id}/descendants/
    /api/v1/warehouse/locations/{id}/siblings/
    /api/v1/warehouse/locations/tree/
    /api/v1/warehouse/locations/barcode_lookup/{barcode}/
    /api/v1/warehouse/locations/bulk_create/
    /api/v1/warehouse/zones/
    /api/v1/warehouse/routes/
    /api/v1/warehouse/capacity/
"""

from rest_framework.routers import DefaultRouter

from apps.inventory.warehouses.api.views import (
    StorageLocationViewSet,
    TransferRouteViewSet,
    WarehouseCapacityViewSet,
    WarehouseViewSet,
    WarehouseZoneViewSet,
)

app_name = "warehouse"

router = DefaultRouter()
router.register(r"warehouses", WarehouseViewSet, basename="warehouse")
router.register(r"locations", StorageLocationViewSet, basename="location")
router.register(r"zones", WarehouseZoneViewSet, basename="zone")
router.register(r"routes", TransferRouteViewSet, basename="route")
router.register(r"capacity", WarehouseCapacityViewSet, basename="capacity")

urlpatterns = router.urls
