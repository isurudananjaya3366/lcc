"""Views for StockAlert and Alert Dashboard."""

import logging
from datetime import timedelta

from django.core.cache import cache
from django.db import models, transaction
from django.db.models import Count, Max, Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django_filters import rest_framework as django_filters
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventory.alerts.constants import ALERT_STATUS_CHOICES, ALERT_TYPE_CHOICES
from apps.inventory.alerts.models import ReorderSuggestion, StockAlert
from apps.inventory.alerts.serializers import (
    AlertDashboardSerializer,
    ReorderSuggestionListSerializer,
    StockAlertListSerializer,
    StockAlertSerializer,
)

logger = logging.getLogger(__name__)


# ── Filters ─────────────────────────────────────────────────────────


class StockAlertFilter(django_filters.FilterSet):
    """Filter set for StockAlert."""

    alert_type = django_filters.CharFilter(field_name="alert_type")
    status = django_filters.CharFilter(field_name="status")
    priority_min = django_filters.NumberFilter(field_name="priority", lookup_expr="gte")
    priority_max = django_filters.NumberFilter(field_name="priority", lookup_expr="lte")
    warehouse = django_filters.UUIDFilter(field_name="warehouse_id")
    product = django_filters.UUIDFilter(field_name="product_id")
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    is_acknowledged = django_filters.BooleanFilter(method="filter_acknowledged")
    is_snoozed = django_filters.BooleanFilter(method="filter_snoozed")

    class Meta:
        model = StockAlert
        fields = [
            "alert_type",
            "status",
            "priority_min",
            "priority_max",
            "warehouse",
            "product",
        ]

    def filter_acknowledged(self, queryset, name, value):
        if value:
            return queryset.exclude(acknowledged_at__isnull=True)
        return queryset.filter(acknowledged_at__isnull=True)

    def filter_snoozed(self, queryset, name, value):
        now = timezone.now()
        if value:
            return queryset.filter(snoozed_until__gt=now)
        return queryset.filter(
            models.Q(snoozed_until__isnull=True) | models.Q(snoozed_until__lte=now)
        )


# ── StockAlertViewSet ───────────────────────────────────────────────


class StockAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only list/retrieve with lifecycle actions.

    Endpoints:
        GET  /alerts/                       - List
        GET  /alerts/{id}/                  - Retrieve
        POST /alerts/{id}/acknowledge/      - Acknowledge
        POST /alerts/{id}/snooze/           - Snooze
        POST /alerts/{id}/resolve/          - Resolve
        POST /alerts/bulk_acknowledge/      - Bulk acknowledge
        GET  /alerts/statistics/            - Aggregated stats
    """

    queryset = StockAlert.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = StockAlertFilter
    search_fields = ["product__name", "product__sku", "message"]
    ordering_fields = ["created_at", "priority", "acknowledged_at", "resolved_at"]
    ordering = ["-priority", "-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return StockAlertListSerializer
        return StockAlertSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("product", "warehouse", "acknowledged_by")
        )

    # ── Lifecycle actions ───────────────────────────────────────

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        """Mark alert as acknowledged by current user."""
        alert = self.get_object()
        if alert.acknowledged_at:
            return Response(
                {"error": "Alert already acknowledged"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if alert.status != "active":
            return Response(
                {"error": "Only active alerts can be acknowledged"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.status = "acknowledged"
        alert.save()
        return Response(StockAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def snooze(self, request, pk=None):
        """
        Snooze alert until specified time.

        Body: {"snoozed_until": "2025-01-25T10:00:00Z"}
        """
        alert = self.get_object()
        raw = request.data.get("snoozed_until")
        if not raw:
            return Response(
                {"error": "snoozed_until is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            snooze_dt = parse_datetime(str(raw))
            if not snooze_dt:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid datetime format"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if snooze_dt <= timezone.now():
            return Response(
                {"error": "Snooze time must be in the future"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if alert.status != "active":
            return Response(
                {"error": "Only active alerts can be snoozed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        alert.snoozed_until = snooze_dt
        alert.save()
        return Response(StockAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Resolve an alert manually."""
        alert = self.get_object()
        if alert.status not in ("active", "acknowledged"):
            return Response(
                {"error": "Alert cannot be resolved"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        alert.status = "resolved"
        alert.resolved_at = timezone.now()
        alert.save()
        return Response(StockAlertSerializer(alert).data)

    @action(detail=False, methods=["post"])
    def bulk_acknowledge(self, request):
        """
        Acknowledge multiple alerts.

        Body: {"alert_ids": ["<uuid>", ...]}
        """
        alert_ids = request.data.get("alert_ids", [])
        if not alert_ids or not isinstance(alert_ids, list):
            return Response(
                {"error": "alert_ids list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            updated = StockAlert.objects.filter(
                id__in=alert_ids,
                status="active",
                acknowledged_at__isnull=True,
            ).update(
                acknowledged_at=timezone.now(),
                acknowledged_by=request.user,
                status="acknowledged",
            )
        return Response(
            {"acknowledged_count": updated, "message": f"{updated} alerts acknowledged"}
        )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Aggregated alert statistics."""
        qs = self.filter_queryset(self.get_queryset())
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        by_type = {}
        for item in qs.values("alert_type").annotate(count=Count("id")):
            by_type[item["alert_type"]] = item["count"]

        return Response(
            {
                "total_active": qs.filter(status="active").count(),
                "total_acknowledged": qs.filter(status="acknowledged").count(),
                "total_resolved": qs.filter(status="resolved").count(),
                "created_today": qs.filter(created_at__gte=today_start).count(),
                "resolved_today": qs.filter(resolved_at__gte=today_start).count(),
                "by_type": by_type,
                "by_priority": {
                    "critical": qs.filter(priority__gte=8).count(),
                    "high": qs.filter(priority__range=(6, 7)).count(),
                    "medium": qs.filter(priority__range=(4, 5)).count(),
                    "low": qs.filter(priority__lte=3).count(),
                },
            }
        )


# ── AlertDashboardView ──────────────────────────────────────────────


class AlertDashboardView(APIView):
    """
    Dashboard summary for stock alerts.

    GET /alerts/dashboard/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 5-minute cache for dashboard data (Task 49)
        cache_key = f"alert_dashboard:{request.user.pk}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        alerts = StockAlert.objects.select_related("product", "warehouse")

        # Summary counts
        total_active = alerts.filter(status="active").count()
        total_acknowledged = alerts.filter(status="acknowledged").count()
        total_snoozed = alerts.filter(status="active", snoozed_until__gt=now).count()
        total_resolved_today = alerts.filter(resolved_at__gte=today_start).count()

        # By type
        by_type = {}
        for item in (
            alerts.filter(status="active")
            .values("alert_type")
            .annotate(count=Count("id"))
        ):
            by_type[item["alert_type"]] = item["count"]

        # By priority
        active = alerts.filter(status="active")
        by_priority = {
            "critical": active.filter(priority__gte=8).count(),
            "high": active.filter(priority__range=(6, 7)).count(),
            "medium": active.filter(priority__range=(4, 5)).count(),
            "low": active.filter(priority__lte=3).count(),
        }

        # By warehouse
        by_warehouse = {}
        for item in (
            active.values("warehouse__name").annotate(count=Count("id"))
        ):
            by_warehouse[item["warehouse__name"] or "All Warehouses"] = item["count"]

        # Recent alerts & resolutions
        recent_alerts = StockAlertListSerializer(
            alerts.order_by("-created_at")[:5], many=True
        ).data
        recent_resolutions = StockAlertListSerializer(
            alerts.filter(status="resolved").order_by("-resolved_at")[:5], many=True
        ).data

        # Products at risk
        products_at_risk_qs = (
            active.values("product_id", "product__name", "product__sku")
            .annotate(alert_count=Count("id"), highest_priority=Max("priority"))
            .order_by("-highest_priority", "-alert_count")[:10]
        )
        products_at_risk = []
        for item in products_at_risk_qs:
            suggestion = ReorderSuggestion.objects.filter(
                product_id=item["product_id"], status="pending"
            ).first()
            d = suggestion.days_until_stockout if suggestion else None
            products_at_risk.append(
                {
                    "product_id": str(item["product_id"]),
                    "product_name": item["product__name"],
                    "sku": item["product__sku"],
                    "alert_count": item["alert_count"],
                    "highest_priority": item["highest_priority"],
                    "days_until_stockout": float(d) if d is not None else None,
                }
            )

        dashboard_data = {
            "total_active_alerts": total_active,
            "total_acknowledged": total_acknowledged,
            "total_snoozed": total_snoozed,
            "total_resolved_today": total_resolved_today,
            "by_type": by_type,
            "by_priority": by_priority,
            "by_warehouse": by_warehouse,
            "recent_alerts": recent_alerts,
            "recent_resolutions": recent_resolutions,
            "products_at_risk": products_at_risk,
            "last_updated": now,
            "monitoring_status": "active",
        }

        serializer = AlertDashboardSerializer(data=dashboard_data)
        serializer.is_valid(raise_exception=True)

        # Cache for 5 minutes
        cache.set(cache_key, serializer.data, timeout=300)

        return Response(serializer.data)


# ── Product Alerts View (Task 77) ──────────────────────────────────


class ProductAlertsView(APIView):
    """
    GET /alerts/products/<product_id>/alerts/

    Returns active alerts, recent history, reorder suggestions,
    and statistics for a specific product.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        from django.db.models import Avg, F

        warehouse_id = request.query_params.get("warehouse")
        alert_status = request.query_params.get("status")
        days = int(request.query_params.get("days", 30))
        days = min(max(days, 1), 365)

        cutoff = timezone.now() - timedelta(days=days)

        # Base alert queryset for this product
        alerts_qs = StockAlert.objects.filter(
            product_id=product_id,
        ).select_related("warehouse")
        if warehouse_id:
            alerts_qs = alerts_qs.filter(warehouse_id=warehouse_id)

        # Active alerts
        active_qs = alerts_qs.filter(status__in=["active", "acknowledged"])
        if alert_status:
            active_qs = alerts_qs.filter(status=alert_status)
        active_alerts = StockAlertListSerializer(
            active_qs.order_by("-created_at")[:20], many=True
        ).data

        # Recent history (resolved)
        history = StockAlertListSerializer(
            alerts_qs.filter(
                status="resolved",
                resolved_at__gte=cutoff,
            ).order_by("-resolved_at")[:20],
            many=True,
        ).data

        # Reorder suggestions
        suggestions_qs = ReorderSuggestion.objects.filter(
            product_id=product_id, status="pending"
        )
        if warehouse_id:
            suggestions_qs = suggestions_qs.filter(warehouse_id=warehouse_id)
        suggestions = ReorderSuggestionListSerializer(
            suggestions_qs.order_by("-urgency")[:10], many=True
        ).data

        # Statistics
        by_type = {}
        for item in (
            alerts_qs.filter(created_at__gte=cutoff)
            .values("alert_type")
            .annotate(count=Count("id"))
        ):
            by_type[item["alert_type"]] = item["count"]

        resolved_with_times = alerts_qs.filter(
            status="resolved",
            resolved_at__isnull=False,
            created_at__gte=cutoff,
        ).annotate(
            resolution_seconds=models.ExpressionWrapper(
                F("resolved_at") - F("created_at"),
                output_field=models.DurationField(),
            )
        )
        avg_res = resolved_with_times.aggregate(avg=Avg("resolution_seconds"))
        avg_hours = None
        if avg_res["avg"]:
            avg_hours = round(avg_res["avg"].total_seconds() / 3600, 2)

        return Response(
            {
                "product_id": str(product_id),
                "active_alerts": active_alerts,
                "recent_history": history,
                "reorder_suggestions": suggestions,
                "statistics": {
                    "by_type": by_type,
                    "total_active": active_qs.count(),
                    "total_in_period": alerts_qs.filter(created_at__gte=cutoff).count(),
                    "avg_resolution_time_hours": avg_hours,
                },
            }
        )
