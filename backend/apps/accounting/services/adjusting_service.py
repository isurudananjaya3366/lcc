"""
Adjusting entry service for the accounting application.

Provides methods for creating GAAP/IFRS-compliant period-end
adjusting entries including accruals and deferrals.
"""

import logging
from decimal import Decimal

from django.db import transaction

from apps.accounting.models.enums import JournalEntryType, JournalSource
from apps.accounting.services.journal_service import JournalEntryService

logger = logging.getLogger(__name__)


class AdjustingServiceError(Exception):
    """Base exception for adjusting entry service errors."""


class AdjustingEntryService:
    """
    Service for creating period-end adjusting journal entries.

    Adjusting entries ensure proper revenue and expense recognition
    across accounting periods per GAAP/IFRS principles.

    Methods:
        create_accrual_entry:  Record incurred but unpaid expenses or
                               earned but unreceived revenue.
        create_deferral_entry: Recognise prepaid expenses or unearned
                               revenue in the correct period.
    """

    @staticmethod
    @transaction.atomic
    def create_accrual_entry(
        entry_date,
        expense_account,
        liability_account,
        amount,
        description="",
        created_by=None,
    ):
        """
        Create an accrual adjusting entry.

        Accrual example (expense incurred, not yet paid):
            DR Salary Expense      10,000
                CR Accrued Salaries         10,000

        Args:
            entry_date: Date of the adjustment.
            expense_account: Account to debit (expense/revenue).
            liability_account: Account to credit (liability/asset).
            amount: Decimal amount to accrue.
            description: Entry description.
            created_by: User creating the entry.

        Returns:
            The created JournalEntry instance.
        """
        if amount <= 0:
            raise AdjustingServiceError("Accrual amount must be positive.")

        lines_data = [
            {
                "account": expense_account,
                "debit_amount": Decimal(str(amount)),
                "credit_amount": Decimal("0"),
                "description": description or "Accrual — debit",
            },
            {
                "account": liability_account,
                "debit_amount": Decimal("0"),
                "credit_amount": Decimal(str(amount)),
                "description": description or "Accrual — credit",
            },
        ]

        entry = JournalEntryService.create_entry(
            entry_date=entry_date,
            lines_data=lines_data,
            description=description or "Accrual adjusting entry",
            entry_type=JournalEntryType.ADJUSTING,
            entry_source=JournalSource.ADJUSTMENT,
            created_by=created_by,
        )

        logger.info("Created accrual entry %s for %s", entry.entry_number, amount)
        return entry

    @staticmethod
    @transaction.atomic
    def create_deferral_entry(
        entry_date,
        deferred_account,
        recognised_account,
        amount,
        description="",
        created_by=None,
    ):
        """
        Create a deferral adjusting entry.

        Deferral example (prepaid expense recognition):
            DR Insurance Expense   5,000
                CR Prepaid Insurance        5,000

        Args:
            entry_date: Date of the adjustment.
            deferred_account: Account to debit (expense being recognised).
            recognised_account: Account to credit (prepaid/unearned).
            amount: Decimal amount to recognise.
            description: Entry description.
            created_by: User creating the entry.

        Returns:
            The created JournalEntry instance.
        """
        if amount <= 0:
            raise AdjustingServiceError("Deferral amount must be positive.")

        lines_data = [
            {
                "account": deferred_account,
                "debit_amount": Decimal(str(amount)),
                "credit_amount": Decimal("0"),
                "description": description or "Deferral — debit",
            },
            {
                "account": recognised_account,
                "debit_amount": Decimal("0"),
                "credit_amount": Decimal(str(amount)),
                "description": description or "Deferral — credit",
            },
        ]

        entry = JournalEntryService.create_entry(
            entry_date=entry_date,
            lines_data=lines_data,
            description=description or "Deferral adjusting entry",
            entry_type=JournalEntryType.ADJUSTING,
            entry_source=JournalSource.ADJUSTMENT,
            created_by=created_by,
        )

        logger.info("Created deferral entry %s for %s", entry.entry_number, amount)
        return entry
