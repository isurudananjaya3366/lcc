"""
Stock API URL routing.

Registers all stock ViewSets with DRF DefaultRouter.

URL structure:
    /api/v1/stock/stock-levels/
    /api/v1/stock/stock-levels/{id}/
    /api/v1/stock/stock-levels/low-stock/
    /api/v1/stock/stock-levels/out-of-stock/
    /api/v1/stock/stock-levels/check-availability/
    /api/v1/stock/stock-movements/
    /api/v1/stock/stock-movements/{id}/
    /api/v1/stock/stock-movements/for-product/
    /api/v1/stock/stock-movements/summary/
    /api/v1/stock/stock-operations/stock-in/
    /api/v1/stock/stock-operations/stock-out/
    /api/v1/stock/stock-operations/transfer/
    /api/v1/stock/stock-operations/adjust/
    /api/v1/stock/stock-takes/
    /api/v1/stock/stock-takes/{id}/
    /api/v1/stock/stock-takes/{id}/start/
    /api/v1/stock/stock-takes/{id}/count/
    /api/v1/stock/stock-takes/{id}/bulk-count/
    /api/v1/stock/stock-takes/{id}/submit/
    /api/v1/stock/stock-takes/{id}/approve/
    /api/v1/stock/stock-takes/{id}/complete/
    /api/v1/stock/stock-takes/{id}/cancel/
    /api/v1/stock/stock-takes/{id}/items/
    /api/v1/stock/stock-takes/{id}/variances/
    /api/v1/stock/stock-takes/{id}/report/
"""

from rest_framework.routers import DefaultRouter

from apps.inventory.stock.api.views import (
    StockLevelViewSet,
    StockMovementViewSet,
    StockOperationViewSet,
    StockTakeViewSet,
)

app_name = "stock"

router = DefaultRouter()
router.register(r"stock-levels", StockLevelViewSet, basename="stocklevel")
router.register(r"stock-movements", StockMovementViewSet, basename="stockmovement")
router.register(r"stock-operations", StockOperationViewSet, basename="stockoperation")
router.register(r"stock-takes", StockTakeViewSet, basename="stocktake")

urlpatterns = router.urls
