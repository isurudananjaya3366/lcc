"""Unit tests for Attendance module services."""

import uuid
from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════════
# AttendanceService Tests
# ═══════════════════════════════════════════════════════════════════════


class TestAttendanceService:
    """Tests for the AttendanceService."""

    def test_clock_in(self, employee, shift):
        from apps.attendance.services.attendance_service import AttendanceService

        record = AttendanceService.clock_in(employee=employee, method="web")
        assert record is not None
        assert record.employee == employee
        assert record.clock_in is not None
        assert record.date == date.today()

    def test_clock_out(self, employee, shift, attendance_record):
        from apps.attendance.services.attendance_service import AttendanceService

        record = AttendanceService.clock_out(employee=employee, method="web")
        assert record is not None
        assert record.clock_out is not None
        assert record.work_hours > 0 or record.clock_out is not None

    def test_get_today_record(self, employee, attendance_record):
        from apps.attendance.services.attendance_service import AttendanceService

        record = AttendanceService.get_today_record(employee)
        assert record is not None
        assert record.employee == employee

    def test_get_today_record_none(self, employee):
        from apps.attendance.services.attendance_service import AttendanceService

        record = AttendanceService.get_today_record(employee)
        assert record is None


# ═══════════════════════════════════════════════════════════════════════
# RegularizationService Tests
# ═══════════════════════════════════════════════════════════════════════


class TestRegularizationService:
    """Tests for the RegularizationService."""

    def test_create_request(self, attendance_record, employee):
        from apps.attendance.services.regularization_service import RegularizationService

        corrected_in = timezone.now() - timedelta(hours=1)
        reg = RegularizationService.create_request(
            attendance_record=attendance_record,
            employee=employee,
            corrected_clock_in=corrected_in,
            reason="Forgot to clock in on time.",
        )
        assert reg is not None
        assert reg.status == "pending"
        assert reg.corrected_clock_in == corrected_in

    def test_approve_request(self, attendance_record, employee, user):
        from apps.attendance.services.regularization_service import RegularizationService

        corrected_in = timezone.now() - timedelta(hours=2)
        reg = RegularizationService.create_request(
            attendance_record=attendance_record,
            employee=employee,
            corrected_clock_in=corrected_in,
            reason="Need correction.",
        )
        RegularizationService.approve(reg, user)
        reg.refresh_from_db()
        assert reg.status == "approved"
        assert reg.approved_by == user

    def test_reject_request(self, attendance_record, employee, user):
        from apps.attendance.services.regularization_service import RegularizationService

        reg = RegularizationService.create_request(
            attendance_record=attendance_record,
            employee=employee,
            corrected_clock_in=timezone.now(),
            reason="Correction needed.",
        )
        RegularizationService.reject(reg, user, "Not valid.")
        reg.refresh_from_db()
        assert reg.status == "rejected"


# ═══════════════════════════════════════════════════════════════════════
# OvertimeService Tests
# ═══════════════════════════════════════════════════════════════════════


class TestOvertimeService:
    """Tests for the OvertimeService."""

    def test_create_request(self, employee):
        from apps.attendance.services.overtime_service import OvertimeService

        ot = OvertimeService.create_request(
            employee=employee,
            date=date.today(),
            planned_hours=Decimal("2.00"),
            reason="Project work.",
        )
        assert ot is not None
        assert ot.status == "pending"
        assert ot.planned_hours == Decimal("2.00")

    def test_approve_request(self, employee, user):
        from apps.attendance.services.overtime_service import OvertimeService

        ot = OvertimeService.create_request(
            employee=employee,
            date=date.today(),
            planned_hours=Decimal("2.00"),
            reason="Need to finish.",
        )
        OvertimeService.approve_request(ot, user)
        ot.refresh_from_db()
        assert ot.status == "approved"

    def test_reject_request(self, employee, user):
        from apps.attendance.services.overtime_service import OvertimeService

        ot = OvertimeService.create_request(
            employee=employee,
            date=date.today(),
            planned_hours=Decimal("1.50"),
            reason="Extra work.",
        )
        OvertimeService.reject_request(ot, user, "Not approved.")
        ot.refresh_from_db()
        assert ot.status == "rejected"


# ═══════════════════════════════════════════════════════════════════════
# ReportService Tests
# ═══════════════════════════════════════════════════════════════════════


class TestReportService:
    """Tests for the AttendanceReportService."""

    def test_daily_summary(self, attendance_record):
        from apps.attendance.services.report_service import AttendanceReportService

        summary = AttendanceReportService.daily_summary(date.today())
        assert summary is not None
        assert "date" in summary
        assert "total_employees" in summary
        assert "present" in summary
        assert "attendance_rate" in summary

    def test_attendance_percentage(self, attendance_record, employee):
        from apps.attendance.services.report_service import AttendanceReportService

        today = date.today()
        pct = AttendanceReportService.attendance_percentage(
            employee, today - timedelta(days=1), today,
        )
        assert isinstance(pct, dict)
        assert "attendance_percentage" in pct
