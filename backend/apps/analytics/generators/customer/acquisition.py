"""
Customer acquisition report generator.

Tracks new customer acquisition volume, source/channel breakdown,
and first-purchase metrics over a given period.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.db.models.functions import TruncMonth
from django.db.models.query import QuerySet

from apps.analytics.generators.base import BaseReportGenerator


class CustomerAcquisitionReport(BaseReportGenerator):
    """Analyse new customer acquisition by channel and first-purchase value."""

    REPORT_TYPE = "CUSTOMER_ACQUISITION"

    def get_base_queryset(self) -> QuerySet:
        from apps.customers.models import Customer

        qs = Customer.objects.filter(is_deleted=False)
        qs = self.apply_date_filter(qs, date_field="created_on")
        return qs

    # ── Generate ──────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()

        total_new = qs.count()

        # ── Channel breakdown ─────────────────────────────────────
        channel_data = (
            qs.values("source")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        channels: list[dict[str, Any]] = []
        for row in channel_data:
            source = row["source"] or "unknown"
            count = row["count"]
            pct = round(count / total_new * 100, 2) if total_new else Decimal("0")
            channels.append(
                {
                    "channel": source,
                    "count": count,
                    "percentage": float(pct),
                }
            )

        # ── First purchase metrics ────────────────────────────────
        first_purchase_qs = qs.filter(first_purchase_date__isnull=False)
        customers_with_purchase = first_purchase_qs.count()
        purchase_rate = (
            round(customers_with_purchase / total_new * 100, 2) if total_new else 0
        )

        purchase_metrics = qs.aggregate(
            avg_value=Avg("total_purchases"),
            min_value=Min("total_purchases"),
            max_value=Max("total_purchases"),
            total_value=Sum("total_purchases"),
        )

        first_purchase = {
            "customers_with_purchase": customers_with_purchase,
            "purchase_rate": float(purchase_rate),
            "avg_first_order_value": float(purchase_metrics["avg_value"] or 0),
            "min_first_order_value": float(purchase_metrics["min_value"] or 0),
            "max_first_order_value": float(purchase_metrics["max_value"] or 0),
            "total_first_order_value": float(purchase_metrics["total_value"] or 0),
        }

        # ── Monthly trend ─────────────────────────────────────────
        monthly = (
            qs.annotate(month=TruncMonth("created_on"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        trend: list[dict[str, Any]] = [
            {
                "period": row["month"].strftime("%Y-%m") if row["month"] else "",
                "count": row["count"],
            }
            for row in monthly
        ]

        # ── Build response ────────────────────────────────────────
        data = channels
        totals = {
            "total_new_customers": total_new,
            "customers_with_purchase": customers_with_purchase,
            "purchase_rate": float(purchase_rate),
        }
        chart_data = {
            "channel_breakdown": channels,
            "monthly_trend": trend,
        }

        response = self.build_response(data, totals=totals, chart_data=chart_data)
        response["first_purchase_metrics"] = first_purchase
        return response
