"""Shift serializers for the Attendance module."""

from rest_framework import serializers

from apps.attendance.models import Shift


class ShiftListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for shift list views."""

    spans_midnight = serializers.BooleanField(read_only=True)

    class Meta:
        model = Shift
        fields = [
            "id",
            "name",
            "code",
            "shift_type",
            "status",
            "start_time",
            "end_time",
            "work_hours",
            "late_grace_minutes",
            "spans_midnight",
            "is_default",
        ]
        read_only_fields = fields


class ShiftSerializer(serializers.ModelSerializer):
    """Full shift serializer with computed fields."""

    spans_midnight = serializers.BooleanField(read_only=True)
    total_duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = [
            "id",
            "name",
            "code",
            "shift_type",
            "status",
            "description",
            "is_default",
            "start_time",
            "end_time",
            "break_start",
            "break_end",
            "work_hours",
            "break_duration_minutes",
            "late_grace_minutes",
            "early_leave_grace_minutes",
            "overtime_start_after",
            "overtime_multiplier",
            "min_hours_for_half_day",
            "min_hours_for_full_day",
            "spans_midnight",
            "total_duration_hours",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "work_hours",
            "break_duration_minutes",
            "spans_midnight",
            "total_duration_hours",
            "created_on",
            "updated_on",
        ]

    def get_total_duration_hours(self, obj):
        td = obj.total_duration
        return round(td.total_seconds() / 3600, 2)

    def validate_code(self, value):
        qs = Shift.objects.filter(code=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Shift code already exists.")
        return value

    def validate(self, attrs):
        start = attrs.get("start_time") or (self.instance.start_time if self.instance else None)
        end = attrs.get("end_time") or (self.instance.end_time if self.instance else None)
        break_start = attrs.get("break_start", getattr(self.instance, "break_start", None))
        break_end = attrs.get("break_end", getattr(self.instance, "break_end", None))

        if break_start and not break_end:
            raise serializers.ValidationError(
                {"break_end": "Break end time is required when break start is set."}
            )
        if break_end and not break_start:
            raise serializers.ValidationError(
                {"break_start": "Break start time is required when break end is set."}
            )
        return attrs
