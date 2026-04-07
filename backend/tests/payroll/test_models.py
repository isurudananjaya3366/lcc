"""Tests for payroll models."""

import pytest
from datetime import date
from decimal import Decimal

from apps.payroll.constants import (
    ComponentType,
    CalculationType,
    ComponentCategory,
    SalaryChangeReason,
)

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────────────────────
# SalaryComponent Tests
# ──────────────────────────────────────────────────────────────


class TestSalaryComponent:
    def test_create_component(self, basic_component):
        assert basic_component.pk is not None
        assert basic_component.name == "Basic Salary"
        assert basic_component.code == "BASIC"
        assert basic_component.component_type == ComponentType.EARNING
        assert basic_component.category == ComponentCategory.BASIC

    def test_code_auto_uppercase(self, tenant_context):
        from apps.payroll.models import SalaryComponent

        comp = SalaryComponent.objects.create(
            name="Test Low",
            code="lower_code",
            component_type=ComponentType.EARNING,
            category=ComponentCategory.ALLOWANCE,
        )
        assert comp.code == "LOWER_CODE"

    def test_code_unique(self, basic_component, tenant_context):
        from apps.payroll.models import SalaryComponent
        from django.db import IntegrityError, transaction

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                SalaryComponent.objects.create(
                    name="Duplicate Basic",
                    code="BASIC",
                    component_type=ComponentType.EARNING,
                    category=ComponentCategory.BASIC,
                )

    def test_soft_delete(self, basic_component):
        basic_component.is_deleted = True
        basic_component.save()
        basic_component.refresh_from_db()
        assert basic_component.is_deleted is True

    def test_str(self, basic_component):
        assert str(basic_component) == "Basic Salary (BASIC)"

    def test_default_values(self, tenant_context):
        from apps.payroll.models import SalaryComponent

        comp = SalaryComponent.objects.create(
            name="Test Defaults",
            code="DEFAULTS",
            component_type=ComponentType.DEDUCTION,
            category=ComponentCategory.STATUTORY,
        )
        assert comp.calculation_type == CalculationType.FIXED
        assert comp.default_value == Decimal("0")
        assert comp.percentage == Decimal("0")
        assert comp.is_taxable is True
        assert comp.is_epf_applicable is False
        assert comp.is_fixed is True
        assert comp.is_active is True
        assert comp.display_order == 0

    def test_deduction_component(self, epf_ee_component):
        assert epf_ee_component.component_type == ComponentType.DEDUCTION
        assert epf_ee_component.category == ComponentCategory.STATUTORY
        assert epf_ee_component.percentage == Decimal("8.00")

    def test_ordering(self, basic_component, transport_component, medical_component):
        from apps.payroll.models import SalaryComponent

        components = list(SalaryComponent.objects.all().values_list("code", flat=True))
        assert components.index("BASIC") < components.index("TRANSPORT")
        assert components.index("TRANSPORT") < components.index("MEDICAL")


# ──────────────────────────────────────────────────────────────
# SalaryTemplate Tests
# ──────────────────────────────────────────────────────────────


class TestSalaryTemplate:
    def test_create_template(self, salary_template):
        assert salary_template.pk is not None
        assert salary_template.name == "Standard Template"
        assert salary_template.code == "STD"
        assert salary_template.is_active is True

    def test_code_unique(self, salary_template, tenant_context):
        from apps.payroll.models import SalaryTemplate
        from django.db import IntegrityError, transaction

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                SalaryTemplate.objects.create(name="Dup", code="STD")

    def test_code_auto_uppercase(self, tenant_context):
        from apps.payroll.models import SalaryTemplate

        tmpl = SalaryTemplate.objects.create(name="Test", code="lower")
        assert tmpl.code == "LOWER"

    def test_str(self, salary_template):
        assert str(salary_template) == "Standard Template (STD)"


# ──────────────────────────────────────────────────────────────
# TemplateComponent Tests
# ──────────────────────────────────────────────────────────────


