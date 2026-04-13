"""
Vendor performance report generator.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.analytics.generators.base import BaseReportGenerator


class VendorPerformanceReport(BaseReportGenerator):
    """Multi-dimensional vendor evaluation with scoring."""

    REPORT_TYPE = "VENDOR_PERFORMANCE"

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
                vendor_payment_terms=F("vendor__payment_terms_days"),
            )
            .annotate(
                order_count=Count("id"),
                total_amount=Coalesce(
                    Sum("total"), Value(0), output_field=DecimalField()
                ),
                paid_amount=Coalesce(
                    Sum("amount_paid"), Value(0), output_field=DecimalField()
                ),
            )
            .order_by("-total_amount")
        )

        # Count on-time deliveries per vendor
        from apps.purchases.models import PurchaseOrder

        data = []
        for row in aggregated:
            vid = row["vendor_id"]
            vendor_qs = qs.filter(vendor_id=vid)

            # Delivery performance
            total_orders = row["order_count"]
            delivered = vendor_qs.filter(received_at__isnull=False)
            on_time = delivered.filter(
                received_at__lte=F("expected_delivery_date")
            ).count()
            delivered_count = delivered.count()
            delivery_rate = (
                on_time / delivered_count * 100 if delivered_count else 100
            )

            # Lead time
            lead_times = []
            for po in delivered:
                if po.order_date and po.received_at:
                    days = (po.received_at.date() - po.order_date).days
                    if days >= 0:
                        lead_times.append(days)
            avg_lead_time = (
                sum(lead_times) / len(lead_times) if lead_times else 0
            )

            # Payment compliance
            total = row["total_amount"] or Decimal("0")
            paid = row["paid_amount"] or Decimal("0")
            payment_pct = float(paid / total * 100) if total else 0

            # Composite score (simplified)
            delivery_score = min(delivery_rate, 100) * 0.40
            lead_score = max(0, 100 - avg_lead_time * 2) * 0.30
            payment_score = min(payment_pct, 100) * 0.30
            total_score = round(delivery_score + lead_score + payment_score, 1)

            if total_score >= 90:
                rating = "A"
            elif total_score >= 80:
                rating = "B"
            elif total_score >= 70:
                rating = "C"
            elif total_score >= 60:
                rating = "D"
            else:
                rating = "F"

            data.append(
                {
                    "vendor_id": str(vid) if vid else None,
                    "vendor_code": row["vendor_code"] or "",
                    "vendor_name": row["vendor_name"] or "Unknown",
                    "order_count": total_orders,
                    "total_amount": float(total),
                    "delivery_rate": round(delivery_rate, 2),
                    "avg_lead_time_days": round(avg_lead_time, 1),
                    "payment_compliance": round(payment_pct, 2),
                    "performance_score": total_score,
                    "rating": rating,
                }
            )

        data.sort(key=lambda r: r["performance_score"], reverse=True)
        totals = self.calculate_totals(data, ["order_count", "total_amount"])
        return self.build_response(data, totals)
