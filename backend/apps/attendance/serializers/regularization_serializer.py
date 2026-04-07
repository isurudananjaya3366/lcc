"""Regularization serializers for the Attendance module."""

from rest_framework import serializers

from apps.attendance.models import AttendanceRegularization


class RegularizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for regularization list views."""

    employee_name = serializers.SerializerMethodField()
    attendance_date = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRegularization
        fields = [
            "id",
            "employee",
            "employee_name",
            "attendance_record",
            "attendance_date",
            "status",
            "reason",
            "created_on",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee else None

    def get_attendance_date(self, obj):
        return obj.attendance_record.date if obj.attendance_record else None


class RegularizationSerializer(serializers.ModelSerializer):
    """Full regularization request serializer."""

    employee_name = serializers.SerializerMethodField()
    attendance_date = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRegularization
        fields = [
            "id",
            "attendance_record",
            "employee",
            "employee_name",
            "attendance_date",
            "original_clock_in",
            "original_clock_out",
            "corrected_clock_in",
            "corrected_clock_out",
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
            "original_clock_in",
            "original_clock_out",
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

    def get_attendance_date(self, obj):
        return obj.attendance_record.date if obj.attendance_record else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.email if obj.approved_by else None

    def validate(self, attrs):
        corrected_in = attrs.get("corrected_clock_in")
        corrected_out = attrs.get("corrected_clock_out")
        if not corrected_in and not corrected_out:
            raise serializers.ValidationError(
                "At least one of corrected_clock_in or corrected_clock_out is required."
            )
        if corrected_in and corrected_out and corrected_out <= corrected_in:
            raise serializers.ValidationError(
                {"corrected_clock_out": "Corrected clock-out must be after corrected clock-in."}
            )
        return attrs
