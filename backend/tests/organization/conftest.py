"""Fixtures for the organization module tests."""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_organization"
TENANT_DOMAIN = "testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for organization tests."""
    with django_db_blocker.unblock():
        with connection.cursor() as cur:
            cur.execute(
                "SELECT nspname FROM pg_catalog.pg_namespace "
                "WHERE nspname = %s",
                [SCHEMA_NAME],
            )
            schema_exists = cur.fetchone() is not None

        if schema_exists:
            try:
                tenant = TenantModel.objects.get(schema_name=SCHEMA_NAME)
                # Ensure domain always points to this tenant (other test suites
                # share the same TENANT_DOMAIN and may have repointed it)
                DomainModel.objects.update_or_create(
                    domain=TENANT_DOMAIN,
                    defaults={"tenant": tenant, "is_primary": True},
                )
                connection.set_tenant(tenant)
                yield tenant
                connection.set_schema_to_public()
                return
            except TenantModel.DoesNotExist:
                with connection.cursor() as cur:
                    cur.execute(
                        "DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_NAME
                    )

        with connection.cursor() as cur:
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
            name="Test Organization Tenant",
            slug="test-organization",
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
        email="orgtest@example.com",
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
def department(tenant_context):
    """Create a basic test department."""
    from apps.organization.models import Department

    return Department.objects.create(
        name="Engineering",
        code="DEPT-ENG",
        status="active",
        description="Engineering department",
        annual_budget=Decimal("1000000.00"),
    )


@pytest.fixture
def child_department(department):
    """Create a child department under Engineering."""
    from apps.organization.models import Department

    return Department.objects.create(
        name="Backend",
        code="DEPT-BE",
        status="active",
        parent=department,
    )


@pytest.fixture
def second_department(tenant_context):
    """Create a second department."""
    from apps.organization.models import Department

    return Department.objects.create(
        name="Human Resources",
        code="DEPT-HR",
        status="active",
        description="HR department",
        annual_budget=Decimal("500000.00"),
    )


@pytest.fixture
def designation(tenant_context):
    """Create a basic test designation."""
    from apps.organization.models import Designation

    return Designation.objects.create(
        title="Software Engineer",
        code="SE",
        status="active",
        level="mid",
        min_salary=Decimal("50000.00"),
        max_salary=Decimal("100000.00"),
    )


@pytest.fixture
def manager_designation(tenant_context):
    """Create a manager designation."""
    from apps.organization.models import Designation

    return Designation.objects.create(
        title="Engineering Manager",
        code="EM",
        status="active",
        level="manager",
        is_manager=True,
        min_salary=Decimal("120000.00"),
        max_salary=Decimal("200000.00"),
    )
