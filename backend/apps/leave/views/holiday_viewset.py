"""Holiday ViewSet with CRUD and calendar views."""

import logging
from datetime import date, timedelta

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from apps.leave.filters import HolidayFilter
from apps.leave.models import Holiday
from apps.leave.serializers import (
    HolidayCalendarSerializer,
    HolidayListSerializer,
    HolidaySerializer,
)

logger = logging.getLogger(__name__)


class HolidayViewSet(ModelViewSet):
    """ViewSet for Holiday CRUD and calendar actions.

    Endpoints:
        GET    /holidays/                   - List holidays
        POST   /holidays/                   - Create holiday
        GET    /holidays/{id}/              - Retrieve holiday
        PUT    /holidays/{id}/              - Update holiday
        PATCH  /holidays/{id}/              - Partial update
        DELETE /holidays/{id}/              - Delete holiday
        GET    /holidays/calendar/          - Calendar view
        GET    /holidays/upcoming/          - Upcoming holidays
        GET    /holidays/check/             - Check if date is holiday
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = HolidayFilter
    search_fields = ["name", "description"]
    ordering_fields = ["date", "name", "holiday_type", "created_on"]
    ordering = ["date"]

    def get_queryset(self):
        return (
            Holiday.objects.filter(is_deleted=False)
            .select_related("department")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return HolidayListSerializer
        if self.action == "calendar":
            return HolidayCalendarSerializer
        return HolidaySerializer

    def perform_destroy(self, instance):
        """Soft delete."""
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    @action(detail=False, methods=["get"], url_path="calendar")
    def calendar(self, request):
        """Return holidays grouped by month for a year."""
        year = request.query_params.get("year", date.today().year)
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = date.today().year

        holidays = self.get_queryset().filter(
            date__year=year,
            is_active=True,
        ).order_by("date")

        by_month = {}
        by_type = {}

        for h in holidays:
            month_key = str(h.date.month)
            by_month.setdefault(month_key, []).append({
                "date": h.date.isoformat(),
                "name": h.name,
                "type": h.holiday_type,
            })
            by_type[h.holiday_type] = by_type.get(h.holiday_type, 0) + 1

        return Response({
            "year": year,
            "total_holidays": holidays.count(),
            "by_month": by_month,
            "by_type": by_type,
        })

    @action(detail=False, methods=["get"], url_path="upcoming")
    def upcoming(self, request):
        """Return upcoming holidays (next 90 days)."""
        today = date.today()
        end = today + timedelta(days=90)

        holidays = self.get_queryset().filter(
            date__gte=today,
            date__lte=end,
            is_active=True,
        ).order_by("date")

        data = [
            {
                "id": str(h.id),
                "date": h.date.isoformat(),
                "name": h.name,
                "holiday_type": h.holiday_type,
                "days_until": (h.date - today).days,
                "description": h.description or "",
            }
            for h in holidays
        ]

        return Response({
            "upcoming_holidays": data,
            "total": len(data),
        })

    @action(detail=False, methods=["get"], url_path="check")
    def check_date(self, request):
        """Check if a specific date is a holiday."""
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"detail": "date query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            check = date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        holiday = self.get_queryset().filter(
            date=check,
            is_active=True,
        ).first()

        if holiday:
            return Response({
                "date": check.isoformat(),
                "is_holiday": True,
                "holiday": {
                    "id": str(holiday.id),
                    "name": holiday.name,
                    "holiday_type": holiday.holiday_type,
                    "description": holiday.description or "",
                    "applies_to": holiday.applies_to,
                },
            })

        return Response({
            "date": check.isoformat(),
            "is_holiday": False,
            "holiday": None,
        })
