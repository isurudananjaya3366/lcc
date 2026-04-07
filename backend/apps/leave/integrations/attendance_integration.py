"""Attendance Integration for Leave Management.

Syncs leave approval/cancellation/recall with the attendance system,
creating or clearing ON_LEAVE attendance records.
"""

import logging
from datetime import timedelta

from django.db import transaction

from apps.leave.constants import LeaveRequestStatus
from apps.leave.models.holiday import Holiday

logger = logging.getLogger(__name__)


class AttendanceIntegration:
    """Integrates leave approvals with the attendance tracking system."""

    def __init__(self, tenant=None):
        self.tenant = tenant

    # ── Core Methods ─────────────────────────────────────────

    @transaction.atomic
    def handle_leave_approval(self, leave_request):
        """Mark attendance records as ON_LEAVE upon leave approval.

        Creates or updates AttendanceRecord for each working day
        in the leave range.

        Args:
            leave_request: Approved LeaveRequest instance.

        Returns:
            Dict with success status and days marked.
        """
        if leave_request.status != LeaveRequestStatus.APPROVED:
            logger.warning(
                "Cannot mark attendance for non-approved request %s",
                leave_request.id,
            )
            return {"success": False, "days_marked": 0, "dates": []}

        working_days = self.get_working_days_in_range(
            leave_request.start_date,
            leave_request.end_date,
            leave_request.employee,
        )

        marked_dates = []
        for day in working_days:
            self._create_or_update_attendance(
                employee=leave_request.employee,
                date=day,
                leave_request=leave_request,
                is_half_day=leave_request.is_half_day,
            )
            marked_dates.append(day.isoformat())

        logger.info(
            "Marked %d attendance records for leave %s",
            len(marked_dates),
            leave_request.id,
        )
        return {
            "success": True,
            "days_marked": len(marked_dates),
            "dates": marked_dates,
        }

    def handle_leave_rejection(self, leave_request):
        """Log rejection — no attendance changes needed."""
        logger.info(
            "Leave request %s rejected — no attendance changes.",
            leave_request.id,
        )

    @transaction.atomic
    def handle_leave_cancellation(self, leave_request):
        """Clear ON_LEAVE attendance records for cancelled/recalled leave.

        Only clears future dates; past records are preserved.

        Args:
            leave_request: Cancelled or recalled LeaveRequest instance.
        """
        from datetime import date as date_type

        today = date_type.today()

        try:
            from apps.attendance.models import AttendanceRecord

            records = AttendanceRecord.objects.filter(
                employee=leave_request.employee,
                date__gte=max(leave_request.start_date, today),
                date__lte=leave_request.end_date,
                status="ON_LEAVE",
            )
            count = records.count()
            records.update(status="PENDING")

            logger.info(
                "Cleared %d attendance records for leave %s",
                count,
                leave_request.id,
            )
        except Exception:
            logger.warning(
                "Could not clear attendance records for leave %s "
                "(attendance module may not be fully configured).",
                leave_request.id,
            )

    def sync_attendance_for_leave(self, leave_request):
        """Manual re-sync of attendance records for a leave request.

        Returns:
            Dict with sync results.
        """
        if leave_request.status == LeaveRequestStatus.APPROVED:
            return self.handle_leave_approval(leave_request)
        elif leave_request.status in (
            LeaveRequestStatus.CANCELLED,
            LeaveRequestStatus.RECALLED,
        ):
            self.handle_leave_cancellation(leave_request)
            return {"success": True, "action": "cleared"}
        return {"success": False, "action": "no_action"}

    # ── Helper Methods ───────────────────────────────────────

    def is_working_day(self, check_date, employee=None):
        """Check if a date is a working day.

        Excludes weekends (Sat/Sun) and holidays.
        """
        # Weekend check
        if check_date.weekday() in (5, 6):
            return False

        # Holiday check
        from django.db.models import Q

        holiday_q = Q(
            date=check_date,
            is_active=True,
            is_deleted=False,
            is_recurring=False,
        )
        scope_q = Q(applies_to="ALL")

        if employee and hasattr(employee, "department") and employee.department:
            scope_q |= Q(applies_to="DEPARTMENT", department=employee.department)

        if Holiday.objects.filter(holiday_q & scope_q).exists():
            return False

        return True

    def get_working_days_in_range(self, start_date, end_date, employee=None):
        """Get list of working days in a date range.

        Args:
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            employee: Optional employee for scoped holidays.

        Returns:
            List of date objects that are working days.
        """
        working_days = []
        current = start_date
        while current <= end_date:
            if self.is_working_day(current, employee):
                working_days.append(current)
            current += timedelta(days=1)
        return working_days

    def _create_or_update_attendance(
        self, employee, date, leave_request, is_half_day=False
    ):
        """Create or update an attendance record for a leave day.

        Args:
            employee: Employee instance.
            date: The date to mark.
            leave_request: Associated LeaveRequest.
            is_half_day: Whether this is a half-day leave.
        """
        status = "HALF_DAY_LEAVE" if is_half_day else "ON_LEAVE"

        try:
            from apps.attendance.models import AttendanceRecord

            AttendanceRecord.objects.update_or_create(
                employee=employee,
                date=date,
                defaults={
                    "status": status,
                },
            )
        except Exception:
            logger.warning(
                "Could not create/update attendance record for %s on %s "
                "(attendance module may not be fully configured).",
                employee.id,
                date,
            )
