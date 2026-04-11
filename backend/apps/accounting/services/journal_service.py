"""
Journal entry service for the accounting application.

Provides transactional operations for creating, updating, posting,
and voiding journal entries with full double-entry validation.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.accounting.models.enums import (
    JournalEntryStatus,
    JournalEntryType,
    JournalSource,
)
from apps.accounting.models.journal_entry import JournalEntry
from apps.accounting.models.journal_line import JournalEntryLine
from apps.accounting.validators.entry_validators import (
    validate_entry,
    validate_line_amounts,
)

logger = logging.getLogger(__name__)


class JournalEntryServiceError(Exception):
    """Base exception for journal entry service errors."""


class EntryNotEditableError(JournalEntryServiceError):
    """Raised when attempting to modify a non-draft entry."""


class EntryNotPostableError(JournalEntryServiceError):
    """Raised when attempting to post an entry that cannot be posted."""


class EntryNotVoidableError(JournalEntryServiceError):
    """Raised when attempting to void an entry that cannot be voided."""


class JournalEntryService:
    """
    Service for journal entry CRUD and workflow operations.

    Methods:
        create_entry:  Create a new journal entry with lines.
        update_entry:  Update a draft entry.
        post_entry:    Post an approved/draft entry to the general ledger.
        void_entry:    Void a posted entry by creating a reversal.
    """

    @staticmethod
    @transaction.atomic
    def create_entry(
        entry_date,
        lines_data,
        description="",
        entry_type=JournalEntryType.MANUAL,
        entry_source=JournalSource.MANUAL,
        reference=None,
        created_by=None,
    ):
        """
        Create a new journal entry with line items.

        Args:
            entry_date: Transaction date.
            lines_data: List of dicts with keys:
                account, debit_amount, credit_amount, description (opt), sort_order (opt).
            description: Entry-level memo.
            entry_type: JournalEntryType value.
            entry_source: JournalSource value.
            reference: Optional source document reference.
            created_by: User creating the entry.

        Returns:
            The created JournalEntry instance.

        Raises:
            ValidationError: If double-entry validation fails.
        """
        entry = JournalEntry(
            entry_date=entry_date,
            entry_type=entry_type,
            entry_source=entry_source,
            reference=reference or "",
            description=description,
            created_by=created_by,
        )
        entry.save()

        for idx, line_data in enumerate(lines_data):
            line = JournalEntryLine(
                journal_entry=entry,
                account=line_data["account"],
                debit_amount=line_data.get("debit_amount", Decimal("0")),
                credit_amount=line_data.get("credit_amount", Decimal("0")),
                description=line_data.get("description", ""),
                sort_order=line_data.get("sort_order", idx),
            )
            validate_line_amounts(line)
            line.save()

        _update_cached_totals(entry)
        validate_entry(entry)

        logger.info("Created journal entry %s", entry.entry_number)
        return entry

    @staticmethod
    @transaction.atomic
    def update_entry(entry, lines_data=None, **fields):
        """
        Update a draft journal entry.

        Args:
            entry: JournalEntry instance.
            lines_data: Optional new line items (replaces existing).
            **fields: Entry-level fields to update (description, reference, etc.).

        Returns:
            The updated JournalEntry instance.

        Raises:
            EntryNotEditableError: If entry is not in DRAFT status.
            ValidationError: If validation fails.
        """
        if not entry.is_editable:
            raise EntryNotEditableError(
                f"Entry {entry.entry_number} is {entry.get_entry_status_display()} "
                f"and cannot be edited."
            )

        for field, value in fields.items():
            if hasattr(entry, field) and field not in ("id", "entry_number", "entry_status"):
                setattr(entry, field, value)
        entry.save()

        if lines_data is not None:
            entry.lines.all().delete()
            for idx, line_data in enumerate(lines_data):
                line = JournalEntryLine(
                    journal_entry=entry,
                    account=line_data["account"],
                    debit_amount=line_data.get("debit_amount", Decimal("0")),
                    credit_amount=line_data.get("credit_amount", Decimal("0")),
                    description=line_data.get("description", ""),
                    sort_order=line_data.get("sort_order", idx),
                )
                validate_line_amounts(line)
                line.save()

            _update_cached_totals(entry)
            validate_entry(entry)

        logger.info("Updated journal entry %s", entry.entry_number)
        return entry

    @staticmethod
    @transaction.atomic
    def post_entry(entry, posted_by=None):
        """
        Post a journal entry to the general ledger.

        Validates the entry, updates account balances, and sets
        the entry status to POSTED.

        Args:
            entry: JournalEntry instance.
            posted_by: User posting the entry.

        Returns:
            The posted JournalEntry instance.

        Raises:
            EntryNotPostableError: If entry cannot be posted.
            ValidationError: If validation fails.
        """
        postable_statuses = {
            JournalEntryStatus.DRAFT,
            JournalEntryStatus.APPROVED,
        }
        if entry.entry_status not in postable_statuses:
            raise EntryNotPostableError(
                f"Entry {entry.entry_number} is {entry.get_entry_status_display()} "
                f"and cannot be posted."
            )

        validate_entry(entry)

        entry.entry_status = JournalEntryStatus.POSTED
        entry.posted_by = posted_by
        entry.posted_at = timezone.now()
        entry.save()

        _update_account_balances(entry)

        logger.info("Posted journal entry %s", entry.entry_number)
        return entry

    @staticmethod
    @transaction.atomic
    def void_entry(entry, voided_by=None, reason=""):
        """
        Void a posted journal entry by creating a reversal entry.

        Creates a new reversing entry with debits and credits swapped,
        and marks the original entry as VOID.

        Args:
            entry: JournalEntry instance to void.
            voided_by: User performing the void.
            reason: Reason for voiding.

        Returns:
            Tuple of (voided_entry, reversal_entry).

        Raises:
            EntryNotVoidableError: If entry cannot be voided.
        """
        if entry.entry_status != JournalEntryStatus.POSTED:
            raise EntryNotVoidableError(
                f"Entry {entry.entry_number} is {entry.get_entry_status_display()} "
                f"and cannot be voided. Only POSTED entries can be voided."
            )

        reversal = JournalEntry(
            entry_date=timezone.now().date(),
            entry_type=JournalEntryType.REVERSING,
            entry_source=entry.entry_source,
            reference=entry.reference,
            description=f"Reversal of {entry.entry_number}: {reason}".strip(),
            created_by=voided_by,
            reversal_of=entry,
        )
        reversal.save()

        for line in entry.lines.all():
            JournalEntryLine.objects.create(
                journal_entry=reversal,
                account=line.account,
                debit_amount=line.credit_amount,
                credit_amount=line.debit_amount,
                description=f"Reversal: {line.description}",
                sort_order=line.sort_order,
            )

        _update_cached_totals(reversal)

        reversal.entry_status = JournalEntryStatus.POSTED
        reversal.posted_by = voided_by
        reversal.posted_at = timezone.now()
        reversal.save()

        _update_account_balances(reversal)

        entry.entry_status = JournalEntryStatus.VOID
        entry.save()

        logger.info(
            "Voided journal entry %s, reversal %s",
            entry.entry_number,
            reversal.entry_number,
        )
        return entry, reversal


def _update_cached_totals(entry):
    """Recalculate and save the cached total_debit and total_credit."""
    from django.db.models import Sum

    totals = entry.lines.aggregate(
        total_debit=Sum("debit_amount"),
        total_credit=Sum("credit_amount"),
    )
    entry.total_debit = totals["total_debit"] or Decimal("0")
    entry.total_credit = totals["total_credit"] or Decimal("0")
    entry.save(update_fields=["total_debit", "total_credit"])


def _update_account_balances(entry):
    """Update account balances from posted entry lines."""
    for line in entry.lines.select_related("account").all():
        account = line.account
        account.recalculate_balance()
        account.save(update_fields=["current_balance"])
