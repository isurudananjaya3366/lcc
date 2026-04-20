"""Fixtures for vendor_bills module tests."""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_vendor_bills"
TENANT_DOMAIN = "vendorbills.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for vendor_bills tests."""
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
            name="Test Vendor Bills Tenant",
            slug="test-vendor-bills",
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
        email="vbtest@example.com",
        password="testpass123",
    )


@pytest.fixture
def second_user(tenant_context):
    """Create a second test user."""
    User = get_user_model()
    return User.objects.create_user(
        email="vbtest2@example.com",
        password="testpass123",
    )


@pytest.fixture
def vendor(tenant_context):
    """Create a test vendor."""
    from apps.vendors.models import Vendor

    return Vendor.objects.create(
        company_name="Test VB Vendor",
        vendor_type="manufacturer",
        status="active",
        primary_email="vendor@vendorbill.test",
        primary_phone="+94771234567",
        payment_terms_days=30,
        credit_limit=Decimal("100000.00"),
    )


@pytest.fixture
def second_vendor(tenant_context):
    """Create a second vendor."""
    from apps.vendors.models import Vendor

    return Vendor.objects.create(
        company_name="Second VB Vendor",
        vendor_type="distributor",
        status="active",
        primary_email="vendor2@vendorbill.test",
    )


@pytest.fixture
def vendor_bill(vendor, user):
    """Create a basic vendor bill."""
    from apps.vendor_bills.models import VendorBill

    return VendorBill.objects.create(
        vendor=vendor,
        created_by=user,
        bill_date="2025-06-01",
        received_date="2025-06-01",
        due_date="2025-07-01",
    )


@pytest.fixture
def vendor_bill_with_lines(vendor_bill):
    """Create a vendor bill with line items."""
    from apps.vendor_bills.models import BillLineItem

    BillLineItem.objects.create(
        vendor_bill=vendor_bill,
        line_number=1,
        item_description="Widget A",
        quantity=Decimal("10"),
        billed_price=Decimal("25.00"),
        tax_rate=Decimal("8.00"),
    )
    BillLineItem.objects.create(
        vendor_bill=vendor_bill,
        line_number=2,
        item_description="Widget B",
        quantity=Decimal("5"),
        billed_price=Decimal("50.00"),
        tax_rate=Decimal("8.00"),
    )
    vendor_bill.refresh_from_db()
    return vendor_bill


@pytest.fixture
def approved_bill(vendor_bill_with_lines):
    """Create an approved vendor bill."""
    from apps.vendor_bills.constants import BILL_STATUS_APPROVED

    bill = vendor_bill_with_lines
    bill.status = BILL_STATUS_APPROVED
    bill.save(update_fields=["status"])
    return bill
