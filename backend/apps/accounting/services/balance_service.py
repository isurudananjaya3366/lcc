"""
Account Balance Service.

Calculates and updates account balances using journal entries and
double-entry bookkeeping conventions.
"""

import logging
from decimal import ROUND_HALF_UP, Decimal

from django.db import models

from apps.accounting.models import Account
from apps.accounting.models.journal import LegacyJournalEntry

logger = logging.getLogger(__name__)

DEBIT_NORMAL_TYPES = {"asset", "expense"}
CREDIT_NORMAL_TYPES = {"liability", "equity", "revenue"}


class AccountBalanceService:
    """
    Service for account balance calculations.

    Respects normal-balance conventions:
    - Asset / Expense: balance = opening + debits − credits
    - Liability / Equity / Revenue: balance = opening + credits − debits
    """

    # ── Public API ──────────────────────────────────────────────────

    @staticmethod
    def calculate_balance(account_id, *, as_of_date=None) -> Decimal:
        """
        Calculate the current (or historical) balance for *account_id*.

        Does NOT update the stored ``current_balance`` field.

        Args:
            account_id: PK of the Account.
            as_of_date: Optional date; limits entries to those on or
                before this date.

        Returns:
            Decimal balance rounded to 2 places.
        """
        account = Account.objects.get(pk=account_id)
        opening = account.opening_balance or Decimal("0.00")

        entries = LegacyJournalEntry.objects.filter(
            account_id=account_id, status="posted"
        )
        if as_of_date is not None:
            entries = entries.filter(entry_date__lte=as_of_date)

        totals = entries.aggregate(
            total_debit=models.Sum("debit"),
            total_credit=models.Sum("credit"),
        )
        total_debit = totals["total_debit"] or Decimal("0.00")
        total_credit = totals["total_credit"] or Decimal("0.00")

        if account.account_type in DEBIT_NORMAL_TYPES:
            balance = opening + total_debit - total_credit
        else:
            balance = opening + total_credit - total_debit

        return balance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def update_balance(account_id) -> Decimal:
        """
        Recalculate and persist the ``current_balance`` for *account_id*.

        Returns the new balance.
        """
        balance = AccountBalanceService.calculate_balance(account_id)
        Account.objects.filter(pk=account_id).update(current_balance=balance)
        logger.debug("Updated balance for account %s to %s", account_id, balance)
        return balance

    @staticmethod
    def get_children_balances(account_id) -> dict:
        """
        Return a dict mapping each child account code to its balance.

        Also includes an ``aggregate`` key with the summed total.
        """
        account = Account.objects.get(pk=account_id)
        children = account.get_children()
        result: dict[str, Decimal] = {}
        aggregate = Decimal("0.00")

        for child in children:
            bal = AccountBalanceService.calculate_balance(child.pk)
            result[child.code] = bal
            aggregate += bal

        result["aggregate"] = aggregate
        return result
