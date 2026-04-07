"""Django Filter classes for the Payroll application."""

import django_filters

from apps.payroll.models import (
    EmployeeSalary,
    EmployeePayroll,
    PayrollPeriod,
    PayrollRun,
    SalaryComponent,
    SalaryGrade,
    SalaryTemplate,
)


class SalaryComponentFilter(django_filters.FilterSet):
    """Filter set for SalaryComponent model."""

    component_type = django_filters.CharFilter(field_name="component_type")
    category = django_filters.CharFilter(field_name="category")
    calculation_type = django_filters.CharFilter(field_name="calculation_type")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_taxable = django_filters.BooleanFilter(field_name="is_taxable")
    is_epf_applicable = django_filters.BooleanFilter(field_name="is_epf_applicable")

    class Meta:
        model = SalaryComponent
        fields = [
            "component_type",
            "category",
            "calculation_type",
            "is_active",
            "is_taxable",
            "is_epf_applicable",
        ]


class SalaryTemplateFilter(django_filters.FilterSet):
    """Filter set for SalaryTemplate model."""

    is_active = django_filters.BooleanFilter(field_name="is_active")
    designation = django_filters.UUIDFilter(field_name="designation__id")

    class Meta:
        model = SalaryTemplate
        fields = ["is_active", "designation"]


class SalaryGradeFilter(django_filters.FilterSet):
    """Filter set for SalaryGrade model."""

    is_active = django_filters.BooleanFilter(field_name="is_active")
    level = django_filters.NumberFilter(field_name="level")

    class Meta:
        model = SalaryGrade
        fields = ["is_active", "level"]


class EmployeeSalaryFilter(django_filters.FilterSet):
    """Filter set for EmployeeSalary model."""

    employee = django_filters.UUIDFilter(field_name="employee__id")
    template = django_filters.UUIDFilter(field_name="template__id")
    is_current = django_filters.BooleanFilter(field_name="is_current")

    class Meta:
        model = EmployeeSalary
        fields = ["employee", "template", "is_current"]


class PayrollPeriodFilter(django_filters.FilterSet):
    """Filter set for PayrollPeriod model."""

    status = django_filters.CharFilter(field_name="status")
    period_year = django_filters.NumberFilter(field_name="period_year")
    period_month = django_filters.NumberFilter(field_name="period_month")
    is_locked = django_filters.BooleanFilter(field_name="is_locked")

    class Meta:
        model = PayrollPeriod
        fields = ["status", "period_year", "period_month", "is_locked"]


class PayrollRunFilter(django_filters.FilterSet):
    """Filter set for PayrollRun model."""

    status = django_filters.CharFilter(field_name="status")
    payroll_period = django_filters.UUIDFilter(field_name="payroll_period__id")
    run_number = django_filters.CharFilter(field_name="run_number", lookup_expr="icontains")

    class Meta:
        model = PayrollRun
        fields = ["status", "payroll_period", "run_number"]


class EmployeePayrollFilter(django_filters.FilterSet):
    """Filter set for EmployeePayroll model."""

    employee = django_filters.UUIDFilter(field_name="employee__id")
    payment_status = django_filters.CharFilter(field_name="payment_status")
    is_verified = django_filters.BooleanFilter(field_name="is_verified")

    class Meta:
        model = EmployeePayroll
        fields = ["employee", "payment_status", "is_verified"]
