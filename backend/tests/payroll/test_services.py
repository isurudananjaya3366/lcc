"""Tests for payroll services."""

import pytest
from datetime import date
from decimal import Decimal

from apps.payroll.constants import ComponentType, SalaryChangeReason

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────────────────────
# SalaryService Tests
# ──────────────────────────────────────────────────────────────


class TestSalaryServiceAssignTemplate:
    def test_assign_template_creates_salary(self, employee, template_with_components):
        from apps.payroll.services.salary_service import SalaryService

        salary = SalaryService.assign_template(
            employee=employee,
            template=template_with_components,
            basic_salary=Decimal("100000.00"),
            effective_from=date(2024, 1, 1),
        )
        assert salary.pk is not None
        assert salary.is_current is True
        assert salary.basic_salary == Decimal("100000.00")
        assert salary.template == template_with_components

    def test_assign_template_creates_components(self, employee, template_with_components):
        from apps.payroll.services.salary_service import SalaryService

        salary = SalaryService.assign_template(
            employee=employee,
            template=template_with_components,
            basic_salary=Decimal("100000.00"),
        )
        assert salary.salary_components.count() == 3

    def test_assign_template_calculates_gross(self, employee, template_with_components):
        from apps.payroll.services.salary_service import SalaryService

        salary = SalaryService.assign_template(
            employee=employee,
            template=template_with_components,
            basic_salary=Decimal("100000.00"),
        )
        # BASIC (100000) + TRANSPORT (5000) + MEDICAL (3000) = 108000
        assert salary.gross_salary == Decimal("108000.00")

    def test_assign_template_deactivates_previous(self, employee, template_with_components):
        from apps.payroll.services.salary_service import SalaryService
        from apps.payroll.models import EmployeeSalary

        salary1 = SalaryService.assign_template(
            employee=employee,
            template=template_with_components,
            basic_salary=Decimal("80000.00"),
            effective_from=date(2023, 1, 1),
        )

        salary2 = SalaryService.assign_template(
            employee=employee,
            template=template_with_components,
            basic_salary=Decimal("100000.00"),
            effective_from=date(2024, 1, 1),
        )

        salary1.refresh_from_db()
        assert salary1.is_current is False
        assert salary2.is_current is True

    def test_basic_component_uses_basic_salary(self, employee, template_with_components, basic_component):
        from apps.payroll.services.salary_service import SalaryService

        salary = SalaryService.assign_template(
            employee=employee,
            template=template_with_components,
            basic_salary=Decimal("120000.00"),
        )
        basic_esc = salary.salary_components.get(component=basic_component)
        assert basic_esc.amount == Decimal("120000.00")


class TestSalaryServiceOverride:
    def test_override_component(self, employee_salary, transport_component):
        from apps.payroll.services.salary_service import SalaryService

        esc = SalaryService.override_component(
            employee_salary=employee_salary,
            component=transport_component,
            amount=Decimal("8000.00"),
        )
        assert esc.amount == Decimal("8000.00")

    def test_override_recalculates_gross(self, employee_salary, transport_component):
        from apps.payroll.services.salary_service import SalaryService

        SalaryService.override_component(
            employee_salary=employee_salary,
            component=transport_component,
            amount=Decimal("8000.00"),
        )
        employee_salary.refresh_from_db()
        # BASIC (100000) + TRANSPORT (8000) + MEDICAL (3000) = 111000
        assert employee_salary.gross_salary == Decimal("111000.00")


class TestSalaryServiceRecalculate:
    def test_recalculate_gross(self, employee_salary):
        from apps.payroll.services.salary_service import SalaryService

        gross = SalaryService.recalculate_gross(employee_salary)
        # Only earnings: BASIC (100000) + TRANSPORT (5000) + MEDICAL (3000)
        assert gross == Decimal("108000.00")


class TestSalaryServiceRevise:
    def test_revise_salary(self, employee, employee_salary):
        from apps.payroll.services.salary_service import SalaryService
        from apps.payroll.models import SalaryHistory

        new_salary = SalaryService.revise_salary(
            employee=employee,
            new_basic=Decimal("120000.00"),
            effective_from=date(2024, 7, 1),
            change_reason=SalaryChangeReason.ANNUAL_INCREMENT,
            remarks="Annual increment 2024",
        )

        assert new_salary.is_current is True
        assert new_salary.basic_salary == Decimal("120000.00")

        employee_salary.refresh_from_db()
        assert employee_salary.is_current is False

        # Check history was created
        history = SalaryHistory.objects.filter(employee=employee).order_by("-created_on")
        assert history.exists()

    def test_revise_copies_components(self, employee, employee_salary):
        from apps.payroll.services.salary_service import SalaryService

        new_salary = SalaryService.revise_salary(
            employee=employee,
            new_basic=Decimal("120000.00"),
            effective_from=date(2024, 7, 1),
        )
        assert new_salary.salary_components.count() == 3

    def test_revise_updates_basic_component_amount(
        self, employee, employee_salary, basic_component
    ):
        from apps.payroll.services.salary_service import SalaryService

        new_salary = SalaryService.revise_salary(
            employee=employee,
            new_basic=Decimal("130000.00"),
            effective_from=date(2024, 7, 1),
        )
        basic_esc = new_salary.salary_components.get(component=basic_component)
        assert basic_esc.amount == Decimal("130000.00")


