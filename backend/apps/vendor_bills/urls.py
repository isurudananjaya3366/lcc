"""Vendor Bills API URL routing.

Registers all vendor bill ViewSets with DRF DefaultRouter.
"""

from rest_framework.routers import DefaultRouter

from apps.vendor_bills.views.bill_viewset import VendorBillViewSet
from apps.vendor_bills.views.payment_viewset import VendorPaymentViewSet

app_name = "vendor_bills"

router = DefaultRouter()
router.register(r"vendor-bills", VendorBillViewSet, basename="vendor-bill")
router.register(r"vendor-payments", VendorPaymentViewSet, basename="vendor-payment")

urlpatterns = router.urls
