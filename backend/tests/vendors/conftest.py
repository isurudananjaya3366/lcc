"""Fixtures for vendor module tests."""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_vendors"
TENANT_DOMAIN = "vendors.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for vendor tests."""
    with django_db_blocker.unblock():
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Test Vendors Tenant",
            slug="test-vendors",
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
        # on tables that may not exist in the test tenant schema.
        connection.set_schema_to_public()
        with connection.cursor() as cur:
            cur.execute(
                "DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_NAME
            )
            # Delete domain and tenant rows directly to avoid
            # Django's cascade collector querying dropped schema tables.
            cur.execute(
                "DELETE FROM %s WHERE tenant_id = %%s"
                % DomainModel._meta.db_table,
                [tenant.pk],
            )
            # Delete any tenant settings before the tenant itself.
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
        email="vendortest@example.com",
        password="testpass123",
    )


@pytest.fixture
def vendor(tenant_context):
    """Create a test vendor."""
    from apps.vendors.models import Vendor

    return Vendor.objects.create(
        company_name="Test Vendor Co",
        vendor_type="manufacturer",
        status="active",
        primary_email="vendor@test.com",
        primary_phone="+94771234567",
        payment_terms_days=30,
        credit_limit=Decimal("100000.00"),
    )


@pytest.fixture
def vendor_with_user(tenant_context, user):
    """Create a test vendor with created_by."""
    from apps.vendors.models import Vendor

    return Vendor.objects.create(
        company_name="Test Vendor With User",
        vendor_type="distributor",
        status="active",
        created_by=user,
    )


@pytest.fixture
def vendor_contact(vendor):
    """Create a test vendor contact."""
    from apps.vendors.models import VendorContact

    return VendorContact.objects.create(
        vendor=vendor,
        first_name="John",
        last_name="Doe",
        email="john@test.com",
        phone="+94771111111",
        role="sales",
        is_primary=True,
    )


@pytest.fixture
def vendor_address(vendor):
    """Create a test vendor address."""
    from apps.vendors.models import VendorAddress

    return VendorAddress.objects.create(
        vendor=vendor,
        address_type="main",
        address_line_1="123 Test Street",
        city="Colombo",
        district="Colombo",
        province="Western",
        is_default=True,
    )


@pytest.fixture
def vendor_bank(vendor):
    """Create a test vendor bank account."""
    from apps.vendors.models import VendorBankAccount

    return VendorBankAccount.objects.create(
        vendor=vendor,
        bank_name="Test Bank",
        account_name="Test Vendor Co",
        account_number="1234567890",
        branch_name="Main Branch",
        currency="LKR",
        is_default=True,
    )


@pytest.fixture
def api_client(user):
    """Authenticated API client with tenant host header."""
    from rest_framework.test import APIClient

    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    return client
