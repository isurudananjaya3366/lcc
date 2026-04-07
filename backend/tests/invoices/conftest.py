"""Invoice test fixtures."""

import pytest
from decimal import Decimal

from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

from apps.invoices.constants import InvoiceStatus, InvoiceType

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_invoices"
TENANT_DOMAIN = "invoices.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create a test tenant schema once per session."""
    with django_db_blocker.unblock():
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Invoices Test Tenant",
            slug="invoices-test",
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
        try:
            from django.db import connection as conn

            conn.set_schema_to_public()
            cursor = conn.cursor()
            cursor.execute(
                f'DROP SCHEMA IF EXISTS "{SCHEMA_NAME}" CASCADE'
            )
            cursor.execute(
                "DELETE FROM tenants_domain WHERE domain = %s",
                [TENANT_DOMAIN],
            )
            cursor.execute(
                "DELETE FROM tenants_tenant WHERE schema_name = %s",
                [SCHEMA_NAME],
            )
        except Exception:
            pass


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
def invoice_data(tenant_context):
    """Basic invoice field data."""
    return {
        "type": InvoiceType.STANDARD,
        "status": InvoiceStatus.DRAFT,
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "customer_phone": "+94771234567",
        "customer_address": "123 Test St, Colombo",
        "business_name": "Test Business Pvt Ltd",
        "business_address": "456 Business Ave, Colombo",
        "business_phone": "+94112345678",
        "business_email": "biz@example.com",
        "business_registration_number": "PV12345",
        "vat_registration_number": "VAT12345678",
        "currency": "LKR",
        "currency_symbol": "LKR",
    }


@pytest.fixture
def line_item_data(tenant_context):
    """Basic line item field data."""
    return {
        "position": 1,
        "description": "Test Product",
        "sku": "TST-001",
        "quantity": Decimal("2"),
        "unit_price": Decimal("1000.00"),
        "tax_rate": Decimal("18.00"),
        "is_taxable": True,
    }
