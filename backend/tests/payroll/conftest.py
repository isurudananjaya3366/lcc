"""Fixtures for payroll module tests."""

import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

from apps.payroll.constants import (
    ComponentType,
    CalculationType,
    ComponentCategory,
    PayrollStatus,
    PaymentStatus,
    LineType,
    SalaryChangeReason,
)

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_payroll"
TENANT_DOMAIN = "payroll.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for payroll tests."""
    with django_db_blocker.unblock():
        # Clean up any stale tenant using raw SQL to avoid cascade issues
        with connection.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_NAME)
            cur.execute(
                "DELETE FROM %s WHERE tenant_id IN "
                "(SELECT id FROM %s WHERE schema_name = %%s)"
                % (DomainModel._meta.db_table, TenantModel._meta.db_table),
                [SCHEMA_NAME],
            )
            cur.execute(
                "DELETE FROM tenants_tenantsettings WHERE tenant_id IN "
                "(SELECT id FROM %s WHERE schema_name = %%s)"
                % TenantModel._meta.db_table,
                [SCHEMA_NAME],
            )
            cur.execute(
                "DELETE FROM %s WHERE schema_name = %%s"
                % TenantModel._meta.db_table,
                [SCHEMA_NAME],
            )

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Payroll Test Tenant",
            slug="test-payroll",
        )
        tenant.save(verbosity=0)

        domain = DomainModel(
            tenant=tenant,
            domain=TENANT_DOMAIN,
            is_primary=True,
        )
        domain.save()

        yield tenant

        # Teardown: drop schema directly to avoid cascade queries
        connection.set_schema_to_public()
        with connection.cursor() as cur:
            cur.execute(
                "DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_NAME
            )
            cur.execute(
                "DELETE FROM %s WHERE tenant_id = %%s"
                % DomainModel._meta.db_table,
                [tenant.pk],
            )
            cur.execute(
                "DELETE FROM tenants_tenantsettings WHERE tenant_id = %s",
                [tenant.pk],
            )
            cur.execute(
                "DELETE FROM %s WHERE id = %%s"
                % TenantModel._meta.db_table,
                [tenant.pk],
            )


@pytest.fixture
def tenant_context(setup_test_tenant, db):
    """Activate tenant schema for a test."""
    connection.set_tenant(setup_test_tenant)
    yield setup_test_tenant
    connection.set_schema_to_public()


# ──────────────────────────────────────────────────────────────
# User & Employee Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def user(tenant_context):
    """Create a test user within tenant context."""
    User = get_user_model()
    return User.objects.create_user(
        email="payrolltest@example.com",
        password="testpass123",
    )


@pytest.fixture
def staff_user(tenant_context):
    """Create a staff user with approval permissions."""
    User = get_user_model()
    return User.objects.create_user(
        email="staffuser@example.com",
        password="testpass123",
        is_staff=True,
    )


@pytest.fixture
def approver_user(tenant_context):
    """Create a separate staff user for approval (to avoid self-approval)."""
    User = get_user_model()
    return User.objects.create_user(
        email="approver@example.com",
        password="testpass123",
        is_staff=True,
    )


@pytest.fixture
def employee(tenant_context, user):
    """Create a test employee."""
    from apps.employees.models import Employee

    return Employee.objects.create(
        first_name="Rajiv",
        last_name="Perera",
        user=user,
        hire_date=date(2023, 1, 15),
    )


@pytest.fixture
def employee_b(tenant_context):
    """Create a second test employee without a linked user."""
    from apps.employees.models import Employee

    return Employee.objects.create(
        first_name="Nimal",
        last_name="Silva",
        hire_date=date(2024, 3, 1),
    )


# ──────────────────────────────────────────────────────────────
# Salary Component Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def basic_component(tenant_context):
    """Create a BASIC salary component."""
    from apps.payroll.models import SalaryComponent

    return SalaryComponent.objects.create(
        name="Basic Salary",
        code="BASIC",
        component_type=ComponentType.EARNING,
        category=ComponentCategory.BASIC,
        calculation_type=CalculationType.FIXED,
        is_taxable=True,
        is_epf_applicable=True,
        is_fixed=True,
        display_order=1,
    )


@pytest.fixture
def transport_component(tenant_context):
    """Create a TRANSPORT allowance component."""
    from apps.payroll.models import SalaryComponent

    return SalaryComponent.objects.create(
        name="Transport Allowance",
        code="TRANSPORT",
        component_type=ComponentType.EARNING,
        category=ComponentCategory.ALLOWANCE,
        calculation_type=CalculationType.FIXED,
        default_value=Decimal("5000.00"),
        is_taxable=True,
        is_epf_applicable=False,
        is_fixed=True,
        display_order=2,
    )


