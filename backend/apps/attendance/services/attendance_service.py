import logging
import math
from datetime import datetime, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.attendance.constants import (
    ATTENDANCE_STATUS_ABSENT,
    ATTENDANCE_STATUS_HALF_DAY,
    ATTENDANCE_STATUS_LATE,
    ATTENDANCE_STATUS_PRESENT,
)

logger = logging.getLogger(__name__)


class AttendanceService:
    """Main service for attendance operations: clock in/out, shift lookup, hours calculation."""

    @classmethod
    def get_current_shift(cls, employee, target_date=None):
        """Determine the applicable shift for an employee on a given date.

        Priority: 1) Individual schedule  2) Department schedule  3) Default shift
        """
        from apps.attendance.models import Shift, ShiftSchedule
        from django.db.models import Q

        if target_date is None:
            target_date = timezone.localdate()

        # 1) Individual schedule
        employee_schedules = (
            ShiftSchedule.objects.filter(
                employee=employee,
                is_active=True,
                is_deleted=False,
                effective_from__lte=target_date,
            )
            .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=target_date))
            .select_related("shift")
            .order_by("-priority")
        )

        for schedule in employee_schedules:
            if schedule.applies_on_date(target_date):
                return schedule.shift

        # 2) Department schedule
        if hasattr(employee, "department") and employee.department_id:
            dept_schedules = (
                ShiftSchedule.objects.filter(
                    department=employee.department,
                    employee__isnull=True,
                    is_active=True,
                    is_deleted=False,
                    effective_from__lte=target_date,
                )
                .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=target_date))
                .select_related("shift")
                .order_by("-priority")
            )
            for schedule in dept_schedules:
                if schedule.applies_on_date(target_date):
                    return schedule.shift

        # 3) Default shift
        default_shift = (
            Shift.objects.filter(is_default=True, is_deleted=False, status="active")
            .first()
        )
        return default_shift

    @classmethod
    @transaction.atomic
    def clock_in(cls, employee, method="web", location=None, ip_address=None):
        """Record employee clock-in.

        Returns the AttendanceRecord.
        """
        from apps.attendance.models import AttendanceRecord

        now = timezone.now()
        today = timezone.localdate()

        record, created = AttendanceRecord.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={"status": ATTENDANCE_STATUS_PRESENT},
        )

        if record.clock_in is not None:
            raise ValueError("Employee has already clocked in today.")

        shift = cls.get_current_shift(employee, today)

        record.clock_in = now
        record.clock_in_method = method
        record.shift = shift

        if location:
            record.clock_in_location = location
        if ip_address:
            record.clock_in_ip = ip_address

        # Detect lateness
        if shift:
            late_minutes = cls.detect_late(now, shift)
            record.late_minutes = late_minutes
            if late_minutes > 0:
                record.status = ATTENDANCE_STATUS_LATE

        record.save()
        logger.info(
            "Clock-in recorded: employee=%s time=%s method=%s",
            employee.pk, now, method,
        )
        return record

    @classmethod
    @transaction.atomic
    def clock_out(cls, employee, method="web", location=None, ip_address=None):
        """Record employee clock-out, calculate hours, determine status.

        Returns the AttendanceRecord.
        """
        from apps.attendance.models import AttendanceRecord

        now = timezone.now()
        today = timezone.localdate()

        try:
            record = AttendanceRecord.objects.get(employee=employee, date=today)
        except AttendanceRecord.DoesNotExist:
            raise ValueError("No clock-in record found for today.")

        if record.clock_in is None:
            raise ValueError("Employee has not clocked in today.")
        if record.clock_out is not None:
            raise ValueError("Employee has already clocked out today.")

        record.clock_out = now
        record.clock_out_method = method

        if location:
            record.clock_out_location = location
        if ip_address:
            record.clock_out_ip = ip_address

        # Detect early departure
        if record.shift:
            early_minutes = cls.detect_early_leave(now, record.shift)
            record.early_departure_minutes = early_minutes

        # Calculate work hours
        cls.calculate_work_hours(record)

        # Determine final status
        cls.determine_status(record)

        record.save()
        logger.info(
            "Clock-out recorded: employee=%s time=%s hours=%.2f",
            employee.pk, now, record.effective_hours,
        )
        return record

    @classmethod
    def detect_late(cls, clock_in_time, shift):
        """Calculate late minutes beyond the grace period.

        Returns integer minutes late (0 if on time).
        """
        shift_start_dt = datetime.combine(clock_in_time.date(), shift.start_time)
        shift_start_dt = timezone.make_aware(
            shift_start_dt, timezone.get_current_timezone()
        ) if timezone.is_naive(shift_start_dt) else shift_start_dt

        effective_start = shift_start_dt + timedelta(
            minutes=shift.late_grace_minutes
        )

        if clock_in_time > effective_start:
            delta = clock_in_time - effective_start
            return int(delta.total_seconds() / 60)
        return 0

    @classmethod
    def detect_early_leave(cls, clock_out_time, shift):
        """Calculate early departure minutes beyond the grace period.

        Returns integer minutes of early departure (0 if stayed until end).
        """
        shift_end_dt = datetime.combine(clock_out_time.date(), shift.end_time)
        # Handle shifts spanning midnight
        if shift.spans_midnight:
            shift_end_dt += timedelta(days=1)
        shift_end_dt = timezone.make_aware(
            shift_end_dt, timezone.get_current_timezone()
        ) if timezone.is_naive(shift_end_dt) else shift_end_dt

        effective_end = shift_end_dt - timedelta(
            minutes=shift.early_leave_grace_minutes
        )

        if clock_out_time < effective_end:
            delta = effective_end - clock_out_time
            return int(delta.total_seconds() / 60)
        return 0

    @classmethod
    def determine_status(cls, record):
        """Determine attendance status based on hours worked and lateness."""
        if record.clock_in is None:
            record.status = ATTENDANCE_STATUS_ABSENT
            return

        shift = record.shift
        if not shift:
            # No shift info — just mark present if clocked in
            record.status = ATTENDANCE_STATUS_PRESENT
            return

        effective = float(record.effective_hours)
        full_day = float(shift.min_hours_for_full_day)
        half_day = float(shift.min_hours_for_half_day)

        if effective >= full_day:
            if record.late_minutes > 0:
                record.status = ATTENDANCE_STATUS_LATE
            else:
                record.status = ATTENDANCE_STATUS_PRESENT
        elif effective >= half_day:
            record.status = ATTENDANCE_STATUS_HALF_DAY
        else:
            record.status = ATTENDANCE_STATUS_ABSENT

    @classmethod
    def calculate_work_hours(cls, record):
        """Calculate work_hours, break_hours, effective_hours, and overtime."""
        if not record.clock_in or not record.clock_out:
            return

        delta = record.clock_out - record.clock_in
        total_minutes = delta.total_seconds() / 60

        # Break hours from shift
        break_minutes = 0
        if record.shift and record.shift.break_duration_minutes:
            break_minutes = record.shift.break_duration_minutes

        work_minutes = total_minutes
        effective_minutes = work_minutes - break_minutes

        record.work_hours = Decimal(str(round(work_minutes / 60, 2)))
        record.break_hours = Decimal(str(round(break_minutes / 60, 2)))
        record.effective_hours = Decimal(str(round(max(effective_minutes, 0) / 60, 2)))

        # Overtime detection
        if record.shift:
            ot_threshold = float(record.shift.overtime_start_after)
            eff = float(record.effective_hours)
            if eff > ot_threshold:
                record.overtime_hours = Decimal(
                    str(round(eff - ot_threshold, 2))
                )

    @classmethod
    def get_today_record(cls, employee):
        """Get or None today's attendance record."""
        from apps.attendance.models import AttendanceRecord

        today = timezone.localdate()
        return AttendanceRecord.objects.filter(
            employee=employee, date=today
        ).first()

    @classmethod
    def get_employee_attendance(cls, employee, start_date, end_date):
        """Get attendance records for an employee in a date range."""
        from apps.attendance.models import AttendanceRecord

        return AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
        ).select_related("shift").order_by("date")
