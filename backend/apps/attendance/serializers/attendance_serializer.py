"""Attendance Record serializers for the Attendance module."""

from rest_framework import serializers

from apps.attendance.models import AttendanceRecord, Shift


class ShiftMinimalSerializer(serializers.ModelSerializer):
    """Minimal shift representation for nested use."""

    class Meta:
        model = Shift
        fields = ["id", "code", "name", "start_time", "end_time"]
        read_only_fields = fields


class EmployeeMinimalSerializer(serializers.Serializer):
    """Minimal employee representation for nested use (read-only)."""

    id = serializers.UUIDField()
    employee_id = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class AttendanceRecordListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for attendance record list views."""

    employee_name = serializers.SerializerMethodField()
    shift_name = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()
    is_early_leave = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "clock_in",
            "clock_out",
            "status",
            "shift",
            "shift_name",
            "work_hours",
            "overtime_hours",
            "late_minutes",
            "early_departure_minutes",
            "is_late",
            "is_early_leave",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}" if obj.employee else None

    def get_shift_name(self, obj):
        return obj.shift.name if obj.shift else None

    def get_is_late(self, obj):
        return obj.late_minutes > 0

    def get_is_early_leave(self, obj):
        return obj.early_departure_minutes > 0


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Full attendance record serializer with nested employee and shift details."""

    employee_detail = EmployeeMinimalSerializer(source="employee", read_only=True)
    shift_detail = ShiftMinimalSerializer(source="shift", read_only=True)
    is_late = serializers.SerializerMethodField()
    is_early_leave = serializers.SerializerMethodField()
    is_clocked_in = serializers.BooleanField(read_only=True)
    is_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "employee",
            "employee_detail",
            "date",
            "clock_in",
            "clock_out",
            "clock_in_method",
            "clock_out_method",
            "status",
            "shift",
            "shift_detail",
            "work_hours",
            "break_hours",
            "effective_hours",
            "late_minutes",
            "early_departure_minutes",
            "overtime_hours",
            "overtime_approved",
            "clock_in_location",
            "clock_out_location",
            "clock_in_ip",
            "clock_out_ip",
            "notes",
            "is_regularized",
            "is_late",
            "is_early_leave",
            "is_clocked_in",
            "is_complete",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "work_hours",
            "break_hours",
            "effective_hours",
            "late_minutes",
            "early_departure_minutes",
            "overtime_hours",
            "is_regularized",
            "is_late",
            "is_early_leave",
            "is_clocked_in",
            "is_complete",
            "created_on",
            "updated_on",
        ]

    def get_is_late(self, obj):
        return obj.late_minutes > 0

    def get_is_early_leave(self, obj):
        return obj.early_departure_minutes > 0


class ClockInSerializer(serializers.Serializer):
    """Serializer for clock-in API endpoint."""

    shift_id = serializers.UUIDField(required=False, allow_null=True)
    clock_in_method = serializers.CharField(default="web", required=False)
    location = serializers.DictField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class ClockOutSerializer(serializers.Serializer):
    """Serializer for clock-out API endpoint."""

    clock_out_method = serializers.CharField(default="web", required=False)
    location = serializers.DictField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
