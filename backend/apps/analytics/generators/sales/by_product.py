"""
Sales by product report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class SalesByProductReport(BaseReportGenerator):
    """Sales breakdown by product with rankings and percentages."""

    REPORT_TYPE = "SALES_BY_PRODUCT"

    def get_base_queryset(self):
        from apps.invoices.models import InvoiceLineItem

        return (
            InvoiceLineItem.objects.filter(
                invoice__status__in=["ISSUED", "PAID", "PARTIAL"],
                invoice__is_deleted=False,
            )
            .select_related("invoice", "product", "product__category")
        )

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()
        qs = self.apply_date_filter(qs, "invoice__issue_date")

        # Apply optional category filter
        category_ids = self.get_filter_value("category")
        if category_ids:
            qs = qs.filter(product__category_id__in=category_ids)

        # Apply optional product filter
        product_ids = self.get_filter_value("product")
        if product_ids:
            qs = qs.filter(product_id__in=product_ids)

        # Aggregate by product
        aggregated = (
            qs.values(
                "product_id",
                product_name=F("product__name"),
                product_sku=F("product__sku"),
                category_name=F("product__category__name"),
            )
            .annotate(
                quantity=Coalesce(
                    Sum("quantity"), Value(0), output_field=DecimalField()
                ),
                revenue=Coalesce(
                    Sum("line_total"), Value(0), output_field=DecimalField()
                ),
                avg_price=Coalesce(
                    Avg("unit_price"), Value(0), output_field=DecimalField()
                ),
            )
            .order_by("-revenue")
        )

        total_revenue = sum(
            (row["revenue"] or Decimal("0")) for row in aggregated
        )

        data = []
        for rank, row in enumerate(aggregated, 1):
            revenue = row["revenue"] or Decimal("0")
            pct = (
                float(revenue / total_revenue * 100)
                if total_revenue
                else 0.0
            )
            data.append(
                {
                    "rank": rank,
                    "product_id": str(row["product_id"]) if row["product_id"] else None,
                    "product_name": row["product_name"] or "Unknown",
                    "sku": row["product_sku"] or "",
                    "category": row["category_name"] or "Uncategorised",
                    "quantity": float(row["quantity"] or 0),
                    "revenue": float(revenue),
                    "avg_price": float(row["avg_price"] or 0),
                    "percentage": round(pct, 2),
                }
            )

        totals = self.calculate_totals(data, ["quantity", "revenue"])
        return self.build_response(data, totals)
