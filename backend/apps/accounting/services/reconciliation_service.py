"""
Reconciliation service for bank reconciliation workflow.

Orchestrates the full reconciliation lifecycle: start, auto-match,
manual match/unmatch, complete, and cancel.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.accounting.models.enums import (
    JournalEntryStatus,
    MatchStatus,
    MatchType,
    ReconciliationStatus,
)

logger = logging.getLogger(__name__)


class ReconciliationError(Exception):
    """Base error for reconciliation operations."""


class ReconciliationStatusError(ReconciliationError):
    """Raised when reconciliation status prevents the operation."""


class ReconciliationService:
    """
    Manages the complete bank reconciliation workflow.

    Usage::

        svc = ReconciliationService()
        recon = svc.start_reconciliation(bank_account, statement, user)
        stats = svc.run_auto_matching(recon)
        svc.match_transactions(recon, line, entry, user)
        svc.complete_reconciliation(recon, user)
    """

    # ── Lifecycle ──────────────────────────────────────────────────

    @transaction.atomic
    def start_reconciliation(self, bank_account, user, statement=None):
        """
        Create a new reconciliation session.

        If a statement is provided, period dates and statement balance
        are extracted from it. Otherwise they must be supplied later.
        """
        from apps.accounting.models.reconciliation import Reconciliation

        start_date = statement.start_date if statement else timezone.now().date()
        end_date = statement.end_date if statement else timezone.now().date()
        statement_balance = (
            statement.closing_balance if statement else Decimal("0.00")
        )
        book_balance = self._get_book_balance_for_period(bank_account, end_date)

        recon = Reconciliation(
            bank_account=bank_account,
            bank_statement=statement,
            start_date=start_date,
            end_date=end_date,
            statement_balance=statement_balance,
            book_balance=book_balance,
            difference=statement_balance - book_balance,
            status=ReconciliationStatus.IN_PROGRESS,
            created_by=user,
        )
        recon.save()

        logger.info(
            "Started reconciliation %s for %s (%s – %s)",
            recon.pk, bank_account, start_date, end_date,
        )
        return recon

    @transaction.atomic
    def run_auto_matching(self, reconciliation):
        """
        Execute automatic matching via MatchingEngine.

        Returns dict with match counts.
        """
        from apps.accounting.models.reconciliation_item import ReconciliationItem
        from apps.accounting.services.matching_engine import MatchingEngine

        self._validate_reconciliation_active(reconciliation)

        engine = MatchingEngine(reconciliation.bank_account)
        statement_id = (
            reconciliation.bank_statement_id
            if reconciliation.bank_statement_id
            else None
        )
        stats = engine.auto_match_batch(statement_id=statement_id)

        # Create ReconciliationItems for newly matched lines
        from apps.accounting.models.statement_line import StatementLine

        matched_lines = StatementLine.objects.filter(
            statement__bank_account=reconciliation.bank_account,
            match_status=MatchStatus.MATCHED,
            matched_entry__isnull=False,
        )
        if statement_id:
            matched_lines = matched_lines.filter(statement_id=statement_id)

        items_created = 0
        for line in matched_lines:
            if not ReconciliationItem.objects.filter(
                reconciliation=reconciliation,
                statement_line=line,
            ).exists():
                ReconciliationItem.objects.create(
                    reconciliation=reconciliation,
                    statement_line=line,
                    journal_entry=line.matched_entry,
                    match_type=MatchType.AUTO,
                )
                items_created += 1

        self.calculate_difference(reconciliation)

        stats["reconciliation_items_created"] = items_created
        return stats

    @transaction.atomic
    def match_transactions(self, reconciliation, statement_line,
                           journal_entry, user, notes=""):
        """Manually match a statement line to a journal entry."""
        from apps.accounting.models.reconciliation_item import ReconciliationItem

        self._validate_reconciliation_active(reconciliation)

        # Mark statement line
        statement_line.matched_entry = journal_entry
        statement_line.match_status = MatchStatus.MATCHED
        statement_line.save(
            update_fields=["matched_entry", "match_status", "updated_at"]
        )

        item = ReconciliationItem.objects.create(
            reconciliation=reconciliation,
            statement_line=statement_line,
            journal_entry=journal_entry,
            match_type=MatchType.MANUAL,
            matched_by=user,
            notes=notes,
        )

        self.calculate_difference(reconciliation)
        return item

    @transaction.atomic
    def unmatch_transaction(self, reconciliation_item):
        """Remove a match and reset the statement line."""
        recon = reconciliation_item.reconciliation
        self._validate_reconciliation_active(recon)

        # Reset statement line
        line = reconciliation_item.statement_line
        line.matched_entry = None
        line.match_status = MatchStatus.UNMATCHED
        line.save(update_fields=["matched_entry", "match_status", "updated_at"])

        reconciliation_item.delete()
        self.calculate_difference(recon)

    @transaction.atomic
    def complete_reconciliation(self, reconciliation, user,
                                force_complete=False):
        """Finalise a reconciliation session."""
        self._validate_reconciliation_active(reconciliation)

        if not force_complete and reconciliation.difference != Decimal("0.00"):
            raise ReconciliationError(
                f"Cannot complete: difference is {reconciliation.difference}. "
                "Use force_complete=True to override."
            )

        reconciliation.status = ReconciliationStatus.COMPLETED
        reconciliation.completed_at = timezone.now()
        reconciliation.completed_by = user
        reconciliation.save(
            update_fields=[
                "status", "completed_at", "completed_by", "updated_at",
            ]
        )

        # Mark statement lines as reconciled
        from apps.accounting.models.statement_line import StatementLine

        StatementLine.objects.filter(
            reconciliation_items__reconciliation=reconciliation,
        ).update(is_reconciled=True)

        # Update bank account reconciliation tracking
        ba = reconciliation.bank_account
        ba.last_reconciled_date = reconciliation.end_date
        ba.last_reconciled_balance = reconciliation.statement_balance
        ba.save(update_fields=[
            "last_reconciled_date", "last_reconciled_balance", "updated_at",
        ])

        logger.info("Completed reconciliation %s", reconciliation.pk)
        return reconciliation

    @transaction.atomic
    def cancel_reconciliation(self, reconciliation, user):
        """Cancel an in-progress reconciliation."""
        self._validate_reconciliation_active(reconciliation)

        reconciliation.status = ReconciliationStatus.CANCELLED
        reconciliation.save(update_fields=["status", "updated_at"])

        logger.info("Cancelled reconciliation %s by %s", reconciliation.pk, user)
        return reconciliation

    @transaction.atomic
    def create_adjustment(self, reconciliation, adjustment_amount,
                          adjustment_type, adjustment_reason, user):
        """
        Create an adjusting journal entry within a reconciliation.

        Args:
            adjustment_amount: Positive decimal amount.
            adjustment_type: 'DEBIT' or 'CREDIT'.
            adjustment_reason: Explanation (min 10 chars).
            user: User creating the adjustment.

        Returns:
            ReconciliationAdjustment instance.
        """
        from apps.accounting.models.reconciliation_adjustment import (
            ReconciliationAdjustment,
        )

        self._validate_reconciliation_active(reconciliation)

        if adjustment_amount <= 0:
            raise ReconciliationError("Adjustment amount must be positive.")
        if len((adjustment_reason or "").strip()) < 10:
            raise ReconciliationError(
                "Adjustment reason must be at least 10 characters."
            )

        adj = ReconciliationAdjustment.objects.create(
            reconciliation=reconciliation,
            adjustment_type=adjustment_type,
            adjustment_amount=adjustment_amount,
            adjustment_reason=adjustment_reason,
            created_by=user,
        )

        self.calculate_difference(reconciliation)
        logger.info(
            "Created %s adjustment of %s for reconciliation %s",
            adjustment_type, adjustment_amount, reconciliation.pk,
        )
        return adj

    # ── Queries ────────────────────────────────────────────────────

    def get_unmatched_statement_lines(self, reconciliation):
        from apps.accounting.models.statement_line import StatementLine

        qs = StatementLine.objects.filter(
            statement__bank_account=reconciliation.bank_account,
            match_status=MatchStatus.UNMATCHED,
        )
        if reconciliation.bank_statement_id:
            qs = qs.filter(statement_id=reconciliation.bank_statement_id)
        return qs.order_by("transaction_date", "line_number")

    def get_unmatched_journal_entries(self, reconciliation):
        from apps.accounting.models.journal_entry import JournalEntry

        gl_account = reconciliation.bank_account.gl_account
        return (
            JournalEntry.objects.filter(
                entry_status=JournalEntryStatus.POSTED,
                lines__account=gl_account,
                entry_date__range=[
                    reconciliation.start_date,
                    reconciliation.end_date,
                ],
            )
            .distinct()
            .exclude(reconciliation_items__reconciliation=reconciliation)
            .order_by("entry_date")
        )

    def get_reconciliation_summary(self, reconciliation):
        from apps.accounting.models.reconciliation_item import ReconciliationItem

        total_stmt = self.get_unmatched_statement_lines(reconciliation).count()
        total_je = self.get_unmatched_journal_entries(reconciliation).count()

        items = ReconciliationItem.objects.filter(
            reconciliation=reconciliation,
        )
        matched_count = items.count()
        auto_count = items.filter(match_type=MatchType.AUTO).count()

        return {
            "total_statement_lines": total_stmt + matched_count,
            "total_journal_entries": total_je + matched_count,
            "matched_count": matched_count,
            "unmatched_statement_count": total_stmt,
            "unmatched_journal_count": total_je,
            "difference": reconciliation.difference,
            "status": reconciliation.status,
            "auto_match_percentage": (
                (auto_count / matched_count * 100) if matched_count else 0.0
            ),
        }

    # ── Calculations ───────────────────────────────────────────────

    @transaction.atomic
    def calculate_difference(self, reconciliation):
        """Recalculate and persist the balance difference."""
        book_balance = self._get_book_balance_for_period(
            reconciliation.bank_account,
            reconciliation.end_date,
        )
        reconciliation.book_balance = book_balance
        reconciliation.difference = (
            reconciliation.statement_balance - book_balance
        )
        reconciliation.save(
            update_fields=["book_balance", "difference", "updated_at"]
        )
        return reconciliation.difference

    def _get_book_balance_for_period(self, bank_account, period_end):
        """Calculate GL account balance through period_end."""
        from apps.accounting.models.journal_line import JournalEntryLine

        gl_account = bank_account.gl_account
        agg = (
            JournalEntryLine.objects.filter(
                account=gl_account,
                journal_entry__entry_status=JournalEntryStatus.POSTED,
                journal_entry__entry_date__lte=period_end,
            )
            .aggregate(
                total_debit=Sum("debit_amount"),
                total_credit=Sum("credit_amount"),
            )
        )
        total_debit = agg["total_debit"] or Decimal("0.00")
        total_credit = agg["total_credit"] or Decimal("0.00")
        return total_debit - total_credit

    # ── Validation ─────────────────────────────────────────────────

    @staticmethod
    def _validate_reconciliation_active(reconciliation):
        if reconciliation.status != ReconciliationStatus.IN_PROGRESS:
            raise ReconciliationStatusError(
                f"Cannot modify reconciliation with status "
                f"'{reconciliation.get_status_display()}'."
            )
