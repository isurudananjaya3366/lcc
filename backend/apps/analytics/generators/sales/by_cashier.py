"""
Sales by cashier report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class SalesByCashierReport(BaseReportGenerator):
    """Sales breakdown by cashier/staff with performance metrics."""

    REPORT_TYPE = "SALES_BY_CASHIER"

    def get_base_queryset(self):
        from apps.invoices.models import Invoice

        return Invoice.objects.filter(
            status__in=["ISSUED", "PAID", "PARTIAL"],
            is_deleted=False,
            created_by__isnull=False,
        ).select_related("created_by")

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()
        qs = self.apply_date_filter(qs, "issue_date")

        aggregated = (
            qs.values(
                "created_by_id",
                first_name=F("created_by__first_name"),
                last_name=F("created_by__last_name"),
                user_email=F("created_by__email"),
            )
            .annotate(
                transaction_count=Count("id"),
                total_sales=Coalesce(
                    Sum("total"), Value(0), output_field=DecimalField()
                ),
                avg_transaction_value=Coalesce(
                    Avg("total"), Value(0), output_field=DecimalField()
                ),
            )
            .order_by("-total_sales")
        )

        # Get team average for comparison
        team_total = sum(
            (r["total_sales"] or Decimal("0")) for r in aggregated
        )
        team_count = len(aggregated) or 1
        team_avg = float(team_total / team_count) if team_count else 0

        data = []
        for rank, row in enumerate(aggregated, 1):
            total = float(row["total_sales"] or 0)
            first = row["first_name"] or ""
            last = row["last_name"] or ""
            cashier_name = f"{first} {last}".strip() or row["user_email"] or "Unknown"

            # Performance level based on comparison to team average
            if team_avg:
                ratio = total / team_avg
            else:
                ratio = 1.0
            if ratio >= 1.2:
                level = "Excellent"
            elif ratio >= 0.9:
                level = "Good"
            elif ratio >= 0.7:
                level = "Average"
            else:
                level = "Below Average"

            data.append(
                {
                    "rank": rank,
                    "cashier_id": str(row["created_by_id"]) if row["created_by_id"] else None,
                    "cashier_name": cashier_name,
                    "transaction_count": row["transaction_count"],
                    "total_sales": total,
                    "avg_transaction_value": float(
                        row["avg_transaction_value"] or 0
                    ),
                    "vs_team_average": round(
                        (total - team_avg) / team_avg * 100
                        if team_avg
                        else 0,
                        2,
                    ),
                    "performance_level": level,
                }
            )

        totals = self.calculate_totals(
            data, ["transaction_count", "total_sales"]
        )
        return self.build_response(data, totals)
