"""
Vendor API URL routing.

Registers all vendor ViewSets with DRF DefaultRouter.
"""

from rest_framework.routers import DefaultRouter

from apps.vendors.views import VendorViewSet

app_name = "vendors"

router = DefaultRouter()
router.register(r"vendors", VendorViewSet, basename="vendor")

urlpatterns = router.urls