class TestTemplateComponent:
    def test_create_template_component(self, template_with_components, basic_component):
        from apps.payroll.models import TemplateComponent

        tc = TemplateComponent.objects.get(
            template=template_with_components, component=basic_component
        )
        assert tc.can_override is False
        assert tc.default_value == Decimal("0")

    def test_unique_together(self, template_with_components, basic_component):
        from apps.payroll.models import TemplateComponent
        from django.db import IntegrityError, transaction

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                TemplateComponent.objects.create(
                    template=template_with_components,
                    component=basic_component,
                    default_value=Decimal("999"),
                )

    def test_template_component_count(self, template_with_components):
        from apps.payroll.models import TemplateComponent

        count = TemplateComponent.objects.filter(
            template=template_with_components
        ).count()
        assert count == 3

    def test_str(self, template_with_components, basic_component):
        from apps.payroll.models import TemplateComponent

        tc = TemplateComponent.objects.get(
            template=template_with_components, component=basic_component
        )
        assert "Standard Template" in str(tc)
        assert "Basic Salary" in str(tc)


# ──────────────────────────────────────────────────────────────
# SalaryGrade Tests
# ──────────────────────────────────────────────────────────────


class TestSalaryGrade:
    def test_create_grade(self, tenant_context):
        from apps.payroll.models import SalaryGrade

        grade = SalaryGrade.objects.create(
            name="Grade 1",
            code="G1",
            level=1,
            min_salary=Decimal("30000.00"),
            max_salary=Decimal("60000.00"),
        )
        assert grade.pk is not None
        assert grade.code == "G1"
        assert grade.is_active is True

    def test_code_auto_uppercase(self, tenant_context):
        from apps.payroll.models import SalaryGrade

        grade = SalaryGrade.objects.create(
            name="Grade Test",
            code="test",
            level=2,
            min_salary=Decimal("40000"),
            max_salary=Decimal("70000"),
        )
        assert grade.code == "TEST"

    def test_grade_with_template(self, salary_template, tenant_context):
        from apps.payroll.models import SalaryGrade

        grade = SalaryGrade.objects.create(
            name="Grade Linked",
            code="GL",
            level=3,
            min_salary=Decimal("50000"),
            max_salary=Decimal("90000"),
            template=salary_template,
        )
        assert grade.template == salary_template

    def test_str(self, tenant_context):
        from apps.payroll.models import SalaryGrade

        grade = SalaryGrade.objects.create(
            name="Entry", code="E1", level=1,
            min_salary=Decimal("30000"), max_salary=Decimal("60000"),
        )
        assert str(grade) == "Entry (E1)"


# ──────────────────────────────────────────────────────────────
# EmployeeSalary Tests
# ──────────────────────────────────────────────────────────────


class TestEmployeeSalary:
    def test_create_employee_salary(self, employee_salary):
        assert employee_salary.pk is not None
        assert employee_salary.basic_salary == Decimal("100000.00")
        assert employee_salary.gross_salary == Decimal("108000.00")
        assert employee_salary.is_current is True

    def test_str(self, employee_salary):
        s = str(employee_salary)
        assert "100000" in s
        assert "2024-01-01" in s

    def test_ordering(self, employee, tenant_context):
        from apps.payroll.models import EmployeeSalary

        s1 = EmployeeSalary.objects.create(
            employee=employee, basic_salary=Decimal("80000"),
            effective_from=date(2023, 1, 1), is_current=False,
        )
        s2 = EmployeeSalary.objects.create(
            employee=employee, basic_salary=Decimal("90000"),
            effective_from=date(2024, 6, 1), is_current=True,
        )
        salaries = list(EmployeeSalary.objects.filter(employee=employee))
        assert salaries[0].effective_from >= salaries[-1].effective_from


# ──────────────────────────────────────────────────────────────
# EmployeeSalaryComponent Tests
# ──────────────────────────────────────────────────────────────


