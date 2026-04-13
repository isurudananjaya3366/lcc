"""
Stock level report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Case, CharField, DecimalField, F, Sum, Value, When
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class StockLevelReport(BaseReportGenerator):
    """Current stock levels by product/location/category with valuation."""

    REPORT_TYPE = "STOCK_LEVEL"

    def get_base_queryset(self):
        from apps.inventory.models import StockLevel

        return StockLevel.objects.select_related(
            "product", "product__category", "warehouse"
        )

    def generate(self) -> dict[str, Any]:
        self.start_timer()
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

        include_zero = self.get_filter_value("include_zero_stock", False)
        if not include_zero:
            qs = qs.filter(quantity__gt=0)

        # Annotate stock status
        qs = qs.annotate(
            available=F("quantity") - F("reserved_quantity"),
            stock_value=F("quantity") * F("cost_per_unit"),
            stock_status=Case(
                When(quantity__lte=0, then=Value("OUT_OF_STOCK")),
                When(quantity__lte=F("reorder_point"), then=Value("LOW_STOCK")),
                default=Value("IN_STOCK"),
                output_field=CharField(),
            ),
        )

        data = []
        for row in qs.order_by("product__name"):
            data.append(
                {
                    "product_id": str(row.product_id),
                    "product_name": row.product.name,
                    "sku": row.product.sku or "",
                    "category": (
                        row.product.category.name
                        if row.product.category
                        else "Uncategorised"
                    ),
                    "warehouse": row.warehouse.name if row.warehouse else "Default",
                    "quantity": float(row.quantity),
                    "reserved": float(row.reserved_quantity),
                    "available": float(row.available),
                    "cost_per_unit": float(row.cost_per_unit or 0),
                    "stock_value": float(row.stock_value or 0),
                    "reorder_point": float(row.reorder_point or 0),
                    "stock_status": row.stock_status,
                    "abc_classification": row.abc_classification or "C",
                }
            )

        totals = self.calculate_totals(
            data, ["quantity", "reserved", "available", "stock_value"]
        )
        return self.build_response(data, totals)
