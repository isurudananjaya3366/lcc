"""
Balance Sheet (Statement of Financial Position) report generator.

Point-in-time snapshot of Assets, Liabilities, and Equity with
the fundamental accounting equation validation:
    Assets = Liabilities + Equity
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

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

# Asset code ranges
CURRENT_ASSET_MIN = "1100"
CURRENT_ASSET_MAX = "1199"
FIXED_ASSET_MIN = "1200"
FIXED_ASSET_MAX = "1799"
DEPRECIATION_MIN = "1800"
DEPRECIATION_MAX = "1899"

# Liability code ranges
CURRENT_LIAB_MIN = "2100"
CURRENT_LIAB_MAX = "2199"
LONG_TERM_LIAB_MIN = "2200"
LONG_TERM_LIAB_MAX = "2999"

# Equity code ranges
CAPITAL_MIN = "3100"
CAPITAL_MAX = "3199"
RETAINED_EARNINGS_MIN = "3200"
RETAINED_EARNINGS_MAX = "3299"
DRAWINGS_MIN = "3300"
DRAWINGS_MAX = "3399"


class BalanceSheetGenerator(BaseReportGenerator):
    """Generates Balance Sheet (Statement of Financial Position) reports."""

    report_type = ReportType.BALANCE_SHEET

    # ── Data Retrieval ──────────────────────────────────────────────

    def get_data(self) -> Dict[str, Any]:
        """Retrieve Balance Sheet data as of the configured date."""
        as_of_date = self._config.as_of_date or self._config.end_date

        # Assets
        current_assets = self._get_section_accounts(
            ACCOUNT_TYPE_ASSET, CURRENT_ASSET_MIN, CURRENT_ASSET_MAX,
        )
        current_assets_data = self._calculate_cumulative_balances(
            current_assets, as_of_date, "debit",
        )
        total_current_assets = sum(a["balance"] for a in current_assets_data)

        fixed_assets = self._get_section_accounts(
            ACCOUNT_TYPE_ASSET, FIXED_ASSET_MIN, FIXED_ASSET_MAX,
        )
        fixed_assets_data = self._calculate_cumulative_balances(
            fixed_assets, as_of_date, "debit",
        )
        total_fixed_gross = sum(a["balance"] for a in fixed_assets_data)

        depreciation = self._get_section_accounts(
            ACCOUNT_TYPE_ASSET, DEPRECIATION_MIN, DEPRECIATION_MAX,
        )
        depreciation_data = self._calculate_cumulative_balances(
            depreciation, as_of_date, "credit",
        )
        total_depreciation = sum(a["balance"] for a in depreciation_data)

        net_fixed_assets = total_fixed_gross - total_depreciation
        total_assets = total_current_assets + net_fixed_assets

        # Liabilities
        current_liabilities = self._get_section_accounts(
            ACCOUNT_TYPE_LIABILITY, CURRENT_LIAB_MIN, CURRENT_LIAB_MAX,
        )
        current_liab_data = self._calculate_cumulative_balances(
            current_liabilities, as_of_date, "credit",
        )
        total_current_liab = sum(a["balance"] for a in current_liab_data)

        long_term_liabilities = self._get_section_accounts(
            ACCOUNT_TYPE_LIABILITY, LONG_TERM_LIAB_MIN, LONG_TERM_LIAB_MAX,
        )
        long_term_liab_data = self._calculate_cumulative_balances(
            long_term_liabilities, as_of_date, "credit",
        )
        total_long_term_liab = sum(a["balance"] for a in long_term_liab_data)
        total_liabilities = total_current_liab + total_long_term_liab

        # Equity
        equity_accounts = self._get_accounts_by_type(ACCOUNT_TYPE_EQUITY)
        equity_data = self._calculate_cumulative_balances(
            equity_accounts, as_of_date, "credit",
        )
        total_equity_accounts = sum(a["balance"] for a in equity_data)

        # Retained earnings includes current net income
        current_net_income = self._calculate_current_net_income(as_of_date)
        total_equity = total_equity_accounts + current_net_income

        total_liabilities_equity = total_liabilities + total_equity

        # Validation
        is_balanced = abs(total_assets - total_liabilities_equity) < Decimal("0.01")

        return {
            "as_of_date": str(as_of_date or ""),
            "current_assets": {
                "accounts": current_assets_data,
                "total": total_current_assets,
            },
            "fixed_assets": {
                "accounts": fixed_assets_data,
                "total_gross": total_fixed_gross,
            },
            "depreciation": {
                "accounts": depreciation_data,
                "total": total_depreciation,
            },
            "net_fixed_assets": net_fixed_assets,
            "total_assets": total_assets,
            "current_liabilities": {
                "accounts": current_liab_data,
                "total": total_current_liab,
            },
            "long_term_liabilities": {
                "accounts": long_term_liab_data,
                "total": total_long_term_liab,
            },
            "total_liabilities": total_liabilities,
            "equity": {
                "accounts": equity_data,
                "total_accounts": total_equity_accounts,
            },
            "current_net_income": current_net_income,
            "total_equity": total_equity,
            "total_liabilities_equity": total_liabilities_equity,
            "is_balanced": is_balanced,
        }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format Balance Sheet data into report structure."""
        result = {
            "title": "Balance Sheet",
            "report_type": ReportType.BALANCE_SHEET,
            "as_of_date": data["as_of_date"],
            "assets": {
                "current_assets": data["current_assets"],
                "fixed_assets": data["fixed_assets"],
                "accumulated_depreciation": data["depreciation"],
                "net_fixed_assets": data["net_fixed_assets"],
                "total_assets": data["total_assets"],
            },
            "liabilities": {
                "current_liabilities": data["current_liabilities"],
                "long_term_liabilities": data["long_term_liabilities"],
                "total_liabilities": data["total_liabilities"],
            },
            "equity": {
                "accounts": data["equity"]["accounts"],
                "total_equity_accounts": data["equity"]["total_accounts"],
                "current_net_income": data["current_net_income"],
                "total_equity": data["total_equity"],
            },
            "total_liabilities_equity": data["total_liabilities_equity"],
            "is_balanced": data["is_balanced"],
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

    # ── Account Queries ─────────────────────────────────────────────

    def _get_section_accounts(
        self, account_type: str, code_min: str, code_max: str,
    ) -> List:
        """Get active non-header accounts in a code range."""
        return list(
            Account.objects.filter(
                account_type=account_type,
                is_active=True,
                is_header=False,
                code__gte=code_min,
                code__lte=code_max,
            ).order_by("code")
        )

    def _get_accounts_by_type(self, account_type: str) -> List:
        """Get all active non-header accounts of a type."""
        return list(
            Account.objects.filter(
                account_type=account_type,
                is_active=True,
                is_header=False,
            ).order_by("code")
        )

    # ── Balance Calculation ─────────────────────────────────────────

    def _calculate_cumulative_balances(
        self,
        accounts: List,
        as_of_date,
        normal_side: str = "debit",
    ) -> List[Dict[str, Any]]:
        """Calculate cumulative balance as of a date for accounts."""
        result = []
        for account in accounts:
            filters = Q(
                account=account,
                journal_entry__entry_status=JournalEntryStatus.POSTED,
            )
            if as_of_date:
                filters &= Q(journal_entry__entry_date__lte=as_of_date)

            totals = JournalEntryLine.objects.filter(filters).aggregate(
                total_debit=Sum("debit_amount"),
                total_credit=Sum("credit_amount"),
            )
            dr = totals["total_debit"] or Decimal("0")
            cr = totals["total_credit"] or Decimal("0")

            if normal_side == "credit":
                balance = cr - dr
            else:
                balance = dr - cr

            if not self._config.include_zero_balances and balance == Decimal("0"):
                continue

            result.append({
                "account_code": account.code,
                "account_name": account.name,
                "account_type": account.account_type,
                "debit": dr,
                "credit": cr,
                "balance": balance,
            })
        return result

    # ── Net Income Calculation ──────────────────────────────────────

    def _calculate_current_net_income(self, as_of_date) -> Decimal:
        """Calculate current period net income for retained earnings."""
        # Revenue (credit normal) - Expenses (debit normal)
        revenue_accounts = Account.objects.filter(
            account_type=ACCOUNT_TYPE_REVENUE,
            is_active=True,
            is_header=False,
        )
        expense_accounts = Account.objects.filter(
            account_type=ACCOUNT_TYPE_EXPENSE,
            is_active=True,
            is_header=False,
        )

        filters = Q(journal_entry__entry_status=JournalEntryStatus.POSTED)
        if as_of_date:
            filters &= Q(journal_entry__entry_date__lte=as_of_date)

        rev_totals = JournalEntryLine.objects.filter(
            filters, account__in=revenue_accounts,
        ).aggregate(
            total_debit=Sum("debit_amount"),
            total_credit=Sum("credit_amount"),
        )
        total_revenue = (
            (rev_totals["total_credit"] or Decimal("0"))
            - (rev_totals["total_debit"] or Decimal("0"))
        )

        exp_totals = JournalEntryLine.objects.filter(
            filters, account__in=expense_accounts,
        ).aggregate(
            total_debit=Sum("debit_amount"),
            total_credit=Sum("credit_amount"),
        )
        total_expenses = (
            (exp_totals["total_debit"] or Decimal("0"))
            - (exp_totals["total_credit"] or Decimal("0"))
        )

        return total_revenue - total_expenses

    # ── Comparison ──────────────────────────────────────────────────

    def _get_comparison_data(self) -> Optional[Dict[str, Any]]:
        """Generate Balance Sheet data for comparison date."""
        comp_as_of = self._config.comparison_as_of_date
        comp_end = self._config.comparison_end_date
        comparison_date = comp_as_of or comp_end

        if not comparison_date:
            return None

        original_as_of = self._config.as_of_date
        original_end = self._config.end_date
        self._config.as_of_date = comparison_date
        self._config.end_date = comparison_date

        try:
            data = self.get_data()
        finally:
            self._config.as_of_date = original_as_of
            self._config.end_date = original_end

        return data

    def _calculate_variances(
        self, current_data: Dict, comparison_data: Dict,
    ) -> Dict[str, Any]:
        """Calculate variances between current and comparison BS."""
        variances = {}
        keys = [
            "total_assets",
            "total_liabilities",
            "total_equity",
            "total_liabilities_equity",
        ]
        for key in keys:
            current_val = current_data.get(key, Decimal("0"))
            comp_val = comparison_data.get(key, Decimal("0"))
            variances[key] = self._calculate_variance(current_val, comp_val)
        return variances
