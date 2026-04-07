"""PayrollHistory serializer for the Payroll module."""

from rest_framework import serializers

from apps.payroll.models import PayrollHistory


class PayrollHistorySerializer(serializers.ModelSerializer):
    """Serializer for payroll history/audit trail entries."""

    action_display = serializers.CharField(
        source="get_action_display", read_only=True
    )
    performed_by_email = serializers.EmailField(
        source="performed_by.email", read_only=True
    )

    class Meta:
        model = PayrollHistory
        fields = [
            "id",
            "payroll_run",
            "action",
            "action_display",
            "previous_status",
            "new_status",
            "performed_by",
            "performed_by_email",
            "performed_at",
            "reason",
            "details",
            "ip_address",
        ]
        read_only_fields = fields
