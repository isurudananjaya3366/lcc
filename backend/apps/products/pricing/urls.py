"""
Pricing API URL configuration.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductPriceViewSet,
    VariantPriceViewSet,
    TieredPricingViewSet,
    VariantTieredPricingViewSet,
    ScheduledPriceViewSet,
    FlashSaleViewSet,
    PriceLookupView,
    BulkPriceLookupView,
    BulkPriceUpdateView,
    BulkScheduleOperationsView,
    PromotionalCalendarView,
)

app_name = "pricing"

router = DefaultRouter()
router.register(r"product-prices", ProductPriceViewSet, basename="product-price")
router.register(r"variant-prices", VariantPriceViewSet, basename="variant-price")
router.register(r"tiered-pricing", TieredPricingViewSet, basename="tiered-pricing")
router.register(
    r"variant-tiered-pricing",
    VariantTieredPricingViewSet,
    basename="variant-tiered-pricing",
)
router.register(
    r"scheduled-prices", ScheduledPriceViewSet, basename="scheduled-price"
)
router.register(r"flash-sales", FlashSaleViewSet, basename="flash-sale")

urlpatterns = [
    path("lookup/", PriceLookupView.as_view(), name="price-lookup"),
    path("bulk-lookup/", BulkPriceLookupView.as_view(), name="bulk-price-lookup"),
    path("bulk-update/", BulkPriceUpdateView.as_view(), name="bulk-price-update"),
    path("schedules/bulk-operations/", BulkScheduleOperationsView.as_view(), name="schedule-bulk-operations"),
    path("promotional-calendar/", PromotionalCalendarView.as_view(), name="promotional-calendar"),
] + router.urls
