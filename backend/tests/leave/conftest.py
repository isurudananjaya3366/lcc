"""Fixtures for leave module production tests."""

import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

from apps.leave.constants import (
    LeaveTypeCategory,
    LeaveRequestStatus,
    HalfDayType,
    HolidayType,
    HolidayScope,
)

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_leave"
TENANT_DOMAIN = "leave.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for leave tests."""
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
            name="Leave Test Tenant",
            slug="test-leave",
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
        email="leavetest@example.com",
        password="testpass123",
    )


@pytest.fixture
def approver_user(tenant_context):
    """Create an approver/manager user within tenant context."""
    User = get_user_model()
    return User.objects.create_user(
        email="approver@example.com",
        password="testpass123",
    )


@pytest.fixture
def employee(tenant_context, user):
    """Create a test employee."""
    from apps.employees.models import Employee

    return Employee.objects.create(
        first_name="John",
        last_name="Doe",
        user=user,
        hire_date=date(2023, 1, 15),
    )


@pytest.fixture
def employee_no_user(tenant_context):
    """Create a test employee without a linked user."""
    from apps.employees.models import Employee

    return Employee.objects.create(
        first_name="Jane",
        last_name="Smith",
        hire_date=date(2024, 6, 1),
    )


@pytest.fixture
def manager_employee(tenant_context, approver_user):
    """Create a manager employee."""
    from apps.employees.models import Employee

    return Employee.objects.create(
        first_name="Manager",
        last_name="Boss",
        user=approver_user,
        hire_date=date(2022, 1, 1),
    )


@pytest.fixture
def department(tenant_context):
    """Create a test department."""
    from apps.organization.models import Department

    return Department.objects.create(
        name="Engineering",
        code="DEPT-ENG",
    )


# ──────────────────────────────────────────────────────────────
# Leave Type Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def annual_leave_type(tenant_context):
    """Create an Annual Leave type (Sri Lankan standard: 14 days)."""
    from apps.leave.models import LeaveType

    return LeaveType.objects.create(
        name="Annual Leave",
        code="AL",
        category=LeaveTypeCategory.ANNUAL,
        default_days_per_year=14,
        is_paid=True,
        is_active=True,
        allow_half_day=True,
        max_consecutive_days=14,
    )


@pytest.fixture
def casual_leave_type(tenant_context):
    """Create a Casual Leave type (Sri Lankan standard: 7 days)."""
    from apps.leave.models import LeaveType

    return LeaveType.objects.create(
        name="Casual Leave",
        code="CL",
        category=LeaveTypeCategory.CASUAL,
        default_days_per_year=7,
        is_paid=True,
        is_active=True,
        allow_half_day=True,
    )


@pytest.fixture
def sick_leave_type(tenant_context):
    """Create a Sick Leave type (Sri Lankan standard: 7 days)."""
    from apps.leave.models import LeaveType

    return LeaveType.objects.create(
        name="Sick Leave",
        code="SL",
        category=LeaveTypeCategory.SICK,
        default_days_per_year=7,
        is_paid=True,
        is_active=True,
        requires_document=True,
        document_after_days=2,
    )


@pytest.fixture
def no_pay_leave_type(tenant_context):
    """Create a No-Pay Leave type."""
    from apps.leave.models import LeaveType

    return LeaveType.objects.create(
        name="No-Pay Leave",
        code="NPL",
        category=LeaveTypeCategory.NO_PAY,
        is_paid=False,
        is_active=True,
    )


@pytest.fixture
def inactive_leave_type(tenant_context):
    """Create an inactive leave type."""
    from apps.leave.models import LeaveType

    return LeaveType.objects.create(
        name="Inactive Leave",
        code="IL",
        category=LeaveTypeCategory.OTHER,
        is_active=False,
    )


# ──────────────────────────────────────────────────────────────
# Leave Policy Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def annual_leave_policy(tenant_context, annual_leave_type):
    """Create a policy for annual leave (ALL employees)."""
    from apps.leave.models import LeavePolicy

    return LeavePolicy.objects.create(
        name="Annual Leave Policy (All)",
        leave_type=annual_leave_type,
        days_per_year=14,
        is_active=True,
        effective_from=date(2024, 1, 1),
    )


@pytest.fixture
def casual_leave_policy(tenant_context, casual_leave_type):
    """Create a policy for casual leave (ALL employees)."""
    from apps.leave.models import LeavePolicy

    return LeavePolicy.objects.create(
        name="Casual Leave Policy (All)",
        leave_type=casual_leave_type,
        days_per_year=7,
        is_active=True,
        effective_from=date(2024, 1, 1),
    )


