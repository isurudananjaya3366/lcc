"""
Sales by period report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, DecimalField, Sum, Value
from django.db.models.functions import (
    Coalesce,
    TruncDay,
    TruncMonth,
    TruncQuarter,
    TruncWeek,
    TruncYear,
)

from apps.analytics.generators.base import BaseReportGenerator


class SalesByPeriodReport(BaseReportGenerator):
    """Time-series sales analysis with period grouping and trend data."""

    REPORT_TYPE = "SALES_BY_PERIOD"

    TRUNC_MAP = {
        "daily": TruncDay,
        "weekly": TruncWeek,
        "monthly": TruncMonth,
        "quarterly": TruncQuarter,
        "yearly": TruncYear,
    }

    def get_base_queryset(self):
        from apps.invoices.models import Invoice

        return Invoice.objects.filter(
            status__in=["ISSUED", "PAID", "PARTIAL"],
            is_deleted=False,
        )

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        grouping = self.get_filter_value("grouping", "daily")
        trunc_cls = self.TRUNC_MAP.get(grouping, TruncDay)

        qs = self.get_base_queryset()
        qs = self.apply_date_filter(qs, "issue_date")

        aggregated = (
            qs.annotate(period=trunc_cls("issue_date"))
            .values("period")
            .annotate(
                order_count=Count("id"),
                total_revenue=Coalesce(
                    Sum("total"), Value(0), output_field=DecimalField()
                ),
                avg_order_value=Coalesce(
                    Avg("total"), Value(0), output_field=DecimalField()
                ),
            )
            .order_by("period")
        )

        data = []
        cumulative = Decimal("0")
        prev_revenue = Decimal("0")

        for row in aggregated:
            revenue = row["total_revenue"] or Decimal("0")
            cumulative += revenue
            growth = revenue - prev_revenue if prev_revenue else Decimal("0")
            growth_pct = (
                float(growth / prev_revenue * 100) if prev_revenue else 0.0
            )

            period_dt = row["period"]
            data.append(
                {
                    "period": period_dt.isoformat() if period_dt else None,
                    "period_label": self._format_period(period_dt, grouping),
                    "order_count": row["order_count"],
                    "total_revenue": float(revenue),
                    "avg_order_value": float(row["avg_order_value"] or 0),
                    "cumulative_revenue": float(cumulative),
                    "revenue_growth": float(growth),
                    "revenue_growth_pct": round(growth_pct, 2),
                }
            )
            prev_revenue = revenue

        totals = self.calculate_totals(data, ["order_count", "total_revenue"])
        chart_data = self._get_chart_data(data)
        return self.build_response(data, totals, chart_data)

    # ── Private Helpers ───────────────────────────────────────────

    @staticmethod
    def _format_period(dt, grouping: str) -> str:
        if dt is None:
            return "Unknown"
        if grouping == "daily":
            return dt.strftime("%Y-%m-%d (%A)")
        if grouping == "weekly":
            return f"Week of {dt.strftime('%Y-%m-%d')}"
        if grouping == "monthly":
            return dt.strftime("%B %Y")
        if grouping == "quarterly":
            q = (dt.month - 1) // 3 + 1
            return f"Q{q} {dt.year}"
        if grouping == "yearly":
            return str(dt.year)
        return dt.isoformat()

    @staticmethod
    def _get_chart_data(data: list[dict[str, Any]]) -> dict[str, Any]:
        if not data:
            return {}
        revenues = [r["total_revenue"] for r in data]
        first_half = sum(revenues[: len(revenues) // 2]) if revenues else 0
        second_half = sum(revenues[len(revenues) // 2 :]) if revenues else 0
        if second_half > first_half:
            direction = "up"
        elif second_half < first_half:
            direction = "down"
        else:
            direction = "stable"

        return {
            "line_chart": [
                {
                    "period": r["period_label"],
                    "revenue": r["total_revenue"],
                    "orders": r["order_count"],
                }
                for r in data
            ],
            "trend": {
                "direction": direction,
                "highest_period": max(data, key=lambda r: r["total_revenue"])["period_label"] if data else None,
                "lowest_period": min(data, key=lambda r: r["total_revenue"])["period_label"] if data else None,
            },
        }
