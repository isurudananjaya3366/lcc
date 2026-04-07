"""
Public price lookup views.
"""

from decimal import Decimal

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product, ProductVariant

from ..serializers import PriceBreakdownSerializer


class PriceLookupView(APIView):
    """
    Public GET endpoint to resolve the effective price of a product or variant.

    Query params: product_id, variant_id (optional), quantity (default 1).
    """

    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 5))  # 5-minute cache
    def get(self, request):
        product_id = request.query_params.get("product_id")
        variant_id = request.query_params.get("variant_id")
        quantity = int(request.query_params.get("quantity", 1))

        if not product_id:
            return Response(
                {"detail": "product_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        variant = None
        if variant_id:
            try:
                variant = ProductVariant.objects.get(pk=variant_id, product=product)
            except ProductVariant.DoesNotExist:
                return Response(
                    {"detail": "Variant not found."}, status=status.HTTP_404_NOT_FOUND
                )

        data = PriceBreakdownSerializer.build_breakdown(
            product, quantity=max(quantity, 1), variant=variant
        )
        return Response(PriceBreakdownSerializer(data).data)


class BulkPriceLookupView(APIView):
    """
    Public POST endpoint to resolve prices for multiple items at once.

    Body: ``{"items": [{"product_id": ..., "variant_id": ..., "quantity": 1}, ...]}``
    """

    permission_classes = [AllowAny]

    def post(self, request):
        items = request.data.get("items", [])
        if not items:
            return Response(
                {"detail": "items list is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        for item in items:
            product_id = item.get("product_id")
            variant_id = item.get("variant_id")
            quantity = int(item.get("quantity", 1))

            try:
                product = Product.objects.get(pk=product_id)
            except (Product.DoesNotExist, ValueError, TypeError):
                results.append({"product_id": product_id, "error": "Product not found."})
                continue

            variant = None
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(pk=variant_id, product=product)
                except (ProductVariant.DoesNotExist, ValueError, TypeError):
                    results.append(
                        {"product_id": product_id, "variant_id": variant_id, "error": "Variant not found."}
                    )
                    continue

            data = PriceBreakdownSerializer.build_breakdown(
                product, quantity=max(quantity, 1), variant=variant
            )
            results.append(PriceBreakdownSerializer(data).data)

        return Response({"results": results})
