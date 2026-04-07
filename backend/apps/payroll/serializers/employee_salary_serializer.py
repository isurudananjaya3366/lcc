"""EmployeeSalary serializers for the Payroll module."""

from rest_framework import serializers

from apps.payroll.models import EmployeeSalary, EmployeeSalaryComponent
from apps.payroll.serializers.component_serializer import SalaryComponentListSerializer
from apps.payroll.services.epf_calculator import EPFCalculator
from apps.payroll.services.etf_calculator import ETFCalculator
from apps.payroll.services.paye_calculator import PAYECalculator


class EmployeeSalaryComponentSerializer(serializers.ModelSerializer):
    """Serializer for employee-specific salary components."""

    component_detail = SalaryComponentListSerializer(
        source="component", read_only=True
    )

    class Meta:
        model = EmployeeSalaryComponent
        fields = [
            "id",
            "component",
            "component_detail",
            "amount",
            "percentage",
            "calculated_amount",
            "is_overridden",
            "notes",
        ]
        read_only_fields = ["id", "component_detail"]


class EmployeeSalaryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for employee salary list views."""

    employee_name = serializers.SerializerMethodField()
    employee_id_display = serializers.SerializerMethodField()
    template_name = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalary
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_id_display",
            "template",
            "template_name",
            "basic_salary",
            "gross_salary",
            "effective_from",
            "effective_to",
            "is_current",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def get_employee_id_display(self, obj):
        return obj.employee.employee_id if hasattr(obj.employee, "employee_id") else str(obj.employee_id)

    def get_template_name(self, obj):
        return obj.template.name if obj.template else None


class EmployeeSalarySerializer(serializers.ModelSerializer):
    """Full serializer with nested salary components and statutory breakdowns."""

    salary_components = EmployeeSalaryComponentSerializer(many=True, read_only=True)
    employee_name = serializers.SerializerMethodField()
    template_name = serializers.SerializerMethodField()
    epf_breakdown = serializers.SerializerMethodField()
    etf_breakdown = serializers.SerializerMethodField()
    paye_breakdown = serializers.SerializerMethodField()
    employer_cost = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalary
        fields = [
            "id",
            "employee",
            "employee_name",
            "template",
            "template_name",
            "basic_salary",
            "gross_salary",
            "effective_from",
            "effective_to",
            "is_current",
            "revision_number",
            "revision_reason",
            "salary_components",
            "epf_breakdown",
            "etf_breakdown",
            "paye_breakdown",
            "employer_cost",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id", "employee_name", "template_name", "gross_salary",
            "salary_components", "epf_breakdown", "etf_breakdown",
            "paye_breakdown", "employer_cost", "created_on", "updated_on",
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

    def get_template_name(self, obj):
        return obj.template.name if obj.template else None

    def get_epf_breakdown(self, obj):
        return EPFCalculator.calculate(obj)

    def get_etf_breakdown(self, obj):
        return ETFCalculator.calculate(obj)

    def get_paye_breakdown(self, obj):
        return PAYECalculator.calculate(obj)

    def get_employer_cost(self, obj):
        epf = EPFCalculator.calculate(obj)
        etf = ETFCalculator.calculate(obj)
        return {
            "gross_salary": obj.gross_salary,
            "epf_employer": epf["employer_contribution"],
            "etf_employer": etf["employer_contribution"],
            "total_employer_cost": obj.gross_salary + epf["employer_contribution"] + etf["employer_contribution"],
        }
