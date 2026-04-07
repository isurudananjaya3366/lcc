"""PayrollPeriod serializers for the Payroll module."""

from rest_framework import serializers

from apps.payroll.models import PayrollPeriod


class PayrollPeriodListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for period list views."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    runs_count = serializers.IntegerField(
        source="payroll_runs.count", read_only=True
    )
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = PayrollPeriod
        fields = [
            "id",
            "name",
            "period_month",
            "period_year",
            "start_date",
            "end_date",
            "pay_date",
            "status",
            "status_display",
            "is_locked",
            "total_working_days",
            "runs_count",
            "is_current",
        ]
        read_only_fields = fields

    def get_is_current(self, obj):
        """Check if this is the current active period."""
        from datetime import date
        today = date.today()
        if obj.start_date and obj.end_date:
            return obj.start_date <= today <= obj.end_date
        return False


class PayrollPeriodSerializer(serializers.ModelSerializer):
    """Full serializer for period detail/create/update."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    locked_by_email = serializers.EmailField(
        source="locked_by.email", read_only=True, default=None
    )
    is_current = serializers.SerializerMethodField()
    can_process = serializers.BooleanField(read_only=True)
    can_approve = serializers.BooleanField(read_only=True)
    can_finalize = serializers.BooleanField(read_only=True)
    can_reverse = serializers.BooleanField(read_only=True)

    class Meta:
        model = PayrollPeriod
        fields = [
            "id",
            "name",
            "period_month",
            "period_year",
            "start_date",
            "end_date",
            "pay_date",
            "status",
            "status_display",
            "total_working_days",
            "is_locked",
            "locked_at",
            "locked_by",
            "locked_by_email",
            "notes",
            "is_current",
            "can_process",
            "can_approve",
            "can_finalize",
            "can_reverse",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "status_display",
            "is_locked",
            "locked_at",
            "locked_by",
            "locked_by_email",
            "is_current",
            "can_process",
            "can_approve",
            "can_finalize",
            "can_reverse",
            "created_on",
            "updated_on",
        ]

    def get_is_current(self, obj):
        from datetime import date
        today = date.today()
        if obj.start_date and obj.end_date:
            return obj.start_date <= today <= obj.end_date
        return False
