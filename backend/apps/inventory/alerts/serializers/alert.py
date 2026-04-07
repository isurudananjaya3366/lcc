"""Serializers for StockAlert and dashboard views."""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.inventory.alerts.constants import ALERT_STATUS_CHOICES, ALERT_TYPE_CHOICES
from apps.inventory.alerts.models import StockAlert

from .config import ProductSummarySerializer, WarehouseSummarySerializer

User = get_user_model()


# ── Nested helpers ──────────────────────────────────────────────────


class UserSummarySerializer(serializers.Serializer):
    """Minimal user info for nesting."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


# ── StockAlert serializers ──────────────────────────────────────────


class StockAlertSerializer(serializers.ModelSerializer):
    """
    Full serializer for StockAlert with nested relationships.

    Includes human-readable displays and action availability flags.
    """

    product = ProductSummarySerializer(read_only=True)
    warehouse = WarehouseSummarySerializer(read_only=True, allow_null=True)
    acknowledged_by = UserSummarySerializer(read_only=True, allow_null=True)

    alert_type_display = serializers.CharField(
        source="get_alert_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    is_snoozed = serializers.SerializerMethodField()
    priority_level = serializers.SerializerMethodField()
    days_since_created = serializers.SerializerMethodField()

    can_acknowledge = serializers.SerializerMethodField()
    can_resolve = serializers.SerializerMethodField()
    can_snooze = serializers.SerializerMethodField()

    class Meta:
        model = StockAlert
        fields = [
            "id",
            "product",
            "warehouse",
            "alert_type",
            "alert_type_display",
            "status",
            "status_display",
            "priority",
            "priority_level",
            "threshold_value",
            "current_stock",
            "message",
            "created_at",
            "updated_at",
            "acknowledged_at",
            "acknowledged_by",
            "resolved_at",
            "snoozed_until",
            "is_snoozed",
            "days_since_created",
            "can_acknowledge",
            "can_resolve",
            "can_snooze",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "acknowledged_at",
            "acknowledged_by",
            "resolved_at",
        ]

    def get_is_snoozed(self, obj):
        if not obj.snoozed_until:
            return False
        return obj.snoozed_until > timezone.now()

    def get_priority_level(self, obj):
        if obj.priority >= 8:
            return "critical"
        if obj.priority >= 6:
            return "high"
        if obj.priority >= 4:
            return "medium"
        return "low"

    def get_days_since_created(self, obj):
        return (timezone.now() - obj.created_at).days

    def get_can_acknowledge(self, obj):
        return obj.status == "active" and obj.acknowledged_at is None

    def get_can_resolve(self, obj):
        return obj.status in ("active", "acknowledged")

    def get_can_snooze(self, obj):
        return obj.status == "active" and not self.get_is_snoozed(obj)

    def validate_snoozed_until(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Snooze date must be in the future")
        return value

    def validate_priority(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Priority must be between 1 and 10")
        return value


class StockAlertListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for alert lists."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    warehouse_name = serializers.CharField(
        source="warehouse.name", read_only=True, default=None
    )

    alert_type_display = serializers.CharField(
        source="get_alert_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = StockAlert
        fields = [
            "id",
            "product_name",
            "product_sku",
            "warehouse_name",
            "alert_type",
            "alert_type_display",
            "status",
            "status_display",
            "priority",
            "current_stock",
            "created_at",
            "acknowledged_at",
        ]
        read_only_fields = fields


# ── Dashboard serializers ───────────────────────────────────────────


class AlertDashboardSerializer(serializers.Serializer):
    """Dashboard summary serializer for stock alerts."""

    total_active_alerts = serializers.IntegerField()
    total_acknowledged = serializers.IntegerField()
    total_snoozed = serializers.IntegerField()
    total_resolved_today = serializers.IntegerField()

    by_type = serializers.DictField(child=serializers.IntegerField())
    by_priority = serializers.DictField(child=serializers.IntegerField())
    by_warehouse = serializers.DictField(child=serializers.IntegerField())

    recent_alerts = StockAlertListSerializer(many=True)
    recent_resolutions = StockAlertListSerializer(many=True)

    products_at_risk = serializers.ListField(child=serializers.DictField())

    last_updated = serializers.DateTimeField()
    monitoring_status = serializers.CharField()


class StockHealthSerializer(serializers.Serializer):
    """Overall stock health metrics."""

    health_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    health_category = serializers.CharField()

    total_products = serializers.IntegerField()

    out_of_stock_count = serializers.IntegerField()
    out_of_stock_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

    low_stock_count = serializers.IntegerField()
    low_stock_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

    critical_count = serializers.IntegerField()
    critical_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

    healthy_count = serializers.IntegerField()
    healthy_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

    categories_at_risk = serializers.ListField(child=serializers.DictField())

    trend = serializers.CharField()

    last_calculated = serializers.DateTimeField()
