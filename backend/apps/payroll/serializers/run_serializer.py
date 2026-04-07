"""PayrollRun serializers for the Payroll module."""

from rest_framework import serializers

from apps.payroll.models import PayrollRun


class PayrollRunListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payroll run list views."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    period_name = serializers.CharField(
        source="payroll_period.name", read_only=True
    )

    class Meta:
        model = PayrollRun
        fields = [
            "id",
            "period_name",
            "run_number",
            "status",
            "status_display",
            "total_employees",
            "total_gross",
            "total_net",
            "started_at",
            "completed_at",
            "created_on",
        ]
        read_only_fields = fields


class PayrollRunSerializer(serializers.ModelSerializer):
    """Full serializer for payroll run detail/create/update."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    period_name = serializers.CharField(
        source="payroll_period.name", read_only=True
    )
    processed_by_email = serializers.EmailField(
        source="processed_by.email", read_only=True, default=None
    )
    approved_by_email = serializers.EmailField(
        source="approved_by.email", read_only=True, default=None
    )
    duration = serializers.DurationField(read_only=True)
    can_approve = serializers.BooleanField(read_only=True)
    has_errors = serializers.BooleanField(read_only=True)

    class Meta:
        model = PayrollRun
        fields = [
            "id",
            "payroll_period",
            "period_name",
            "run_number",
            "status",
            "status_display",
            "started_at",
            "completed_at",
            "duration",
            "total_employees",
            "total_gross",
            "total_deductions",
            "total_net",
            "total_epf_employee",
            "total_epf_employer",
            "total_etf",
            "total_paye",
            "processed_by",
            "processed_by_email",
            "submitted_by",
            "submitted_at",
            "approved_by",
            "approved_by_email",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "finalized_by",
            "finalized_at",
            "reversed_by",
            "reversed_at",
            "bank_file_generated",
            "payment_reference",
            "payment_date",
            "paid_at",
            "error_count",
            "errors",
            "has_errors",
            "can_approve",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "status_display",
            "period_name",
            "started_at",
            "completed_at",
            "duration",
            "total_employees",
            "total_gross",
            "total_deductions",
            "total_net",
            "total_epf_employee",
            "total_epf_employer",
            "total_etf",
            "total_paye",
            "processed_by",
            "processed_by_email",
            "submitted_by",
            "submitted_at",
            "approved_by",
            "approved_by_email",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "finalized_by",
            "finalized_at",
            "reversed_by",
            "reversed_at",
            "bank_file_generated",
            "payment_reference",
            "payment_date",
            "paid_at",
            "error_count",
            "errors",
            "has_errors",
            "can_approve",
            "created_on",
            "updated_on",
        ]
