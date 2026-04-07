"""Payment URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payments.views import PaymentReportView, PaymentViewSet, RefundViewSet

app_name = "payments"

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"refunds", RefundViewSet, basename="refund")

urlpatterns = [
    path("", include(router.urls)),
    path("reports/", PaymentReportView.as_view(), name="payment-reports"),
]
