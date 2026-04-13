"""
Purchase by vendor report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class PurchaseByVendorReport(BaseReportGenerator):
    """Purchase analysis grouped by vendor with ranking and payment status."""

    REPORT_TYPE = "PURCHASE_VENDOR"

    def get_base_queryset(self):
        from apps.purchases.models import PurchaseOrder

        return PurchaseOrder.objects.exclude(
            status__in=["draft", "cancelled"]
        ).select_related("vendor")

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()
        qs = self.apply_date_filter(qs, "order_date")

        vendor_ids = self.get_filter_value("vendor_ids")
        if vendor_ids:
            qs = qs.filter(vendor_id__in=vendor_ids)

        aggregated = (
            qs.values(
                "vendor_id",
                vendor_code=F("vendor__vendor_code"),
                vendor_name=F("vendor__company_name"),
            )
            .annotate(
                order_count=Count("id"),
                total_amount=Coalesce(
                    Sum("total"), Value(0), output_field=DecimalField()
                ),
                paid_amount=Coalesce(
                    Sum("amount_paid"), Value(0), output_field=DecimalField()
                ),
                avg_order_value=Coalesce(
                    Avg("total"), Value(0), output_field=DecimalField()
                ),
            )
            .order_by("-total_amount")
        )

        grand_total = sum(
            (r["total_amount"] or Decimal("0")) for r in aggregated
        )

        data = []
        for rank, row in enumerate(aggregated, 1):
            total = row["total_amount"] or Decimal("0")
            paid = row["paid_amount"] or Decimal("0")
            pending = total - paid
            payment_pct = float(paid / total * 100) if total else 0.0

            if payment_pct >= 100:
                payment_status = "PAID"
            elif payment_pct > 0:
                payment_status = "PARTIAL"
            else:
                payment_status = "UNPAID"

            # Tiering
            if rank <= 5:
                tier = "A"
            elif rank <= 15:
                tier = "B"
            else:
                tier = "C"

            data.append(
                {
                    "rank": rank,
                    "vendor_id": str(row["vendor_id"]) if row["vendor_id"] else None,
                    "vendor_code": row["vendor_code"] or "",
                    "vendor_name": row["vendor_name"] or "Unknown",
                    "order_count": row["order_count"],
                    "total_amount": float(total),
                    "paid_amount": float(paid),
                    "pending_amount": float(pending),
                    "payment_percentage": round(payment_pct, 2),
                    "payment_status": payment_status,
                    "avg_order_value": float(row["avg_order_value"] or 0),
                    "spend_percentage": (
                        round(float(total / grand_total * 100), 2)
                        if grand_total
                        else 0.0
                    ),
                    "tier": tier,
                }
            )

        totals = self.calculate_totals(
            data, ["order_count", "total_amount", "paid_amount", "pending_amount"]
        )
        return self.build_response(data, totals)
