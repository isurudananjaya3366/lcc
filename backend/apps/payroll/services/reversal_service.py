"""PayrollReversalService for reversing and correcting finalized payroll runs."""

import logging
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.payroll.constants import HistoryAction, PayrollStatus

logger = logging.getLogger(__name__)


class PayrollReversalService:
    """Handles reversal of finalized payroll runs and creation of correction runs."""

    @transaction.atomic
    def reverse(self, run_id, reversed_by, reason):
        """Reverse a finalized payroll run.

        Args:
            run_id: UUID of the PayrollRun.
            reversed_by: User performing the reversal.
            reason: Mandatory reversal reason.

        Returns:
            Reversed PayrollRun instance.
        """
        from apps.payroll.models import PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        if not reason or not reason.strip():
            raise ValidationError("Reversal reason is required.")

        self._check_reversal_permission(reversed_by)

        run = PayrollRun.objects.select_related("payroll_period").get(pk=run_id)

        if run.status != PayrollStatus.FINALIZED:
            raise ValidationError(
                f"Cannot reverse: status is {run.status}, expected FINALIZED."
            )

        previous_status = run.status

        # Mark employee payroll records as reversed
        from apps.payroll.models import EmployeePayroll
        EmployeePayroll.objects.filter(payroll_run=run).update(
            is_reversed=True, is_locked=False
        )

        # Unlock the period
        period = run.payroll_period
        period.is_locked = False
        period.save(update_fields=["is_locked", "updated_on"])

        # Update run status and tracking
        run.status = PayrollStatus.REVERSED
        run.reversed_by = reversed_by
        run.reversed_at = timezone.now()
        run.notes = f"Reversed: {reason}"
        run.save(update_fields=[
            "status", "reversed_by", "reversed_at", "notes", "updated_on",
        ])

        PayrollHistory.objects.create(
            payroll_run=run,
            action=HistoryAction.REVERSED,
            previous_status=previous_status,
            new_status=run.status,
            performed_by=reversed_by,
            reason=reason,
            details={
                "reversal_reason": reason,
                "original_status": previous_status,
                "period_unlocked": True,
            },
        )

        logger.info("Payroll run %s reversed by %s: %s", run_id, reversed_by, reason)
        self._send_notification(run, "reversed", reversed_by)
        return run

    @transaction.atomic
    def create_correction_run(self, original_run_id, corrections, created_by):
        """Create a correction run after reversal.

        Args:
            original_run_id: UUID of the original (reversed) PayrollRun.
            corrections: List of dicts with employee_id and adjustments.
            created_by: User creating the correction.

        Returns:
            New PayrollRun instance (correction run).
        """
        from apps.payroll.models import PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        original_run = PayrollRun.objects.get(pk=original_run_id)

        if original_run.status != PayrollStatus.REVERSED:
            raise ValidationError(
                f"Cannot create correction: original run status is {original_run.status}, "
                f"expected REVERSED."
            )

        # Get next run number for this period
        max_run = PayrollRun.objects.filter(
            payroll_period=original_run.payroll_period,
        ).order_by("-run_number").first()
        next_run_number = (max_run.run_number + 1) if max_run else 1

        correction_run = PayrollRun.objects.create(
            payroll_period=original_run.payroll_period,
            run_number=next_run_number,
            status=PayrollStatus.DRAFT,
            processed_by=created_by,
            notes=f"Correction run for Run #{original_run.run_number}",
        )

        # Store correction details
        correction_summary = {
            "original_run_id": str(original_run_id),
            "corrections": corrections,
            "total_adjustments": len(corrections),
        }

        PayrollHistory.objects.create(
            payroll_run=correction_run,
            action=HistoryAction.CORRECTED,
            previous_status="",
            new_status=PayrollStatus.DRAFT,
            performed_by=created_by,
            details=correction_summary,
        )

        logger.info(
            "Correction run %s created for original run %s by %s",
            correction_run.pk, original_run_id, created_by,
        )
        return correction_run

    def calculate_adjustment(self, original, corrected):
        """Calculate adjustment between original and corrected amounts.

        Args:
            original: Original amount (Decimal).
            corrected: Corrected amount (Decimal).

        Returns:
            dict with adjustment, direction, and description.
        """
        original = Decimal(str(original))
        corrected = Decimal(str(corrected))
        adjustment = corrected - original

        if adjustment > 0:
            direction = "additional"
            description = f"Additional payment of LKR {adjustment}"
        elif adjustment < 0:
            direction = "recovery"
            description = f"Recovery of LKR {abs(adjustment)}"
        else:
            direction = "no_change"
            description = "No adjustment required"

        return {
            "adjustment": adjustment,
            "direction": direction,
            "description": description,
        }

    def _check_reversal_permission(self, user):
        """Verify user has payroll reversal permission."""
        if not (user.is_staff or user.has_perm("payroll.reverse_payroll")):
            raise PermissionDenied("User does not have payroll reversal permission.")

    def _send_notification(self, run, action, performed_by):
        """Send notification email for reversal events.

        Stub implementation — logs the event.
        """
        logger.info(
            "Notification: Payroll run %s %s by %s (period: %s)",
            run.pk, action, performed_by, run.payroll_period,
        )
