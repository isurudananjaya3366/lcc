"""Overtime Request serializers for the Attendance module."""

from rest_framework import serializers

from apps.attendance.models import OvertimeRequest


class OvertimeRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for overtime request list views."""

    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = OvertimeRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "planned_hours",
            "actual_hours",
            "status",
            "created_on",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee else None


class OvertimeRequestSerializer(serializers.ModelSerializer):
    """Full overtime request serializer."""

    employee_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OvertimeRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "attendance_record",
            "date",
            "planned_hours",
            "actual_hours",
            "reason",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "actual_hours",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "created_on",
            "updated_on",
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.email if obj.approved_by else None

    def validate_planned_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Planned hours must be positive.")
        return value
