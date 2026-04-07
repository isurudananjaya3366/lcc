"""LeaveBalance ViewSet (read-only with summary actions)."""

import logging

from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from apps.leave.filters import LeaveBalanceFilter
from apps.leave.models import LeaveBalance
from apps.leave.serializers import LeaveBalanceListSerializer, LeaveBalanceSerializer

logger = logging.getLogger(__name__)


class LeaveBalanceViewSet(ReadOnlyModelViewSet):
    """Read-only ViewSet for LeaveBalance with summary actions.

    Endpoints:
        GET    /balances/                   - List balances
        GET    /balances/{id}/              - Retrieve balance
        GET    /balances/summary/           - Balance summary
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LeaveBalanceFilter
    search_fields = [
        "employee__first_name",
        "employee__last_name",
        "employee__employee_id",
    ]
    ordering_fields = ["year", "used_days", "created_on"]
    ordering = ["-year", "employee"]

    def get_queryset(self):
        return (
            LeaveBalance.objects.filter(is_deleted=False)
            .select_related("employee", "leave_type")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return LeaveBalanceListSerializer
        return LeaveBalanceSerializer

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        """Return balance summary grouped by leave type."""
        from django.utils import timezone

        year = request.query_params.get("year", timezone.now().year)
        employee_id = request.query_params.get("employee")

        qs = self.get_queryset().filter(year=year, is_active=True)

        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        balances = []
        for bal in qs:
            total = bal.opening_balance + bal.allocated_days + bal.carried_from_previous
            balances.append({
                "leave_type": f"{bal.leave_type.name} ({bal.leave_type.code})",
                "allocated": str(total),
                "used": str(bal.used_days),
                "pending": str(bal.pending_days),
                "available": str(bal.available_days),
            })

        return Response({
            "year": int(year),
            "balances": balances,
            "total_entries": len(balances),
        })
