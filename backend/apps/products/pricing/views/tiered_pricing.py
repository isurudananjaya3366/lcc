"""
Tiered pricing ViewSets.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import TieredPricing, VariantTieredPricing
from ..permissions import HasPricingPermission
from ..serializers import TieredPricingSerializer, VariantTieredPricingSerializer


class TieredPricingViewSet(ModelViewSet):
    """CRUD + bulk-create / copy for product tiered pricing."""

    permission_classes = [IsAuthenticated, HasPricingPermission]
    serializer_class = TieredPricingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["product", "is_active", "tier_type"]
    search_fields = ["product__name"]
    ordering_fields = ["min_quantity", "tier_price"]
    ordering = ["min_quantity"]

    def get_queryset(self):
        return TieredPricing.objects.select_related("product").all()

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Create multiple tiers in one request.

        Expects ``{"tiers": [{"product": ..., "min_quantity": ..., ...}, ...]}``
        """
        tiers_data = request.data.get("tiers", [])
        if not tiers_data:
            return Response(
                {"detail": "tiers list is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = TieredPricingSerializer(data=tiers_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="copy")
    def copy(self, request):
        """Copy all tiers from one product to another.

        Expects ``{"source_product_id": ..., "target_product_id": ...}``
        """
        source = request.data.get("source_product_id")
        target = request.data.get("target_product_id")
        if not source or not target:
            return Response(
                {"detail": "source_product_id and target_product_id required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        created = TieredPricing.copy_tiers(source, target)
        return Response(
            {
                "count": len(created),
                "tiers": TieredPricingSerializer(created, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )


class VariantTieredPricingViewSet(ModelViewSet):
    """CRUD for variant-level tiered pricing."""

    permission_classes = [IsAuthenticated, HasPricingPermission]
    serializer_class = VariantTieredPricingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["variant", "is_active", "tier_type"]
    search_fields = ["variant__sku"]
    ordering_fields = ["min_quantity", "tier_price"]
    ordering = ["min_quantity"]

    def get_queryset(self):
        return VariantTieredPricing.objects.select_related(
            "variant", "variant__product"
        ).all()
