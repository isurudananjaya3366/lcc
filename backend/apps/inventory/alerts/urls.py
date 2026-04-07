"""
Alerts & Reorder API URL routing.

Registers stock-config, global-settings, alerts, and reorder ViewSets plus
standalone views for dashboard and stock health.

URL structure:
    /api/v1/alerts/stock-config/
    /api/v1/alerts/stock-config/{id}/
    /api/v1/alerts/stock-config/{id}/reset_to_defaults/
    /api/v1/alerts/stock-config/summary/
    /api/v1/alerts/stock-config/bulk/
    /api/v1/alerts/stock-config/bulk_exclude/
    /api/v1/alerts/global-settings/
    /api/v1/alerts/alerts/
    /api/v1/alerts/alerts/{id}/
    /api/v1/alerts/alerts/{id}/acknowledge/
    /api/v1/alerts/alerts/{id}/snooze/
    /api/v1/alerts/alerts/{id}/resolve/
    /api/v1/alerts/alerts/bulk_acknowledge/
    /api/v1/alerts/alerts/statistics/
    /api/v1/alerts/reorder/
    /api/v1/alerts/reorder/{id}/
    /api/v1/alerts/reorder/{id}/convert_to_po/
    /api/v1/alerts/reorder/{id}/dismiss/
    /api/v1/alerts/reorder/bulk_convert/
    /api/v1/alerts/reorder/summary/
    /api/v1/alerts/reorder/report/
    /api/v1/alerts/reorder/email_report/
    /api/v1/alerts/dashboard/
    /api/v1/alerts/health/
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.inventory.alerts.views import (
    AlertDashboardView,
    GlobalStockSettingsViewSet,
    ProductAlertsView,
    ProductStockConfigViewSet,
    ReorderSuggestionViewSet,
    StockAlertViewSet,
    StockHealthView,
)

app_name = "alerts"

router = DefaultRouter()
router.register(r"stock-config", ProductStockConfigViewSet, basename="stockconfig")
router.register(r"global-settings", GlobalStockSettingsViewSet, basename="globalsettings")
router.register(r"alerts", StockAlertViewSet, basename="alert")
router.register(r"reorder", ReorderSuggestionViewSet, basename="reorder")

urlpatterns = [
    path("dashboard/", AlertDashboardView.as_view(), name="dashboard"),
    path("health/", StockHealthView.as_view(), name="health"),
    path(
        "products/<uuid:product_id>/alerts/",
        ProductAlertsView.as_view(),
        name="product-alerts",
    ),
] + router.urls
