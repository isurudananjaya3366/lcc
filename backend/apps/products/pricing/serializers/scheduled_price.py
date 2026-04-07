"""
ScheduledPrice and FlashSale serializers.
"""

from rest_framework import serializers

from ..models import FlashSale, ScheduledPrice
from ..utils import format_lkr


class ScheduledPriceSerializer(serializers.ModelSerializer):
    price_formatted = serializers.SerializerMethodField()
    is_active_now = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledPrice
        fields = [
            "id",
            "product",
            "variant",
            "name",
            "description",
            "sale_price",
            "price_formatted",
            "start_datetime",
            "end_datetime",
            "status",
            "priority",
            "is_active_now",
            "is_pending",
            "is_expired",
            "days_remaining",
            "created_by",
        ]
        read_only_fields = ["id", "status", "is_active_now", "is_pending", "is_expired", "days_remaining", "created_by"]

    def get_price_formatted(self, obj):
        return format_lkr(obj.sale_price)

    def get_days_remaining(self, obj):
        from django.utils import timezone

        if obj.is_expired:
            return 0
        delta = obj.end_datetime - timezone.now()
        return max(0, delta.days)

    def validate(self, data):
        start = data.get("start_datetime")
        end = data.get("end_datetime")
        if start and end and end <= start:
            raise serializers.ValidationError({"end_datetime": "Must be after start_datetime."})
        product = data.get("product")
        variant = data.get("variant")
        if not product and not variant:
            raise serializers.ValidationError("Must specify a product or variant.")
        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class FlashSaleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="scheduled_price.name", read_only=True)
    sale_price = serializers.DecimalField(source="scheduled_price.sale_price", max_digits=12, decimal_places=2, read_only=True)
    start_datetime = serializers.DateTimeField(source="scheduled_price.start_datetime", read_only=True)
    end_datetime = serializers.DateTimeField(source="scheduled_price.end_datetime", read_only=True)
    status = serializers.CharField(source="scheduled_price.status", read_only=True)
    quantity_remaining = serializers.IntegerField(read_only=True)
    percent_sold = serializers.FloatField(read_only=True)
    urgency_level = serializers.CharField(read_only=True)
    urgency_message = serializers.SerializerMethodField()

    class Meta:
        model = FlashSale
        fields = [
            "scheduled_price",
            "name",
            "sale_price",
            "start_datetime",
            "end_datetime",
            "status",
            "max_quantity",
            "quantity_sold",
            "quantity_remaining",
            "percent_sold",
            "is_sold_out",
            "urgency_level",
            "urgency_message",
        ]
        read_only_fields = [
            "quantity_sold",
            "quantity_remaining",
            "percent_sold",
            "is_sold_out",
            "urgency_level",
        ]

    def get_urgency_message(self, obj):
        return obj.get_urgency_message()
