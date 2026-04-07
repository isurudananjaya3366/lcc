"""
Goods Receipt Note ViewSet.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.purchases.models.goods_receipt import GoodsReceipt
from apps.purchases.serializers.grn_serializer import (
    GRNDetailSerializer,
    GRNListSerializer,
)


class GRNViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for Goods Receipt Notes with lifecycle actions."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["purchase_order", "status"]
    search_fields = ["grn_number", "purchase_order__po_number"]
    ordering_fields = ["grn_number", "received_at", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return GoodsReceipt.objects.select_related(
            "purchase_order", "received_by"
        ).prefetch_related("line_items")

    def get_serializer_class(self):
        if self.action == "list":
            return GRNListSerializer
        return GRNDetailSerializer

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        """Mark a GRN as completed."""
        from apps.purchases.constants import GRN_STATUS_COMPLETED

        grn = self.get_object()
        grn.status = GRN_STATUS_COMPLETED
        grn.save(update_fields=["status", "updated_on"])
        return Response(GRNDetailSerializer(grn).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancel a GRN."""
        from apps.purchases.constants import GRN_STATUS_CANCELLED

        grn = self.get_object()
        grn.status = GRN_STATUS_CANCELLED
        grn.save(update_fields=["status", "updated_on"])
        return Response(GRNDetailSerializer(grn).data)
