"""
Shared fixtures for attendance module tests.

Provides tenant-aware fixtures for testing attendance models, services,
and API endpoints against a real PostgreSQL database with proper
tenant schema isolation.
"""

import uuid
from datetime import date, time, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
from rest_framework.test import APIClient

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_attendance"
TENANT_DOMAIN = "attendance.testserver"

User = get_user_model()


# ═══════════════════════════════════════════════════════════════════════
# Tenant Lifecycle Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for attendance tests."""
    with django_db_blocker.unblock():
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Attendance Test Tenant",
            slug="attendance-test",
        )
        tenant.save(verbosity=0)

        domain = DomainModel(
            tenant=tenant,
            domain=TENANT_DOMAIN,
            is_primary=True,
        )
        domain.save()

        yield tenant

        # Teardown: raw SQL to avoid cascade queries on dropped schema
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


@pytest.fixture(autouse=True)
def tenant_context(setup_test_tenant, db):
    """Activate the test tenant schema for every test."""
    connection.set_tenant(setup_test_tenant)
    yield setup_test_tenant
    connection.set_schema_to_public()


# ═══════════════════════════════════════════════════════════════════════
# User & Auth Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def user(tenant_context):
    """Create a test platform user."""
    return User.objects.create_user(
        email=f"att-{uuid.uuid4().hex[:6]}@example.com",
        password="testpass123",
    )


@pytest.fixture
def api_client(user):
    """Authenticated API client with tenant host header."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    client._user = user
    return client


# ═══════════════════════════════════════════════════════════════════════
# Model Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def department(tenant_context):
    """Create a test department."""
    from apps.organization.models import Department

    return Department.objects.create(
        name="Engineering",
        code="ENG",
        status="active",
    )


@pytest.fixture
def employee(tenant_context, user, department):
    """Create a test employee linked to the user."""
    from apps.employees.models import Employee

    return Employee.objects.create(
        user=user,
        first_name="Test",
        last_name="Employee",
        employee_id=f"EMP-{uuid.uuid4().hex[:4].upper()}",
        email=user.email,
        date_of_birth=date(1990, 1, 1),
        gender="male",
        hire_date=date(2024, 1, 1),
        department=department,
        status="active",
        employment_type="full_time",
    )


@pytest.fixture
def shift(tenant_context):
    """Create a default day shift."""
    from apps.attendance.models import Shift

    return Shift.objects.create(
        name="Regular Day Shift",
        code=f"SHF-{uuid.uuid4().hex[:4].upper()}",
        shift_type="regular",
        status="active",
        start_time=time(9, 0),
        end_time=time(17, 30),
        break_start=time(13, 0),
        break_end=time(13, 30),
        is_default=True,
    )


@pytest.fixture
def attendance_record(tenant_context, employee, shift):
    """Create a basic attendance record for today."""
    from django.utils import timezone

    from apps.attendance.models import AttendanceRecord

    now = timezone.now()
    return AttendanceRecord.objects.create(
        employee=employee,
        date=date.today(),
        clock_in=now,
        status="present",
        shift=shift,
        clock_in_method="web",
    )
