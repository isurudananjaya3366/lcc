"""
Task 85 — API endpoint tests.

Tests the ViewSets / APIViews by importing them and verifying
configuration (filter backends, permission classes, action methods).
No HTTP requests are sent — these are structural/config tests.
"""

import pytest
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.products.pricing.views import (
    ProductPriceViewSet,
    VariantPriceViewSet,
    TieredPricingViewSet,
    VariantTieredPricingViewSet,
    ScheduledPriceViewSet,
    FlashSaleViewSet,
    PriceLookupView,
    BulkPriceLookupView,
    BulkPriceUpdateView,
)


# =========================================================================
# ProductPriceViewSet
# =========================================================================

class TestProductPriceViewSetConfig:
    def test_permission_classes(self):
        assert IsAuthenticated in ProductPriceViewSet.permission_classes

    def test_ordering_default(self):
        assert ProductPriceViewSet.ordering == ["-created_on"]

    def test_has_breakdown_action(self):
        assert hasattr(ProductPriceViewSet, "breakdown")

    def test_has_set_sale_price_action(self):
        assert hasattr(ProductPriceViewSet, "set_sale_price")

    def test_has_bulk_price_update_action(self):
        assert hasattr(ProductPriceViewSet, "bulk_price_update")

    def test_filter_fields(self):
        assert "product" in ProductPriceViewSet.filterset_fields
        assert "is_taxable" in ProductPriceViewSet.filterset_fields

    def test_search_fields(self):
        assert "product__name" in ProductPriceViewSet.search_fields


# =========================================================================
# VariantPriceViewSet
# =========================================================================

class TestVariantPriceViewSetConfig:
    def test_permission_classes(self):
        assert IsAuthenticated in VariantPriceViewSet.permission_classes

    def test_ordering_default(self):
        assert VariantPriceViewSet.ordering == ["-created_on"]


# =========================================================================
# TieredPricingViewSet
# =========================================================================

class TestTieredPricingViewSetConfig:
    def test_has_bulk_create_action(self):
        assert hasattr(TieredPricingViewSet, "bulk_create")

    def test_has_copy_action(self):
        assert hasattr(TieredPricingViewSet, "copy")

    def test_ordering_by_min_quantity(self):
        assert TieredPricingViewSet.ordering == ["min_quantity"]


# =========================================================================
# ScheduledPriceViewSet
# =========================================================================

class TestScheduledPriceViewSetConfig:
    def test_has_activate_action(self):
        assert hasattr(ScheduledPriceViewSet, "activate")

    def test_has_deactivate_action(self):
        assert hasattr(ScheduledPriceViewSet, "deactivate")

    def test_has_upcoming_action(self):
        assert hasattr(ScheduledPriceViewSet, "upcoming")

    def test_has_active_action(self):
        assert hasattr(ScheduledPriceViewSet, "active")

    def test_has_conflicts_action(self):
        assert hasattr(ScheduledPriceViewSet, "conflicts")


# =========================================================================
# FlashSaleViewSet
# =========================================================================

class TestFlashSaleViewSetConfig:
    def test_has_availability_action(self):
        assert hasattr(FlashSaleViewSet, "availability")

    def test_has_active_now_action(self):
        assert hasattr(FlashSaleViewSet, "active_now")


# =========================================================================
# Public Lookup Views
# =========================================================================

class TestPriceLookupViewConfig:
    def test_allows_any(self):
        assert AllowAny in PriceLookupView.permission_classes

    def test_has_get_method(self):
        assert hasattr(PriceLookupView, "get")


class TestBulkPriceLookupViewConfig:
    def test_allows_any(self):
        assert AllowAny in BulkPriceLookupView.permission_classes

    def test_has_post_method(self):
        assert hasattr(BulkPriceLookupView, "post")


# =========================================================================
# BulkPriceUpdateView
# =========================================================================

class TestBulkPriceUpdateViewConfig:
    def test_requires_auth(self):
        assert IsAuthenticated in BulkPriceUpdateView.permission_classes

    def test_has_post_method(self):
        assert hasattr(BulkPriceUpdateView, "post")


# =========================================================================
# URL registration
# =========================================================================

class TestURLConfiguration:
    def test_urlpatterns_not_empty(self):
        from apps.products.pricing.urls import urlpatterns
        assert len(urlpatterns) > 0

    def test_app_name(self):
        from apps.products.pricing.urls import app_name
        assert app_name == "pricing"

    def test_router_routes_registered(self):
        from apps.products.pricing.urls import router
        # registry is a list of (prefix, viewset, basename) tuples
        route_names = [r[2] for r in router.registry]
        assert "product-price" in route_names
        assert "variant-price" in route_names
        assert "tiered-pricing" in route_names
        assert "scheduled-price" in route_names
        assert "flash-sale" in route_names
