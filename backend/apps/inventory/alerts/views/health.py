"""Stock health overview endpoint."""

import logging
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventory.alerts.models import StockAlert
from apps.inventory.alerts.serializers import StockHealthSerializer
from apps.inventory.stock.models import StockLevel

logger = logging.getLogger(__name__)


class StockHealthView(APIView):
    """
    GET /inventory/health/

    Stock health score and category breakdown.
    Health = 100 - (OOS% × 2 + LowStock% × 1 + Critical% × 0.5), clamped [0-100].

    Query params:
    - warehouse: UUID — filter by warehouse
    - category: UUID — filter by product category
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        warehouse_id = request.query_params.get("warehouse")
        category_id = request.query_params.get("category")

        # 10-minute cache per filter combination
        cache_key = f"stock_health:{warehouse_id or 'all'}:{category_id or 'all'}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        levels = StockLevel.objects.all()
        if warehouse_id:
            levels = levels.filter(warehouse_id=warehouse_id)
        if category_id:
            levels = levels.filter(product__category_id=category_id)

        total = levels.count()

        if total == 0:
            data = StockHealthSerializer(
                {
                    "health_score": 100.0,
                    "health_category": "excellent",
                    "total_products": 0,
                    "healthy_count": 0,
                    "low_stock_count": 0,
                    "critical_count": 0,
                    "out_of_stock_count": 0,
                    "healthy_percentage": 100.0,
                    "low_stock_percentage": 0.0,
                    "critical_percentage": 0.0,
                    "out_of_stock_percentage": 0.0,
                    "categories_at_risk": [],
                    "trend": "stable",
                    "last_calculated": timezone.now(),
                }
            ).data
            cache.set(cache_key, data, timeout=600)
            return Response(data)

        # Count problematic stock levels
        oos = levels.filter(quantity=0).count()
        # Low stock: open low-stock alerts
        alert_base = StockAlert.objects.filter(status__in=["active", "acknowledged"])
        if warehouse_id:
            alert_base = alert_base.filter(warehouse_id=warehouse_id)
        if category_id:
            alert_base = alert_base.filter(product__category_id=category_id)

        low_stock_product_ids = (
            alert_base.filter(alert_type="low_stock")
            .values_list("product_id", flat=True)
            .distinct()
        )
        low = levels.filter(product_id__in=low_stock_product_ids).exclude(quantity=0).count()

        # Critical: high-priority alerts (priority >= 3 = critical/OOS level)
        critical_product_ids = (
            alert_base.filter(alert_type="critical_stock")
            .values_list("product_id", flat=True)
            .distinct()
        )
        critical = levels.filter(product_id__in=critical_product_ids).exclude(quantity=0).count()
        healthy = total - oos - low - critical

        oos_pct = (oos / total) * 100
        low_pct = (low / total) * 100
        crit_pct = (critical / total) * 100
        healthy_pct = (healthy / total) * 100

        score = max(0.0, min(100.0, 100 - (oos_pct * 2 + low_pct * 1 + crit_pct * 0.5)))
        category = self._get_category(score)

        # Categories at risk
        cats = (
            alert_base
            .values("product__category__name")
            .annotate(cnt=Count("id"))
            .order_by("-cnt")[:5]
        )
        categories_at_risk = [
            {"category": c["product__category__name"] or "Uncategorized", "alert_count": c["cnt"]}
            for c in cats
        ]

        trend = self._calculate_trend(warehouse_id, category_id)

        data = {
            "health_score": round(score, 2),
            "health_category": category,
            "total_products": total,
            "healthy_count": healthy,
            "low_stock_count": low,
            "critical_count": critical,
            "out_of_stock_count": oos,
            "healthy_percentage": round(healthy_pct, 2),
            "low_stock_percentage": round(low_pct, 2),
            "critical_percentage": round(crit_pct, 2),
            "out_of_stock_percentage": round(oos_pct, 2),
            "categories_at_risk": categories_at_risk,
            "trend": trend,
            "last_calculated": timezone.now(),
        }
        result = StockHealthSerializer(data).data
        cache.set(cache_key, result, timeout=600)
        return Response(result)

    @staticmethod
    def _get_category(score):
        if score >= 90:
            return "excellent"
        if score >= 75:
            return "good"
        if score >= 60:
            return "fair"
        if score >= 40:
            return "poor"
        return "critical"

    @staticmethod
    def _calculate_trend(warehouse_id=None, category_id=None):
        """Compare resolved vs new alerts in last 7 days."""
        week_ago = timezone.now() - timedelta(days=7)
        base = StockAlert.objects.all()
        if warehouse_id:
            base = base.filter(warehouse_id=warehouse_id)
        if category_id:
            base = base.filter(product__category_id=category_id)

        resolved = base.filter(
            status="resolved", resolved_at__gte=week_ago
        ).count()
        new_alerts = base.filter(created_at__gte=week_ago).count()
        if new_alerts == 0 and resolved == 0:
            return "stable"
        if resolved > new_alerts:
            return "improving"
        if new_alerts > resolved:
            return "declining"
        return "stable"
