"""
Receipt module URL configuration.

Registers receipt and template endpoints under the POS URL namespace.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pos.receipts.views.receipt import ReceiptExportView, ReceiptViewSet
from apps.pos.receipts.views.template import ReceiptTemplateViewSet

router = DefaultRouter()
router.register(r"receipts", ReceiptViewSet, basename="receipt")
router.register(
    r"receipt-templates", ReceiptTemplateViewSet, basename="receipt-template"
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "receipts/export/",
        ReceiptExportView.as_view(),
        name="receipt-export",
    ),
]
