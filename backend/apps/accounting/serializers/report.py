"""
Report serializers for validating query parameters
and formatting report API responses.
"""

from rest_framework import serializers

from apps.accounting.reports.enums import (
    ComparisonType,
    DetailLevel,
    ReportPeriod,
    ReportType,
)


class ReportQuerySerializer(serializers.Serializer):
    """Base query parameter serializer for report endpoints."""

    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    as_of_date = serializers.DateField(required=False)
    detail_level = serializers.ChoiceField(
        choices=DetailLevel.choices,
        default=DetailLevel.SUMMARY,
        required=False,
    )
    include_comparison = serializers.BooleanField(default=False, required=False)
    include_zero_balances = serializers.BooleanField(default=False, required=False)
    comparison_start_date = serializers.DateField(required=False)
    comparison_end_date = serializers.DateField(required=False)
    comparison_as_of_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and start > end:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )
        return attrs


class TrialBalanceQuerySerializer(ReportQuerySerializer):
    """Query params for Trial Balance."""

    pass


class ProfitLossQuerySerializer(ReportQuerySerializer):
    """Query params for Profit & Loss."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("start_date") or not attrs.get("end_date"):
            raise serializers.ValidationError(
                "start_date and end_date are required for Profit & Loss."
            )
        return attrs


class BalanceSheetQuerySerializer(ReportQuerySerializer):
    """Query params for Balance Sheet."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("as_of_date") and not attrs.get("end_date"):
            raise serializers.ValidationError(
                "as_of_date or end_date is required for Balance Sheet."
            )
        return attrs


class CashFlowQuerySerializer(ReportQuerySerializer):
    """Query params for Cash Flow Statement."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("start_date") or not attrs.get("end_date"):
            raise serializers.ValidationError(
                "start_date and end_date are required for Cash Flow."
            )
        return attrs


class GeneralLedgerQuerySerializer(ReportQuerySerializer):
    """Query params for General Ledger."""

    account_code = serializers.CharField(required=False)
    code_from = serializers.CharField(required=False)
    code_to = serializers.CharField(required=False)


class ScheduleReportSerializer(serializers.Serializer):
    """Serializer for scheduling recurring reports."""

    report_type = serializers.ChoiceField(choices=ReportType.choices)
    frequency = serializers.ChoiceField(
        choices=ReportPeriod.choices,
        help_text="How often to generate the report.",
    )
    recipients = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1,
    )
    export_format = serializers.ChoiceField(
        choices=[("pdf", "PDF"), ("excel", "Excel")],
        default="pdf",
    )
    detail_level = serializers.ChoiceField(
        choices=DetailLevel.choices,
        default=DetailLevel.SUMMARY,
        required=False,
    )
    include_comparison = serializers.BooleanField(default=False, required=False)
