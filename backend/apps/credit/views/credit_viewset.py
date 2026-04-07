"""
Credit ViewSet.

Provides CRUD + custom actions for CustomerCredit accounts:
approve, suspend, adjust_limit, write_off, record_payment,
transactions, aging_report, statistics.
"""

import logging
from decimal import Decimal, InvalidOperation

from django.db.models import Avg, Count, Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.credit.constants import CreditStatus
from apps.credit.filters import CreditFilterSet
from apps.credit.models import CustomerCredit
from apps.credit.serializers import (
    CreditListSerializer,
    CreditTransactionSerializer,
    CustomerCreditSerializer,
)
from apps.credit.services.credit_service import (
    CreditAccountError,
    CreditService,
    InsufficientCreditError,
)

logger = logging.getLogger(__name__)


class CreditViewSet(ModelViewSet):
    """ViewSet for customer credit accounts."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CreditFilterSet
    search_fields = [
        "customer__first_name",
        "customer__last_name",
        "customer__email",
    ]
    ordering_fields = [
        "credit_limit",
        "available_credit",
        "outstanding_balance",
        "created_on",
    ]
    ordering = ["-created_on"]

    def get_queryset(self):
        return CustomerCredit.objects.select_related("customer").filter(
            is_deleted=False
        )

    def get_serializer_class(self):
        if self.action == "list":
            return CreditListSerializer
        return CustomerCreditSerializer

    # ── Read-only detail actions ────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="transactions")
    def transactions(self, request, pk=None):
        """List transactions for this credit account."""
        credit = self.get_object()
        txns = credit.transactions.order_by("-transaction_date")
        page = self.paginate_queryset(txns)
        if page is not None:
            serializer = CreditTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CreditTransactionSerializer(txns, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="aging-report")
    def aging_report(self, request, pk=None):
        """Return aging buckets for this credit account."""
        credit = self.get_object()
        service = CreditService(credit)
        buckets = service.calculate_aging_buckets()
        return Response(buckets)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """Aggregate credit statistics across all accounts."""
        qs = self.get_queryset()
        data = {
            "total_accounts": qs.count(),
            "active_accounts": qs.filter(status=CreditStatus.ACTIVE).count(),
            "suspended_accounts": qs.filter(
                status=CreditStatus.SUSPENDED
            ).count(),
            "total_credit_limit": str(
                qs.aggregate(total=Sum("credit_limit"))["total"]
                or Decimal("0.00")
            ),
            "total_outstanding": str(
                qs.aggregate(total=Sum("outstanding_balance"))["total"]
                or Decimal("0.00")
            ),
            "average_utilization": str(
                qs.aggregate(avg=Avg("outstanding_balance"))["avg"]
                or Decimal("0.00")
            ),
            "overdue_count": sum(
                1 for c in qs.filter(status=CreditStatus.ACTIVE) if c.is_payment_overdue
            ),
        }
        return Response(data)

    # ── Admin actions ───────────────────────────────────────────────

    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
        permission_classes=[IsAdminUser],
    )
    def approve(self, request, pk=None):
        """Approve a pending credit account."""
        credit = self.get_object()
        if credit.status != CreditStatus.PENDING_APPROVAL:
            return Response(
                {"detail": "Only pending accounts can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        credit.status = CreditStatus.ACTIVE
        credit.approved_by = request.user
        from django.utils import timezone

        credit.approved_at = timezone.now()
        credit.save(update_fields=["status", "approved_by", "approved_at", "updated_on"])
        return Response(CustomerCreditSerializer(credit).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="suspend",
        permission_classes=[IsAdminUser],
    )
    def suspend(self, request, pk=None):
        """Suspend a credit account."""
        credit = self.get_object()
        reason = request.data.get("reason", "")
        service = CreditService(credit)
        try:
            service.suspend_account(reason=reason, user=request.user)
        except CreditAccountError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        credit.refresh_from_db()
        return Response(CustomerCreditSerializer(credit).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="adjust-limit",
        permission_classes=[IsAdminUser],
    )
    def adjust_limit(self, request, pk=None):
        """Adjust the credit limit for an account."""
        credit = self.get_object()
        new_limit = request.data.get("credit_limit")
        if new_limit is None:
            return Response(
                {"detail": "credit_limit is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            new_limit = Decimal(str(new_limit))
        except (InvalidOperation, TypeError, ValueError):
            return Response(
                {"detail": "Invalid credit_limit value."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_limit < Decimal("0"):
            return Response(
                {"detail": "credit_limit must be non-negative."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        old_limit = credit.credit_limit
        credit.credit_limit = new_limit
        # Adjust available credit by the difference
        credit.available_credit += new_limit - old_limit
        if credit.available_credit < Decimal("0"):
            credit.available_credit = Decimal("0")
        credit.save(update_fields=["credit_limit", "available_credit", "updated_on"])
        notes = f"Credit limit adjusted from {old_limit} to {new_limit} by admin."
        service = CreditService(credit)
        service.record_adjustment(
            amount=new_limit - old_limit, notes=notes, user=request.user
        )
        return Response(CustomerCreditSerializer(credit).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="write-off",
        permission_classes=[IsAdminUser],
    )
    def write_off(self, request, pk=None):
        """Write off outstanding balance (admin only)."""
        credit = self.get_object()
        amount = request.data.get("amount")
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
        service = CreditService(credit)
        try:
            service.write_off(amount=amount, notes=notes, user=request.user)
        except (CreditAccountError, InsufficientCreditError) as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        credit.refresh_from_db()
        return Response(CustomerCreditSerializer(credit).data)

    # ── Customer action ─────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="record-payment")
    def record_payment(self, request, pk=None):
        """Record a payment against the credit account."""
        credit = self.get_object()
        amount = request.data.get("amount")
        payment_method = request.data.get("payment_method", "")
        payment_reference = request.data.get("payment_reference", "")
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

        service = CreditService(credit)
        try:
            txn = service.record_payment(
                amount=amount,
                payment_method=payment_method,
                payment_reference=payment_reference,
                notes=notes,
                user=request.user,
            )
        except (CreditAccountError, InsufficientCreditError) as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            CreditTransactionSerializer(txn).data,
            status=status.HTTP_201_CREATED,
        )
