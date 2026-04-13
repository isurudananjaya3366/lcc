"""
Purchase by category report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class PurchaseByCategoryReport(BaseReportGenerator):
    """Purchase analysis grouped by product category with breakdown."""

    REPORT_TYPE = "PURCHASE_CATEGORY"

    def get_base_queryset(self):
        from apps.purchases.models import POLineItem

        return POLineItem.objects.filter(
            purchase_order__status__in=["confirmed", "received", "closed"],
        ).select_related(
            "purchase_order", "product", "product__category"
        )

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()
        qs = self.apply_date_filter(qs, "purchase_order__order_date")

        category_ids = self.get_filter_value("category_ids")
        if category_ids:
            qs = qs.filter(product__category_id__in=category_ids)

        aggregated = (
            qs.values(
                category_id=F("product__category_id"),
                category_name=F("product__category__name"),
            )
            .annotate(
                total_items=Coalesce(
                    Sum("quantity_ordered"), Value(0), output_field=DecimalField()
                ),
                order_count=Count("purchase_order_id", distinct=True),
                total_amount=Coalesce(
                    Sum("line_total"), Value(0), output_field=DecimalField()
                ),
                avg_price=Coalesce(
                    Avg("unit_price"), Value(0), output_field=DecimalField()
                ),
            )
            .order_by("-total_amount")
        )

        grand_total = sum(
            (r["total_amount"] or Decimal("0")) for r in aggregated
        )

        data = []
        cumulative_pct = 0.0
        for row in aggregated:
            total = row["total_amount"] or Decimal("0")
            pct = float(total / grand_total * 100) if grand_total else 0.0
            cumulative_pct += pct

            if pct >= 20:
                size = "Large"
            elif pct >= 10:
                size = "Medium"
            else:
                size = "Small"

            data.append(
                {
                    "category_id": str(row["category_id"]) if row["category_id"] else None,
                    "category_name": row["category_name"] or "Uncategorised",
                    "total_items": float(row["total_items"] or 0),
                    "order_count": row["order_count"],
                    "total_amount": float(total),
                    "avg_price": float(row["avg_price"] or 0),
                    "percentage": round(pct, 2),
                    "cumulative_percentage": round(cumulative_pct, 2),
                    "size_class": size,
                }
            )

        totals = self.calculate_totals(
            data, ["total_items", "order_count", "total_amount"]
        )
        return self.build_response(data, totals)
