"""Fixtures for payslip module tests."""

import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_payslip"
TENANT_DOMAIN = "payslip.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for payslip tests."""
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
            name="Payslip Test Tenant",
            slug="test-payslip",
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
# User Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def user(tenant_context):
    """Create a test user within tenant context."""
    User = get_user_model()
    return User.objects.create_user(
        email="paysliptest@example.com",
        password="testpass123",
    )


@pytest.fixture
def admin_user(tenant_context):
    """Create an admin staff user."""
    User = get_user_model()
    return User.objects.create_user(
        email="admin@example.com",
        password="testpass123",
        is_staff=True,
        is_superuser=True,
    )


# ──────────────────────────────────────────────────────────────
# Employee Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def employee(tenant_context, user):
    """Create a test employee linked to user."""
    from apps.employees.models import Employee

    return Employee.objects.create(
        first_name="Kamal",
        last_name="Fernando",
        user=user,
        hire_date=date(2023, 1, 15),
        email="kamal@example.com",
    )


# ──────────────────────────────────────────────────────────────
# Payroll Period & EmployeePayroll Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def payroll_period(tenant_context):
    """Create a payroll period."""
    from apps.payroll.models import PayrollPeriod

    return PayrollPeriod.objects.create(
        period_month=1,
        period_year=2026,
        name="January 2026",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        pay_date=date(2026, 1, 31),
    )


@pytest.fixture
def payroll_run(tenant_context, payroll_period, admin_user):
    """Create a payroll run."""
    from apps.payroll.models import PayrollRun

    return PayrollRun.objects.create(
        payroll_period=payroll_period,
        processed_by=admin_user,
    )


@pytest.fixture
def employee_payroll(tenant_context, payroll_run, employee):
    """Create an employee payroll record."""
    from apps.payroll.models import EmployeePayroll

    return EmployeePayroll.objects.create(
        payroll_run=payroll_run,
        employee=employee,
        days_worked=22,
    )


# ──────────────────────────────────────────────────────────────
# Payslip Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def payslip(tenant_context, employee, payroll_period, employee_payroll):
    """Create a basic payslip in DRAFT status."""
    from apps.payslip.models import Payslip

    return Payslip.objects.create(
        employee=employee,
        payroll_period=payroll_period,
        employee_payroll=employee_payroll,
    )


@pytest.fixture
def payslip_with_lines(payslip):
    """Create a payslip with earning and deduction line items."""
    from apps.payslip.models import PayslipDeduction, PayslipEarning

    PayslipEarning.objects.create(
        payslip=payslip,
        component_code="BASIC",
        component_name="Basic Salary",
        amount=Decimal("50000.00"),
        ytd_amount=Decimal("50000.00"),
        display_order=1,
    )
    PayslipEarning.objects.create(
        payslip=payslip,
        component_code="TRANSPORT",
        component_name="Transport Allowance",
        amount=Decimal("5000.00"),
        ytd_amount=Decimal("5000.00"),
        display_order=2,
    )
    PayslipDeduction.objects.create(
        payslip=payslip,
        component_code="EPF_EE",
        component_name="EPF (Employee)",
        amount=Decimal("4000.00"),
        ytd_amount=Decimal("4000.00"),
        display_order=1,
    )
    return payslip


@pytest.fixture
def payslip_template(tenant_context):
    """Create an active payslip template."""
    from apps.payslip.models import PayslipTemplate

    return PayslipTemplate.objects.create(
        is_active=True,
        company_name="Test Company (Pvt) Ltd",
        company_address="123 Test Street, Colombo 01",
        company_phone="0112345678",
        company_email="hr@testcompany.lk",
        epf_number="EPF/12345",
        etf_number="ETF/12345",
        footer_text="This is a computer-generated payslip.",
        show_footer=True,
    )


@pytest.fixture
def api_client():
    """Return an API client."""
    from rest_framework.test import APIClient

    return APIClient(HTTP_HOST=TENANT_DOMAIN)
