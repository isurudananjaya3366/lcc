"""PayrollApprovalService for managing the payroll approval workflow."""

import logging

from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from apps.payroll.constants import HistoryAction, PayrollStatus

logger = logging.getLogger(__name__)


class PayrollApprovalService:
    """Manages submission, approval, and rejection of payroll runs."""

    # Valid status transitions for approval workflow
    VALID_TRANSITIONS = {
        PayrollStatus.PROCESSED: PayrollStatus.PENDING_APPROVAL,
        PayrollStatus.PENDING_APPROVAL: [PayrollStatus.APPROVED, PayrollStatus.REJECTED],
        PayrollStatus.REJECTED: PayrollStatus.PROCESSED,
    }

    def submit_for_approval(self, run_id, submitted_by):
        """Submit a processed payroll run for approval.

        Args:
            run_id: UUID of the PayrollRun.
            submitted_by: User submitting the run.

        Returns:
            Updated PayrollRun instance.
        """
        from apps.payroll.models import PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        run = PayrollRun.objects.get(pk=run_id)

        if run.status != PayrollStatus.PROCESSED:
            raise ValidationError(
                f"Cannot submit for approval: status is {run.status}, expected PROCESSED."
            )

        if run.error_count > 0:
            raise ValidationError(
                f"Cannot submit: payroll run has {run.error_count} processing errors."
            )

        previous_status = run.status
        run.status = PayrollStatus.PENDING_APPROVAL
        run.submitted_by = submitted_by
        run.submitted_at = timezone.now()
        run.save(update_fields=["status", "submitted_by", "submitted_at", "updated_on"])

        PayrollHistory.objects.create(
            payroll_run=run,
            action=HistoryAction.SUBMITTED,
            previous_status=previous_status,
            new_status=run.status,
            performed_by=submitted_by,
            details={
                "employee_count": run.total_employees,
                "error_count": run.error_count,
                "total_gross": str(run.total_gross),
            },
        )

        logger.info("Payroll run %s submitted for approval by %s", run_id, submitted_by)
        return run

    def approve(self, run_id, approved_by, notes=""):
        """Approve a submitted payroll run.

        Args:
            run_id: UUID of the PayrollRun.
            approved_by: User approving the run.
            notes: Optional approval notes.

        Returns:
            Updated PayrollRun instance.
        """
        from apps.payroll.models import PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        run = PayrollRun.objects.get(pk=run_id)

        if run.status != PayrollStatus.PENDING_APPROVAL:
            raise ValidationError(
                f"Cannot approve: status is {run.status}, expected PENDING_APPROVAL."
            )

        self._check_approval_permission(approved_by)

        # Prevent self-approval
        if run.submitted_by and run.submitted_by == approved_by:
            raise ValidationError(
                "Cannot approve your own submission. A different approver is required."
            )

        previous_status = run.status
        run.status = PayrollStatus.APPROVED
        run.approved_by = approved_by
        run.approved_at = timezone.now()
        if notes:
            run.notes = notes
        run.save(update_fields=["status", "approved_by", "approved_at", "notes", "updated_on"])

        PayrollHistory.objects.create(
            payroll_run=run,
            action=HistoryAction.APPROVED,
            previous_status=previous_status,
            new_status=run.status,
            performed_by=approved_by,
            details={
                "approval_notes": notes,
                "total_employees": run.total_employees,
            },
        )

        logger.info("Payroll run %s approved by %s", run_id, approved_by)
        self._send_notification(run, "approved", approved_by)
        return run

    def reject(self, run_id, rejected_by, reason):
        """Reject a submitted payroll run with a mandatory reason.

        Args:
            run_id: UUID of the PayrollRun.
            rejected_by: User rejecting the run.
            reason: Mandatory rejection reason.

        Returns:
            Updated PayrollRun instance.
        """
        from apps.payroll.models import PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        if not reason or not reason.strip():
            raise ValidationError("Rejection reason is required.")

        run = PayrollRun.objects.get(pk=run_id)

        if run.status != PayrollStatus.PENDING_APPROVAL:
            raise ValidationError(
                f"Cannot reject: status is {run.status}, expected PENDING_APPROVAL."
            )

        self._check_approval_permission(rejected_by)

        previous_status = run.status
        run.status = PayrollStatus.REJECTED
        run.rejected_by = rejected_by
        run.rejected_at = timezone.now()
        run.notes = f"Rejected: {reason}"
        run.save(update_fields=["status", "rejected_by", "rejected_at", "notes", "updated_on"])

        PayrollHistory.objects.create(
            payroll_run=run,
            action=HistoryAction.REJECTED,
            previous_status=previous_status,
            new_status=run.status,
            performed_by=rejected_by,
            reason=reason,
            details={
                "rejection_reason": reason,
            },
        )

        logger.info("Payroll run %s rejected by %s: %s", run_id, rejected_by, reason)
        self._send_notification(run, "rejected", rejected_by)
        return run

    def get_pending_approvals(self):
        """Get all payroll runs awaiting approval."""
        from apps.payroll.models import PayrollRun

        return PayrollRun.objects.filter(
            status=PayrollStatus.PENDING_APPROVAL,
        ).select_related("payroll_period").order_by("-created_on")

    def get_approval_history(self, run_id):
        """Get approval-related history entries for a payroll run."""
        from apps.payroll.models.payroll_history import PayrollHistory

        return PayrollHistory.objects.filter(
            payroll_run_id=run_id,
            action__in=[
                HistoryAction.SUBMITTED,
                HistoryAction.APPROVED,
                HistoryAction.REJECTED,
            ],
        ).order_by("-performed_at")

    def _check_approval_permission(self, user):
        """Verify user has payroll approval permission."""
        if not (user.is_staff or user.has_perm("payroll.approve_payroll")):
            raise PermissionDenied("User does not have payroll approval permission.")

    def reprocess(self, run_id, requested_by):
        """Move a rejected run back to PROCESSED for reprocessing.

        Args:
            run_id: UUID of the PayrollRun.
            requested_by: User requesting reprocessing.

        Returns:
            Updated PayrollRun instance.
        """
        from apps.payroll.models import PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        run = PayrollRun.objects.get(pk=run_id)

        if run.status != PayrollStatus.REJECTED:
            raise ValidationError(
                f"Cannot reprocess: status is {run.status}, expected REJECTED."
            )

        previous_status = run.status
        run.status = PayrollStatus.PROCESSED
        run.rejected_by = None
        run.rejected_at = None
        run.save(update_fields=["status", "rejected_by", "rejected_at", "updated_on"])

        PayrollHistory.objects.create(
            payroll_run=run,
            action=HistoryAction.CORRECTED,
            previous_status=previous_status,
            new_status=run.status,
            performed_by=requested_by,
            details={"action": "reprocess_after_rejection"},
        )

        logger.info("Payroll run %s moved back to PROCESSED by %s", run_id, requested_by)
        return run

    def _send_notification(self, run, action, performed_by):
        """Send notification email for approval workflow events.

        Stub implementation — logs the event. Full email integration
        can be connected to Django's send_mail or a notification service.
        """
        logger.info(
            "Notification: Payroll run %s %s by %s (period: %s)",
            run.pk, action, performed_by, run.payroll_period,
        )
