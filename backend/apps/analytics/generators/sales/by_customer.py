"""
Sales by customer report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class SalesByCustomerReport(BaseReportGenerator):
    """Sales breakdown by customer with rankings and order counts."""

    REPORT_TYPE = "SALES_BY_CUSTOMER"

    def get_base_queryset(self):
        from apps.invoices.models import Invoice

        return Invoice.objects.filter(
            status__in=["ISSUED", "PAID", "PARTIAL"],
            is_deleted=False,
            customer__isnull=False,
        ).select_related("customer")

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()
        qs = self.apply_date_filter(qs, "issue_date")

        aggregated = (
            qs.values(
                "customer_id",
                display_name=F("customer__display_name"),
            )
            .annotate(
                order_count=Count("id"),
                total_amount=Coalesce(
                    Sum("total"), Value(0), output_field=DecimalField()
                ),
                avg_order_value=Coalesce(
                    Avg("total"), Value(0), output_field=DecimalField()
                ),
            )
            .order_by("-total_amount")
        )

        data = []
        for rank, row in enumerate(aggregated, 1):
            data.append(
                {
                    "rank": rank,
                    "customer_id": str(row["customer_id"]) if row["customer_id"] else None,
                    "customer_name": row["display_name"] or "Unknown",
                    "order_count": row["order_count"],
                    "total_amount": float(row["total_amount"] or 0),
                    "avg_order_value": float(row["avg_order_value"] or 0),
                }
            )

        totals = self.calculate_totals(data, ["order_count", "total_amount"])
        return self.build_response(data, totals)