@pytest.fixture
def medical_component(tenant_context):
    """Create a MEDICAL allowance component."""
    from apps.payroll.models import SalaryComponent

    return SalaryComponent.objects.create(
        name="Medical Allowance",
        code="MEDICAL",
        component_type=ComponentType.EARNING,
        category=ComponentCategory.ALLOWANCE,
        calculation_type=CalculationType.FIXED,
        default_value=Decimal("3000.00"),
        is_taxable=False,
        is_epf_applicable=False,
        is_fixed=True,
        display_order=3,
    )


@pytest.fixture
def epf_ee_component(tenant_context):
    """Create an EPF Employee deduction component."""
    from apps.payroll.models import SalaryComponent

    return SalaryComponent.objects.create(
        name="EPF (Employee)",
        code="EPF_EE",
        component_type=ComponentType.DEDUCTION,
        category=ComponentCategory.STATUTORY,
        calculation_type=CalculationType.PERCENTAGE_OF_BASIC,
        percentage=Decimal("8.00"),
        is_taxable=False,
        is_epf_applicable=False,
        is_fixed=False,
        display_order=10,
    )


@pytest.fixture
def paye_component(tenant_context):
    """Create a PAYE tax deduction component."""
    from apps.payroll.models import SalaryComponent

    return SalaryComponent.objects.create(
        name="PAYE Tax",
        code="PAYE",
        component_type=ComponentType.DEDUCTION,
        category=ComponentCategory.TAX,
        calculation_type=CalculationType.FORMULA,
        is_taxable=False,
        is_epf_applicable=False,
        is_fixed=False,
        display_order=11,
    )


# ──────────────────────────────────────────────────────────────
# Template Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def salary_template(tenant_context):
    """Create a salary template."""
    from apps.payroll.models import SalaryTemplate

    return SalaryTemplate.objects.create(
        name="Standard Template",
        code="STD",
        description="Standard salary template for testing",
    )


@pytest.fixture
def template_with_components(salary_template, basic_component, transport_component, medical_component):
    """Create a salary template with BASIC + TRANSPORT + MEDICAL components."""
    from apps.payroll.models import TemplateComponent

    TemplateComponent.objects.create(
        template=salary_template,
        component=basic_component,
        default_value=Decimal("0"),
        can_override=False,
    )
    TemplateComponent.objects.create(
        template=salary_template,
        component=transport_component,
        default_value=Decimal("5000.00"),
    )
    TemplateComponent.objects.create(
        template=salary_template,
        component=medical_component,
        default_value=Decimal("3000.00"),
    )
    return salary_template


# ──────────────────────────────────────────────────────────────
# Statutory Settings Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def epf_settings(tenant_context):
    """Create EPF settings with standard Sri Lanka rates."""
    from apps.payroll.models import EPFSettings

    return EPFSettings.objects.create(
        employee_rate=Decimal("8.00"),
        employer_rate=Decimal("12.00"),
        is_active=True,
    )


@pytest.fixture
def etf_settings(tenant_context):
    """Create ETF settings with standard Sri Lanka rate."""
    from apps.payroll.models import ETFSettings

    return ETFSettings.objects.create(
        employer_rate=Decimal("3.00"),
        is_active=True,
    )


@pytest.fixture
def paye_slabs(tenant_context):
    """Create 2024 PAYE tax slabs for Sri Lanka."""
    from apps.payroll.models import PAYETaxSlab

    slabs = [
        {"tax_year": 2024, "order": 0, "from_amount": Decimal("0"), "to_amount": Decimal("1200000"), "rate": Decimal("0.00")},
        {"tax_year": 2024, "order": 1, "from_amount": Decimal("1200001"), "to_amount": Decimal("1700000"), "rate": Decimal("6.00")},
        {"tax_year": 2024, "order": 2, "from_amount": Decimal("1700001"), "to_amount": Decimal("2200000"), "rate": Decimal("12.00")},
        {"tax_year": 2024, "order": 3, "from_amount": Decimal("2200001"), "to_amount": Decimal("2700000"), "rate": Decimal("18.00")},
        {"tax_year": 2024, "order": 4, "from_amount": Decimal("2700001"), "to_amount": Decimal("3200000"), "rate": Decimal("24.00")},
        {"tax_year": 2024, "order": 5, "from_amount": Decimal("3200001"), "to_amount": Decimal("3700000"), "rate": Decimal("30.00")},
        {"tax_year": 2024, "order": 6, "from_amount": Decimal("3700001"), "to_amount": None, "rate": Decimal("36.00")},
    ]
    created = []
    for slab in slabs:
        created.append(PAYETaxSlab.objects.create(**slab))
    return created


