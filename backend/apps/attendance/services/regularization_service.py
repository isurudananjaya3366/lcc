import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.attendance.constants import (
    REGULARIZATION_STATUS_APPROVED,
    REGULARIZATION_STATUS_PENDING,
    REGULARIZATION_STATUS_REJECTED,
)

DEFAULT_ESCALATION_DAYS = 3

logger = logging.getLogger(__name__)


class RegularizationService:
    """Service for attendance regularization workflow (Request→Approval→Apply)."""

    @classmethod
    @transaction.atomic
    def create_request(cls, attendance_record, employee, corrected_clock_in=None, corrected_clock_out=None, reason=""):
        """Create a regularization request.

        Returns:
            AttendanceRegularization instance.
        """
        from apps.attendance.models.regularization import AttendanceRegularization

        regularization = AttendanceRegularization.objects.create(
            attendance_record=attendance_record,
            employee=employee,
            original_clock_in=attendance_record.clock_in,
            original_clock_out=attendance_record.clock_out,
            corrected_clock_in=corrected_clock_in,
            corrected_clock_out=corrected_clock_out,
            reason=reason,
            status=REGULARIZATION_STATUS_PENDING,
        )
        logger.info(
            "Regularization requested: employee=%s date=%s",
            employee.pk, attendance_record.date,
        )
        return regularization

    @classmethod
    @transaction.atomic
    def approve(cls, regularization, approved_by):
        """Approve a regularization request and apply corrections."""
        if regularization.status != REGULARIZATION_STATUS_PENDING:
            raise ValueError("Only pending regularizations can be approved.")

        regularization.status = REGULARIZATION_STATUS_APPROVED
        regularization.approved_by = approved_by
        regularization.approved_at = timezone.now()
        regularization.save()

        # Apply corrections to the attendance record
        record = regularization.attendance_record
        if regularization.corrected_clock_in:
            record.clock_in = regularization.corrected_clock_in
        if regularization.corrected_clock_out:
            record.clock_out = regularization.corrected_clock_out

        record.is_regularized = True
        record.regularized_by = approved_by

        # Recalculate hours and status
        from apps.attendance.services.attendance_service import AttendanceService

        if record.clock_in and record.clock_out:
            AttendanceService.calculate_work_hours(record)
            AttendanceService.determine_status(record)

        record.save()
        logger.info(
            "Regularization approved: id=%s by=%s",
            regularization.pk, approved_by,
        )
        return regularization

    @classmethod
    @transaction.atomic
    def reject(cls, regularization, rejected_by, rejection_reason=""):
        """Reject a regularization request."""
        if regularization.status != REGULARIZATION_STATUS_PENDING:
            raise ValueError("Only pending regularizations can be rejected.")

        regularization.status = REGULARIZATION_STATUS_REJECTED
        regularization.approved_by = rejected_by
        regularization.approved_at = timezone.now()
        regularization.rejection_reason = rejection_reason
        regularization.save()

        logger.info(
            "Regularization rejected: id=%s by=%s reason=%s",
            regularization.pk, rejected_by, rejection_reason,
        )
        return regularization

    @classmethod
    def get_pending_requests(cls, department=None):
        """Get all pending regularization requests, optionally filtered by department."""
        from apps.attendance.models.regularization import AttendanceRegularization

        qs = AttendanceRegularization.objects.filter(
            status=REGULARIZATION_STATUS_PENDING,
            is_deleted=False,
        ).select_related("employee", "attendance_record")

        if department:
            qs = qs.filter(employee__department=department)

        return qs.order_by("created_on")

    @classmethod
    @transaction.atomic
    def bulk_approve(cls, regularization_ids, approved_by):
        """Approve multiple regularization requests at once.

        Returns:
            list of approved AttendanceRegularization instances.
        """
        from apps.attendance.models.regularization import AttendanceRegularization

        regularizations = AttendanceRegularization.objects.filter(
            pk__in=regularization_ids,
            status=REGULARIZATION_STATUS_PENDING,
            is_deleted=False,
        )
        approved = []
        for reg in regularizations:
            cls.approve(reg, approved_by)
            approved.append(reg)
        logger.info("Bulk approved %d regularizations by %s", len(approved), approved_by)
        return approved

    @classmethod
    @transaction.atomic
    def bulk_reject(cls, regularization_ids, rejected_by, rejection_reason=""):
        """Reject multiple regularization requests at once.

        Returns:
            list of rejected AttendanceRegularization instances.
        """
        from apps.attendance.models.regularization import AttendanceRegularization

        regularizations = AttendanceRegularization.objects.filter(
            pk__in=regularization_ids,
            status=REGULARIZATION_STATUS_PENDING,
            is_deleted=False,
        )
        rejected = []
        for reg in regularizations:
            cls.reject(reg, rejected_by, rejection_reason)
            rejected.append(reg)
        logger.info("Bulk rejected %d regularizations by %s", len(rejected), rejected_by)
        return rejected

    @classmethod
    def get_escalation_candidates(cls, days=None):
        """Get pending regularizations older than the escalation threshold.

        Args:
            days: Number of days after which a request is considered stale.
                  Defaults to DEFAULT_ESCALATION_DAYS.

        Returns:
            QuerySet of stale pending regularizations.
        """
        if days is None:
            days = DEFAULT_ESCALATION_DAYS
        from apps.attendance.models.regularization import AttendanceRegularization

        cutoff = timezone.now() - timedelta(days=days)
        return AttendanceRegularization.objects.filter(
            status=REGULARIZATION_STATUS_PENDING,
            is_deleted=False,
            created_on__lte=cutoff,
        ).select_related("employee", "attendance_record").order_by("created_on")

    @classmethod
    def escalate_stale_requests(cls, days=None):
        """Flag stale pending requests for manager attention.

        Returns:
            int: Number of escalated requests.
        """
        stale = cls.get_escalation_candidates(days=days)
        count = stale.count()
        if count:
            logger.warning(
                "Escalation: %d regularization requests pending for >%d days",
                count, days or DEFAULT_ESCALATION_DAYS,
            )
        return count
