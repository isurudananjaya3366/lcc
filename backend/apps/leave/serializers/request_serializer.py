"""LeaveRequest serializers for the Leave Management module."""

from django.utils import timezone
from rest_framework import serializers

from apps.leave.constants import HalfDayType, LeaveRequestStatus
from apps.leave.models import LeaveRequest


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating leave requests."""

    class Meta:
        model = LeaveRequest
        fields = [
            "leave_type",
            "start_date",
            "end_date",
            "is_half_day",
            "half_day_type",
            "reason",
            "contact_during_leave",
            "attachment",
        ]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        is_half_day = attrs.get("is_half_day", False)
        half_day_type = attrs.get("half_day_type")

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be before start date."}
            )

        if is_half_day:
            if not half_day_type:
                raise serializers.ValidationError(
                    {"half_day_type": "Half-day type is required when is_half_day is True."}
                )
            if start_date and end_date and start_date != end_date:
                raise serializers.ValidationError(
                    {"is_half_day": "Half-day leave must have the same start and end date."}
                )
        elif half_day_type:
            raise serializers.ValidationError(
                {"half_day_type": "Half-day type should be empty when is_half_day is False."}
            )

        return attrs


class LeaveRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for leave request list views."""

    employee_name = serializers.SerializerMethodField()
    leave_type_name = serializers.SerializerMethodField()
    leave_type_code = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    days_until_start = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "leave_type",
            "leave_type_name",
            "leave_type_code",
            "start_date",
            "end_date",
            "total_days",
            "is_half_day",
            "status",
            "status_display",
            "submitted_at",
            "days_until_start",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def get_leave_type_name(self, obj):
        return obj.leave_type.name if obj.leave_type else None

    def get_leave_type_code(self, obj):
        return obj.leave_type.code if obj.leave_type else None

    def get_days_until_start(self, obj):
        if obj.start_date:
            delta = (obj.start_date - timezone.now().date()).days
            return max(delta, 0)
        return None


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Full leave request serializer with nested details and permissions."""

    employee_name = serializers.SerializerMethodField()
    leave_type_name = serializers.SerializerMethodField()
    leave_type_code = serializers.SerializerMethodField()
    leave_type_color = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    approved_by_name = serializers.SerializerMethodField()
    days_until_start = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_submit = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    can_approve = serializers.SerializerMethodField()
    can_reject = serializers.SerializerMethodField()
    can_recall = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "leave_type",
            "leave_type_name",
            "leave_type_code",
            "leave_type_color",
            "start_date",
            "end_date",
            "total_days",
            "is_half_day",
            "half_day_type",
            "reason",
            "contact_during_leave",
            "status",
            "status_display",
            "submitted_at",
            "attachment",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "recalled_at",
            "recalled_reason",
            "days_until_start",
            "is_past",
            "can_edit",
            "can_submit",
            "can_cancel",
            "can_approve",
            "can_reject",
            "can_recall",
            "created_on",
            "updated_on",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def get_leave_type_name(self, obj):
        return obj.leave_type.name if obj.leave_type else None

    def get_leave_type_code(self, obj):
        return obj.leave_type.code if obj.leave_type else None

    def get_leave_type_color(self, obj):
        return obj.leave_type.color if obj.leave_type else None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}".strip()
        return None

    def get_days_until_start(self, obj):
        if obj.start_date:
            delta = (obj.start_date - timezone.now().date()).days
            return max(delta, 0)
        return None

    def get_is_past(self, obj):
        if obj.end_date:
            return obj.end_date < timezone.now().date()
        return False

    def get_can_edit(self, obj):
        return obj.status == LeaveRequestStatus.DRAFT

    def get_can_submit(self, obj):
        return obj.status == LeaveRequestStatus.DRAFT

    def get_can_cancel(self, obj):
        return obj.status in (LeaveRequestStatus.PENDING, LeaveRequestStatus.APPROVED)

    def get_can_approve(self, obj):
        return obj.status == LeaveRequestStatus.PENDING

    def get_can_reject(self, obj):
        return obj.status == LeaveRequestStatus.PENDING

    def get_can_recall(self, obj):
        return obj.status == LeaveRequestStatus.APPROVED


class WorkflowActionSerializer(serializers.Serializer):
    """Serializer for leave request workflow actions."""

    action = serializers.ChoiceField(
        choices=["submit", "approve", "reject", "cancel", "recall"],
    )
    reason = serializers.CharField(required=False, allow_blank=True, default="")
    comments = serializers.CharField(required=False, allow_blank=True, default="")
