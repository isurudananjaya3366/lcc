"""
Approval service for the accounting application.

Provides a workflow for journal entry approval with configurable
threshold-based auto-approval and manual review methods.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.accounting.models.enums import JournalEntryStatus

logger = logging.getLogger(__name__)

# Default threshold — entries below this amount are auto-approved.
DEFAULT_AUTO_APPROVE_THRESHOLD = Decimal("10000.00")


class ApprovalServiceError(Exception):
    """Base exception for approval service errors."""


class ApprovalService:
    """
    Service for journal entry approval workflow.

    Workflow:
        DRAFT → PENDING_APPROVAL → APPROVED → (ready to post)
        DRAFT → PENDING_APPROVAL → DRAFT (rejected, returned)

    Below the auto-approve threshold, entries skip PENDING_APPROVAL
    and move directly to APPROVED.
    """

    def __init__(self, auto_approve_threshold=None):
        self.auto_approve_threshold = (
            auto_approve_threshold
            if auto_approve_threshold is not None
            else DEFAULT_AUTO_APPROVE_THRESHOLD
        )

    @transaction.atomic
    def request_approval(self, entry, requested_by=None):
        """
        Submit a draft entry for approval.

        If the entry total is below the auto-approve threshold the
        entry is automatically approved. Otherwise it moves to
        PENDING_APPROVAL.

        Args:
            entry: JournalEntry instance (must be DRAFT).
            requested_by: User requesting approval.

        Returns:
            The updated JournalEntry instance.
        """
        if entry.entry_status != JournalEntryStatus.DRAFT:
            raise ApprovalServiceError(
                f"Entry {entry.entry_number} is {entry.get_entry_status_display()} "
                f"— only DRAFT entries can be submitted for approval."
            )

        if not entry.is_balanced:
            raise ApprovalServiceError(
                f"Entry {entry.entry_number} is not balanced "
                f"(debit={entry.total_debit}, credit={entry.total_credit})."
            )

        if entry.total_debit <= self.auto_approve_threshold:
            entry.entry_status = JournalEntryStatus.APPROVED
            entry.save()
            logger.info(
                "Auto-approved entry %s (amount %s <= threshold %s)",
                entry.entry_number,
                entry.total_debit,
                self.auto_approve_threshold,
            )
        else:
            entry.entry_status = JournalEntryStatus.PENDING_APPROVAL
            entry.save()
            logger.info(
                "Entry %s submitted for approval (amount %s > threshold %s)",
                entry.entry_number,
                entry.total_debit,
                self.auto_approve_threshold,
            )

        return entry

    @transaction.atomic
    def approve_entry(self, entry, approved_by=None):
        """
        Approve a pending entry.

        Args:
            entry: JournalEntry instance (must be PENDING_APPROVAL).
            approved_by: User approving the entry.

        Returns:
            The approved JournalEntry instance.
        """
        if entry.entry_status != JournalEntryStatus.PENDING_APPROVAL:
            raise ApprovalServiceError(
                f"Entry {entry.entry_number} is {entry.get_entry_status_display()} "
                f"— only PENDING_APPROVAL entries can be approved."
            )

        # Segregation of duties: approver must differ from creator
        if (
            approved_by
            and entry.created_by
            and approved_by.pk == entry.created_by.pk
        ):
            raise ApprovalServiceError(
                "The approver cannot be the same user who created the entry."
            )

        entry.entry_status = JournalEntryStatus.APPROVED
        entry.save()

        logger.info(
            "Entry %s approved by %s",
            entry.entry_number,
            approved_by,
        )
        return entry

    @transaction.atomic
    def reject_entry(self, entry, rejected_by=None, reason=""):
        """
        Reject a pending entry, returning it to DRAFT.

        Args:
            entry: JournalEntry instance (must be PENDING_APPROVAL).
            rejected_by: User rejecting the entry.
            reason: Rejection reason.

        Returns:
            The rejected JournalEntry instance (status = DRAFT).
        """
        if entry.entry_status != JournalEntryStatus.PENDING_APPROVAL:
            raise ApprovalServiceError(
                f"Entry {entry.entry_number} is {entry.get_entry_status_display()} "
                f"— only PENDING_APPROVAL entries can be rejected."
            )

        entry.entry_status = JournalEntryStatus.DRAFT
        entry.save()

        logger.info(
            "Entry %s rejected by %s — reason: %s",
            entry.entry_number,
            rejected_by,
            reason or "(none)",
        )
        return entry

    @staticmethod
    def get_pending_approvals():
        """Return a queryset of entries awaiting approval."""
        from apps.accounting.models.journal_entry import JournalEntry

        return JournalEntry.objects.filter(
            entry_status=JournalEntryStatus.PENDING_APPROVAL,
        ).order_by("created_at")
