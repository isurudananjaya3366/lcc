"""EmployeePayroll and PayrollLineItem serializers for the Payroll module."""

from rest_framework import serializers

from apps.payroll.models import EmployeePayroll, PayrollLineItem


class PayrollLineItemSerializer(serializers.ModelSerializer):
    """Serializer for payroll line items."""

    component_name = serializers.CharField(
        source="component.name", read_only=True
    )
    line_type_display = serializers.CharField(
        source="get_line_type_display", read_only=True
    )

    class Meta:
        model = PayrollLineItem
        fields = [
            "id",
            "component",
            "component_name",
            "line_type",
            "line_type_display",
            "base_amount",
            "calculated_amount",
            "adjustment_amount",
            "final_amount",
            "description",
            "calculation_notes",
        ]
        read_only_fields = fields


class EmployeePayrollListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for employee payroll list views."""

    payment_status_display = serializers.CharField(
        source="get_payment_status_display", read_only=True
    )
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.SerializerMethodField()

    class Meta:
        model = EmployeePayroll
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_code",
            "basic_salary",
            "gross_salary",
            "total_deductions",
            "net_salary",
            "payment_status",
            "payment_status_display",
            "is_verified",
            "is_locked",
            "is_reversed",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return obj.get_employee_name()

    def get_employee_code(self, obj):
        return obj.get_employee_code()


class EmployeePayrollSerializer(serializers.ModelSerializer):
    """Full serializer for employee payroll detail view."""

    payment_status_display = serializers.CharField(
        source="get_payment_status_display", read_only=True
    )
    line_items = PayrollLineItemSerializer(many=True, read_only=True)
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.SerializerMethodField()

    class Meta:
        model = EmployeePayroll
        fields = [
            "id",
            "payroll_run",
            "employee",
            "employee_name",
            "employee_code",
            "employee_salary",
            "salary_snapshot",
            "days_worked",
            "days_absent",
            "unpaid_leave_days",
            "overtime_hours",
            "late_count",
            "basic_salary",
            "overtime_amount",
            "gross_salary",
            "total_deductions",
            "net_salary",
            "epf_employee",
            "epf_employer",
            "etf",
            "paye_tax",
            "bank_account",
            "payment_reference",
            "payment_date",
            "payment_status",
            "payment_status_display",
            "is_verified",
            "is_locked",
            "is_reversed",
            "notes",
            "line_items",
            "created_on",
            "updated_on",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return obj.get_employee_name()

    def get_employee_code(self, obj):
        return obj.get_employee_code()