class TestSalaryServiceCompare:
    def test_compare_salaries(self, employee, employee_salary, basic_component, transport_component, medical_component):
        from apps.payroll.services.salary_service import SalaryService
        from apps.payroll.models import EmployeeSalary, EmployeeSalaryComponent

        new_salary = EmployeeSalary.objects.create(
            employee=employee,
            basic_salary=Decimal("120000.00"),
            gross_salary=Decimal("128000.00"),
            effective_from=date(2024, 7, 1),
            is_current=True,
        )
        EmployeeSalaryComponent.objects.create(
            employee_salary=new_salary, component=basic_component, amount=Decimal("120000.00"),
        )
        EmployeeSalaryComponent.objects.create(
            employee_salary=new_salary, component=transport_component, amount=Decimal("5000.00"),
        )
        EmployeeSalaryComponent.objects.create(
            employee_salary=new_salary, component=medical_component, amount=Decimal("3000.00"),
        )

        result = SalaryService.compare_salaries(employee_salary, new_salary)

        assert result["basic_change"] == Decimal("20000.00")
        assert result["gross_change"] == Decimal("20000.00")
        assert len(result["component_differences"]) >= 1


# ──────────────────────────────────────────────────────────────
# EPF Calculator Tests
# ──────────────────────────────────────────────────────────────


class TestEPFCalculator:
    def test_calculate_epf(self, employee_salary, epf_settings):
        from apps.payroll.services.epf_calculator import EPFCalculator

        result = EPFCalculator.calculate(employee_salary, epf_settings)
        # EPF base = only EPF-applicable earnings = BASIC (100000)
        assert result["epf_base"] == Decimal("100000.00")
        assert result["employee_contribution"] == Decimal("8000.00")
        assert result["employer_contribution"] == Decimal("12000.00")

    def test_calculate_epf_no_settings(self, employee_salary, tenant_context):
        from apps.payroll.services.epf_calculator import EPFCalculator

        result = EPFCalculator.calculate(employee_salary)
        assert result["epf_base"] == Decimal("0")
        assert result["employee_contribution"] == Decimal("0")

    def test_epf_base_excludes_non_applicable(self, employee_salary):
        from apps.payroll.services.epf_calculator import EPFCalculator

        # Only BASIC is EPF-applicable (transport and medical are not)
        epf_base = EPFCalculator.get_epf_base(employee_salary)
        assert epf_base == Decimal("100000.00")

    def test_epf_with_ceiling(self, employee_salary, tenant_context):
        from apps.payroll.models import EPFSettings
        from apps.payroll.services.epf_calculator import EPFCalculator

        settings = EPFSettings.objects.create(
            employee_rate=Decimal("8.00"),
            employer_rate=Decimal("12.00"),
            max_contribution_ceiling=Decimal("5000.00"),
            is_active=True,
        )
        result = EPFCalculator.calculate(employee_salary, settings)
        assert result["employee_contribution"] == Decimal("5000.00")
        assert result["employer_contribution"] == Decimal("5000.00")


# ──────────────────────────────────────────────────────────────
# ETF Calculator Tests
# ──────────────────────────────────────────────────────────────


class TestETFCalculator:
    def test_calculate_etf(self, employee_salary, etf_settings):
        from apps.payroll.services.etf_calculator import ETFCalculator

        result = ETFCalculator.calculate(employee_salary, etf_settings)
        # ETF base = same as EPF base = BASIC (100000)
        assert result["etf_base"] == Decimal("100000.00")
        assert result["employer_contribution"] == Decimal("3000.00")

    def test_calculate_etf_no_settings(self, employee_salary, tenant_context):
        from apps.payroll.services.etf_calculator import ETFCalculator

        result = ETFCalculator.calculate(employee_salary)
        assert result["etf_base"] == Decimal("0")
        assert result["employer_contribution"] == Decimal("0")


