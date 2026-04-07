"""
Reorder report and calendar services.

Generates summary reports grouped by urgency, category, supplier
and provides calendar-view of expected stockout dates.
"""

import logging
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


class ReorderReportService:
    """Generate reports for pending reorder suggestions."""

    @staticmethod
    def generate_reorder_report(include_dismissed=False):
        """
        Comprehensive reorder report with groupings and top-N lists.

        Returns dict with summary, groupings, and ranked lists.
        """
        from apps.inventory.alerts.models import ReorderSuggestion

        qs = ReorderSuggestion.objects.select_related(
            "product", "product__category", "suggested_supplier", "warehouse",
        )
        if not include_dismissed:
            qs = qs.filter(status="pending")

        summary = ReorderReportService.get_summary_statistics(qs)
        by_urgency = ReorderReportService.group_by_urgency(qs)
        by_category = ReorderReportService.group_by_category(qs)
        by_supplier = ReorderReportService.group_by_supplier(qs)

        top_by_value = list(qs.order_by("-estimated_cost")[:20])
        soonest_stockouts = list(
            qs.filter(days_until_stockout__isnull=False)
            .order_by("days_until_stockout")[:20]
        )

        return {
            "generated_at": timezone.now(),
            "summary": summary,
            "by_urgency": by_urgency,
            "by_category": by_category,
            "by_supplier": by_supplier,
            "top_by_value": top_by_value,
            "soonest_stockouts": soonest_stockouts,
        }

    @staticmethod
    def get_summary_statistics(suggestions):
        agg = suggestions.aggregate(
            total_count=Count("id"),
            total_cost=Sum("estimated_cost"),
            total_quantity=Sum("suggested_qty"),
            critical_count=Count("id", filter=Q(urgency="critical")),
            high_count=Count("id", filter=Q(urgency="high")),
            medium_count=Count("id", filter=Q(urgency="medium")),
            low_count=Count("id", filter=Q(urgency="low")),
        )
        return {
            "total_suggestions": agg["total_count"] or 0,
            "total_estimated_cost": agg["total_cost"] or Decimal("0"),
            "total_quantity": agg["total_quantity"] or Decimal("0"),
            "critical_count": agg["critical_count"] or 0,
            "high_count": agg["high_count"] or 0,
            "medium_count": agg["medium_count"] or 0,
            "low_count": agg["low_count"] or 0,
        }

    @staticmethod
    def group_by_urgency(suggestions):
        return list(
            suggestions.values("urgency")
            .annotate(count=Count("id"), total_cost=Sum("estimated_cost"), total_qty=Sum("suggested_qty"))
            .order_by("-urgency")
        )

    @staticmethod
    def group_by_category(suggestions):
        return list(
            suggestions.values("product__category__name")
            .annotate(count=Count("id"), total_cost=Sum("estimated_cost"), total_qty=Sum("suggested_qty"))
            .order_by("-total_cost")
        )

    @staticmethod
    def group_by_supplier(suggestions):
        return list(
            suggestions.filter(suggested_supplier__isnull=False)
            .values("suggested_supplier__name")
            .annotate(count=Count("id"), total_cost=Sum("estimated_cost"), total_qty=Sum("suggested_qty"))
            .order_by("-total_cost")
        )

    @staticmethod
    def format_for_email(report_data):
        """Return simple HTML summary suitable for email body."""
        s = report_data["summary"]
        html = (
            f"<h2>Reorder Report</h2>"
            f"<p>Generated: {report_data['generated_at']:%Y-%m-%d %H:%M}</p>"
            f"<table border='1' cellpadding='5'>"
            f"<tr><th>Metric</th><th>Value</th></tr>"
            f"<tr><td>Total Suggestions</td><td>{s['total_suggestions']}</td></tr>"
            f"<tr><td>Total Est. Cost (LKR)</td><td>{s['total_estimated_cost']:,.2f}</td></tr>"
            f"<tr><td>Critical</td><td>{s['critical_count']}</td></tr>"
            f"<tr><td>High</td><td>{s['high_count']}</td></tr>"
            f"<tr><td>Medium</td><td>{s['medium_count']}</td></tr>"
            f"<tr><td>Low</td><td>{s['low_count']}</td></tr>"
            f"</table>"
        )
        return html


class ReorderCalendarService:
    """Generate calendar-view data of expected stockout dates."""

    @staticmethod
    def get_stockout_calendar(year=None, month=None):
        """
        Return dict mapping date → list of suggestion summaries for
        the given *year*/*month*.
        """
        import calendar as cal
        from datetime import timedelta

        from apps.inventory.alerts.models import ReorderSuggestion

        now = timezone.now()
        year = year or now.year
        month = month or now.month

        _, last_day = cal.monthrange(year, month)
        start = timezone.datetime(year, month, 1).date()
        end = timezone.datetime(year, month, last_day).date()

        suggestions = (
            ReorderSuggestion.objects.filter(
                status="pending",
                days_until_stockout__isnull=False,
            )
            .select_related("product")
        )

        events_by_date = {}
        for s in suggestions:
            d = s.days_until_stockout
            if d is None:
                continue
            stockout_date = (now + timedelta(days=float(d))).date()
            if start <= stockout_date <= end:
                events_by_date.setdefault(stockout_date.isoformat(), []).append({
                    "suggestion_id": str(s.id),
                    "product_name": str(s.product),
                    "urgency": s.urgency,
                    "days_until_stockout": float(d),
                })

        return {
            "year": year,
            "month": month,
            "events": events_by_date,
        }

    @staticmethod
    def get_calendar_events(days_ahead=60):
        """
        Flat list of upcoming stockout events for the next *days_ahead* days.
        """
        from datetime import timedelta

        from apps.inventory.alerts.models import ReorderSuggestion

        now = timezone.now()
        suggestions = (
            ReorderSuggestion.objects.filter(
                status="pending",
                days_until_stockout__isnull=False,
                days_until_stockout__lte=days_ahead,
            )
            .select_related("product")
            .order_by("days_until_stockout")
        )

        events = []
        for s in suggestions:
            d = s.days_until_stockout
            if d is None:
                continue
            events.append({
                "suggestion_id": str(s.id),
                "product_name": str(s.product),
                "urgency": s.urgency,
                "stockout_date": (now + timedelta(days=float(d))).date().isoformat(),
                "days_until_stockout": float(d),
            })
        return events
