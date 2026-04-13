"""
Serializers for the analytics API.

Provides read/write serializers for report definitions, instances,
saved reports, and scheduled reports.
"""

from rest_framework import serializers

from apps.analytics.enums import ReportFormat
from apps.analytics.models import (
    ReportDefinition,
    ReportInstance,
    SavedReport,
    ScheduledReport,
    ScheduleHistory,
)

# ── Report Definition ─────────────────────────────────────────────


class ReportDefinitionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDefinition
        fields = ["id", "code", "name", "category", "is_active"]
        read_only_fields = fields


class ReportDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDefinition
        fields = [
            "id",
            "code",
            "name",
            "description",
            "category",
            "available_filters",
            "is_active",
            "default_format",
            "allows_scheduling",
            "allows_export",
            "max_date_range_days",
            "estimated_time_seconds",
            "created_on",
            "updated_on",
        ]
        read_only_fields = fields


# ── Report Instance ───────────────────────────────────────────────


class ReportInstanceSerializer(serializers.ModelSerializer):
    report_definition_name = serializers.CharField(
        source="report_definition.name", read_only=True
    )
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = ReportInstance
        fields = [
            "id",
            "report_definition",
            "report_definition_name",
            "filter_parameters",
            "output_format",
            "status",
            "output_file",
            "file_size",
            "user",
            "user_name",
            "started_at",
            "generated_at",
            "generation_time_seconds",
            "error_message",
            "created_on",
        ]
        read_only_fields = fields

    def get_user_name(self, obj) -> str:
        if obj.user:
            return obj.user.full_name or obj.user.email
        return ""


# ── Report Generation Request ────────────────────────────────────


class ReportGenerationSerializer(serializers.Serializer):
    report_code = serializers.CharField(max_length=100)
    parameters = serializers.DictField(required=False, default=dict)
    format = serializers.ChoiceField(
        choices=ReportFormat.choices,
        default=ReportFormat.JSON,
    )

    def validate_report_code(self, value):
        if not ReportDefinition.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(
                f"No active report definition with code: {value}"
            )
        return value


# ── Saved Report ──────────────────────────────────────────────────


class SavedReportSerializer(serializers.ModelSerializer):
    report_definition_name = serializers.CharField(
        source="report_definition.name", read_only=True
    )
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = SavedReport
        fields = [
            "id",
            "name",
            "description",
            "report_definition",
            "report_definition_name",
            "filters_config",
            "output_format",
            "is_public",
            "owner",
            "owner_name",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "owner",
            "owner_name",
            "report_definition_name",
            "created_on",
            "updated_on",
        ]

    def get_owner_name(self, obj) -> str:
        if obj.owner:
            return obj.owner.full_name or obj.owner.email
        return ""


# ── Scheduled Report ─────────────────────────────────────────────


class ScheduledReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledReport
        fields = [
            "id",
            "saved_report",
            "frequency",
            "time_of_day",
            "day_of_week",
            "day_of_month",
            "is_active",
            "recipients",
            "email_subject",
            "email_body",
            "attach_pdf",
            "include_csv",
            "include_excel",
            "cc_emails",
            "bcc_emails",
            "next_run",
            "last_run",
            "last_status",
            "created_by",
            "created_by_name",
            "created_on",
        ]
        read_only_fields = [
            "id",
            "next_run",
            "last_run",
            "last_status",
            "created_by",
            "created_by_name",
            "created_on",
        ]

    def get_created_by_name(self, obj) -> str:
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.email
        return ""


class ScheduledReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledReport
        fields = [
            "saved_report",
            "frequency",
            "time_of_day",
            "day_of_week",
            "day_of_month",
            "is_active",
            "recipients",
            "email_subject",
            "email_body",
            "attach_pdf",
            "include_csv",
            "include_excel",
            "cc_emails",
            "bcc_emails",
        ]


# ── Schedule History ──────────────────────────────────────────────


class ScheduleHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleHistory
        fields = [
            "id",
            "scheduled_report",
            "run_at",
            "status",
            "report_instance",
            "error_message",
            "recipients_count",
            "email_sent",
            "execution_time_seconds",
            "file_size_bytes",
        ]
        read_only_fields = fields