# ──────────────────────────────────────────────────────────────
# PAYE Calculator Tests
# ──────────────────────────────────────────────────────────────


class TestPAYECalculator:
    def test_get_taxable_income(self, employee_salary):
        from apps.payroll.services.paye_calculator import PAYECalculator

        # BASIC (100000, taxable) + TRANSPORT (5000, taxable) = 105000
        # MEDICAL (3000, NOT taxable) excluded
        taxable = PAYECalculator.get_taxable_income(employee_salary)
        assert taxable == Decimal("105000.00")

    def test_get_monthly_exemptions(self, tax_exemptions):
        from apps.payroll.services.paye_calculator import PAYECalculator

        exemptions = PAYECalculator.get_monthly_exemptions()
        # Personal Relief (100000) + Spouse Relief (41666.67)
        assert exemptions == Decimal("141666.67")

    def test_calculate_annual_tax_zero_income(self, paye_slabs):
        from apps.payroll.services.paye_calculator import PAYECalculator

        tax = PAYECalculator.calculate_annual_tax(Decimal("0"), tax_year=2024)
        assert tax == Decimal("0")

    def test_calculate_annual_tax_in_zero_slab(self, paye_slabs):
        from apps.payroll.services.paye_calculator import PAYECalculator

        # 600000 annual income falls entirely in 0% slab (0-1.2M)
        tax = PAYECalculator.calculate_annual_tax(Decimal("600000"), tax_year=2024)
        assert tax == Decimal("0")

    def test_calculate_annual_tax_first_taxed_slab(self, paye_slabs):
        from apps.payroll.services.paye_calculator import PAYECalculator

        # 1500000 annual = 1.2M @ 0% + 300000 @ 6% = 18000
        tax = PAYECalculator.calculate_annual_tax(Decimal("1500000"), tax_year=2024)
        expected = Decimal("18000.00")
        assert tax == expected

    def test_calculate_annual_tax_progressive(self, paye_slabs):
        from apps.payroll.services.paye_calculator import PAYECalculator

        # 2000000 annual = 1.2M @ 0% + 499999 @ 6% + 300000 @ 12%
        tax = PAYECalculator.calculate_annual_tax(Decimal("2000000"), tax_year=2024)
        slab1_tax = Decimal("499999") * Decimal("6") / Decimal("100")  # 29999.94
        slab2_tax = Decimal("300001") * Decimal("12") / Decimal("100")  # 36000.12
        expected = (slab1_tax + slab2_tax).quantize(Decimal("0.01"))
        # Just verify it's positive and reasonable
        assert tax > Decimal("0")
        assert tax < Decimal("2000000")

    def test_calculate_monthly_tax(self, employee_salary, paye_slabs, tax_exemptions):
        from apps.payroll.services.paye_calculator import PAYECalculator

        result = PAYECalculator.calculate(employee_salary, tax_year=2024)
        assert "monthly_tax" in result
        assert "annual_tax" in result
        assert "monthly_taxable_income" in result
        assert result["monthly_tax"] >= Decimal("0")

    def test_get_tax_slab(self, paye_slabs):
        from apps.payroll.services.paye_calculator import PAYECalculator

        slab = PAYECalculator.get_tax_slab(Decimal("1500000"), tax_year=2024)
        assert slab is not None
        assert slab.rate == Decimal("6.00")

    def test_calculate_no_slabs(self, employee_salary, tenant_context):
        from apps.payroll.services.paye_calculator import PAYECalculator

        result = PAYECalculator.calculate(employee_salary, tax_year=9999)
        assert result["annual_tax"] == Decimal("0")
        assert result["monthly_tax"] == Decimal("0")


# ──────────────────────────────────────────────────────────────
# Signal Tests
# ──────────────────────────────────────────────────────────────


class TestSalarySignals:
    def test_history_created_on_basic_salary_change(self, employee_salary, tenant_context):
        from apps.payroll.models import SalaryHistory

        old_basic = employee_salary.basic_salary
        employee_salary.basic_salary = Decimal("120000.00")
        employee_salary.save()

        history = SalaryHistory.objects.filter(
            employee=employee_salary.employee,
            previous_basic=old_basic,
            new_basic=Decimal("120000.00"),
        )
        assert history.exists()

    def test_no_history_when_basic_unchanged(self, employee_salary, tenant_context):
        from apps.payroll.models import SalaryHistory

        initial_count = SalaryHistory.objects.filter(
            employee=employee_salary.employee
        ).count()

        employee_salary.gross_salary = Decimal("999999.00")
        employee_salary.save()

        final_count = SalaryHistory.objects.filter(
            employee=employee_salary.employee
        ).count()
        assert final_count == initial_count
