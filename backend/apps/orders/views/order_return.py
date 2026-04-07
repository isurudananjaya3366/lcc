"""
Return ViewSet — approve/reject/receive actions (Task 89).
"""

import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.orders.models.order_return import OrderReturn
from apps.orders.serializers.order_return import (
    OrderReturnListSerializer,
    OrderReturnSerializer,
    ReturnActionSerializer,
    ReturnCreateSerializer,
)

logger = logging.getLogger(__name__)


class ReturnViewSet(ModelViewSet):
    """
    ViewSet for Order Returns.

    Endpoints
    ---------
    GET    /returns/                           — list
    POST   /returns/                           — create return request
    GET    /returns/{id}/                       — retrieve
    POST   /returns/{id}/approve/               — approve return
    POST   /returns/{id}/reject/                — reject return
    POST   /returns/{id}/receive/               — receive & inspect
    POST   /returns/{id}/refund/                — process refund
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            OrderReturn.objects.select_related("order", "requested_by")
            .prefetch_related("return_line_items__order_line_item")
            .filter(is_deleted=False)
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderReturnListSerializer
        if self.action == "create":
            return ReturnCreateSerializer
        return OrderReturnSerializer

    def create(self, request, *args, **kwargs):
        """Create a return request."""
        serializer = ReturnCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        order_id = request.data.get("order")

        try:
            from apps.orders.models import Order, OrderLineItem
            from apps.orders.services.return_service import (
                ReturnService,
                ReturnError,
            )

            order = Order.objects.get(id=order_id)

            # Resolve line item references
            items_data = []
            for item in data["items"]:
                line_item = OrderLineItem.objects.get(
                    id=item["order_line_item"],
                    order=order,
                )
                items_data.append({
                    "order_line_item": line_item,
                    "quantity": item["quantity"],
                })

            order_return = ReturnService.create_return_request(
                order=order,
                items_data=items_data,
                reason=data["reason"],
                reason_detail=data.get("reason_detail", ""),
                user=request.user,
                refund_shipping=data.get("refund_shipping", False),
                notes=data.get("notes", ""),
                request=request,
            )
        except (Order.DoesNotExist, OrderLineItem.DoesNotExist):
            return Response(
                {"detail": "Order or line item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ReturnError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            OrderReturnSerializer(order_return).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_return(self, request, pk=None):
        """Approve a return request."""
        order_return = self.get_object()
        action_ser = ReturnActionSerializer(data=request.data)
        action_ser.is_valid(raise_exception=True)

        try:
            from apps.orders.services.return_service import (
                ReturnService,
                ReturnError,
            )

            order_return = ReturnService.approve_return(
                order_return,
                user=request.user,
                notes=action_ser.validated_data.get("notes", ""),
                request=request,
            )
        except ReturnError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(OrderReturnSerializer(order_return).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject_return(self, request, pk=None):
        """Reject a return request."""
        order_return = self.get_object()
        action_ser = ReturnActionSerializer(data=request.data)
        action_ser.is_valid(raise_exception=True)

        rejection_reason = action_ser.validated_data.get(
            "rejection_reason", ""
        )
        if not rejection_reason:
            return Response(
                {"detail": "Rejection reason is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from apps.orders.services.return_service import (
                ReturnService,
                ReturnError,
            )

            order_return = ReturnService.reject_return(
                order_return,
                rejection_reason=rejection_reason,
                user=request.user,
                request=request,
            )
        except ReturnError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(OrderReturnSerializer(order_return).data)

    @action(detail=True, methods=["post"], url_path="receive")
    def receive_return(self, request, pk=None):
        """Receive and inspect returned items."""
        order_return = self.get_object()
        inspections = request.data.get("inspections", [])

        if not inspections:
            return Response(
                {"detail": "Inspections data is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from apps.orders.services.return_service import (
                ReturnService,
                ReturnError,
            )

            # Resolve return line item references
            resolved = []
            for insp in inspections:
                rli = order_return.return_line_items.get(
                    id=insp["return_line_item"]
                )
                resolved.append({
                    "return_line_item": rli,
                    "condition": insp.get("condition", ""),
                    "inspection_notes": insp.get("inspection_notes", ""),
                })

            order_return = ReturnService.receive_return(
                order_return,
                inspections=resolved,
                user=request.user,
                request=request,
            )
        except ReturnError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(OrderReturnSerializer(order_return).data)

    @action(detail=True, methods=["post"], url_path="refund")
    def process_refund(self, request, pk=None):
        """Process a refund for a received return."""
        order_return = self.get_object()
        refund_method = request.data.get("refund_method", "")

        if not refund_method:
            return Response(
                {"detail": "Refund method is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from apps.orders.services.return_service import (
                ReturnService,
                ReturnError,
            )

            order_return = ReturnService.process_refund(
                order_return,
                refund_method=refund_method,
                user=request.user,
                request=request,
            )
        except ReturnError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(OrderReturnSerializer(order_return).data)
