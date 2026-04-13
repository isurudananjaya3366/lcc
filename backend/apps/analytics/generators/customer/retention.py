"""
Customer retention report generator.

Measures repeat purchase behaviour, retention/churn rates,
and cohort-based analysis over a given period.
"""

from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.db.models.functions import TruncMonth
from django.db.models.query import QuerySet
from django.utils import timezone

from apps.analytics.generators.base import BaseReportGenerator


class CustomerRetentionReport(BaseReportGenerator):
    """Analyse customer retention, churn, and repeat purchase behaviour."""

    REPORT_TYPE = "CUSTOMER_RETENTION"
    DEFAULT_CHURN_MONTHS = 3

    def get_base_queryset(self) -> QuerySet:
        from apps.customers.models import Customer

        return Customer.objects.filter(is_deleted=False, status="active")

    # ── Generate ──────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()

        churn_months = int(
            self.get_filter_value("churn_months", self.DEFAULT_CHURN_MONTHS)
        )
        churn_cutoff = timezone.now().date() - timedelta(days=churn_months * 30)

        total_customers = qs.count()

        # Repeat = order_count >= 2
        repeat_customers = qs.filter(order_count__gte=2).count()
        one_time_customers = qs.filter(order_count=1).count()
        zero_purchase = qs.filter(order_count=0).count()

        retention_rate = (
            round(repeat_customers / total_customers * 100, 2)
            if total_customers
            else Decimal("0")
        )

        # Churn = had at least 1 purchase but none since cutoff
        churned_qs = qs.filter(
            order_count__gte=1,
            last_purchase_date__lt=churn_cutoff,
        )
        churn_count = churned_qs.count()
        active_purchasers = qs.filter(order_count__gte=1).count()
        churn_rate = (
            round(churn_count / active_purchasers * 100, 2)
            if active_purchasers
            else Decimal("0")
        )

        # ── Repeat purchase metrics ──────────────────────────────
        repeat_metrics = qs.filter(order_count__gte=2).aggregate(
            avg_orders=Avg("order_count"),
            avg_value=Avg("total_purchases"),
            total_value=Sum("total_purchases"),
        )

        # ── Cohort analysis (by acquisition month) ───────────────
        cohort_data = (
            qs.filter(first_purchase_date__isnull=False)
            .annotate(cohort=TruncMonth("created_on"))
            .values("cohort")
            .annotate(
                cohort_size=Count("id"),
                repeat_count=Count("id", filter=Q(order_count__gte=2)),
                churned=Count(
                    "id",
                    filter=Q(
                        order_count__gte=1,
                        last_purchase_date__lt=churn_cutoff,
                    ),
                ),
                avg_lifetime_value=Avg("total_purchases"),
            )
            .order_by("cohort")
        )
        cohorts: list[dict[str, Any]] = []
        for row in cohort_data:
            cohort_size = row["cohort_size"]
            cohorts.append(
                {
                    "cohort": (
                        row["cohort"].strftime("%Y-%m") if row["cohort"] else ""
                    ),
                    "cohort_size": cohort_size,
                    "repeat_count": row["repeat_count"],
                    "retention_rate": (
                        round(row["repeat_count"] / cohort_size * 100, 2)
                        if cohort_size
                        else 0
                    ),
                    "churned": row["churned"],
                    "avg_lifetime_value": float(
                        row["avg_lifetime_value"] or 0
                    ),
                }
            )

        # ── Churn risk segmentation ──────────────────────────────
        now = timezone.now().date()
        segments = {
            "low_risk": qs.filter(
                last_purchase_date__gte=now - timedelta(days=30),
            ).count(),
            "medium_risk": qs.filter(
                last_purchase_date__lt=now - timedelta(days=30),
                last_purchase_date__gte=now - timedelta(days=60),
            ).count(),
            "high_risk": qs.filter(
                last_purchase_date__lt=now - timedelta(days=60),
                last_purchase_date__gte=now - timedelta(days=90),
            ).count(),
            "churned": churn_count,
        }

        # ── Build response ────────────────────────────────────────
        data = cohorts
        totals = {
            "total_customers": total_customers,
            "repeat_customers": repeat_customers,
            "one_time_customers": one_time_customers,
            "zero_purchase_customers": zero_purchase,
            "retention_rate": float(retention_rate),
            "churn_count": churn_count,
            "churn_rate": float(churn_rate),
            "avg_repeat_orders": float(repeat_metrics["avg_orders"] or 0),
            "avg_repeat_value": float(repeat_metrics["avg_value"] or 0),
            "total_repeat_value": float(repeat_metrics["total_value"] or 0),
        }
        chart_data = {
            "cohort_retention": cohorts,
            "churn_risk_segments": segments,
        }

        response = self.build_response(data, totals=totals, chart_data=chart_data)
        response["churn_risk_segments"] = segments
        return response
