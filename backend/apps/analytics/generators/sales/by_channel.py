"""
Sales by channel report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Case, CharField, Count, DecimalField, Sum, Value, When
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator

CHANNEL_NAMES = {
    "POS": "Point of Sale",
    "WEBSTORE": "Online Store",
    "MOBILE": "Mobile App",
    "OTHER": "Other",
}


class SalesByChannelReport(BaseReportGenerator):
    """Sales comparison across channels (POS, Webstore, etc.)."""

    REPORT_TYPE = "SALES_BY_CHANNEL"

    def get_base_queryset(self):
        from apps.invoices.models import Invoice

        return Invoice.objects.filter(
            status__in=["ISSUED", "PAID", "PARTIAL"],
            is_deleted=False,
        )

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()
        qs = self.apply_date_filter(qs, "issue_date")

        # Derive channel from order source or fall back to POS
        qs = qs.annotate(
            channel=Case(
                When(order__source__isnull=False, then="order__source"),
                default=Value("POS"),
                output_field=CharField(),
            )
        )

        aggregated = (
            qs.values("channel")
            .annotate(
                order_count=Count("id"),
                total_revenue=Coalesce(
                    Sum("total"), Value(0), output_field=DecimalField()
                ),
                avg_order_value=Coalesce(
                    Avg("total"), Value(0), output_field=DecimalField()
                ),
            )
            .order_by("-total_revenue")
        )

        grand_revenue = sum(
            (r["total_revenue"] or Decimal("0")) for r in aggregated
        )
        grand_orders = sum((r["order_count"] or 0) for r in aggregated)

        data = []
        for row in aggregated:
            revenue = row["total_revenue"] or Decimal("0")
            orders = row["order_count"] or 0
            channel_code = (row["channel"] or "OTHER").upper()
            data.append(
                {
                    "channel": channel_code,
                    "channel_name": CHANNEL_NAMES.get(channel_code, channel_code),
                    "order_count": orders,
                    "total_revenue": float(revenue),
                    "avg_order_value": float(row["avg_order_value"] or 0),
                    "revenue_percentage": (
                        round(float(revenue / grand_revenue * 100), 2)
                        if grand_revenue
                        else 0.0
                    ),
                    "order_percentage": (
                        round(orders / grand_orders * 100, 2)
                        if grand_orders
                        else 0.0
                    ),
                }
            )

        totals = self.calculate_totals(data, ["order_count", "total_revenue"])
        return self.build_response(data, totals)
