"""
Cash Flow Statement report generator (Indirect Method).

Reconciles accrual-basis net income to cash by adjusting for
non-cash items and working capital changes.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.db.models import Q, Sum

from apps.accounting.constants import (
    ACCOUNT_TYPE_ASSET,
    ACCOUNT_TYPE_EQUITY,
    ACCOUNT_TYPE_EXPENSE,
    ACCOUNT_TYPE_LIABILITY,
    ACCOUNT_TYPE_REVENUE,
)
from apps.accounting.models.account import Account
from apps.accounting.models.enums import JournalEntryStatus
from apps.accounting.models.journal_line import JournalEntryLine
from apps.accounting.reports.base import BaseReportGenerator
from apps.accounting.reports.enums import ReportType

# Cash & Cash Equivalent accounts
CASH_CODE_MIN = "1001"
CASH_CODE_MAX = "1049"

# Working capital accounts (operating)
AR_CODE_MIN = "1150"
AR_CODE_MAX = "1159"
INVENTORY_CODE_MIN = "1160"
INVENTORY_CODE_MAX = "1169"
PREPAID_CODE_MIN = "1170"
PREPAID_CODE_MAX = "1189"
AP_CODE_MIN = "2100"
AP_CODE_MAX = "2199"

# Depreciation expense
DEPRECIATION_EXP_CODE_MIN = "5600"
DEPRECIATION_EXP_CODE_MAX = "5699"

# Investing accounts (fixed assets)
FIXED_ASSET_CODE_MIN = "1200"
FIXED_ASSET_CODE_MAX = "1399"

# Financing accounts
LONG_TERM_DEBT_MIN = "2200"
LONG_TERM_DEBT_MAX = "2299"
EQUITY_CODE_MIN = "3000"
EQUITY_CODE_MAX = "3999"


class CashFlowGenerator(BaseReportGenerator):
    """Generates Cash Flow Statement using the indirect method."""

    report_type = ReportType.CASH_FLOW

    # ── Data Retrieval ──────────────────────────────────────────────

    def get_data(self) -> Dict[str, Any]:
        """Retrieve cash flow data."""
        start_date, end_date = self._get_date_range()

        net_income = self._calculate_net_income(start_date, end_date)
        depreciation = self._get_depreciation_addback(start_date, end_date)
        wc_changes = self._get_working_capital_changes(start_date, end_date)

        operating_cash = (
            net_income + depreciation + wc_changes["net_change"]
        )

        investing = self._get_investing_activities(start_date, end_date)
        financing = self._get_financing_activities(start_date, end_date)

        net_cash_change = operating_cash + investing["net"] + financing["net"]

        beginning_cash = self._get_cash_balance_before(start_date)
        ending_cash = beginning_cash + net_cash_change

        return {
            "start_date": str(start_date or ""),
            "end_date": str(end_date or ""),
            "operating": {
                "net_income": net_income,
                "depreciation": depreciation,
                "working_capital_changes": wc_changes["items"],
                "net_wc_change": wc_changes["net_change"],
                "total": operating_cash,
            },
            "investing": investing,
            "financing": financing,
            "net_cash_change": net_cash_change,
            "beginning_cash": beginning_cash,
            "ending_cash": ending_cash,
        }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format cash flow data into report structure."""
        result = {
            "title": "Cash Flow Statement",
            "report_type": ReportType.CASH_FLOW,
            "period": {
                "start_date": data["start_date"],
                "end_date": data["end_date"],
            },
            "operating_activities": data["operating"],
            "investing_activities": data["investing"],
            "financing_activities": data["financing"],
            "net_cash_change": data["net_cash_change"],
            "beginning_cash": data["beginning_cash"],
            "ending_cash": data["ending_cash"],
            "display_options": {
                "detail_level": self._config.detail_level,
                "include_comparison": self._config.include_comparison,
            },
        }
        # Pass through comparison and variance data if present
        if "comparison" in data:
            result["comparison"] = data["comparison"]
        if "variances" in data:
            result["variances"] = data["variances"]
        return result

    # ── Operating Activities ────────────────────────────────────────

    def _calculate_net_income(self, start_date, end_date) -> Decimal:
        """Get net income for the period (Revenue - Expenses)."""
        filters = Q(journal_entry__entry_status=JournalEntryStatus.POSTED)
        if start_date:
            filters &= Q(journal_entry__entry_date__gte=start_date)
        if end_date:
            filters &= Q(journal_entry__entry_date__lte=end_date)

        rev = JournalEntryLine.objects.filter(
            filters,
            account__account_type=ACCOUNT_TYPE_REVENUE,
        ).aggregate(
            dr=Sum("debit_amount"), cr=Sum("credit_amount"),
        )
        total_revenue = (rev["cr"] or Decimal("0")) - (rev["dr"] or Decimal("0"))

        exp = JournalEntryLine.objects.filter(
            filters,
            account__account_type=ACCOUNT_TYPE_EXPENSE,
        ).aggregate(
            dr=Sum("debit_amount"), cr=Sum("credit_amount"),
        )
        total_expense = (exp["dr"] or Decimal("0")) - (exp["cr"] or Decimal("0"))

        return total_revenue - total_expense

    def _get_depreciation_addback(self, start_date, end_date) -> Decimal:
        """Get depreciation expense to add back (non-cash)."""
        accounts = Account.objects.filter(
            account_type=ACCOUNT_TYPE_EXPENSE,
            is_active=True,
            is_header=False,
            code__gte=DEPRECIATION_EXP_CODE_MIN,
            code__lte=DEPRECIATION_EXP_CODE_MAX,
        )
        filters = Q(
            account__in=accounts,
            journal_entry__entry_status=JournalEntryStatus.POSTED,
        )
        if start_date:
            filters &= Q(journal_entry__entry_date__gte=start_date)
        if end_date:
            filters &= Q(journal_entry__entry_date__lte=end_date)

        totals = JournalEntryLine.objects.filter(filters).aggregate(
            dr=Sum("debit_amount"), cr=Sum("credit_amount"),
        )
        return (totals["dr"] or Decimal("0")) - (totals["cr"] or Decimal("0"))

    def _get_working_capital_changes(
        self, start_date, end_date,
    ) -> Dict[str, Any]:
        """Calculate working capital changes."""
        items = []
        net = Decimal("0")

        # Current asset increases use cash (negative)
        wc_items = [
            ("Accounts Receivable", ACCOUNT_TYPE_ASSET, AR_CODE_MIN, AR_CODE_MAX, True),
            ("Inventory", ACCOUNT_TYPE_ASSET, INVENTORY_CODE_MIN, INVENTORY_CODE_MAX, True),
            ("Prepaid Expenses", ACCOUNT_TYPE_ASSET, PREPAID_CODE_MIN, PREPAID_CODE_MAX, True),
            ("Accounts Payable", ACCOUNT_TYPE_LIABILITY, AP_CODE_MIN, AP_CODE_MAX, False),
        ]

        for label, acct_type, code_min, code_max, is_asset in wc_items:
            change = self._calculate_balance_change(
                acct_type, code_min, code_max, start_date, end_date,
            )
            # For assets: increase in asset = cash used (negative for CF)
            # For liabilities: increase in liability = cash retained (positive)
            cash_impact = -change if is_asset else change
            items.append({"label": label, "change": cash_impact})
            net += cash_impact

        return {"items": items, "net_change": net}

    # ── Investing Activities ────────────────────────────────────────

    def _get_investing_activities(
        self, start_date, end_date,
    ) -> Dict[str, Any]:
        """Calculate investing cash flows from fixed asset changes."""
        change = self._calculate_balance_change(
            ACCOUNT_TYPE_ASSET, FIXED_ASSET_CODE_MIN, FIXED_ASSET_CODE_MAX,
            start_date, end_date,
        )
        # Increase in fixed assets = cash spent (negative)
        items = [{"label": "Property, Plant & Equipment", "change": -change}]
        return {"items": items, "net": -change}

    # ── Financing Activities ────────────────────────────────────────

    def _get_financing_activities(
        self, start_date, end_date,
    ) -> Dict[str, Any]:
        """Calculate financing cash flows."""
        items = []
        net = Decimal("0")

        # Long-term debt changes
        debt_change = self._calculate_balance_change(
            ACCOUNT_TYPE_LIABILITY, LONG_TERM_DEBT_MIN, LONG_TERM_DEBT_MAX,
            start_date, end_date,
        )
        items.append({"label": "Long-term Borrowings", "change": debt_change})
        net += debt_change

        # Equity changes
        equity_change = self._calculate_balance_change(
            ACCOUNT_TYPE_EQUITY, EQUITY_CODE_MIN, EQUITY_CODE_MAX,
            start_date, end_date,
        )
        items.append({"label": "Equity Changes", "change": equity_change})
        net += equity_change

        return {"items": items, "net": net}

    # ── Cash Balance ────────────────────────────────────────────────

    def _get_cash_balance_before(self, date) -> Decimal:
        """Get total cash & cash equivalents balance before a date."""
        accounts = Account.objects.filter(
            account_type=ACCOUNT_TYPE_ASSET,
            is_active=True,
            is_header=False,
            code__gte=CASH_CODE_MIN,
            code__lte=CASH_CODE_MAX,
        )
        filters = Q(
            account__in=accounts,
            journal_entry__entry_status=JournalEntryStatus.POSTED,
        )
        if date:
            filters &= Q(journal_entry__entry_date__lt=date)

        totals = JournalEntryLine.objects.filter(filters).aggregate(
            dr=Sum("debit_amount"), cr=Sum("credit_amount"),
        )
        return (totals["dr"] or Decimal("0")) - (totals["cr"] or Decimal("0"))

    # ── Helpers ──────────────────────────────────────────────────────

    def _calculate_balance_change(
        self, account_type: str, code_min: str, code_max: str,
        start_date, end_date,
    ) -> Decimal:
        """Calculate net balance change for accounts in a code range."""
        accounts = Account.objects.filter(
            account_type=account_type,
            is_active=True,
            is_header=False,
            code__gte=code_min,
            code__lte=code_max,
        )
        filters = Q(
            account__in=accounts,
            journal_entry__entry_status=JournalEntryStatus.POSTED,
        )
        if start_date:
            filters &= Q(journal_entry__entry_date__gte=start_date)
        if end_date:
            filters &= Q(journal_entry__entry_date__lte=end_date)

        totals = JournalEntryLine.objects.filter(filters).aggregate(
            dr=Sum("debit_amount"), cr=Sum("credit_amount"),
        )
        dr = totals["dr"] or Decimal("0")
        cr = totals["cr"] or Decimal("0")

        # For assets/expenses (debit normal): positive = increase
        # For liabilities/equity/revenue (credit normal): positive = increase
        if account_type in (ACCOUNT_TYPE_ASSET, ACCOUNT_TYPE_EXPENSE):
            return dr - cr
        return cr - dr

    # ── Comparison ──────────────────────────────────────────────────

    def _get_comparison_data(self) -> Optional[Dict[str, Any]]:
        """Generate cash flow data for comparison period."""
        comp_start, comp_end = self._get_comparison_range()
        if not comp_start and not comp_end:
            return None

        original_start = self._config.start_date
        original_end = self._config.end_date
        self._config.start_date = comp_start
        self._config.end_date = comp_end

        try:
            return self.get_data()
        finally:
            self._config.start_date = original_start
            self._config.end_date = original_end

    def _calculate_variances(
        self, current_data: Dict, comparison_data: Dict,
    ) -> Dict[str, Any]:
        """Calculate variances between current and comparison CF."""
        variances = {}
        for key in ("net_cash_change", "beginning_cash", "ending_cash"):
            current_val = current_data.get(key, Decimal("0"))
            comp_val = comparison_data.get(key, Decimal("0"))
            variances[key] = self._calculate_variance(current_val, comp_val)

        for section in ("operating", "investing", "financing"):
            current_val = current_data.get(section, {})
            comp_val = comparison_data.get(section, {})
            current_total = current_val.get("total", current_val.get("net", Decimal("0")))
            comp_total = comp_val.get("total", comp_val.get("net", Decimal("0")))
            variances[section] = self._calculate_variance(current_total, comp_total)

        return variances
