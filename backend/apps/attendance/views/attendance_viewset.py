"""Attendance Record ViewSet with filtering and custom actions."""

import logging
from datetime import date

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.attendance.filters import AttendanceRecordFilter
from apps.attendance.models import AttendanceRecord
from apps.attendance.serializers import (
    AttendanceRecordListSerializer,
    AttendanceRecordSerializer,
)
from apps.attendance.services.report_service import AttendanceReportService

logger = logging.getLogger(__name__)


class AttendanceViewSet(ModelViewSet):
    """ViewSet for Attendance Record CRUD and reporting actions."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AttendanceRecordFilter
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_id"]
    ordering_fields = ["date", "clock_in", "clock_out", "status", "work_hours", "created_on"]
    ordering = ["-date"]

    def get_queryset(self):
        return (
            AttendanceRecord.objects.filter(is_deleted=False)
            .select_related("employee", "shift")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return AttendanceRecordListSerializer
        return AttendanceRecordSerializer

    def perform_destroy(self, instance):
        """Soft delete."""
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    # ── Custom Actions ──────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="my-attendance")
    def my_attendance(self, request):
        """Return the current user's attendance records."""
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(user=request.user, is_deleted=False)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "No employee profile found for current user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        qs = self.filter_queryset(self.get_queryset().filter(employee=employee))
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = AttendanceRecordListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = AttendanceRecordListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Return today's attendance summary."""
        today = date.today()
        summary = AttendanceReportService.daily_summary(today)
        return Response(summary)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Return attendance summary for a date range and optional employee."""
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        employee_id = request.query_params.get("employee")

        if not date_from or not date_to:
            return Response(
                {"detail": "date_from and date_to query params are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if employee_id:
            data = AttendanceReportService.employee_history(
                employee_id, date_from, date_to,
            )
        else:
            data = AttendanceReportService.monthly_summary(date_from[:7])

        return Response(data)

    @action(detail=False, methods=["get"])
    def export(self, request):
        """Export attendance records as CSV."""
        from django.http import HttpResponse

        from apps.attendance.services.export_service import AttendanceExportService

        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        export_type = request.query_params.get("type", "daily")

        if export_type == "monthly" and date_from:
            csv_content = AttendanceExportService.export_monthly_csv(date_from[:7])
            filename = f"attendance_monthly_{date_from[:7]}.csv"
        elif export_type == "late" and date_from and date_to:
            csv_content = AttendanceExportService.export_late_arrivals_csv(
                date_from, date_to,
            )
            filename = f"attendance_late_{date_from}_to_{date_to}.csv"
        elif date_from:
            csv_content = AttendanceExportService.export_daily_csv(date_from)
            filename = f"attendance_daily_{date_from}.csv"
        else:
            return Response(
                {"detail": "date_from query param is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
