"""Payslip line item serializers for earnings, deductions, and employer contributions."""

from rest_framework import serializers

from apps.payslip.models import PayslipDeduction, PayslipEarning, PayslipEmployerContribution


class PayslipEarningSerializer(serializers.ModelSerializer):
    """Serializer for payslip earning line items."""

    class Meta:
        model = PayslipEarning
        fields = [
            "id",
            "component_code",
            "component_name",
            "amount",
            "ytd_amount",
            "display_order",
        ]
        read_only_fields = fields


class PayslipDeductionSerializer(serializers.ModelSerializer):
    """Serializer for payslip deduction line items."""

    class Meta:
        model = PayslipDeduction
        fields = [
            "id",
            "component_code",
            "component_name",
            "amount",
            "ytd_amount",
            "display_order",
        ]
        read_only_fields = fields


class PayslipEmployerContributionSerializer(serializers.ModelSerializer):
    """Serializer for payslip employer contribution line items."""

    class Meta:
        model = PayslipEmployerContribution
        fields = [
            "id",
            "component_code",
            "component_name",
            "amount",
            "ytd_amount",
            "display_order",
        ]
        read_only_fields = fields
