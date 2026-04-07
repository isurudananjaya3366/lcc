from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pos.cart.views import POSCartViewSet
from apps.pos.payment.views import (
    PaymentCompleteView,
    PaymentHistoryView,
    PaymentProcessView,
    PaymentRefundView,
    PaymentStatusView,
    SplitPaymentView,
)
from apps.pos.search.views import (
    BarcodeScanView,
    ProductSearchView,
    QuickButtonGroupListView,
    SearchHistoryView,
)
from apps.pos.terminal.views import POSSessionViewSet, POSTerminalViewSet

app_name = "pos"

router = DefaultRouter()
router.register(r"terminals", POSTerminalViewSet, basename="terminal")
router.register(r"sessions", POSSessionViewSet, basename="session")
router.register(r"cart", POSCartViewSet, basename="cart")

urlpatterns = [
    # Router-based endpoints
    path("", include(router.urls)),
    # Search
    path("search/", ProductSearchView.as_view(), name="product-search"),
    path(
        "search/barcode/",
        BarcodeScanView.as_view(),
        name="barcode-scan",
    ),
    path(
        "search/quick-buttons/",
        QuickButtonGroupListView.as_view(),
        name="quick-buttons",
    ),
    path(
        "search/history/",
        SearchHistoryView.as_view(),
        name="search-history",
    ),
    # Payment
    path(
        "payment/process/",
        PaymentProcessView.as_view(),
        name="payment-process",
    ),
    path(
        "payment/split/",
        SplitPaymentView.as_view(),
        name="payment-split",
    ),
    path(
        "payment/complete/",
        PaymentCompleteView.as_view(),
        name="payment-complete",
    ),
    path(
        "payment/history/",
        PaymentHistoryView.as_view(),
        name="payment-history",
    ),
    path(
        "payment/<uuid:pk>/refund/",
        PaymentRefundView.as_view(),
        name="payment-refund",
    ),
    path(
        "payment/<uuid:pk>/status/",
        PaymentStatusView.as_view(),
        name="payment-status",
    ),
    # Receipts
    path("", include("apps.pos.receipts.urls")),
]
