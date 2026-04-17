"""
Store API views for the LankaCommerce webstore.

Provides public read-only endpoints for product listing, detail,
related products, reviews, and category listing.
"""

from django.db import models as django_models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.products.models import Category, Product

from .serializers import StoreCategorySerializer, StoreProductSerializer


class StoreProductViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = StoreProductSerializer
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["selling_price", "name", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        qs = (
            Product.objects.filter(
                is_webstore_visible=True,
                status="active",
            )
            .select_related("category", "brand")
            .prefetch_related("images", "variants__option_values__option_type")
        )

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)

        min_price = self.request.query_params.get("min_price")
        if min_price:
            qs = qs.filter(selling_price__gte=min_price)

        max_price = self.request.query_params.get("max_price")
        if max_price:
            qs = qs.filter(selling_price__lte=max_price)

        if self.request.query_params.get("featured") == "true":
            qs = qs.filter(featured=True)

        if self.request.query_params.get("on_sale") == "true":
            qs = qs.filter(mrp__isnull=False).filter(
                selling_price__lt=django_models.F("mrp")
            )

        return qs

    @action(detail=True, methods=["get"], url_path="related")
    def related(self, request, slug=None):
        product = self.get_object()
        limit = min(int(request.query_params.get("limit", 4)), 20)
        related_qs = (
            Product.objects.filter(
                is_webstore_visible=True,
                status="active",
                category=product.category,
            )
            .exclude(pk=product.pk)
            .select_related("category")
            .prefetch_related("images")[:limit]
        )
        serializer = self.get_serializer(related_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="reviews")
    def reviews(self, request, slug=None):
        # Reviews model not yet implemented — return empty paginated response
        return Response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )


class StoreCategoryViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = StoreCategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by("name")
