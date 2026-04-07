"""Check-in/Check-out API views for the Attendance module."""

import logging
from datetime import date

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.models import AttendanceRecord
from apps.attendance.serializers import (
    AttendanceRecordSerializer,
    ClockInSerializer,
    ClockOutSerializer,
)
from apps.attendance.services.attendance_service import AttendanceService
from apps.attendance.services.mobile_service import MobileCheckInService

logger = logging.getLogger(__name__)


class CheckInView(APIView):
    """Clock-in endpoint for the current authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.employees.models import Employee

        serializer = ClockInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            employee = Employee.objects.get(user=request.user, is_deleted=False)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "No employee profile found for current user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if already clocked in today
        today = date.today()
        existing = AttendanceRecord.objects.filter(
            employee=employee, date=today, is_deleted=False,
        ).first()
        if existing and existing.clock_in:
            return Response(
                {
                    "status": "error",
                    "code": "ALREADY_CLOCKED_IN",
                    "message": "You have already clocked in today.",
                    "data": {
                        "existing_attendance": AttendanceRecordSerializer(existing).data,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Geofence / GPS validation for mobile check-ins ──
        location = serializer.validated_data.get("location")
        method = serializer.validated_data.get("clock_in_method", "web")
        if method == "mobile" and location:
            validation = MobileCheckInService.validate_check_in(
                latitude=location.get("latitude"),
                longitude=location.get("longitude"),
                accuracy=location.get("accuracy"),
            )
            if not validation.get("is_valid"):
                return Response(
                    {
                        "status": "error",
                        "code": "GEOFENCE_VIOLATION",
                        "message": validation.get("reason", "Location validation failed."),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        record = AttendanceService.clock_in(
            employee=employee,
            method=method,
            ip_address=request.META.get("REMOTE_ADDR"),
            location=serializer.validated_data.get("location"),
        )
        return Response(
            {
                "status": "success",
                "message": "Clock-in successful.",
                "data": AttendanceRecordSerializer(record).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CheckOutView(APIView):
    """Clock-out endpoint for the current authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.employees.models import Employee

        serializer = ClockOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            employee = Employee.objects.get(user=request.user, is_deleted=False)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "No employee profile found for current user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        today = date.today()
        record = AttendanceRecord.objects.filter(
            employee=employee, date=today, is_deleted=False,
        ).first()
        if not record or not record.clock_in:
            return Response(
                {
                    "status": "error",
                    "code": "NO_CLOCK_IN_FOUND",
                    "message": "No clock-in record found for today.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if record.clock_out:
            return Response(
                {
                    "status": "error",
                    "code": "ALREADY_CLOCKED_OUT",
                    "message": "You have already clocked out today.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        record = AttendanceService.clock_out(
            employee=employee,
            method=serializer.validated_data.get("clock_out_method", "web"),
            ip_address=request.META.get("REMOTE_ADDR"),
            location=serializer.validated_data.get("location"),
        )
        return Response(
            {
                "status": "success",
                "message": "Clock-out successful.",
                "data": AttendanceRecordSerializer(record).data,
            },
            status=status.HTTP_200_OK,
        )


class CheckStatusView(APIView):
    """Check current attendance status for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.employees.models import Employee

        try:
            employee = Employee.objects.get(user=request.user, is_deleted=False)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "No employee profile found for current user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        today = date.today()
        record = AttendanceRecord.objects.filter(
            employee=employee, date=today, is_deleted=False,
        ).first()

        if not record:
            return Response({
                "date": str(today),
                "status": "not_clocked_in",
                "record": None,
            })

        return Response({
            "date": str(today),
            "status": "clocked_out" if record.clock_out else "clocked_in",
            "record": AttendanceRecordSerializer(record).data,
        })
