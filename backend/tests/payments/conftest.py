"""Payment test fixtures."""

import pytest
from decimal import Decimal

from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

from apps.payments.constants import PaymentMethod, PaymentStatus

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_payments"
TENANT_DOMAIN = "payments.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create a test tenant schema once per session."""
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
            name="Payments Test Tenant",
            slug="payments-test",
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
    """Activate the test tenant schema for a test."""
    connection.set_tenant(setup_test_tenant)
    yield setup_test_tenant
    connection.set_schema_to_public()


@pytest.fixture
def user(tenant_context):
    """Create and return a regular user within the tenant schema."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        email="testuser@example.com",
        password="testpass123",
    )


@pytest.fixture
def staff_user(tenant_context):
    """Create and return a staff user within the tenant schema."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        email="staff@example.com",
        password="staffpass123",
        is_staff=True,
    )


@pytest.fixture
def customer(tenant_context):
    """Create and return a test customer."""
    from apps.customers.models import Customer

    return Customer.objects.create(
        first_name="Test",
        last_name="Customer",
        business_name="Test Customer Pvt Ltd",
        email="customer@example.com",
        phone="+94771234567",
    )


@pytest.fixture
def invoice(tenant_context, customer):
    """Create and return a test invoice."""
    from apps.invoices.models import Invoice

    return Invoice.objects.create(
        status="ISSUED",
        customer=customer,
        customer_name=customer.business_name,
        customer_email=customer.email,
        total=Decimal("10000.00"),
        balance_due=Decimal("10000.00"),
        amount_paid=Decimal("0.00"),
        currency="LKR",
    )


@pytest.fixture
def payment_data():
    """Return basic payment creation data."""
    return {
        "method": PaymentMethod.CASH,
        "amount": Decimal("5000.00"),
        "currency": "LKR",
        "notes": "Test payment",
    }


@pytest.fixture
def payment(tenant_context, customer, payment_data):
    """Create and return a test payment in PENDING status."""
    from apps.payments.models import Payment
    from apps.payments.services.number_generator import PaymentNumberGenerator

    return Payment.objects.create(
        payment_number=PaymentNumberGenerator.generate(),
        customer=customer,
        **payment_data,
    )


@pytest.fixture
def completed_payment(tenant_context, customer, invoice):
    """Create and return a COMPLETED payment."""
    from apps.payments.models import Payment
    from apps.payments.services.number_generator import PaymentNumberGenerator

    return Payment.objects.create(
        payment_number=PaymentNumberGenerator.generate(),
        customer=customer,
        invoice=invoice,
        method=PaymentMethod.CASH,
        status=PaymentStatus.COMPLETED,
        amount=Decimal("5000.00"),
        currency="LKR",
    )


@pytest.fixture
def api_client(tenant_context):
    """Return an API client configured for the test tenant."""
    from rest_framework.test import APIClient

    return APIClient(HTTP_HOST=TENANT_DOMAIN)
