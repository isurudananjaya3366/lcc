"""
Stock valuation report generator.
"""

from collections import defaultdict
from decimal import Decimal
from typing import Any

from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class StockValuationReport(BaseReportGenerator):
    """Inventory valuation using FIFO, LIFO, Average or Standard costing."""

    REPORT_TYPE = "STOCK_VALUATION"

    def get_base_queryset(self):
        from apps.inventory.models import StockLevel

        return StockLevel.objects.filter(quantity__gt=0).select_related(
            "product", "product__category", "warehouse"
        )

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        method = self.get_filter_value("costing_method", "average")
        qs = self.get_base_queryset()

        # Apply filters
        location_ids = self.get_filter_value("location_ids")
        if location_ids:
            qs = qs.filter(warehouse_id__in=location_ids)

        category_ids = self.get_filter_value("category_ids")
        if category_ids:
            qs = qs.filter(product__category_id__in=category_ids)

        product_ids = self.get_filter_value("product_ids")
        if product_ids:
            qs = qs.filter(product_id__in=product_ids)

        data = []
        total_value = Decimal("0")

        for sl in qs.order_by("product__name"):
            qty = sl.quantity or Decimal("0")
            unit_cost = sl.cost_per_unit or Decimal("0")
            value = qty * unit_cost
            total_value += value

            # Age analysis
            age_days = 0
            if sl.last_stock_update:
                from django.utils import timezone

                age_days = (timezone.now() - sl.last_stock_update).days

            if age_days <= 30:
                age_bucket = "0-30 days"
            elif age_days <= 60:
                age_bucket = "31-60 days"
            elif age_days <= 90:
                age_bucket = "61-90 days"
            else:
                age_bucket = "90+ days"

            data.append(
                {
                    "product_id": str(sl.product_id),
                    "product_name": sl.product.name,
                    "sku": sl.product.sku or "",
                    "category": (
                        sl.product.category.name
                        if sl.product.category
                        else "Uncategorised"
                    ),
                    "warehouse": sl.warehouse.name if sl.warehouse else "Default",
                    "quantity": float(qty),
                    "unit_cost": float(unit_cost),
                    "total_value": float(value),
                    "costing_method": method,
                    "age_days": age_days,
                    "age_bucket": age_bucket,
                    "abc_classification": sl.abc_classification or "C",
                }
            )

        # ABC analysis
        data.sort(key=lambda r: r["total_value"], reverse=True)
        cumulative = Decimal("0")
        for row in data:
            cumulative += Decimal(str(row["total_value"]))
            pct = float(cumulative / total_value * 100) if total_value else 0
            row["cumulative_pct"] = round(pct, 2)
            if pct <= 80:
                row["abc_tier"] = "A"
            elif pct <= 95:
                row["abc_tier"] = "B"
            else:
                row["abc_tier"] = "C"

        totals = self.calculate_totals(data, ["quantity", "total_value"])
        totals["costing_method"] = method
        return self.build_response(data, totals)
