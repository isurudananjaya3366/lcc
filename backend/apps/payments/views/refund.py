"""Refund ViewSet."""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.payments.exceptions import RefundError
from apps.payments.filters import RefundFilter
from apps.payments.models import Refund
from apps.payments.serializers import (
    RefundApproveSerializer,
    RefundCreateSerializer,
    RefundListSerializer,
    RefundRejectSerializer,
    RefundSerializer,
)

logger = logging.getLogger(__name__)


class RefundViewSet(ModelViewSet):
    """
    ViewSet for Refunds.

    Endpoints
    ---------
    GET    /refunds/                   — list
    POST   /refunds/                   — request refund
    GET    /refunds/{id}/              — retrieve
    POST   /refunds/{id}/approve/      — approve refund
    POST   /refunds/{id}/reject/       — reject refund
    POST   /refunds/{id}/process/      — process refund
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RefundFilter
    search_fields = ["refund_number", "original_payment__payment_number"]
    ordering_fields = ["created_on", "amount", "status"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return Refund.objects.select_related(
            "original_payment",
            "original_payment__customer",
            "requested_by",
            "approved_by",
            "processed_by",
        ).all()

    def get_serializer_class(self):
        if self.action == "list":
            return RefundListSerializer
        if self.action == "create":
            return RefundCreateSerializer
        return RefundSerializer

    def perform_create(self, serializer):
        """Request refund via service."""
        from apps.payments.models import Payment
        from apps.payments.services.refund_service import RefundService

        data = serializer.validated_data
        original_payment = Payment.objects.get(id=data["payment_id"])

        refund = RefundService.request_refund(
            original_payment=original_payment,
            amount=data["amount"],
            reason=data["reason"],
            reason_notes=data.get("reason_notes", ""),
            refund_method=data.get("refund_method", "ORIGINAL"),
            user=self.request.user,
        )
        self._created_refund = refund

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except RefundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            RefundSerializer(self._created_refund).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a pending refund."""
        from apps.payments.services.refund_service import RefundService

        refund = self.get_object()
        approve_serializer = RefundApproveSerializer(data=request.data)
        approve_serializer.is_valid(raise_exception=True)
        try:
            RefundService.approve_refund(refund, user=request.user)
        except RefundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundSerializer(refund).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a pending refund."""
        from apps.payments.services.refund_service import RefundService

        refund = self.get_object()
        reject_serializer = RefundRejectSerializer(data=request.data)
        reject_serializer.is_valid(raise_exception=True)
        notes = reject_serializer.validated_data.get("notes", "")
        try:
            RefundService.reject_refund(refund, notes=notes, user=request.user)
        except RefundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundSerializer(refund).data)

    @action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        """Process an approved refund."""
        from apps.payments.services.refund_service import RefundService

        refund = self.get_object()
        try:
            RefundService.process_refund(refund, user=request.user)
        except RefundError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundSerializer(refund).data)
