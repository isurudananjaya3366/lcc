"""LeaveBalance serializers for the Leave Management module."""

from django.utils import timezone
from rest_framework import serializers

from apps.leave.models import LeaveBalance


class EmployeeMinimalSerializer(serializers.Serializer):
    """Minimal employee representation for nested use."""

    id = serializers.UUIDField()
    employee_id = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class LeaveBalanceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for balance list views."""

    leave_type_name = serializers.SerializerMethodField()
    leave_type_code = serializers.SerializerMethodField()
    available_days = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True,
    )
    utilization_percentage = serializers.SerializerMethodField()
    balance_status = serializers.SerializerMethodField()

    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "employee",
            "leave_type",
            "leave_type_name",
            "leave_type_code",
            "year",
            "opening_balance",
            "allocated_days",
            "used_days",
            "pending_days",
            "carried_from_previous",
            "available_days",
            "utilization_percentage",
            "balance_status",
        ]
        read_only_fields = fields

    def get_leave_type_name(self, obj):
        return obj.leave_type.name if obj.leave_type else None

    def get_leave_type_code(self, obj):
        return obj.leave_type.code if obj.leave_type else None

    def get_utilization_percentage(self, obj):
        total = obj.opening_balance + obj.allocated_days + obj.carried_from_previous
        if not total:
            return 0
        return round(float(obj.used_days / total * 100), 1)

    def get_balance_status(self, obj):
        total = obj.opening_balance + obj.allocated_days + obj.carried_from_previous
        if not total:
            return "GOOD"
        pct = float(obj.available_days / total * 100)
        if pct >= 75:
            return "GOOD"
        if pct >= 50:
            return "HEALTHY"
        if pct >= 25:
            return "LOW"
        return "CRITICAL"


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Full balance serializer with nested employee and leave type."""

    employee_detail = EmployeeMinimalSerializer(source="employee", read_only=True)
    leave_type_name = serializers.SerializerMethodField()
    leave_type_code = serializers.SerializerMethodField()
    available_days = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True,
    )
    utilization_percentage = serializers.SerializerMethodField()
    balance_status = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "employee",
            "employee_detail",
            "leave_type",
            "leave_type_name",
            "leave_type_code",
            "year",
            "opening_balance",
            "allocated_days",
            "used_days",
            "pending_days",
            "encashed_days",
            "carried_from_previous",
            "carry_forward_expiry",
            "last_accrual_date",
            "is_active",
            "available_days",
            "utilization_percentage",
            "balance_status",
            "status_color",
            "days_until_expiry",
            "created_on",
            "updated_on",
        ]
        read_only_fields = fields

    def get_leave_type_name(self, obj):
        return obj.leave_type.name if obj.leave_type else None

    def get_leave_type_code(self, obj):
        return obj.leave_type.code if obj.leave_type else None

    def get_utilization_percentage(self, obj):
        total = obj.opening_balance + obj.allocated_days + obj.carried_from_previous
        if not total:
            return 0
        return round(float(obj.used_days / total * 100), 1)

    def get_balance_status(self, obj):
        total = obj.opening_balance + obj.allocated_days + obj.carried_from_previous
        if not total:
            return "GOOD"
        pct = float(obj.available_days / total * 100)
        if pct >= 75:
            return "GOOD"
        if pct >= 50:
            return "HEALTHY"
        if pct >= 25:
            return "LOW"
        return "CRITICAL"

    def get_status_color(self, obj):
        status = self.get_balance_status(obj)
        return {
            "GOOD": "#4CAF50",
            "HEALTHY": "#2196F3",
            "LOW": "#FF9800",
            "CRITICAL": "#F44336",
        }.get(status, "#9E9E9E")

    def get_days_until_expiry(self, obj):
        if obj.carry_forward_expiry:
            delta = (obj.carry_forward_expiry - timezone.now().date()).days
            return max(delta, 0)
        return None
