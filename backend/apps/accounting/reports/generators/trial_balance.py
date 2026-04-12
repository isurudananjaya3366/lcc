"""
Trial Balance report generator.

Generates a Trial Balance report showing account balances at a point
in time, with opening balances, period movements, and closing balances.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Q, Sum

logger = logging.getLogger(__name__)

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

# Ordered account types for display
ACCOUNT_TYPE_ORDER = {
    ACCOUNT_TYPE_ASSET: 1,
    ACCOUNT_TYPE_LIABILITY: 2,
    ACCOUNT_TYPE_EQUITY: 3,
    ACCOUNT_TYPE_REVENUE: 4,
    ACCOUNT_TYPE_EXPENSE: 5,
}

ACCOUNT_TYPE_DISPLAY = {
    ACCOUNT_TYPE_ASSET: "Assets",
    ACCOUNT_TYPE_LIABILITY: "Liabilities",
    ACCOUNT_TYPE_EQUITY: "Equity",
    ACCOUNT_TYPE_REVENUE: "Revenue",
    ACCOUNT_TYPE_EXPENSE: "Expenses",
}


class TrialBalanceGenerator(BaseReportGenerator):
    """Generates Trial Balance reports."""

    report_type = ReportType.TRIAL_BALANCE

    # ── Data Retrieval ──────────────────────────────────────────────

    def get_data(self) -> Dict[str, Any]:
        """Retrieve trial balance data from journal entries."""
        start_date, end_date = self._get_date_range()
        as_of_date = self._config.as_of_date

        # For TB, if no start/end provided, use as_of_date
        if not end_date and as_of_date:
            end_date = as_of_date

        accounts = self._get_accounts()
        account_balances = []

        for account in accounts:
            balance = self._calculate_balance(account, start_date, end_date)
            if balance and self._should_include_in_report(balance):
                account_balances.append(balance)

        grouped = self._group_by_type(account_balances)
        totals = self._calculate_totals(account_balances)
        validation = self._validate_totals(totals)

        return {
            "as_of_date": str(as_of_date or end_date or ""),
            "start_date": str(start_date or ""),
            "end_date": str(end_date or ""),
            "accounts": account_balances,
            "groups": grouped,
            "totals": totals,
            "validation": validation,
        }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format trial balance data into report structure."""
        result = {
            "title": "Trial Balance",
            "report_type": ReportType.TRIAL_BALANCE,
            "period": {
                "as_of_date": data.get("as_of_date", ""),
                "start_date": data.get("start_date", ""),
                "end_date": data.get("end_date", ""),
            },
            "account_groups": data["groups"],
            "grand_totals": data["totals"],
            "is_balanced": data["validation"]["is_balanced"],
            "validation": data["validation"],
            "display_options": {
                "detail_level": self._config.detail_level,
                "include_zero_balances": self._config.include_zero_balances,
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

    def _get_accounts(self, account_types=None) -> List:
        """Get active accounts ordered by tree structure."""
        qs = Account.objects.filter(
            is_active=True,
            is_header=False,
        ).order_by("tree_id", "lft", "code")

        if account_types:
            qs = qs.filter(account_type__in=account_types)

        return list(qs)

    # ── Balance Calculations ────────────────────────────────────────

    def _calculate_balance(
        self,
        account: Account,
        start_date,
        end_date,
    ) -> Optional[Dict[str, Any]]:
        """Calculate complete balance for a single account."""
        opening_debit, opening_credit = self._calculate_opening_balance(
            account, start_date,
        )
        period_debit, period_credit = self._calculate_period_movements(
            account, start_date, end_date,
        )
        closing_debit, closing_credit = self._calculate_closing_balance(
            opening_debit, opening_credit,
            period_debit, period_credit,
        )

        balance_amount = closing_debit - closing_credit
        balance_side = "DEBIT" if balance_amount >= 0 else "CREDIT"

        return {
            "account_code": account.code,
            "account_name": account.name,
            "account_type": account.account_type,
            "parent_code": account.parent.code if account.parent else None,
            "opening_debit": opening_debit,
            "opening_credit": opening_credit,
            "period_debit": period_debit,
            "period_credit": period_credit,
            "closing_debit": closing_debit,
            "closing_credit": closing_credit,
            "balance_side": balance_side,
            "balance_amount": abs(balance_amount),
        }

    def _calculate_opening_balance(
        self, account: Account, start_date,
    ) -> Tuple[Decimal, Decimal]:
        """Sum all posted entries before start_date."""
        if not start_date:
            return Decimal("0"), Decimal("0")

        totals = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__entry_date__lt=start_date,
            journal_entry__entry_status=JournalEntryStatus.POSTED,
        ).aggregate(
            total_debit=Sum("debit_amount"),
            total_credit=Sum("credit_amount"),
        )
        return (
            totals["total_debit"] or Decimal("0"),
            totals["total_credit"] or Decimal("0"),
        )

    def _calculate_period_movements(
        self, account: Account, start_date, end_date,
    ) -> Tuple[Decimal, Decimal]:
        """Sum all posted entries within the period."""
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
        return (
            totals["total_debit"] or Decimal("0"),
            totals["total_credit"] or Decimal("0"),
        )

    def _calculate_closing_balance(
        self,
        opening_debit: Decimal,
        opening_credit: Decimal,
        period_debit: Decimal,
        period_credit: Decimal,
    ) -> Tuple[Decimal, Decimal]:
        """Calculate closing balance from opening + period."""
        total_dr = opening_debit + period_debit
        total_cr = opening_credit + period_credit

        if total_dr >= total_cr:
            return total_dr - total_cr, Decimal("0")
        return Decimal("0"), total_cr - total_dr

    # ── Grouping & Totals ───────────────────────────────────────────

    def _group_by_type(
        self, balances: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Group account balances by account type."""
        groups = {}
        for balance in balances:
            acct_type = balance["account_type"]
            if acct_type not in groups:
                groups[acct_type] = {
                    "account_type": acct_type,
                    "display_name": ACCOUNT_TYPE_DISPLAY.get(
                        acct_type, acct_type
                    ),
                    "order": ACCOUNT_TYPE_ORDER.get(acct_type, 99),
                    "accounts": [],
                }
            groups[acct_type]["accounts"].append(balance)

        # Add subtotals
        for group in groups.values():
            group["subtotals"] = self._sum_balances(group["accounts"])

        return sorted(groups.values(), key=lambda g: g["order"])

    def _calculate_totals(
        self, balances: List[Dict],
    ) -> Dict[str, Decimal]:
        """Calculate grand totals across all accounts."""
        return self._sum_balances(balances)

    def _sum_balances(
        self, balances: List[Dict],
    ) -> Dict[str, Decimal]:
        """Sum balance columns."""
        result = {
            "opening_debit": Decimal("0"),
            "opening_credit": Decimal("0"),
            "period_debit": Decimal("0"),
            "period_credit": Decimal("0"),
            "closing_debit": Decimal("0"),
            "closing_credit": Decimal("0"),
        }
        for b in balances:
            for key in result:
                result[key] += b.get(key, Decimal("0"))
        return result

    def _validate_totals(
        self, totals: Dict[str, Decimal],
    ) -> Dict[str, Any]:
        """Validate that debits equal credits."""
        opening_ok = totals["opening_debit"] == totals["opening_credit"]
        period_ok = totals["period_debit"] == totals["period_credit"]
        closing_ok = totals["closing_debit"] == totals["closing_credit"]

        errors = []
        if not opening_ok:
            errors.append(
                f"Opening imbalance: DR {totals['opening_debit']} "
                f"!= CR {totals['opening_credit']}"
            )
        if not period_ok:
            errors.append(
                f"Period imbalance: DR {totals['period_debit']} "
                f"!= CR {totals['period_credit']}"
            )
        if not closing_ok:
            errors.append(
                f"Closing imbalance: DR {totals['closing_debit']} "
                f"!= CR {totals['closing_credit']}"
            )

        return {
            "is_balanced": opening_ok and period_ok and closing_ok,
            "opening_balanced": opening_ok,
            "period_balanced": period_ok,
            "closing_balanced": closing_ok,
            "errors": errors,
        }

    # ── Comparison ──────────────────────────────────────────────────

    def _get_comparison_data(self) -> Optional[Dict[str, Any]]:
        """Generate trial balance data for comparison period."""
        comp_start, comp_end = self._get_comparison_range()
        comp_as_of = self._config.comparison_as_of_date

        if not comp_end and not comp_as_of:
            return None

        if not comp_end and comp_as_of:
            comp_end = comp_as_of

        # Validate comparison dates
        start_date, end_date = self._get_date_range()
        if comp_end and start_date and comp_end >= start_date:
            logger.warning(
                "Comparison period end (%s) overlaps current start (%s)",
                comp_end, start_date,
            )

        accounts = self._get_accounts()
        balances = []
        for account in accounts:
            balance = self._calculate_balance(account, comp_start, comp_end)
            if balance:
                balances.append(balance)

        return {
            "start_date": str(comp_start or ""),
            "end_date": str(comp_end or ""),
            "accounts": balances,
            "groups": self._group_by_type(balances),
            "totals": self._calculate_totals(balances),
        }

    def _calculate_variances(
        self, current_data: Dict, comparison_data: Dict,
    ) -> Dict[str, Any]:
        """Calculate variances between current and comparison TB."""
        variances = {}
        current_map = {
            a["account_code"]: a for a in current_data.get("accounts", [])
        }
        comp_map = {
            a["account_code"]: a
            for a in comparison_data.get("accounts", [])
        }

        # Union of all account codes from both periods
        all_codes = set(current_map.keys()) | set(comp_map.keys())

        for code in all_codes:
            current = current_map.get(code, {})
            prior = comp_map.get(code, {})
            current_bal = current.get("balance_amount", Decimal("0"))
            prior_bal = prior.get("balance_amount", Decimal("0"))
            acct_type = current.get(
                "account_type", prior.get("account_type", ""),
            )
            variances[code] = self._calculate_variance(
                current_bal, prior_bal, account_type=acct_type,
            )

        # Build variance summary: top 10 material variances
        material = [
            {
                "account_code": code,
                "account_name": current_map.get(
                    code, comp_map.get(code, {}),
                ).get("account_name", ""),
                **v,
            }
            for code, v in variances.items()
            if v.get("is_material")
        ]
        material.sort(key=lambda x: abs(x["amount"]), reverse=True)

        return {
            "accounts": variances,
            "variance_summary": {
                "material_variances_count": len(material),
                "total_favorable_count": sum(
                    1 for m in material if m["classification"] == "favorable"
                ),
                "total_unfavorable_count": sum(
                    1 for m in material if m["classification"] == "unfavorable"
                ),
                "top_variances": material[:10],
            },
        }

    # ── Helpers ──────────────────────────────────────────────────────

    def _should_include_in_report(self, balance: Dict) -> bool:
        """Check if account should appear in the report."""
        if self._config.include_zero_balances:
            return True
        zero = Decimal("0")
        return (
            balance["closing_debit"] != zero
            or balance["closing_credit"] != zero
            or balance["period_debit"] != zero
            or balance["period_credit"] != zero
        )
