"""
Invoices URL routing.

Registers all invoice-related API endpoints.
"""

from rest_framework.routers import DefaultRouter

from apps.invoices.views import InvoiceViewSet

app_name = "invoices"

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet, basename="invoice")

urlpatterns = router.urls
