"""Vendor performance serializer."""

from rest_framework import serializers
from apps.vendors.models import VendorPerformance


class VendorPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for VendorPerformance."""
    class Meta:
        model = VendorPerformance
        fields = [
            "id", "period_start", "period_end",
            "on_time_delivery_rate", "quality_score",
            "avg_response_time_hours", "overall_rating",
            "total_orders_count", "orders_on_time", "orders_late",
            "items_received", "items_defective",
            "calculated_at",
        ]
        read_only_fields = fields
