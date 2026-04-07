import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.attendance.constants import (
    OVERTIME_STATUS_APPROVED,
    OVERTIME_STATUS_PENDING,
    OVERTIME_STATUS_REJECTED,
)

logger = logging.getLogger(__name__)


class OvertimeService:
    """Service for overtime detection, calculation, and request management."""

    @classmethod
    def detect_overtime(cls, attendance_record):
        """Detect if an attendance record qualifies for overtime.

        Returns hours of overtime (Decimal), or 0 if none.
        """
        if not attendance_record.shift:
            return Decimal("0")

        ot_threshold = float(attendance_record.shift.overtime_start_after)
        effective = float(attendance_record.effective_hours)

        if effective > ot_threshold:
            return Decimal(str(round(effective - ot_threshold, 2)))
        return Decimal("0")

    @classmethod
    def calculate_overtime(cls, record, shift=None, multiplier=None):
        """Calculate overtime hours and pay equivalent.

        Returns dict with hours, multiplier, effective_hours.
        """
        shift = shift or record.shift
        if not shift:
            return {"hours": Decimal("0"), "multiplier": Decimal("1"), "effective_hours": Decimal("0")}

        ot_hours = cls.detect_overtime(record)
        ot_multiplier = multiplier or shift.overtime_multiplier

        return {
            "hours": ot_hours,
            "multiplier": ot_multiplier,
            "effective_hours": Decimal(str(round(float(ot_hours) * float(ot_multiplier), 2))),
        }

    @classmethod
    def get_overtime_hours(cls, employee, start_date, end_date):
        """Get total overtime hours for an employee in a date range."""
        from apps.attendance.models import AttendanceRecord

        records = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
            overtime_hours__gt=0,
        )
        total = sum(float(r.overtime_hours) for r in records)
        return Decimal(str(round(total, 2)))

    @classmethod
    @transaction.atomic
    def create_request(cls, employee, date, planned_hours, reason, attendance_record=None):
        """Create an overtime request."""
        from apps.attendance.models.overtime_request import OvertimeRequest

        request = OvertimeRequest.objects.create(
            employee=employee,
            attendance_record=attendance_record,
            date=date,
            planned_hours=planned_hours,
            reason=reason,
            status=OVERTIME_STATUS_PENDING,
        )
        logger.info("Overtime request created: employee=%s date=%s hours=%s", employee.pk, date, planned_hours)
        return request

    @classmethod
    @transaction.atomic
    def approve_request(cls, overtime_request, approved_by):
        """Approve an overtime request."""
        if overtime_request.status != OVERTIME_STATUS_PENDING:
            raise ValueError("Only pending requests can be approved.")

        overtime_request.status = OVERTIME_STATUS_APPROVED
        overtime_request.approved_by = approved_by
        overtime_request.approved_at = timezone.now()
        overtime_request.save()

        # If linked to an attendance record, mark overtime as approved
        if overtime_request.attendance_record:
            overtime_request.attendance_record.overtime_approved = True
            overtime_request.attendance_record.save(update_fields=["overtime_approved", "updated_on"])

        logger.info("Overtime request approved: id=%s by=%s", overtime_request.pk, approved_by)
        return overtime_request

    @classmethod
    @transaction.atomic
    def reject_request(cls, overtime_request, rejected_by, rejection_reason=""):
        """Reject an overtime request."""
        if overtime_request.status != OVERTIME_STATUS_PENDING:
            raise ValueError("Only pending requests can be rejected.")

        overtime_request.status = OVERTIME_STATUS_REJECTED
        overtime_request.approved_by = rejected_by
        overtime_request.approved_at = timezone.now()
        overtime_request.rejection_reason = rejection_reason
        overtime_request.save()

        logger.info("Overtime request rejected: id=%s by=%s", overtime_request.pk, rejected_by)
        return overtime_request

    @classmethod
    def get_pending_requests(cls, department=None):
        """Get pending overtime requests, optionally filtered by department."""
        from apps.attendance.models.overtime_request import OvertimeRequest

        qs = OvertimeRequest.objects.filter(
            status=OVERTIME_STATUS_PENDING,
            is_deleted=False,
        ).select_related("employee", "attendance_record")

        if department:
            qs = qs.filter(employee__department=department)

        return qs.order_by("created_on")

    @classmethod
    def validate_overtime_request(cls, employee, date, planned_hours):
        """Validate overtime request against settings (daily/monthly limits).

        Returns (is_valid, errors_list).
        """
        from apps.attendance.models.attendance_settings import AttendanceSettings

        errors = []
        try:
            settings = AttendanceSettings.get_for_tenant(employee.tenant_id if hasattr(employee, 'tenant_id') else None)
        except Exception:
            return True, []

        # Check daily limit
        if planned_hours and settings.max_overtime_hours_per_day:
            if Decimal(str(planned_hours)) > settings.max_overtime_hours_per_day:
                errors.append(
                    f"Planned hours ({planned_hours}) exceed daily limit "
                    f"({settings.max_overtime_hours_per_day})."
                )

        # Check monthly limit
        if settings.max_overtime_hours_per_month:
            month_start = date.replace(day=1)
            from calendar import monthrange
            _, last_day = monthrange(date.year, date.month)
            month_end = date.replace(day=last_day)
            monthly_total = cls.get_overtime_hours(employee, month_start, month_end)
            projected = monthly_total + Decimal(str(planned_hours or 0))
            if projected > settings.max_overtime_hours_per_month:
                errors.append(
                    f"Monthly overtime would be {projected}h, "
                    f"exceeds limit ({settings.max_overtime_hours_per_month}h)."
                )

        return len(errors) == 0, errors

    @classmethod
    def process_overtime(cls, attendance_record):
        """End-to-end overtime processing: detect, calculate, update record."""
        ot_hours = cls.detect_overtime(attendance_record)
        if ot_hours > 0:
            attendance_record.overtime_hours = ot_hours
            attendance_record.save(update_fields=["overtime_hours", "updated_on"])
            logger.info(
                "Overtime processed: record=%s hours=%s",
                attendance_record.pk, ot_hours,
            )
        return ot_hours

    @classmethod
    def get_overtime_summary(cls, start_date, end_date, department=None):
        """Get overtime summary statistics for a date range.

        Returns dict with total_hours, total_requests, by_status counts.
        """
        from apps.attendance.models import AttendanceRecord
        from apps.attendance.models.overtime_request import OvertimeRequest

        # Overtime hours from attendance records
        record_qs = AttendanceRecord.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
            overtime_hours__gt=0,
        )
        if department:
            record_qs = record_qs.filter(employee__department=department)

        total_hours = sum(float(r.overtime_hours) for r in record_qs)

        # Overtime requests summary
        request_qs = OvertimeRequest.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
        )
        if department:
            request_qs = request_qs.filter(employee__department=department)

        return {
            "period": {"start": start_date, "end": end_date},
            "total_overtime_hours": Decimal(str(round(total_hours, 2))),
            "total_requests": request_qs.count(),
            "pending": request_qs.filter(status=OVERTIME_STATUS_PENDING).count(),
            "approved": request_qs.filter(status=OVERTIME_STATUS_APPROVED).count(),
            "rejected": request_qs.filter(status=OVERTIME_STATUS_REJECTED).count(),
        }
