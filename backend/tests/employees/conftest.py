"""Fixtures for employees module tests."""

import pytest
from datetime import date
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_employees"
TENANT_DOMAIN = "testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for employees tests."""
    with django_db_blocker.unblock():
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Test Employees Tenant",
            slug="test-employees",
        )
        tenant.save(verbosity=0)

        domain = DomainModel(
            tenant=tenant,
            domain=TENANT_DOMAIN,
            is_primary=True,
        )
        domain.save()

        yield tenant

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


@pytest.fixture
def user(tenant_context):
    """Create a test user within tenant context."""
    User = get_user_model()
    return User.objects.create_user(
        email="emptest@example.com",
        password="testpass123",
    )


@pytest.fixture
def employee(tenant_context):
    """Create a basic test employee."""
    from apps.employees.models import Employee
    return Employee.objects.create(
        first_name="John",
        last_name="Silva",
        nic_number="199123456789",
        email="john.silva@example.com",
        mobile="+94712345678",
        date_of_birth=date(1991, 1, 15),
        gender="male",
        employment_type="full_time",
        status="active",
        hire_date=date(2024, 1, 1),
    )


@pytest.fixture
def second_employee(tenant_context):
    """Create a second test employee."""
    from apps.employees.models import Employee
    return Employee.objects.create(
        first_name="Jane",
        last_name="Perera",
        nic_number="199545678901",
        email="jane.perera@example.com",
        mobile="+94771234567",
        date_of_birth=date(1995, 6, 20),
        gender="female",
        employment_type="full_time",
        status="active",
        hire_date=date(2024, 3, 15),
    )


@pytest.fixture
def employee_address(employee):
    """Create a test employee address."""
    from apps.employees.models import EmployeeAddress
    return EmployeeAddress.objects.create(
        employee=employee,
        address_type="permanent",
        line1="123 Main Street",
        city="Colombo",
        province="western",
        postal_code="10100",
        is_primary=True,
    )


@pytest.fixture
def emergency_contact(employee):
    """Create a test emergency contact."""
    from apps.employees.models import EmergencyContact
    return EmergencyContact.objects.create(
        employee=employee,
        name="Mary Silva",
        relationship="spouse",
        phone="+94712345679",
        priority=1,
    )


@pytest.fixture
def employee_bank_account(employee):
    """Create a test bank account."""
    from apps.employees.models import EmployeeBankAccount
    return EmployeeBankAccount.objects.create(
        employee=employee,
        bank_name="Bank of Ceylon",
        branch_name="Colombo Fort",
        account_number="1234567890",
        account_type="savings",
        is_primary=True,
    )
