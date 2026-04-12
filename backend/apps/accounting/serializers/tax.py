"""Serializers for tax reporting models."""

from rest_framework import serializers

from apps.accounting.models import (
    EPFReturn,
    ETFReturn,
    PAYEReturn,
    TaxConfiguration,
    TaxPeriodRecord,
    TaxSubmission,
    VATReturn,
)


class TaxConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxConfiguration
        fields = [
            "id",
            "vat_registration_no",
            "is_svat_registered",
            "vat_filing_period",
            "epf_registration_no",
            "etf_registration_no",
            "tin_number",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaxPeriodRecordSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = TaxPeriodRecord
        fields = [
            "id",
            "tax_configuration",
            "tax_type",
            "period_type",
            "year",
            "period_number",
            "start_date",
            "end_date",
            "due_date",
            "filing_status",
            "filed_date",
            "accepted_date",
            "is_active",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_overdue", "created_at", "updated_at"]


class VATReturnSerializer(serializers.ModelSerializer):
    is_refund_position = serializers.BooleanField(read_only=True)

    class Meta:
        model = VATReturn
        fields = [
            "id",
            "period",
            "reference_number",
            "output_vat",
            "input_vat",
            "net_vat_payable",
            "line_items",
            "status",
            "filed_date",
            "filed_by",
            "is_refund_position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reference_number",
            "net_vat_payable",
            "is_refund_position",
            "created_at",
            "updated_at",
        ]


class PAYEReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = PAYEReturn
        fields = [
            "id",
            "period",
            "reference_number",
            "total_employees",
            "total_remuneration",
            "total_paye_deducted",
            "employee_details",
            "status",
            "filed_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reference_number",
            "created_at",
            "updated_at",
        ]


class EPFReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = EPFReturn
        fields = [
            "id",
            "period",
            "reference_number",
            "total_employees",
            "total_employee_contribution",
            "total_employer_contribution",
            "total_contribution",
            "employee_schedule",
            "status",
            "filed_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reference_number",
            "total_contribution",
            "created_at",
            "updated_at",
        ]


class ETFReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETFReturn
        fields = [
            "id",
            "period",
            "reference_number",
            "total_employees",
            "total_contribution",
            "total_gross_salary",
            "employee_schedule",
            "status",
            "filed_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reference_number",
            "created_at",
            "updated_at",
        ]


class TaxSubmissionSerializer(serializers.ModelSerializer):
    is_submitted_on_time = serializers.BooleanField(read_only=True)
    has_confirmation_document = serializers.BooleanField(read_only=True)

    class Meta:
        model = TaxSubmission
        fields = [
            "id",
            "tax_period",
            "submitted_by",
            "submission_reference",
            "submitted_at",
            "status",
            "confirmation_document",
            "notes",
            "is_submitted_on_time",
            "has_confirmation_document",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_submitted_on_time",
            "has_confirmation_document",
            "created_at",
            "updated_at",
        ]


class TaxCalendarSerializer(serializers.Serializer):
    """Read-only serializer for the tax-calendar endpoint."""

    current_month = serializers.CharField()
    deadlines = serializers.ListField()
    overdue = serializers.ListField()
