"""
Order ViewSet — full CRUD + status actions (Tasks 84, 86, 87).
"""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.orders.constants import OrderStatus
from apps.orders.filters import OrderFilter
from apps.orders.models import Order
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderLineItemSerializer,
    OrderListSerializer,
    OrderSerializer,
    OrderStatusActionSerializer,
)
from apps.orders.services.order_service import (
    InvalidStatusTransition,
    OrderLockedError,
    OrderValidationError,
)

logger = logging.getLogger(__name__)


class OrderViewSet(ModelViewSet):
    """
    ViewSet for Orders.

    Endpoints
    ---------
    GET    /orders/                          — list
    POST   /orders/                          — create
    GET    /orders/{id}/                      — retrieve
    PUT    /orders/{id}/                      — update
    PATCH  /orders/{id}/                      — partial_update
    DELETE /orders/{id}/                      — destroy (draft only)
    POST   /orders/{id}/confirm/              — confirm order
    POST   /orders/{id}/process/              — start processing
    POST   /orders/{id}/ship/                 — mark shipped
    POST   /orders/{id}/deliver/              — mark delivered
    POST   /orders/{id}/complete/             — mark completed
    POST   /orders/{id}/cancel/               — cancel order
    POST   /orders/{id}/duplicate/            — duplicate order
    GET    /orders/{id}/line_items/           — list line items
    POST   /orders/{id}/line_items/           — add line item
    GET    /orders/{id}/history/              — audit history
    GET    /orders/{id}/available_actions/    — list available actions
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = [
        "order_number",
        "customer_name",
        "customer_email",
        "notes",
        "line_items__item_name",
        "line_items__item_sku",
    ]
    ordering_fields = [
        "created_on",
        "total_amount",
        "order_number",
        "status",
    ]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            Order.objects.select_related(
                "customer", "created_by", "quote", "pos_session"
            )
            .prefetch_related("line_items")
            .filter(is_deleted=False)
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        from apps.orders.services.order_service import OrderService

        data = serializer.validated_data
        items_data = data.pop("items", None)
        order = OrderService.create_order(
            data=data,
            items_data=items_data,
            user=self.request.user,
        )
        serializer.instance = order

    def perform_destroy(self, instance):
        if not instance.is_draft:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only draft orders can be deleted."
            )
        instance.delete()

    # ── Status Actions (Task 87) ─────────────────────────────────

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm_order(self, request, pk=None):
        """Confirm a pending order."""
        return self._transition(request, OrderStatus.CONFIRMED)

    @action(detail=True, methods=["post"], url_path="process")
    def process_order(self, request, pk=None):
        """Start processing a confirmed order."""
        return self._transition(request, OrderStatus.PROCESSING)

    @action(detail=True, methods=["post"], url_path="ship")
    def ship_order(self, request, pk=None):
        """Mark order as shipped."""
        return self._transition(request, OrderStatus.SHIPPED)

    @action(detail=True, methods=["post"], url_path="deliver")
    def deliver_order(self, request, pk=None):
        """Mark order as delivered."""
        return self._transition(request, OrderStatus.DELIVERED)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_order(self, request, pk=None):
        """Mark order as completed."""
        return self._transition(request, OrderStatus.COMPLETED)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        """Cancel the order."""
        order = self.get_object()
        action_ser = OrderStatusActionSerializer(data=request.data)
        action_ser.is_valid(raise_exception=True)
        reason = action_ser.validated_data.get("reason", "")

        try:
            from apps.orders.services.cancellation_service import (
                CancellationService,
            )

            order = CancellationService.cancel_order(
                order, user=request.user, reason=reason, request=request,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            OrderSerializer(order, context={"request": request}).data
        )

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate_order(self, request, pk=None):
        """Duplicate the order."""
        order = self.get_object()
        try:
            from apps.orders.services.order_service import OrderService

            new_order = OrderService.duplicate_order(
                order.id, user=request.user
            )
        except OrderValidationError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            OrderSerializer(new_order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    # ── Line Items ───────────────────────────────────────────────

    @action(detail=True, methods=["get", "post"], url_path="line_items")
    def line_items(self, request, pk=None):
        """List or add line items for an order."""
        order = self.get_object()

        if request.method == "GET":
            items = order.line_items.order_by("position")
            serializer = OrderLineItemSerializer(items, many=True)
            return Response(serializer.data)

        # POST — create
        if order.is_locked:
            return Response(
                {"detail": "Cannot add items to a locked order."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OrderLineItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(order=order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ── History ──────────────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Return audit log entries for the order."""
        order = self.get_object()
        entries = (
            order.history.order_by("-created_on")
            .values(
                "id",
                "event_type",
                "description",
                "created_on",
                "old_values",
                "new_values",
                "actor_name",
            )[:100]
        )
        return Response(list(entries))

    # ── Available Actions ────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="available_actions")
    def available_actions(self, request, pk=None):
        """Return the actions available for the order's current state."""
        order = self.get_object()
        from apps.orders.constants import ALLOWED_TRANSITIONS

        transitions = ALLOWED_TRANSITIONS.get(order.status, [])
        actions = []
        for target in transitions:
            actions.append({
                "action": target.value,
                "label": target.label,
            })

        # Additional actions
        if order.is_draft:
            actions.append({"action": "delete", "label": "Delete"})
        if not order.is_locked:
            actions.append({"action": "duplicate", "label": "Duplicate"})

        return Response({"actions": actions})

    # ── Private Helpers ──────────────────────────────────────────

    def _transition(self, request, target_status):
        """Helper for status transition actions."""
        order = self.get_object()
        action_ser = OrderStatusActionSerializer(data=request.data)
        action_ser.is_valid(raise_exception=True)
        notes = action_ser.validated_data.get("notes", "")

        try:
            from apps.orders.services.order_service import OrderService

            order = OrderService.transition_status(
                order,
                target_status,
                user=request.user,
                notes=notes,
                request=request,
            )
        except (InvalidStatusTransition, OrderLockedError) as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            OrderSerializer(order, context={"request": request}).data
        )
