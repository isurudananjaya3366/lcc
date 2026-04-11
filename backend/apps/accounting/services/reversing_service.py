"""
Reversing entry service for the accounting application.

Provides methods for creating and scheduling reversing entries
that automatically reverse adjusting entries at the start of
the next accounting period.
"""

import logging
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.db import transaction

from apps.accounting.models.enums import (
    JournalEntryStatus,
    JournalEntryType,
    JournalSource,
)
from apps.accounting.models.journal_entry import JournalEntry
from apps.accounting.models.journal_line import JournalEntryLine

logger = logging.getLogger(__name__)


class ReversingServiceError(Exception):
    """Base exception for reversing entry service errors."""


class ReversingEntryService:
    """
    Service for creating and scheduling reversing journal entries.

    Reversing entries swap all debits and credits of an adjusting
    entry and are typically dated the first day of the next period.

    Methods:
        create_reversal:    Create an immediate reversal of an entry.
        schedule_reversal:  Create a reversal dated to next period start.
    """

    @staticmethod
    @transaction.atomic
    def create_reversal(entry, reversal_date=None, created_by=None):
        """
        Create a reversing entry for a posted adjusting entry.

        Swaps all debit and credit amounts and links back to the
        original via the ``reversal_of`` FK.

        Args:
            entry: JournalEntry to reverse (must be POSTED).
            reversal_date: Date for the reversal entry. Defaults to
                           the original entry_date.
            created_by: User creating the reversal.

        Returns:
            The created reversal JournalEntry instance.

        Raises:
            ReversingServiceError: If the entry cannot be reversed.
        """
        if entry.entry_status != JournalEntryStatus.POSTED:
            raise ReversingServiceError(
                f"Entry {entry.entry_number} is {entry.get_entry_status_display()} "
                f"— only POSTED entries can be reversed."
            )

        if entry.reversed_by.exists():
            raise ReversingServiceError(
                f"Entry {entry.entry_number} already has a reversal."
            )

        reversal = JournalEntry(
            entry_date=reversal_date or entry.entry_date,
            entry_type=JournalEntryType.REVERSING,
            entry_source=entry.entry_source,
            reference=entry.reference,
            description=f"Reversal of {entry.entry_number}",
            created_by=created_by,
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

        logger.info(
            "Created reversal %s for entry %s",
            reversal.entry_number,
            entry.entry_number,
        )
        return reversal

    @staticmethod
    @transaction.atomic
    def schedule_reversal(entry, created_by=None):
        """
        Create a reversal entry dated the first day of the next period.

        Determines the next period start from the original entry date
        and creates a DRAFT reversal entry on that date.

        Args:
            entry: JournalEntry to reverse (must be POSTED ADJUSTING).
            created_by: User creating the reversal.

        Returns:
            The created reversal JournalEntry instance.
        """
        if entry.entry_type != JournalEntryType.ADJUSTING:
            raise ReversingServiceError(
                f"Entry {entry.entry_number} is not an adjusting entry. "
                f"Only ADJUSTING entries can be scheduled for reversal."
            )

        # First day of the next month
        next_period_start = (entry.entry_date + relativedelta(months=1)).replace(day=1)

        reversal = ReversingEntryService.create_reversal(
            entry=entry,
            reversal_date=next_period_start,
            created_by=created_by,
        )

        logger.info(
            "Scheduled reversal %s for %s (next period: %s)",
            reversal.entry_number,
            entry.entry_number,
            next_period_start,
        )
        return reversal


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
