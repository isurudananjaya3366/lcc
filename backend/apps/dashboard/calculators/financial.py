"""Financial KPI calculator — computes financial performance metrics."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import F, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.dashboard.calculators.base import BaseKPICalculator
from apps.dashboard.services.cache_service import get_cached_kpi, set_cached_kpi


class FinancialKPICalculator(BaseKPICalculator):
    """Calculates financial KPIs from accounting, invoice, and bill data."""

    CACHE_NAME = "financial"

    def _get_revenue_accounts(self):
        """Get active revenue accounts."""
        from apps.accounting.models import Account

        return Account.objects.filter(
            account_type="revenue",
            status="ACTIVE",
        )

    def _get_expense_accounts(self):
        """Get active expense accounts."""
        from apps.accounting.models import Account

        return Account.objects.filter(
            account_type="expense",
            status="ACTIVE",
        )

    def _get_posted_journal_lines(self, start_date, end_date):
        """Get posted journal entry lines for a date range."""
        from apps.accounting.models import JournalEntryLine

        return JournalEntryLine.objects.filter(
            journal_entry__entry_status="POSTED",
            journal_entry__entry_date__gte=start_date,
            journal_entry__entry_date__lte=end_date,
        )

    def calculate_revenue(self, period, filters=None):
        """Calculate current period revenue from revenue accounts."""
        start, end = self.get_date_range(period)
        lines = self._get_posted_journal_lines(start, end).filter(
            account__account_type="revenue",
        )
        # Revenue is credit-normal: credits increase revenue
        revenue = (
            lines.aggregate(
                total=Sum("credit_amount") - Sum("debit_amount")
            )["total"]
            or Decimal("0")
        )
        revenue = abs(revenue)

        prev_start, prev_end = self.get_previous_date_range(period)
        prev_lines = self._get_posted_journal_lines(prev_start, prev_end).filter(
            account__account_type="revenue",
        )
        prev_revenue = abs(
            prev_lines.aggregate(
                total=Sum("credit_amount") - Sum("debit_amount")
            )["total"]
            or Decimal("0")
        )

        change = self.calculate_change(revenue, prev_revenue)
        return self.format_result(
            value=revenue,
            label="Revenue",
            format_type="currency",
            **change,
        )

    def calculate_expenses(self, period, filters=None):
        """Calculate current period expenses."""
        start, end = self.get_date_range(period)
        lines = self._get_posted_journal_lines(start, end).filter(
            account__account_type="expense",
        )
        # Expenses are debit-normal: debits increase expenses
        expenses = (
            lines.aggregate(
                total=Sum("debit_amount") - Sum("credit_amount")
            )["total"]
            or Decimal("0")
        )
        expenses = abs(expenses)

        prev_start, prev_end = self.get_previous_date_range(period)
        prev_lines = self._get_posted_journal_lines(prev_start, prev_end).filter(
            account__account_type="expense",
        )
        prev_expenses = abs(
            prev_lines.aggregate(
                total=Sum("debit_amount") - Sum("credit_amount")
            )["total"]
            or Decimal("0")
        )

        change = self.calculate_change(expenses, prev_expenses)
        return self.format_result(
            value=expenses,
            label="Expenses",
            format_type="currency",
            **change,
        )

    def calculate_net_income(self, period, filters=None):
        """Calculate net income (revenue - expenses)."""
        revenue_result = self.calculate_revenue(period, filters)
        expense_result = self.calculate_expenses(period, filters)

        revenue = Decimal(str(revenue_result["value"]))
        expenses = Decimal(str(expense_result["value"]))
        net_income = revenue - expenses

        return self.format_result(
            value=net_income,
            label="Net Income",
            format_type="currency",
            revenue=revenue,
            expenses=expenses,
        )

    def calculate_gross_profit_margin(self, period, filters=None):
        """Calculate gross profit margin: (Revenue - COGS) / Revenue * 100."""
        start, end = self.get_date_range(period)

        # Revenue
        rev_lines = self._get_posted_journal_lines(start, end).filter(
            account__account_type="revenue",
        )
        revenue = abs(
            rev_lines.aggregate(
                total=Sum("credit_amount") - Sum("debit_amount")
            )["total"]
            or Decimal("0")
        )

        # COGS — typically expense accounts with 'cost of' or 'COGS' in name
        cogs_lines = self._get_posted_journal_lines(start, end).filter(
            account__account_type="expense",
            account__name__icontains="cost",
        )
        cogs = abs(
            cogs_lines.aggregate(
                total=Sum("debit_amount") - Sum("credit_amount")
            )["total"]
            or Decimal("0")
        )

        if revenue > 0:
            margin = ((revenue - cogs) / revenue) * 100
        else:
            margin = Decimal("0")

        return self.format_result(
            value=round(margin, 2),
            label="Gross Profit Margin",
            format_type="percent",
            revenue=revenue,
            cogs=cogs,
        )

    def calculate_net_profit_margin(self, period, filters=None):
        """Calculate net profit margin: Net Income / Revenue * 100."""
        net_income_result = self.calculate_net_income(period, filters)
        net_income = Decimal(str(net_income_result["value"]))
        revenue = Decimal(str(net_income_result.get("revenue", 0)))

        if revenue > 0:
            margin = (net_income / revenue) * 100
        else:
            margin = Decimal("0")

        return self.format_result(
            value=round(margin, 2),
            label="Net Profit Margin",
            format_type="percent",
        )

    def calculate_cash_position(self, period=None, filters=None):
        """Calculate current cash balance from cash/bank accounts."""
        from apps.accounting.models import Account

        cash_accounts = Account.objects.filter(
            account_type="asset",
            status="ACTIVE",
            name__iregex=r"(cash|bank|petty)",
        )
        total_cash = (
            cash_accounts.aggregate(total=Sum("current_balance"))["total"]
            or Decimal("0")
        )

        return self.format_result(
            value=total_cash,
            label="Cash Position",
            format_type="currency",
        )

    def calculate_accounts_receivable(self, period=None, filters=None):
        """Calculate total outstanding accounts receivable."""
        from apps.invoices.models import Invoice

        total_ar = (
            Invoice.objects.filter(
                status__in=["ISSUED", "SENT", "PARTIAL", "OVERDUE"],
                is_deleted=False,
            ).aggregate(total=Sum("balance_due"))["total"]
            or Decimal("0")
        )

        return self.format_result(
            value=total_ar,
            label="Accounts Receivable",
            format_type="currency",
        )

    def calculate_ar_aging(self, period=None, filters=None):
        """Calculate AR aging summary in 30/60/90+ day buckets."""
        from apps.invoices.models import Invoice

        today = timezone.now().date()
        outstanding = Invoice.objects.filter(
            status__in=["ISSUED", "SENT", "PARTIAL", "OVERDUE"],
            is_deleted=False,
            due_date__isnull=False,
        )

        current = outstanding.filter(due_date__gte=today).aggregate(
            total=Sum("balance_due")
        )["total"] or Decimal("0")

        days_30 = outstanding.filter(
            due_date__lt=today,
            due_date__gte=today - timedelta(days=30),
        ).aggregate(total=Sum("balance_due"))["total"] or Decimal("0")

        days_60 = outstanding.filter(
            due_date__lt=today - timedelta(days=30),
            due_date__gte=today - timedelta(days=60),
        ).aggregate(total=Sum("balance_due"))["total"] or Decimal("0")

        days_90_plus = outstanding.filter(
            due_date__lt=today - timedelta(days=60),
        ).aggregate(total=Sum("balance_due"))["total"] or Decimal("0")

        return self.format_result(
            value={
                "current": current,
                "30_days": days_30,
                "60_days": days_60,
                "90_plus": days_90_plus,
                "total": current + days_30 + days_60 + days_90_plus,
            },
            label="AR Aging Summary",
            format_type="currency",
        )

    def calculate_accounts_payable(self, period=None, filters=None):
        """Calculate total outstanding accounts payable."""
        from apps.vendor_bills.models import VendorBill

        total_ap = (
            VendorBill.objects.filter(
                status__in=["approved", "partial", "overdue"],
                is_deleted=False,
            ).aggregate(
                total=Sum(F("total") - F("amount_paid"))
            )["total"]
            or Decimal("0")
        )

        return self.format_result(
            value=total_ap,
            label="Accounts Payable",
            format_type="currency",
        )

    def calculate_ap_aging(self, period=None, filters=None):
        """Calculate AP aging summary in 30/60/90+ day buckets."""
        from apps.vendor_bills.models import VendorBill

        today = timezone.now().date()
        outstanding = VendorBill.objects.filter(
            status__in=["approved", "partial", "overdue"],
            is_deleted=False,
        ).annotate(
            outstanding=F("total") - F("amount_paid"),
        )

        current = outstanding.filter(due_date__gte=today).aggregate(
            total=Sum("outstanding")
        )["total"] or Decimal("0")

        days_30 = outstanding.filter(
            due_date__lt=today,
            due_date__gte=today - timedelta(days=30),
        ).aggregate(total=Sum("outstanding"))["total"] or Decimal("0")

        days_60 = outstanding.filter(
            due_date__lt=today - timedelta(days=30),
            due_date__gte=today - timedelta(days=60),
        ).aggregate(total=Sum("outstanding"))["total"] or Decimal("0")

        days_90_plus = outstanding.filter(
            due_date__lt=today - timedelta(days=60),
        ).aggregate(total=Sum("outstanding"))["total"] or Decimal("0")

        return self.format_result(
            value={
                "current": current,
                "30_days": days_30,
                "60_days": days_60,
                "90_plus": days_90_plus,
                "total": current + days_30 + days_60 + days_90_plus,
            },
            label="AP Aging Summary",
            format_type="currency",
        )

    def calculate_current_ratio(self, period=None, filters=None):
        """Calculate current ratio: Current Assets / Current Liabilities."""
        from apps.accounting.models import Account

        current_assets = (
            Account.objects.filter(
                account_type="asset",
                category="CURRENT",
                status="ACTIVE",
            ).aggregate(total=Sum("current_balance"))["total"]
            or Decimal("0")
        )

        current_liabilities = abs(
            Account.objects.filter(
                account_type="liability",
                category="CURRENT",
                status="ACTIVE",
            ).aggregate(total=Sum("current_balance"))["total"]
            or Decimal("1")
        )

        ratio = current_assets / current_liabilities if current_liabilities else Decimal("0")

        return self.format_result(
            value=round(ratio, 2),
            label="Current Ratio",
            format_type="decimal",
            current_assets=current_assets,
            current_liabilities=current_liabilities,
        )

    def calculate_quick_ratio(self, period=None, filters=None):
        """Calculate quick ratio: (Current Assets - Inventory) / Current Liabilities."""
        from apps.accounting.models import Account

        current_assets = (
            Account.objects.filter(
                account_type="asset",
                category="CURRENT",
                status="ACTIVE",
            ).aggregate(total=Sum("current_balance"))["total"]
            or Decimal("0")
        )

        # Subtract inventory value from current assets
        inventory_value = (
            Account.objects.filter(
                account_type="asset",
                status="ACTIVE",
                name__icontains="inventory",
            ).aggregate(total=Sum("current_balance"))["total"]
            or Decimal("0")
        )

        current_liabilities = abs(
            Account.objects.filter(
                account_type="liability",
                category="CURRENT",
                status="ACTIVE",
            ).aggregate(total=Sum("current_balance"))["total"]
            or Decimal("1")
        )

        quick_assets = current_assets - inventory_value
        ratio = quick_assets / current_liabilities if current_liabilities else Decimal("0")

        return self.format_result(
            value=round(ratio, 2),
            label="Quick Ratio",
            format_type="decimal",
        )

    def calculate_revenue_trend(self, period=None, filters=None):
        """Generate monthly revenue data for trend chart (last 12 months)."""
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1) - timedelta(days=365)

        monthly_revenue = (
            self._get_posted_journal_lines(start_date, end_date)
            .filter(account__account_type="revenue")
            .annotate(month=TruncMonth("journal_entry__entry_date"))
            .values("month")
            .annotate(
                revenue=Sum("credit_amount") - Sum("debit_amount"),
            )
            .order_by("month")
        )

        items = [
            {
                "month": str(m["month"].date()) if m["month"] else "",
                "revenue": abs(m["revenue"] or Decimal("0")),
            }
            for m in monthly_revenue
        ]

        return self.format_result(
            value=items,
            label="Revenue Trend",
            format_type="number",
        )

    def calculate(self, kpi_code: str, period: str = "month") -> dict:
        """Route to the appropriate financial KPI calculation."""
        methods = {
            "revenue": self.calculate_revenue,
            "expenses": self.calculate_expenses,
            "net_income": self.calculate_net_income,
            "gross_profit_margin": self.calculate_gross_profit_margin,
            "net_profit_margin": self.calculate_net_profit_margin,
            "cash_position": self.calculate_cash_position,
            "accounts_receivable": self.calculate_accounts_receivable,
            "ar_aging": self.calculate_ar_aging,
            "accounts_payable": self.calculate_accounts_payable,
            "ap_aging": self.calculate_ap_aging,
            "current_ratio": self.calculate_current_ratio,
            "quick_ratio": self.calculate_quick_ratio,
            "revenue_trend": self.calculate_revenue_trend,
        }
        method = methods.get(kpi_code)
        if method is None:
            return {"error": f"Unknown financial KPI: {kpi_code}"}
        return method(period)
