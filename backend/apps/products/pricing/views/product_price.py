"""
Product price ViewSets.
"""

from decimal import Decimal, InvalidOperation

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import ProductPrice, VariantPrice
from ..permissions import HasPricingPermission
from ..serializers import (
    ProductPriceSerializer,
    ProductPriceUpdateSerializer,
    VariantPriceSerializer,
    PriceBreakdownSerializer,
)


class ProductPriceViewSet(ModelViewSet):
    """CRUD + custom actions for product prices."""

    permission_classes = [IsAuthenticated, HasPricingPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["product", "is_taxable", "is_active"]
    search_fields = ["product__name", "product__sku"]
    ordering_fields = ["base_price", "sale_price", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            ProductPrice.objects.select_related("product", "tax_class")
            .prefetch_related("product__variants")
            .all()
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ProductPriceUpdateSerializer
        return ProductPriceSerializer

    @action(detail=True, methods=["get"], url_path="breakdown")
    def breakdown(self, request, pk=None):
        """Return a full price breakdown for this product price."""
        product_price = self.get_object()
        quantity = int(request.query_params.get("quantity", 1))
        data = PriceBreakdownSerializer.build_breakdown(
            product_price.product, quantity=max(quantity, 1)
        )
        serializer = PriceBreakdownSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="set-sale-price")
    def set_sale_price(self, request, pk=None):
        """Quick-set a sale price on a product."""
        product_price = self.get_object()
        sale_price = request.data.get("sale_price")
        if sale_price is None:
            return Response(
                {"detail": "sale_price is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            sale_price = Decimal(str(sale_price))
        except (InvalidOperation, ValueError, TypeError):
            return Response(
                {"detail": "Invalid sale_price value."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if sale_price < 0:
            return Response(
                {"detail": "sale_price cannot be negative."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product_price.sale_price = sale_price if sale_price > 0 else None
        product_price.save(update_fields=["sale_price", "updated_at"])
        return Response(ProductPriceSerializer(product_price).data)

    @action(detail=False, methods=["post"], url_path="bulk-update")
    def bulk_price_update(self, request):
        """Bulk update base/sale prices by percentage or absolute amount."""
        update_type = request.data.get("update_type")  # percentage | absolute
        field = request.data.get("field", "base_price")
        value = request.data.get("value")
        product_ids = request.data.get("product_ids", [])

        if update_type not in ("percentage", "absolute"):
            return Response(
                {"detail": "update_type must be 'percentage' or 'absolute'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if field not in ("base_price", "sale_price"):
            return Response(
                {"detail": "field must be 'base_price' or 'sale_price'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            value = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Response(
                {"detail": "Invalid value."}, status=status.HTTP_400_BAD_REQUEST
            )

        qs = self.get_queryset()
        if product_ids:
            qs = qs.filter(product_id__in=product_ids)

        preview = request.data.get("preview", False)
        updates = []
        with transaction.atomic():
            for pp in qs:
                old_val = getattr(pp, field) or Decimal("0")
                if update_type == "percentage":
                    new_val = old_val * (1 + value / 100)
                else:
                    new_val = old_val + value
                new_val = max(new_val, Decimal("0")).quantize(Decimal("0.01"))
                updates.append(
                    {
                        "id": str(pp.pk),
                        "product_id": str(pp.product_id),
                        "old_value": str(old_val),
                        "new_value": str(new_val),
                    }
                )
                if not preview:
                    setattr(pp, field, new_val)
                    pp.save(update_fields=[field, "updated_at"])

        return Response(
            {
                "preview": preview,
                "count": len(updates),
                "updates": updates,
            }
        )


class VariantPriceViewSet(ModelViewSet):
    """CRUD for variant prices."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["variant", "use_product_price", "is_active"]
    search_fields = ["variant__sku"]
    ordering_fields = ["base_price", "created_on"]
    ordering = ["-created_on"]

    serializer_class = VariantPriceSerializer

    def get_queryset(self):
        return VariantPrice.objects.select_related("variant", "variant__product").all()
