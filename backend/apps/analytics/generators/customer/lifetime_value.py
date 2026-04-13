"""
Customer lifetime value report generator.

Calculates historical and predicted CLV per customer with
tier segmentation (High / Medium / Low).
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, F, Max, Min, Sum
from django.db.models.functions import Coalesce, ExtractDay
from django.db.models.query import QuerySet

from apps.analytics.generators.base import BaseReportGenerator


class CustomerLifetimeValueReport(BaseReportGenerator):
    """Calculate CLV per customer and segment by tier."""

    REPORT_TYPE = "CUSTOMER_LIFETIME_VALUE"

    def get_base_queryset(self) -> QuerySet:
        from apps.customers.models import Customer

        qs = Customer.objects.filter(
            is_deleted=False,
            order_count__gte=1,
        )
        customer_type = self.get_filter_value("customer_type")
        if customer_type:
            qs = qs.filter(customer_type=customer_type)
        segment = self.get_filter_value("segment")
        if segment:
            # Will be filtered after CLV calculation
            pass
        return qs

    # ── Generate ──────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()

        customers: list[dict[str, Any]] = []
        for c in qs.iterator():
            historical_value = float(c.total_purchases or 0)
            order_count = c.order_count or 0
            avg_order_value = (
                round(historical_value / order_count, 2) if order_count else 0
            )

            # Predicted CLV = AOV × Frequency × Estimated Lifespan (years)
            # Estimated lifespan based on tenure so far, minimum 1 year
            tenure_days = 0
            if c.first_purchase_date and c.last_purchase_date:
                tenure_days = (c.last_purchase_date - c.first_purchase_date).days

            tenure_years = max(tenure_days / 365, 1)
            annual_frequency = order_count / tenure_years if tenure_years else 0
            predicted_annual = avg_order_value * annual_frequency
            # Predict 3-year forward value
            predicted_clv = round(predicted_annual * 3, 2)
            total_clv = round(historical_value + predicted_clv, 2)

            customers.append(
                {
                    "customer_id": str(c.id),
                    "customer_name": c.display_name or f"{c.first_name} {c.last_name}".strip(),
                    "customer_code": c.customer_code,
                    "customer_type": c.customer_type,
                    "order_count": order_count,
                    "historical_value": historical_value,
                    "avg_order_value": avg_order_value,
                    "tenure_days": tenure_days,
                    "annual_frequency": round(annual_frequency, 2),
                    "predicted_clv": predicted_clv,
                    "total_clv": total_clv,
                }
            )

        # Sort descending by CLV
        customers.sort(key=lambda x: x["total_clv"], reverse=True)

        # ── Tier segmentation ─────────────────────────────────────
        total = len(customers)
        if total:
            top_20_idx = max(int(total * 0.2), 1)
            bottom_20_idx = total - max(int(total * 0.2), 1)
            for i, row in enumerate(customers):
                if i < top_20_idx:
                    row["tier"] = "high"
                elif i >= bottom_20_idx:
                    row["tier"] = "low"
                else:
                    row["tier"] = "medium"
                row["rank"] = i + 1
        else:
            pass  # empty list

        # Filter by segment if requested
        segment = self.get_filter_value("segment")
        if segment and segment in ("high", "medium", "low"):
            customers = [c for c in customers if c["tier"] == segment]

        # ── Tier summary ──────────────────────────────────────────
        tier_summary: dict[str, Any] = {}
        for tier in ("high", "medium", "low"):
            tier_rows = [c for c in customers if c.get("tier") == tier]
            tier_summary[tier] = {
                "count": len(tier_rows),
                "total_clv": round(sum(r["total_clv"] for r in tier_rows), 2),
                "avg_clv": (
                    round(
                        sum(r["total_clv"] for r in tier_rows) / len(tier_rows), 2
                    )
                    if tier_rows
                    else 0
                ),
            }

        # ── Aggregates ────────────────────────────────────────────
        all_clv = [c["total_clv"] for c in customers]
        totals = {
            "total_customers": len(customers),
            "total_clv": round(sum(all_clv), 2) if all_clv else 0,
            "avg_clv": (
                round(sum(all_clv) / len(all_clv), 2) if all_clv else 0
            ),
            "max_clv": max(all_clv) if all_clv else 0,
            "min_clv": min(all_clv) if all_clv else 0,
        }
        chart_data = {
            "tier_distribution": tier_summary,
            "top_10": customers[:10],
        }

        response = self.build_response(data=customers, totals=totals, chart_data=chart_data)
        response["tier_summary"] = tier_summary
        return response
