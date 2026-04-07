"""
URL configuration for the Credit & Loyalty module.

Registers routes for credit accounts, loyalty accounts,
store credit, promotions, and dashboard.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.credit.views import (
    CreditLoyaltyDashboardView,
    CreditViewSet,
    LoyaltyViewSet,
    StoreCreditViewSet,
)

app_name = "credit"

router = DefaultRouter()
router.register(r"credit", CreditViewSet, basename="credit")
router.register(r"loyalty", LoyaltyViewSet, basename="loyalty")
router.register(r"store-credit", StoreCreditViewSet, basename="store-credit")

urlpatterns = [
    path("dashboard/", CreditLoyaltyDashboardView.as_view(), name="dashboard"),
] + router.urls