class TestEmployeeSalaryComponent:
    def test_components_created(self, employee_salary):
        from apps.payroll.models import EmployeeSalaryComponent

        count = EmployeeSalaryComponent.objects.filter(
            employee_salary=employee_salary
        ).count()
        assert count == 3

    def test_unique_together(self, employee_salary, basic_component):
        from apps.payroll.models import EmployeeSalaryComponent
        from django.db import IntegrityError, transaction

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                EmployeeSalaryComponent.objects.create(
                    employee_salary=employee_salary,
                    component=basic_component,
                    amount=Decimal("999"),
                )

    def test_str(self, employee_salary):
        from apps.payroll.models import EmployeeSalaryComponent

        esc = employee_salary.salary_components.first()
        s = str(esc)
        assert ":" in s


# ──────────────────────────────────────────────────────────────
# SalaryHistory Tests
# ──────────────────────────────────────────────────────────────


class TestSalaryHistory:
    def test_create_history(self, employee, tenant_context):
        from apps.payroll.models import SalaryHistory

        history = SalaryHistory.objects.create(
            employee=employee,
            previous_basic=Decimal("80000"),
            new_basic=Decimal("100000"),
            previous_gross=Decimal("88000"),
            new_gross=Decimal("108000"),
            effective_date=date(2024, 1, 1),
            change_reason=SalaryChangeReason.ANNUAL_INCREMENT,
            remarks="Annual review",
        )
        assert history.pk is not None
        assert history.change_reason == SalaryChangeReason.ANNUAL_INCREMENT

    def test_str(self, employee, tenant_context):
        from apps.payroll.models import SalaryHistory

        history = SalaryHistory.objects.create(
            employee=employee,
            previous_basic=Decimal("50000"),
            new_basic=Decimal("60000"),
            effective_date=date(2024, 6, 1),
        )
        s = str(history)
        assert "50000" in s
        assert "60000" in s


# ──────────────────────────────────────────────────────────────
# Statutory Settings Tests
# ──────────────────────────────────────────────────────────────


class TestEPFSettings:
    def test_create_settings(self, epf_settings):
        assert epf_settings.pk is not None
        assert epf_settings.employee_rate == Decimal("8.00")
        assert epf_settings.employer_rate == Decimal("12.00")
        assert epf_settings.is_active is True

    def test_str(self, epf_settings):
        s = str(epf_settings)
        assert "8" in s
        assert "12" in s


class TestETFSettings:
    def test_create_settings(self, etf_settings):
        assert etf_settings.pk is not None
        assert etf_settings.employer_rate == Decimal("3.00")

    def test_str(self, etf_settings):
        assert "3" in str(etf_settings)


class TestPAYETaxSlab:
    def test_create_slabs(self, paye_slabs):
        assert len(paye_slabs) == 7

    def test_slab_ordering(self, paye_slabs):
        from apps.payroll.models import PAYETaxSlab

        slabs = list(PAYETaxSlab.objects.filter(tax_year=2024))
        for i in range(len(slabs) - 1):
            assert slabs[i].from_amount < slabs[i + 1].from_amount

    def test_zero_rate_slab(self, paye_slabs):
        first = paye_slabs[0]
        assert first.rate == Decimal("0.00")
        assert first.order == 0
        assert first.from_amount == Decimal("0")

    def test_last_slab_no_upper_limit(self, paye_slabs):
        last = paye_slabs[-1]
        assert last.to_amount is None
        assert last.rate == Decimal("36.00")

    def test_str(self, paye_slabs):
        s = str(paye_slabs[0])
        assert "Slab 0:" in s
        assert "2024" in s


class TestTaxExemption:
    def test_create_exemption(self, tax_exemptions):
        assert len(tax_exemptions) == 2
        pr = tax_exemptions[0]
        assert pr.code == "PERSONAL"
        assert pr.monthly_amount == Decimal("100000.00")
        assert pr.tax_year == 2024
        assert pr.exemption_type == "PERSONAL"

    def test_str(self, tax_exemptions):
        assert "Personal Relief" in str(tax_exemptions[0])
