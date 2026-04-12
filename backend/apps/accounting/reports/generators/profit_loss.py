"""
Profit & Loss (Income Statement) report generator.

Generates a P&L report with revenue, COGS, gross profit,
operating expenses, other income/expenses, and net income.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Q, Sum

from apps.accounting.constants import ACCOUNT_TYPE_EXPENSE, ACCOUNT_TYPE_REVENUE
from apps.accounting.models.account import Account
from apps.accounting.models.enums import JournalEntryStatus
from apps.accounting.models.journal_line import JournalEntryLine
from apps.accounting.reports.base import BaseReportGenerator
from apps.accounting.reports.enums import ReportType

# Code range boundaries
REVENUE_CODE_MAX = "4899"
OTHER_INCOME_CODE_MIN = "4900"
COGS_CODE_MIN = "5100"
COGS_CODE_MAX = "5199"
OPEX_CODE_MIN = "5200"
OPEX_CODE_MAX = "5799"
OTHER_EXP_CODE_MIN = "5800"
OTHER_EXP_CODE_MAX = "5899"


class ProfitLossGenerator(BaseReportGenerator):
    """Generates Profit & Loss (Income Statement) reports."""

    report_type = ReportType.PROFIT_LOSS

    # ── Data Retrieval ──────────────────────────────────────────────

    def get_data(self) -> Dict[str, Any]:
        """Retrieve P&L data from journal entries."""
        start_date, end_date = self._get_date_range()

        revenue_accounts = self._get_revenue_accounts()
        revenue_data = self._calculate_account_balances(
            revenue_accounts, start_date, end_date, normal_side="credit",
        )
        total_revenue = sum(a["balance"] for a in revenue_data)

        other_income_accounts = self._get_other_income_accounts()
        other_income_data = self._calculate_account_balances(
            other_income_accounts, start_date, end_date, normal_side="credit",
        )
        total_other_income = sum(a["balance"] for a in other_income_data)

        cogs_accounts = self._get_cogs_accounts()
        cogs_data = self._calculate_account_balances(
            cogs_accounts, start_date, end_date, normal_side="debit",
        )
        total_cogs = sum(a["balance"] for a in cogs_data)

        gross_profit = total_revenue - total_cogs

        opex_accounts = self._get_operating_expense_accounts()
        opex_data = self._calculate_account_balances(
            opex_accounts, start_date, end_date, normal_side="debit",
        )
        total_opex = sum(a["balance"] for a in opex_data)

        operating_income = gross_profit - total_opex

        other_exp_accounts = self._get_other_expense_accounts()
        other_exp_data = self._calculate_account_balances(
            other_exp_accounts, start_date, end_date, normal_side="debit",
        )
        total_other_expenses = sum(a["balance"] for a in other_exp_data)

        net_income = operating_income + total_other_income - total_other_expenses

        return {
            "start_date": str(start_date or ""),
            "end_date": str(end_date or ""),
            "revenue": {
                "accounts": revenue_data,
                "total": total_revenue,
            },
            "cost_of_goods_sold": {
                "accounts": cogs_data,
                "total": total_cogs,
            },
            "gross_profit": {
                "amount": gross_profit,
                "margin_percentage": self._pct(gross_profit, total_revenue),
            },
            "operating_expenses": {
                "accounts": opex_data,
                "total": total_opex,
            },
            "operating_income": {
                "amount": operating_income,
                "margin_percentage": self._pct(operating_income, total_revenue),
            },
            "other_income": {
                "accounts": other_income_data,
                "total": total_other_income,
            },
            "other_expenses": {
                "accounts": other_exp_data,
                "total": total_other_expenses,
            },
            "net_income": {
                "amount": net_income,
                "margin_percentage": self._pct(net_income, total_revenue),
            },
            "total_revenue": total_revenue,
        }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format P&L data into report structure."""
        result = {
            "title": "Profit & Loss Statement",
            "report_type": ReportType.PROFIT_LOSS,
            "period": {
                "start_date": data["start_date"],
                "end_date": data["end_date"],
            },
            "revenue": data["revenue"],
            "cost_of_goods_sold": data["cost_of_goods_sold"],
            "gross_profit": data["gross_profit"],
            "operating_expenses": data["operating_expenses"],
            "operating_income": data["operating_income"],
            "other_income": data["other_income"],
            "other_expenses": data["other_expenses"],
            "net_income": data["net_income"],
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

    def _get_revenue_accounts(self) -> List:
        """Get revenue accounts (code 4000-4899)."""
        return list(
            Account.objects.filter(
                account_type=ACCOUNT_TYPE_REVENUE,
                is_active=True,
                is_header=False,
                code__lte=REVENUE_CODE_MAX,
            ).order_by("code")
        )

    def _get_other_income_accounts(self) -> List:
        """Get other income accounts (code 4900+)."""
        return list(
            Account.objects.filter(
                account_type=ACCOUNT_TYPE_REVENUE,
                is_active=True,
                is_header=False,
                code__gte=OTHER_INCOME_CODE_MIN,
            ).order_by("code")
        )

    def _get_cogs_accounts(self) -> List:
        """Get COGS accounts (code 5100-5199)."""
        return list(
            Account.objects.filter(
                account_type=ACCOUNT_TYPE_EXPENSE,
                is_active=True,
                is_header=False,
                code__gte=COGS_CODE_MIN,
                code__lte=COGS_CODE_MAX,
            ).order_by("code")
        )

    def _get_operating_expense_accounts(self) -> List:
        """Get operating expense accounts (code 5200-5799)."""
        return list(
            Account.objects.filter(
                account_type=ACCOUNT_TYPE_EXPENSE,
                is_active=True,
                is_header=False,
                code__gte=OPEX_CODE_MIN,
                code__lte=OPEX_CODE_MAX,
            ).order_by("code")
        )

    def _get_other_expense_accounts(self) -> List:
        """Get other expense accounts (code 5800-5899)."""
        return list(
            Account.objects.filter(
                account_type=ACCOUNT_TYPE_EXPENSE,
                is_active=True,
                is_header=False,
                code__gte=OTHER_EXP_CODE_MIN,
                code__lte=OTHER_EXP_CODE_MAX,
            ).order_by("code")
        )

    # ── Balance Calculation ─────────────────────────────────────────

    def _calculate_account_balances(
        self,
        accounts: List,
        start_date,
        end_date,
        normal_side: str = "debit",
    ) -> List[Dict[str, Any]]:
        """Calculate period balance for a list of accounts."""
        result = []
        for account in accounts:
            filters = Q(
                account=account,
                journal_entry__entry_status=JournalEntryStatus.POSTED,
            )
            if start_date:
                filters &= Q(journal_entry__entry_date__gte=start_date)
            if end_date:
                filters &= Q(journal_entry__entry_date__lte=end_date)

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

    # ── Comparison ──────────────────────────────────────────────────

    def _get_comparison_data(self) -> Optional[Dict[str, Any]]:
        """Generate P&L data for comparison period."""
        comp_start, comp_end = self._get_comparison_range()
        if not comp_start and not comp_end:
            return None

        # Temporarily swap dates
        original_start = self._config.start_date
        original_end = self._config.end_date
        self._config.start_date = comp_start
        self._config.end_date = comp_end

        try:
            data = self.get_data()
        finally:
            self._config.start_date = original_start
            self._config.end_date = original_end

        return data

    def _calculate_variances(
        self, current_data: Dict, comparison_data: Dict,
    ) -> Dict[str, Any]:
        """Calculate variances between current and comparison P&L."""
        variances = {}
        keys = [
            ("revenue", "total"),
            ("cost_of_goods_sold", "total"),
            ("gross_profit", "amount"),
            ("operating_expenses", "total"),
            ("operating_income", "amount"),
            ("other_income", "total"),
            ("other_expenses", "total"),
            ("net_income", "amount"),
        ]
        for section, field in keys:
            current_val = current_data.get(section, {}).get(field, Decimal("0"))
            comp_val = comparison_data.get(section, {}).get(field, Decimal("0"))
            variances[section] = self._calculate_variance(current_val, comp_val)
        return variances

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _pct(value: Decimal, total: Decimal) -> Decimal:
        """Calculate percentage of total."""
        if total and total != Decimal("0"):
            return round((value / total) * Decimal("100"), 2)
        return Decimal("0")