@pytest.fixture
def tax_exemptions(tenant_context):
    """Create standard tax exemptions."""
    from apps.payroll.models import TaxExemption

    exemptions = [
        TaxExemption.objects.create(
            name="Personal Relief",
            code="PERSONAL",
            exemption_type="PERSONAL",
            tax_year=2024,
            annual_amount=Decimal("1200000.00"),
            monthly_amount=Decimal("100000.00"),
            max_claims=1,
        ),
        TaxExemption.objects.create(
            name="Spouse Relief",
            code="SPOUSE",
            exemption_type="SPOUSE",
            tax_year=2024,
            annual_amount=Decimal("500000.00"),
            monthly_amount=Decimal("41666.67"),
            max_claims=1,
        ),
    ]
    return exemptions


# ──────────────────────────────────────────────────────────────
# Employee Salary Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def employee_salary(employee, basic_component, transport_component, medical_component, tenant_context):
    """Create an employee salary with components for calculation tests."""
    from apps.payroll.models import EmployeeSalary, EmployeeSalaryComponent

    salary = EmployeeSalary.objects.create(
        employee=employee,
        basic_salary=Decimal("100000.00"),
        gross_salary=Decimal("108000.00"),
        effective_from=date(2024, 1, 1),
        is_current=True,
    )
    EmployeeSalaryComponent.objects.create(
        employee_salary=salary,
        component=basic_component,
        amount=Decimal("100000.00"),
    )
    EmployeeSalaryComponent.objects.create(
        employee_salary=salary,
        component=transport_component,
        amount=Decimal("5000.00"),
    )
    EmployeeSalaryComponent.objects.create(
        employee_salary=salary,
        component=medical_component,
        amount=Decimal("3000.00"),
    )
    return salary


# ──────────────────────────────────────────────────────────────
# SP06 Payroll Processing Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def payroll_period(tenant_context):
    """Create a payroll period for testing."""
    from apps.payroll.models import PayrollPeriod

    return PayrollPeriod.objects.create(
        period_month=1,
        period_year=2024,
        name="January 2024",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        pay_date=date(2024, 1, 25),
        total_working_days=22,
    )


@pytest.fixture
def payroll_settings(tenant_context):
    """Create payroll settings."""
    from apps.payroll.models import PayrollSettings

    return PayrollSettings.objects.create(
        default_pay_day=25,
        attendance_cutoff_day=20,
        require_approval=True,
        auto_create_period=False,
    )


@pytest.fixture
def payroll_run(payroll_period, user):
    """Create a payroll run in DRAFT status."""
    from apps.payroll.models import PayrollRun

    return PayrollRun.objects.create(
        payroll_period=payroll_period,
        run_number=1,
        status=PayrollStatus.DRAFT,
    )


@pytest.fixture
def processed_run(payroll_period, user):
    """Create a PROCESSED payroll run."""
    from apps.payroll.models import PayrollRun

    return PayrollRun.objects.create(
        payroll_period=payroll_period,
        run_number=2,
        status=PayrollStatus.PROCESSED,
        processed_by=user,
        total_employees=1,
        total_gross=Decimal("108000.00"),
        total_net=Decimal("95000.00"),
    )


@pytest.fixture
def employee_payroll_record(payroll_run, employee, employee_salary):
    """Create an employee payroll record."""
    from apps.payroll.models import EmployeePayroll

    return EmployeePayroll.objects.create(
        payroll_run=payroll_run,
        employee=employee,
        employee_salary=employee_salary,
        days_worked=22,
        days_absent=0,
        basic_salary=Decimal("100000.00"),
        gross_salary=Decimal("108000.00"),
        total_deductions=Decimal("8000.00"),
        net_salary=Decimal("100000.00"),
        epf_employee=Decimal("8000.00"),
        epf_employer=Decimal("12000.00"),
        etf=Decimal("3000.00"),
        paye_tax=Decimal("0.00"),
    )


@pytest.fixture
def payroll_line_item(employee_payroll_record, basic_component):
    """Create a payroll line item."""
    from apps.payroll.models import PayrollLineItem

    return PayrollLineItem.objects.create(
        employee_payroll=employee_payroll_record,
        component=basic_component,
        line_type=LineType.EARNING,
        base_amount=Decimal("100000.00"),
        calculated_amount=Decimal("100000.00"),
        final_amount=Decimal("100000.00"),
    )
