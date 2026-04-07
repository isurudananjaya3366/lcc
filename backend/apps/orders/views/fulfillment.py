"""
Fulfillment ViewSet — pick/pack/ship/deliver actions (Task 88).
"""

import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.orders.models.fulfillment import Fulfillment
from apps.orders.serializers.fulfillment import (
    FulfillmentListSerializer,
    FulfillmentSerializer,
)

logger = logging.getLogger(__name__)


class FulfillmentViewSet(ModelViewSet):
    """
    ViewSet for Fulfillments.

    Endpoints
    ---------
    GET    /fulfillments/                          — list
    GET    /fulfillments/{id}/                      — retrieve
    POST   /fulfillments/{id}/pick/                 — pick items
    POST   /fulfillments/{id}/pack/                 — pack items
    POST   /fulfillments/{id}/ship/                 — mark shipped
    POST   /fulfillments/{id}/deliver/              — confirm delivery
    GET    /fulfillments/{id}/progress/             — fulfillment progress
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return (
            Fulfillment.objects.select_related("order", "warehouse")
            .prefetch_related("line_items__order_line_item")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return FulfillmentListSerializer
        return FulfillmentSerializer

    @action(detail=True, methods=["post"], url_path="pick")
    def pick_items(self, request, pk=None):
        """Mark fulfillment items as picked."""
        fulfillment = self.get_object()
        try:
            from apps.orders.services.fulfillment_service import (
                FulfillmentService,
            )

            FulfillmentService.pick_items(
                fulfillment,
                pick_data=request.data.get("items", []),
                user=request.user,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        fulfillment.refresh_from_db()
        return Response(FulfillmentSerializer(fulfillment).data)

    @action(detail=True, methods=["post"], url_path="pack")
    def pack_items(self, request, pk=None):
        """Mark fulfillment as packed."""
        fulfillment = self.get_object()
        try:
            from apps.orders.services.fulfillment_service import (
                FulfillmentService,
            )

            FulfillmentService.pack_order(
                fulfillment,
                package_data=request.data,
                user=request.user,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        fulfillment.refresh_from_db()
        return Response(FulfillmentSerializer(fulfillment).data)

    @action(detail=True, methods=["post"], url_path="ship")
    def ship_fulfillment(self, request, pk=None):
        """Mark fulfillment as shipped."""
        fulfillment = self.get_object()
        try:
            from apps.orders.services.fulfillment_service import (
                FulfillmentService,
            )

            FulfillmentService.ship_order(
                fulfillment,
                shipping_data=request.data,
                user=request.user,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        fulfillment.refresh_from_db()
        return Response(FulfillmentSerializer(fulfillment).data)

    @action(detail=True, methods=["post"], url_path="deliver")
    def deliver_fulfillment(self, request, pk=None):
        """Confirm delivery of fulfillment."""
        fulfillment = self.get_object()
        try:
            from apps.orders.services.fulfillment_service import (
                FulfillmentService,
            )

            FulfillmentService.confirm_delivery(
                fulfillment,
                delivery_data=request.data,
                user=request.user,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        fulfillment.refresh_from_db()
        return Response(FulfillmentSerializer(fulfillment).data)

    @action(detail=True, methods=["get"], url_path="progress")
    def progress(self, request, pk=None):
        """Get fulfillment progress for the parent order."""
        fulfillment = self.get_object()
        try:
            from apps.orders.services.fulfillment_service import (
                FulfillmentService,
            )

            progress = FulfillmentService.get_fulfillment_progress(
                fulfillment.order
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(progress)
