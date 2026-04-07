"""
Analytics service for barcode scan data.

Analyses usage patterns, identifies hot/cold locations, and generates
optimisation recommendations for warehouse layout.
"""

import logging

from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class ScanAnalytics:
    """Analyse barcode scan patterns for warehouse optimisation."""

    def __init__(self, days=30):
        self.days = days
        self.start_date = timezone.now() - timezone.timedelta(days=days)

    def _base_qs(self, success_only=True):
        from apps.inventory.warehouses.models import BarcodeScan

        qs = BarcodeScan.objects.filter(created_on__gte=self.start_date)
        if success_only:
            qs = qs.filter(success=True)
        return qs

    # ── frequency / hot-cold ──────────────────────────────────────────

    def get_scan_frequency(self, location=None):
        qs = self._base_qs()
        if location:
            return qs.filter(location=location).count()
        return list(
            qs.values("location__code")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

    def get_hot_locations(self, limit=20):
        return list(
            self._base_qs()
            .values("location__code", "location__warehouse__name")
            .annotate(scan_count=Count("id"))
            .order_by("-scan_count")[:limit]
        )

    def get_cold_locations(self, limit=20):
        return list(
            self._base_qs()
            .values("location__code", "location__warehouse__name")
            .annotate(scan_count=Count("id"))
            .order_by("scan_count")[:limit]
        )

    # ── trends & distribution ─────────────────────────────────────────

    def get_scan_trends(self, period="day"):
        qs = self._base_qs()
        if period == "day":
            return list(
                qs.values("created_on__date")
                .annotate(count=Count("id"))
                .order_by("created_on__date")
            )
        if period == "hour":
            return list(
                qs.values("created_on__hour")
                .annotate(count=Count("id"))
                .order_by("created_on__hour")
            )
        # week – group by iso_week_day is DB-specific; fall back to date
        return list(
            qs.values("created_on__date")
            .annotate(count=Count("id"))
            .order_by("created_on__date")
        )

    def get_scan_type_distribution(self):
        return list(
            self._base_qs(success_only=False)
            .values("scan_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

    # ── user & device ─────────────────────────────────────────────────

    def get_user_statistics(self):
        return list(
            self._base_qs(success_only=False)
            .values("user__username")
            .annotate(
                total_scans=Count("id"),
                successful_scans=Count("id", filter=Q(success=True)),
                failed_scans=Count("id", filter=Q(success=False)),
            )
            .order_by("-total_scans")
        )

    def get_device_performance(self):
        return list(
            self._base_qs(success_only=False)
            .filter(device_id__isnull=False)
            .values("device_id")
            .annotate(
                total_scans=Count("id"),
                successful_scans=Count("id", filter=Q(success=True)),
            )
            .order_by("-total_scans")
        )

    # ── error rate ────────────────────────────────────────────────────

    def get_error_rate(self):
        total = self._base_qs(success_only=False).count()
        if total == 0:
            return 0.0
        failed = self._base_qs(success_only=False).filter(success=False).count()
        return (failed / total) * 100

    # ── optimisation report ───────────────────────────────────────────

    def generate_optimization_report(self):
        hot = self.get_hot_locations(10)
        cold = self.get_cold_locations(10)
        error_rate = self.get_error_rate()

        recommendations = [
            {
                "type": "relocate_items",
                "description": "Move frequently picked items to more accessible locations",
                "hot_locations": hot[:3],
            },
            {
                "type": "audit_slow_items",
                "description": "Review rarely accessed items for obsolescence",
                "cold_locations": cold[:3],
            },
        ]
        if error_rate > 5:
            recommendations.append(
                {
                    "type": "improve_scanning",
                    "description": f"Investigate {error_rate:.1f}% failed scans",
                }
            )

        return {
            "period_days": self.days,
            "total_scans": self._base_qs(success_only=False).count(),
            "hot_locations": hot,
            "cold_locations": cold,
            "error_rate": error_rate,
            "recommendations": recommendations,
        }