# ──────────────────────────────────────────────────────────────
# Leave Balance Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def annual_balance(tenant_context, employee, annual_leave_type):
    """Create an annual leave balance for the current year."""
    from apps.leave.models import LeaveBalance

    return LeaveBalance.objects.create(
        employee=employee,
        leave_type=annual_leave_type,
        year=date.today().year,
        opening_balance=Decimal("14.00"),
        allocated_days=Decimal("0.00"),
        used_days=Decimal("0.00"),
        pending_days=Decimal("0.00"),
        is_active=True,
    )


@pytest.fixture
def balance_with_carry_forward(tenant_context, employee, annual_leave_type):
    """Create a balance with carry-forward days and expiry date."""
    from apps.leave.models import LeaveBalance

    return LeaveBalance.objects.create(
        employee=employee,
        leave_type=annual_leave_type,
        year=date.today().year,
        opening_balance=Decimal("14.00"),
        carried_from_previous=Decimal("5.00"),
        carry_forward_expiry=date(date.today().year, 6, 30),
        is_active=True,
    )


@pytest.fixture
def casual_balance(tenant_context, employee, casual_leave_type):
    """Create a casual leave balance."""
    from apps.leave.models import LeaveBalance

    return LeaveBalance.objects.create(
        employee=employee,
        leave_type=casual_leave_type,
        year=date.today().year,
        opening_balance=Decimal("7.00"),
        is_active=True,
    )


# ──────────────────────────────────────────────────────────────
# Leave Request Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def draft_leave_request(tenant_context, employee, annual_leave_type):
    """Create a draft leave request."""
    from apps.leave.models import LeaveRequest

    return LeaveRequest.objects.create(
        employee=employee,
        leave_type=annual_leave_type,
        start_date=date(date.today().year, 7, 1),
        end_date=date(date.today().year, 7, 5),
        total_days=Decimal("5.00"),
        status=LeaveRequestStatus.DRAFT,
        reason="Annual vacation",
    )


@pytest.fixture
def pending_leave_request(tenant_context, employee, annual_leave_type):
    """Create a pending leave request."""
    from apps.leave.models import LeaveRequest
    from django.utils import timezone

    return LeaveRequest.objects.create(
        employee=employee,
        leave_type=annual_leave_type,
        start_date=date(date.today().year, 8, 1),
        end_date=date(date.today().year, 8, 3),
        total_days=Decimal("3.00"),
        status=LeaveRequestStatus.PENDING,
        reason="Personal leave",
        submitted_at=timezone.now(),
    )


@pytest.fixture
def approved_leave_request(tenant_context, employee, annual_leave_type, approver_user):
    """Create an approved leave request."""
    from apps.leave.models import LeaveRequest
    from django.utils import timezone

    return LeaveRequest.objects.create(
        employee=employee,
        leave_type=annual_leave_type,
        start_date=date(date.today().year, 9, 1),
        end_date=date(date.today().year, 9, 2),
        total_days=Decimal("2.00"),
        status=LeaveRequestStatus.APPROVED,
        reason="Short trip",
        submitted_at=timezone.now(),
        approved_by=approver_user,
        approved_at=timezone.now(),
    )


# ──────────────────────────────────────────────────────────────
# Holiday Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def public_holiday(tenant_context):
    """Create a public holiday."""
    from apps.leave.models import Holiday

    return Holiday.objects.create(
        name="Sinhala and Tamil New Year",
        date=date(date.today().year, 4, 14),
        holiday_type=HolidayType.PUBLIC,
        applies_to=HolidayScope.ALL,
        is_active=True,
    )


@pytest.fixture
def company_holiday(tenant_context):
    """Create a company holiday."""
    from apps.leave.models import Holiday

    return Holiday.objects.create(
        name="Company Anniversary",
        date=date(date.today().year, 3, 15),
        holiday_type=HolidayType.COMPANY,
        applies_to=HolidayScope.ALL,
        is_active=True,
    )


@pytest.fixture
def department_holiday(tenant_context, department):
    """Create a department-specific holiday."""
    from apps.leave.models import Holiday

    return Holiday.objects.create(
        name="Engineering Day",
        date=date(date.today().year, 10, 1),
        holiday_type=HolidayType.COMPANY,
        applies_to=HolidayScope.DEPARTMENT,
        department=department,
        is_active=True,
    )
