"""
Stock movement report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class StockMovementReport(BaseReportGenerator):
    """Stock in/out transactions with running balance."""

    REPORT_TYPE = "STOCK_MOVEMENT"

    def get_base_queryset(self):
        from apps.inventory.models import StockMovement

        return StockMovement.objects.filter(
            is_reversed=False,
        ).select_related("product", "from_warehouse", "to_warehouse", "created_by")

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()
        qs = self.apply_date_filter(qs, "movement_date")

        # Filters
        movement_types = self.get_filter_value("movement_types")
        if movement_types:
            qs = qs.filter(movement_type__in=movement_types)

        location_ids = self.get_filter_value("location_ids")
        if location_ids:
            qs = qs.filter(
                from_warehouse_id__in=location_ids
            ) | qs.filter(to_warehouse_id__in=location_ids)

        product_ids = self.get_filter_value("product_ids")
        if product_ids:
            qs = qs.filter(product_id__in=product_ids)

        qs = qs.order_by("movement_date", "id")

        # Build data with running balance
        running_balances: dict[str, Decimal] = {}  # keyed by product_id
        data = []
        for mov in qs:
            product_key = str(mov.product_id)
            qty = mov.quantity or Decimal("0")

            if mov.movement_type in ("STOCK_IN",):
                delta = qty
            elif mov.movement_type in ("STOCK_OUT",):
                delta = -qty
            elif mov.movement_type == "ADJUSTMENT":
                delta = qty  # can be negative
            else:
                delta = Decimal("0")

            balance = running_balances.get(product_key, Decimal("0")) + delta
            running_balances[product_key] = balance

            first = mov.created_by.first_name if mov.created_by else ""
            last = mov.created_by.last_name if mov.created_by else ""
            user_name = f"{first} {last}".strip() or (
                mov.created_by.username if mov.created_by else ""
            )

            data.append(
                {
                    "movement_id": str(mov.id),
                    "movement_date": (
                        mov.movement_date.isoformat() if mov.movement_date else None
                    ),
                    "product_id": product_key,
                    "product_name": mov.product.name if mov.product else "Unknown",
                    "sku": mov.product.sku if mov.product else "",
                    "movement_type": mov.movement_type,
                    "quantity": float(qty),
                    "from_warehouse": (
                        mov.from_warehouse.name if mov.from_warehouse else ""
                    ),
                    "to_warehouse": (
                        mov.to_warehouse.name if mov.to_warehouse else ""
                    ),
                    "reference_number": mov.reference_number or "",
                    "reason": mov.reason or "",
                    "cost_per_unit": float(mov.cost_per_unit or 0),
                    "created_by": user_name,
                    "running_balance": float(balance),
                }
            )

        totals = self.calculate_totals(data, ["quantity"])
        totals["movement_count"] = len(data)
        return self.build_response(data, totals)
