"""
Product Search API view for POS.

Provides combined search, barcode scanning, quick buttons,
and search history endpoints.
"""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pos.search.models import QuickButtonGroup
from apps.pos.search.serializers import (
    BarcodeScanRequestSerializer,
    ProductSearchRequestSerializer,
    ProductSearchResultSerializer,
    QuickButtonGroupSerializer,
    SearchHistorySerializer,
)
from apps.pos.search.services.product_search_service import (
    ProductSearchService,
)

logger = logging.getLogger(__name__)


class ProductSearchView(APIView):
    """
    POST /api/v1/pos/search/  — combined product search
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = ProductSearchRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        query = ser.validated_data["query"]
        category = ser.validated_data.get("category")
        limit = ser.validated_data.get("limit", 20)

        results = ProductSearchService.combined_search(
            query=query, limit=limit
        )

        if category:
            results = ProductSearchService.filter_by_category(
                results, category
            )

        # Record search history (best-effort)
        terminal = getattr(request, "_pos_terminal", None)
        ProductSearchService.record_search(
            user=request.user,
            terminal=terminal,
            query=query,
            result_count=len(results),
            search_method="combined",
        )

        return Response(
            ProductSearchResultSerializer(results, many=True).data
        )


class BarcodeScanView(APIView):
    """
    POST /api/v1/pos/search/barcode/  — barcode lookup
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = BarcodeScanRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        barcode = ser.validated_data["barcode"]

        result = ProductSearchService.barcode_search(barcode)

        terminal = getattr(request, "_pos_terminal", None)
        ProductSearchService.record_search(
            user=request.user,
            terminal=terminal,
            query=barcode,
            result_count=1 if result else 0,
            search_method="barcode",
        )

        if not result:
            return Response(
                {"detail": "No product found for this barcode."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            ProductSearchResultSerializer(result).data
        )


class QuickButtonGroupListView(APIView):
    """
    GET /api/v1/pos/search/quick-buttons/  — quick-button groups
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        terminal_id = request.query_params.get("terminal")
        qs = QuickButtonGroup.objects.filter(
            is_active=True, is_deleted=False
        ).order_by("display_order")
        if terminal_id:
            qs = qs.filter(terminals__id=terminal_id)
        return Response(QuickButtonGroupSerializer(qs, many=True).data)


class SearchHistoryView(APIView):
    """
    GET /api/v1/pos/search/history/  — recent searches for user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        limit = min(max(limit, 1), 50)
        results = ProductSearchService.get_recent_searches(
            user=request.user, limit=limit
        )
        return Response(SearchHistorySerializer(results, many=True).data)
