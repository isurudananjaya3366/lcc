"""
General Ledger report generator.

Shows detailed transaction-level data with running balances
for individual accounts or ranges of accounts.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.db.models import Q, Sum

from apps.accounting.constants import ACCOUNT_TYPE_ASSET, ACCOUNT_TYPE_EXPENSE
from apps.accounting.models.account import Account
from apps.accounting.models.enums import JournalEntryStatus
from apps.accounting.models.journal_line import JournalEntryLine
from apps.accounting.reports.base import BaseReportGenerator
from apps.accounting.reports.enums import ReportType


class GeneralLedgerGenerator(BaseReportGenerator):
    """Generates General Ledger reports with transaction details."""

    report_type = ReportType.GENERAL_LEDGER

    def __init__(self, config, account_code=None, code_from=None, code_to=None):
        """
        Initialize with optional account filtering.

        Args:
            config: ReportConfig instance.
            account_code: Single account code to filter.
            code_from: Start of account code range.
            code_to: End of account code range.
        """
        super().__init__(config)
        self._account_code = account_code
        self._code_from = code_from
        self._code_to = code_to

    # ── Data Retrieval ──────────────────────────────────────────────

    def get_data(self) -> Dict[str, Any]:
        """Retrieve general ledger data with transaction details."""
        start_date, end_date = self._get_date_range()
        accounts = self._get_filtered_accounts()

        account_ledgers = []
        total_debits = Decimal("0")
        total_credits = Decimal("0")
        total_transactions = 0

        for account in accounts:
            ledger = self._build_account_ledger(account, start_date, end_date)
            if ledger["transactions"] or self._config.include_zero_balances:
                account_ledgers.append(ledger)
                total_debits += ledger["total_debits"]
                total_credits += ledger["total_credits"]
                total_transactions += ledger["transaction_count"]

        return {
            "start_date": str(start_date or ""),
            "end_date": str(end_date or ""),
            "accounts": account_ledgers,
            "summary": {
                "total_accounts": len(account_ledgers),
                "total_transactions": total_transactions,
                "total_debit_movements": total_debits,
                "total_credit_movements": total_credits,
                "balanced": total_debits == total_credits,
            },
        }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format general ledger data into report structure."""
        result = {
            "title": "General Ledger",
            "report_type": ReportType.GENERAL_LEDGER,
            "period": {
                "start_date": data["start_date"],
                "end_date": data["end_date"],
            },
            "filter": self._get_filter_description(),
            "accounts": data["accounts"],
            "summary": data["summary"],
            "display_options": {
                "detail_level": self._config.detail_level,
            },
        }
        # Pass through comparison and variance data if present
        if "comparison" in data:
            result["comparison"] = data["comparison"]
        if "variances" in data:
            result["variances"] = data["variances"]
        return result

    # ── Account Filtering ──────────────────────────────────────────

    def _get_filtered_accounts(self) -> List:
        """Get accounts based on filter criteria."""
        qs = Account.objects.filter(
            is_active=True,
            is_header=False,
        ).order_by("code")

        if self._account_code:
            qs = qs.filter(code=self._account_code)
        elif self._code_from and self._code_to:
            qs = qs.filter(code__gte=self._code_from, code__lte=self._code_to)
        elif self._code_from:
            qs = qs.filter(code__gte=self._code_from)
        elif self._code_to:
            qs = qs.filter(code__lte=self._code_to)

        return list(qs)

    def _get_filter_description(self) -> str:
        """Describe the current filter for display."""
        if self._account_code:
            return f"Account: {self._account_code}"
        if self._code_from and self._code_to:
            return f"Range: {self._code_from} – {self._code_to}"
        return "All Accounts"

    # ── Ledger Building ─────────────────────────────────────────────

    def _build_account_ledger(
        self, account: Account, start_date, end_date,
    ) -> Dict[str, Any]:
        """Build complete ledger entry for a single account."""
        is_debit_normal = account.account_type in (
            ACCOUNT_TYPE_ASSET, ACCOUNT_TYPE_EXPENSE,
        )
        normal_side = "debit" if is_debit_normal else "credit"

        opening = self._calculate_opening_balance(
            account, start_date, is_debit_normal,
        )

        transactions = self._get_transactions(account, start_date, end_date)
        total_debits = Decimal("0")
        total_credits = Decimal("0")
        running_balance = opening

        for txn in transactions:
            dr = txn["debit_amount"]
            cr = txn["credit_amount"]
            total_debits += dr
            total_credits += cr

            if is_debit_normal:
                running_balance = running_balance + dr - cr
            else:
                running_balance = running_balance + cr - dr

            txn["running_balance"] = running_balance

        closing = running_balance

        return {
            "account_code": account.code,
            "account_name": account.name,
            "account_type": account.account_type,
            "normal_balance": normal_side,
            "opening_balance": opening,
            "opening_balance_type": "Dr" if opening >= 0 else "Cr",
            "closing_balance": closing,
            "closing_balance_type": "Dr" if closing >= 0 else "Cr",
            "transactions": transactions,
            "transaction_count": len(transactions),
            "total_debits": total_debits,
            "total_credits": total_credits,
        }

    def _calculate_opening_balance(
        self, account: Account, start_date, is_debit_normal: bool,
    ) -> Decimal:
        """Calculate account balance before start_date."""
        if not start_date:
            return Decimal("0")

        totals = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__entry_date__lt=start_date,
            journal_entry__entry_status=JournalEntryStatus.POSTED,
        ).aggregate(
            dr=Sum("debit_amount"),
            cr=Sum("credit_amount"),
        )
        dr = totals["dr"] or Decimal("0")
        cr = totals["cr"] or Decimal("0")

        if is_debit_normal:
            return dr - cr
        return cr - dr

    def _get_transactions(
        self, account: Account, start_date, end_date,
    ) -> List[Dict[str, Any]]:
        """Get chronological transaction details for an account."""
        filters = Q(
            account=account,
            journal_entry__entry_status=JournalEntryStatus.POSTED,
        )
        if start_date:
            filters &= Q(journal_entry__entry_date__gte=start_date)
        if end_date:
            filters &= Q(journal_entry__entry_date__lte=end_date)

        lines = (
            JournalEntryLine.objects.filter(filters)
            .select_related("journal_entry")
            .order_by(
                "journal_entry__entry_date",
                "journal_entry__entry_number",
            )
        )

        return [
            {
                "date": str(line.journal_entry.entry_date),
                "entry_number": line.journal_entry.entry_number,
                "description": line.description or "",
                "debit_amount": line.debit_amount or Decimal("0"),
                "credit_amount": line.credit_amount or Decimal("0"),
                "running_balance": Decimal("0"),  # filled in later
            }
            for line in lines
        ]
