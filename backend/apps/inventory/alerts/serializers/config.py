"""Serializers for stock configuration models."""

from decimal import Decimal

from rest_framework import serializers

from apps.inventory.alerts.models import GlobalStockSettings, ProductStockConfig
from apps.inventory.alerts.services import ConfigResolver


# ── Nested summary serializers ──────────────────────────────────────


class ProductSummarySerializer(serializers.Serializer):
    """Minimal product info for nesting."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    sku = serializers.CharField(read_only=True)


class WarehouseSummarySerializer(serializers.Serializer):
    """Minimal warehouse info for nesting."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)


# ── ProductStockConfig ──────────────────────────────────────────────


class ProductStockConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductStockConfig with effective configuration.

    Includes inherited values from category and global settings.
    """

    # Nested read-only fields
    product = ProductSummarySerializer(read_only=True)
    warehouse = WarehouseSummarySerializer(read_only=True, allow_null=True)

    # Write-only ID fields
    product_id = serializers.UUIDField(write_only=True)
    warehouse_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    # Calculated field
    effective_config = serializers.SerializerMethodField()

    class Meta:
        model = ProductStockConfig
        fields = [
            "id",
            "product",
            "product_id",
            "warehouse",
            "warehouse_id",
            "low_stock_threshold",
            "reorder_point",
            "reorder_quantity",
            "auto_hide_when_oos",
            "allow_backorder",
            "preferred_supplier",
            "lead_time_days",
            "exclude_from_monitoring",
            "exclusion_reason",
            "allow_auto_reorder",
            "effective_config",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on", "effective_config"]

    def get_effective_config(self, obj):
        """
        Get effective configuration including inherited values.

        Returns dict with all config values and their sources.
        """
        effective = ConfigResolver.resolve_for_product(
            product=obj.product,
            warehouse=obj.warehouse,
        )
        sources = effective.get("sources", {})
        return {
            "low_stock_threshold": {
                "value": float(effective["low_stock_threshold"])
                if effective.get("low_stock_threshold")
                else None,
                "source": sources.get("low_stock_threshold", self._get_config_source(obj, "low_stock_threshold")),
            },
            "reorder_point": {
                "value": float(effective["reorder_point"]) if effective.get("reorder_point") else None,
                "source": sources.get("reorder_point", self._get_config_source(obj, "reorder_point")),
            },
            "reorder_quantity": {
                "value": float(effective["reorder_quantity"])
                if effective.get("reorder_quantity")
                else None,
                "source": sources.get("reorder_quantity", self._get_config_source(obj, "reorder_quantity")),
            },
            "auto_hide_when_oos": {
                "value": effective.get("auto_hide_when_oos"),
                "source": sources.get("auto_hide_when_oos", self._get_config_source(obj, "auto_hide_when_oos")),
            },
            "allow_backorder": {
                "value": effective.get("allow_backorder"),
                "source": sources.get("allow_backorder", self._get_config_source(obj, "allow_backorder")),
            },
        }

    @staticmethod
    def _get_config_source(obj, field_name):
        """Determine where config value comes from."""
        if getattr(obj, field_name, None) is not None:
            return "product"

        # Check category
        try:
            cat = obj.product.category
            if cat:
                cat_cfg = getattr(cat, "stock_config", None)
                if cat_cfg and getattr(cat_cfg, field_name, None) is not None:
                    return "category"
        except Exception:
            pass

        return "global"

    def validate_low_stock_threshold(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Low stock threshold must be >= 0")
        return value

    def validate_reorder_quantity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Reorder quantity must be > 0")
        return value

    def validate(self, data):
        low_threshold = data.get("low_stock_threshold")
        reorder_point = data.get("reorder_point")
        if low_threshold and reorder_point and reorder_point < low_threshold:
            raise serializers.ValidationError(
                "Reorder point should be >= low stock threshold"
            )
        return data


# ── GlobalStockSettings ─────────────────────────────────────────────


class GlobalStockSettingsSerializer(serializers.ModelSerializer):
    """Serializer for GlobalStockSettings (singleton per tenant)."""

    class Meta:
        model = GlobalStockSettings
        fields = [
            "id",
            "default_low_threshold",
            "default_reorder_point",
            "default_reorder_qty",
            "enable_auto_reorder",
            "monitoring_frequency",
            "monitoring_start_hour",
            "monitoring_end_hour",
            "use_eoq_calculation",
            "ordering_cost_lkr",
            "holding_cost_percent",
            "target_service_level",
            "safety_stock_days",
            "auto_reorder_enabled",
            "auto_reorder_min_urgency",
            "auto_reorder_max_value_lkr",
            "reorder_suggestions_enabled",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]
