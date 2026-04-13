"""Base KPI calculator — abstract base class for all KPI calculators."""

import abc
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.dashboard.enums import KPIPeriod


class BaseKPICalculator(abc.ABC):
    """Abstract base class that all KPI calculators must extend.

    Implements the Strategy pattern for flexible KPI calculations.
    Each concrete calculator implements domain-specific KPI computations.
    """

    def get_date_range(self, period: str) -> tuple[date, date]:
        """Return (start_date, end_date) for the given KPIPeriod."""
        today = timezone.now().date()

        if period == KPIPeriod.TODAY:
            return today, today
        elif period == KPIPeriod.YESTERDAY:
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        elif period == KPIPeriod.WEEK:
            start = today - timedelta(days=today.weekday())
            return start, today
        elif period == KPIPeriod.LAST_WEEK:
            end = today - timedelta(days=today.weekday() + 1)
            start = end - timedelta(days=6)
            return start, end
        elif period == KPIPeriod.MONTH:
            start = today.replace(day=1)
            return start, today
        elif period == KPIPeriod.LAST_MONTH:
            end = today.replace(day=1) - timedelta(days=1)
            start = end.replace(day=1)
            return start, end
        elif period == KPIPeriod.QUARTER:
            quarter_month = ((today.month - 1) // 3) * 3 + 1
            start = today.replace(month=quarter_month, day=1)
            return start, today
        elif period == KPIPeriod.YEAR:
            start = today.replace(month=1, day=1)
            return start, today
        elif period == KPIPeriod.LAST_YEAR:
            start = today.replace(year=today.year - 1, month=1, day=1)
            end = today.replace(year=today.year - 1, month=12, day=31)
            return start, end
        else:
            return today, today

    def get_previous_date_range(self, period: str) -> tuple[date, date]:
        """Return the previous period date range for comparison."""
        start, end = self.get_date_range(period)
        duration = (end - start).days + 1
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=duration - 1)
        return prev_start, prev_end

    def calculate_change(
        self, current: Decimal, previous: Decimal
    ) -> dict:
        """Calculate change percentage and trend direction."""
        if previous and previous != 0:
            change_percent = ((current - previous) / abs(previous)) * 100
        else:
            change_percent = Decimal("0")

        if current > previous:
            trend = "up"
        elif current < previous:
            trend = "down"
        else:
            trend = "stable"

        return {
            "previous_value": previous,
            "change_percent": round(change_percent, 2),
            "trend": trend,
        }

    def format_result(
        self,
        value,
        label: str,
        format_type: str = "number",
        **kwargs,
    ) -> dict:
        """Build a standard KPI result dict."""
        result = {
            "value": value,
            "label": label,
            "format_type": format_type,
        }
        result.update(kwargs)
        return result

    @abc.abstractmethod
    def calculate(self, period: str, filters: dict | None = None) -> list[dict]:
        """Calculate all KPIs for this calculator.

        Args:
            period: KPIPeriod value.
            filters: Optional filters (location, category, etc.).

        Returns:
            List of KPI result dicts.
        """
