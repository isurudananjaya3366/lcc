"""Unit tests for Attendance module models."""

import uuid
from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════════
# Shift Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestShiftModel:
    """Tests for the Shift model."""

    def test_create_shift(self, shift):
        assert shift.pk is not None
        assert shift.name == "Regular Day Shift"
        assert shift.shift_type == "regular"
        assert shift.status == "active"

    def test_shift_str(self, shift):
        assert shift.code in str(shift)
        assert shift.name in str(shift)

    def test_shift_spans_midnight_false(self, shift):
        assert shift.spans_midnight is False

    def test_shift_spans_midnight_true(self, tenant_context):
        from apps.attendance.models import Shift

        night_shift = Shift.objects.create(
            name="Night Shift",
            code=f"SHF-N-{uuid.uuid4().hex[:4].upper()}",
            shift_type="night",
            start_time=time(22, 0),
            end_time=time(6, 0),
        )
        assert night_shift.spans_midnight is True

    def test_shift_work_hours_auto_calculated(self, shift):
        assert shift.work_hours is not None
        assert shift.work_hours > 0

    def test_shift_break_duration_auto_calculated(self, shift):
        # 13:00 - 13:30 = 30 minutes
        assert shift.break_duration_minutes == 30

    def test_shift_total_duration(self, shift):
        # 9:00 - 17:30 = 8.5 hours
        td = shift.total_duration
        assert td == timedelta(hours=8, minutes=30)

    def test_shift_effective_work_duration(self, shift):
        # 8.5h - 30min break = 8h
        ed = shift.effective_work_duration
        assert ed == timedelta(hours=8)

    def test_shift_unique_code(self, shift, tenant_context):
        from apps.attendance.models import Shift

        with pytest.raises(ValidationError):
            Shift.objects.create(
                name="Duplicate Code Shift",
                code=shift.code,
                start_time=time(8, 0),
                end_time=time(16, 0),
            )

    def test_shift_break_validation_start_only(self, tenant_context):
        from apps.attendance.models import Shift

        with pytest.raises(ValidationError):
            Shift.objects.create(
                name="Bad Break Shift",
                code=f"SHF-B-{uuid.uuid4().hex[:4].upper()}",
                start_time=time(8, 0),
                end_time=time(16, 0),
                break_start=time(12, 0),
                break_end=None,
            )


# ═══════════════════════════════════════════════════════════════════════
# AttendanceRecord Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestAttendanceRecordModel:
    """Tests for the AttendanceRecord model."""

    def test_create_attendance_record(self, attendance_record):
        assert attendance_record.pk is not None
        assert attendance_record.date == date.today()
        assert attendance_record.status == "present"

    def test_attendance_str(self, attendance_record):
        result = str(attendance_record)
        assert "present" in result

    def test_is_clocked_in(self, attendance_record):
        assert attendance_record.is_clocked_in is True

    def test_is_complete(self, attendance_record):
        assert attendance_record.is_complete is False

    def test_is_complete_after_clock_out(self, attendance_record):
        from django.utils import timezone

        attendance_record.clock_out = timezone.now()
        attendance_record.save()
        assert attendance_record.is_complete is True

    def test_unique_employee_date(self, attendance_record, employee):
        from apps.attendance.models import AttendanceRecord

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                AttendanceRecord.objects.create(
                    employee=employee,
                    date=date.today(),
                    status="present",
                )


# ═══════════════════════════════════════════════════════════════════════
# Regularization Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestRegularizationModel:
    """Tests for the AttendanceRegularization model."""

    def test_create_regularization(self, attendance_record, employee):
        from django.utils import timezone

        from apps.attendance.models import AttendanceRegularization

        reg = AttendanceRegularization.objects.create(
            attendance_record=attendance_record,
            employee=employee,
            original_clock_in=attendance_record.clock_in,
            corrected_clock_in=timezone.now() - timedelta(hours=1),
            reason="Forgot to clock in on time.",
        )
        assert reg.pk is not None
        assert reg.is_pending is True
        assert reg.is_approved is False
        assert reg.is_rejected is False
        assert reg.status == "pending"

    def test_regularization_str(self, attendance_record, employee):
        from apps.attendance.models import AttendanceRegularization

        reg = AttendanceRegularization.objects.create(
            attendance_record=attendance_record,
            employee=employee,
            reason="Test",
        )
        result = str(reg)
        assert "pending" in result


# ═══════════════════════════════════════════════════════════════════════
# OvertimeRequest Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestOvertimeRequestModel:
    """Tests for the OvertimeRequest model."""

    def test_create_overtime_request(self, employee):
        from apps.attendance.models import OvertimeRequest

        ot = OvertimeRequest.objects.create(
            employee=employee,
            date=date.today(),
            planned_hours=Decimal("2.00"),
            reason="Project deadline.",
        )
        assert ot.pk is not None
        assert ot.status == "pending"
        assert ot.planned_hours == Decimal("2.00")

    def test_overtime_request_str(self, employee):
        from apps.attendance.models import OvertimeRequest

        ot = OvertimeRequest.objects.create(
            employee=employee,
            date=date.today(),
            planned_hours=Decimal("3.00"),
            reason="Urgent client work.",
        )
        result = str(ot)
        assert "3.00" in result


# ═══════════════════════════════════════════════════════════════════════
# AttendanceSettings Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestAttendanceSettingsModel:
    """Tests for the AttendanceSettings model."""

    def test_create_settings(self, setup_test_tenant):
        from apps.attendance.models import AttendanceSettings

        settings = AttendanceSettings.objects.create(
            tenant_id=setup_test_tenant.pk,
            default_late_grace_minutes=15,
        )
        assert settings.pk is not None
        assert settings.default_late_grace_minutes == 15

    def test_get_for_tenant(self, setup_test_tenant):
        from apps.attendance.models import AttendanceSettings

        # Clean up any existing settings first
        AttendanceSettings.objects.filter(tenant_id=setup_test_tenant.pk).delete()
        settings = AttendanceSettings.get_for_tenant(setup_test_tenant)
        assert settings is not None
        assert settings.tenant_id == setup_test_tenant.pk
