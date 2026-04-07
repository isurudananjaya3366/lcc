"""Payslip serializers for list and detail views."""

from decimal import Decimal

from rest_framework import serializers

from apps.payslip.models import Payslip
from apps.payslip.serializers.payslip_line import (
    PayslipDeductionSerializer,
    PayslipEarningSerializer,
    PayslipEmployerContributionSerializer,
)


class PayslipListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payslip list views."""

    employee_name = serializers.SerializerMethodField()
    period_name = serializers.SerializerMethodField()
    pdf_available = serializers.BooleanField(source="has_pdf", read_only=True)

    class Meta:
        model = Payslip
        fields = [
            "id",
            "slip_number",
            "employee_name",
            "period_name",
            "status",
            "email_sent",
            "view_count",
            "download_count",
            "generated_at",
            "pdf_available",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return str(obj.employee) if obj.employee else ""

    def get_period_name(self, obj):
        return getattr(obj.payroll_period, "name", str(obj.payroll_period)) if obj.payroll_period else ""


class PayslipDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer with nested line items and summary."""

    employee_name = serializers.SerializerMethodField()
    period_name = serializers.SerializerMethodField()
    pdf_available = serializers.BooleanField(source="has_pdf", read_only=True)
    earnings = PayslipEarningSerializer(many=True, read_only=True)
    deductions = PayslipDeductionSerializer(many=True, read_only=True)
    employer_contributions = PayslipEmployerContributionSerializer(many=True, read_only=True)
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Payslip
        fields = [
            "id",
            "slip_number",
            "employee",
            "employee_name",
            "payroll_period",
            "period_name",
            "employee_payroll",
            "status",
            "generated_at",
            "generated_by",
            "pdf_file",
            "pdf_available",
            "email_sent",
            "sent_at",
            "sent_to",
            "first_viewed_at",
            "view_count",
            "first_downloaded_at",
            "download_count",
            "earnings",
            "deductions",
            "employer_contributions",
            "summary",
            "created_on",
            "updated_on",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return str(obj.employee) if obj.employee else ""

    def get_period_name(self, obj):
        return getattr(obj.payroll_period, "name", str(obj.payroll_period)) if obj.payroll_period else ""

    def get_summary(self, obj):
        total_earnings = sum(
            (e.amount for e in obj.earnings.all()), Decimal("0")
        )
        total_deductions = sum(
            (d.amount for d in obj.deductions.all()), Decimal("0")
        )
        net_pay = total_earnings - total_deductions
        return {
            "total_earnings": str(total_earnings),
            "total_deductions": str(total_deductions),
            "net_pay": str(net_pay),
        }
