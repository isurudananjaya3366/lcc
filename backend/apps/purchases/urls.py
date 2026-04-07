"""
Purchase Order API URL routing.

Registers all purchase order ViewSets with DRF DefaultRouter.
"""

from rest_framework.routers import DefaultRouter

from apps.purchases.views.po_viewset import POViewSet
from apps.purchases.views.grn_viewset import GRNViewSet

app_name = "purchases"

router = DefaultRouter()
router.register(r"purchase-orders", POViewSet, basename="purchase-order")
router.register(r"goods-receipts", GRNViewSet, basename="goods-receipt")

urlpatterns = router.urls
