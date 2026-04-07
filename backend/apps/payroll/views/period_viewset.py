"""PayrollPeriod ViewSet."""

import logging

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.payroll.filters import PayrollPeriodFilter
from apps.payroll.models import PayrollPeriod
from apps.payroll.serializers.period_serializer import (
    PayrollPeriodListSerializer,
    PayrollPeriodSerializer,
)

logger = logging.getLogger(__name__)


class PayrollPeriodViewSet(ModelViewSet):
    """ViewSet for PayrollPeriod CRUD and management actions.

    Endpoints:
        GET    /periods/              - List periods
        POST   /periods/              - Create period
        GET    /periods/{id}/         - Retrieve period
        PUT    /periods/{id}/         - Update period
        DELETE /periods/{id}/         - Delete period
        POST   /periods/{id}/lock/    - Lock period
        POST   /periods/{id}/unlock/  - Unlock period
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PayrollPeriodFilter
    search_fields = ["name"]
    ordering_fields = ["period_year", "period_month", "start_date", "pay_date", "created_on"]
    ordering = ["-period_year", "-period_month"]

    def get_queryset(self):
        return PayrollPeriod.objects.select_related("locked_by").all()

    def get_serializer_class(self):
        if self.action == "list":
            return PayrollPeriodListSerializer
        return PayrollPeriodSerializer

    @action(detail=True, methods=["post"], url_path="lock")
    def lock(self, request, pk=None):
        """Lock a payroll period to prevent modifications."""
        period = self.get_object()
        if period.is_locked:
            return Response(
                {"detail": "Period is already locked."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        period.is_locked = True
        period.locked_at = timezone.now()
        period.locked_by = request.user
        period.save(update_fields=["is_locked", "locked_at", "locked_by"])
        serializer = self.get_serializer(period)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="unlock")
    def unlock(self, request, pk=None):
        """Unlock a payroll period."""
        period = self.get_object()
        if not period.is_locked:
            return Response(
                {"detail": "Period is not locked."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        period.is_locked = False
        period.locked_at = None
        period.locked_by = None
        period.save(update_fields=["is_locked", "locked_at", "locked_by"])
        serializer = self.get_serializer(period)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Get the current active payroll period."""
        from datetime import date
        today = date.today()
        try:
            period = PayrollPeriod.objects.filter(
                start_date__lte=today,
                end_date__gte=today,
            ).first()
            if not period:
                return Response(
                    {"detail": "No current payroll period found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = self.get_serializer(period)
            return Response(serializer.data)
        except Exception:
            return Response(
                {"detail": "Error retrieving current period."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
