"""
Store Credit ViewSet.

Provides read-only listing/retrieval + custom actions:
issue, redeem, balance.
"""

import logging
from decimal import Decimal, InvalidOperation

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.credit.filters import StoreCreditFilterSet
from apps.credit.models import StoreCredit
from apps.credit.serializers import (
    StoreCreditSerializer,
    StoreCreditTransactionSerializer,
)
from apps.credit.services.store_credit_service import StoreCreditService

logger = logging.getLogger(__name__)


class StoreCreditViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Read-only ViewSet for store credit with issue/redeem actions."""

    permission_classes = [IsAuthenticated]
    serializer_class = StoreCreditSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StoreCreditFilterSet
    search_fields = [
        "customer__first_name",
        "customer__last_name",
        "customer__email",
    ]
    ordering_fields = ["balance", "total_issued", "expiry_date", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return StoreCredit.objects.select_related(
            "customer", "issued_by"
        ).filter(is_deleted=False)

    @action(detail=True, methods=["get"], url_path="balance")
    def balance(self, request, pk=None):
        """Return the current balance for this store credit."""
        credit = self.get_object()
        data = {
            "customer_id": str(credit.customer_id),
            "balance": str(credit.balance),
            "available_balance": str(credit.get_available_balance()),
            "is_expired": credit.is_expired,
            "expiry_date": credit.expiry_date,
        }
        return Response(data)

    @action(detail=True, methods=["get"], url_path="transactions")
    def transactions(self, request, pk=None):
        """List transactions for this store credit."""
        credit = self.get_object()
        txns = credit.transactions.order_by("-created_on")
        page = self.paginate_queryset(txns)
        if page is not None:
            serializer = StoreCreditTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = StoreCreditTransactionSerializer(txns, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="issue",
        permission_classes=[IsAdminUser],
    )
    def issue(self, request, pk=None):
        """Issue additional store credit (admin only)."""
        credit = self.get_object()
        amount = request.data.get("amount")
        source = request.data.get("source", "adjustment")
        reference = request.data.get("reference", "")
        notes = request.data.get("notes", "")

        if amount is None:
            return Response(
                {"detail": "amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response(
                {"detail": "Invalid amount value."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if amount <= Decimal("0"):
            return Response(
                {"detail": "amount must be positive."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = StoreCreditService.issue_credit(
                customer_id=credit.customer_id,
                amount=amount,
                source=source,
                reference=reference,
                issued_by=request.user,
                notes=notes,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        credit.refresh_from_db()
        return Response(
            StoreCreditSerializer(credit).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="redeem")
    def redeem(self, request, pk=None):
        """Redeem store credit."""
        credit = self.get_object()
        amount = request.data.get("amount")
        order_id = request.data.get("order_id")
        notes = request.data.get("notes", "")

        if amount is None:
            return Response(
                {"detail": "amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response(
                {"detail": "Invalid amount value."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if amount <= Decimal("0"):
            return Response(
                {"detail": "amount must be positive."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = StoreCreditService.redeem_credit(
                customer_id=credit.customer_id,
                amount=amount,
                order_id=order_id,
                performed_by=request.user,
                notes=notes,
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        credit.refresh_from_db()
        return Response(StoreCreditSerializer(credit).data)
