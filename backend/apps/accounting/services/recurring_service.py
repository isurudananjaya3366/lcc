"""
Recurring entry service for the accounting application.

Processes due recurring entries by creating journal entries from
their linked templates and advancing the schedule.
"""

import logging
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone

from apps.accounting.models.enums import RecurringFrequency
from apps.accounting.models.recurring_entry import RecurringEntry
from apps.accounting.services.journal_service import JournalEntryService
from apps.accounting.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class RecurringServiceError(Exception):
    """Base exception for recurring service errors."""


class RecurringService:
    """
    Service for processing recurring journal entries.

    Methods:
        process_due_entries:  Find and process all entries due today.
        process_single:       Process a single recurring entry.
    """

    @staticmethod
    def process_due_entries():
        """
        Find and process all active recurring entries that are due.

        Queries for entries where is_active=True and next_run_date <= today,
        creates journal entries from their templates, and advances schedules.

        Returns:
            List of created JournalEntry instances.
        """
        today = timezone.now().date()
        due_entries = RecurringEntry.objects.filter(
            is_active=True,
            next_run_date__lte=today,
        ).select_related("template", "created_by")

        created_entries = []
        for recurring in due_entries:
            try:
                entry = RecurringService.process_single(recurring, today)
                created_entries.append(entry)
            except Exception:
                logger.exception(
                    "Failed to process recurring entry %s (template: %s)",
                    recurring.pk,
                    recurring.template.name,
                )

        logger.info(
            "Processed %d/%d due recurring entries",
            len(created_entries),
            due_entries.count(),
        )
        return created_entries

    @staticmethod
    @transaction.atomic
    def process_single(recurring, run_date=None):
        """
        Process a single recurring entry.

        Creates a journal entry from the template, optionally auto-posts
        it, then advances the recurring schedule.

        Args:
            recurring: RecurringEntry instance.
            run_date: The effective date for the entry (defaults to today).

        Returns:
            The created JournalEntry instance.
        """
        run_date = run_date or timezone.now().date()

        entry = TemplateService.create_from_template(
            template=recurring.template,
            entry_date=run_date,
            description=recurring.description or None,
            created_by=recurring.created_by,
        )

        if recurring.auto_post:
            JournalEntryService.post_entry(entry, posted_by=recurring.created_by)

        # Advance schedule
        recurring.last_run_date = run_date
        recurring.next_run_date = _calculate_next_run(
            run_date, recurring.frequency
        )

        # Deactivate if past end_date
        if recurring.end_date and recurring.next_run_date > recurring.end_date:
            recurring.is_active = False
            logger.info(
                "Recurring entry %s deactivated — end_date %s reached",
                recurring.pk,
                recurring.end_date,
            )

        recurring.save()

        logger.info(
            "Processed recurring entry %s → %s (next: %s)",
            recurring.pk,
            entry.entry_number,
            recurring.next_run_date,
        )
        return entry


def _calculate_next_run(current_date, frequency):
    """
    Calculate the next run date based on frequency.

    Uses python-dateutil relativedelta for month/year arithmetic
    to handle edge cases (month-end, leap years).
    """
    if frequency == RecurringFrequency.DAILY:
        return current_date + timedelta(days=1)
    elif frequency == RecurringFrequency.WEEKLY:
        return current_date + timedelta(weeks=1)
    elif frequency == RecurringFrequency.MONTHLY:
        return current_date + relativedelta(months=1)
    elif frequency == RecurringFrequency.QUARTERLY:
        return current_date + relativedelta(months=3)
    elif frequency == RecurringFrequency.YEARLY:
        return current_date + relativedelta(years=1)
    else:
        raise RecurringServiceError(f"Unknown frequency: {frequency}")
