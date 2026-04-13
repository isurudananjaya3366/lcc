"""Dashboard serializers for KPI data and layout configuration."""

from rest_framework import serializers

from apps.dashboard.models import DashboardLayout, KPIAlert, KPIDefinition


class KPIDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for KPI definition metadata."""

    class Meta:
        model = KPIDefinition
        fields = [
            "id",
            "name",
            "code",
            "description",
            "category",
            "default_widget_type",
            "format_type",
            "is_active",
            "sort_order",
        ]
        read_only_fields = fields


class KPIResultSerializer(serializers.Serializer):
    """Serializer for a single KPI calculation result."""

    value = serializers.FloatField()
    label = serializers.CharField()
    change = serializers.FloatField(required=False, allow_null=True)
    extra = serializers.DictField(required=False, default=dict)


class KPICategorySerializer(serializers.Serializer):
    """Serializer for a category of KPI results."""

    category = serializers.CharField()
    kpis = serializers.DictField(child=KPIResultSerializer())


class KPIAlertSerializer(serializers.ModelSerializer):
    """Serializer for KPI alert configuration."""

    kpi_name = serializers.CharField(source="kpi.name", read_only=True)
    kpi_code = serializers.CharField(source="kpi.code", read_only=True)

    class Meta:
        model = KPIAlert
        fields = [
            "id",
            "kpi",
            "kpi_name",
            "kpi_code",
            "warning_threshold",
            "critical_threshold",
            "comparison",
            "notify_email",
            "notify_dashboard",
            "is_active",
            "last_triggered",
        ]
        read_only_fields = ["id", "kpi_name", "kpi_code", "last_triggered"]


class DashboardLayoutSerializer(serializers.ModelSerializer):
    """Serializer for user dashboard layout configuration."""

    class Meta:
        model = DashboardLayout
        fields = [
            "id",
            "name",
            "widgets",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_widgets(self, value):
        """Validate widget configuration structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Widgets must be a JSON object.")
        if "widgets" in value and not isinstance(value["widgets"], list):
            raise serializers.ValidationError(
                "widgets.widgets must be a list."
            )
        return value


class DashboardAllKPIsSerializer(serializers.Serializer):
    """Serializer for the combined all-KPIs response."""

    sales = serializers.DictField()
    inventory = serializers.DictField()
    financial = serializers.DictField()
    hr = serializers.DictField()
    alerts = KPIAlertSerializer(many=True, required=False)
