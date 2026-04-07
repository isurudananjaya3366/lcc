"""Fixtures for purchases module tests."""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_purchases"
TENANT_DOMAIN = "purchases.testserver"


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create and destroy a test tenant for purchases tests."""
    with django_db_blocker.unblock():
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Test Purchases Tenant",
            slug="test-purchases",
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
        email="purchtest@example.com",
        password="testpass123",
    )


@pytest.fixture
def second_user(tenant_context):
    """Create a second test user."""
    User = get_user_model()
    return User.objects.create_user(
        email="purchtest2@example.com",
        password="testpass123",
    )


@pytest.fixture
def vendor(tenant_context):
    """Create a test vendor."""
    from apps.vendors.models import Vendor

    return Vendor.objects.create(
        company_name="Test Purchase Vendor",
        vendor_type="manufacturer",
        status="active",
        primary_email="vendor@purchase.test",
        primary_phone="+94771234567",
        payment_terms_days=30,
        credit_limit=Decimal("100000.00"),
    )


@pytest.fixture
def second_vendor(tenant_context):
    """Create a second test vendor."""
    from apps.vendors.models import Vendor

    return Vendor.objects.create(
        company_name="Second Vendor",
        vendor_type="distributor",
        status="active",
        primary_email="vendor2@purchase.test",
    )


@pytest.fixture
def purchase_order(tenant_context, vendor, user):
    """Create a test purchase order."""
    from apps.purchases.models import PurchaseOrder

    return PurchaseOrder.objects.create(
        vendor=vendor,
        created_by=user,
    )


@pytest.fixture
def po_with_lines(purchase_order):
    """Create a PO with line items."""
    from apps.purchases.models import POLineItem

    POLineItem.objects.create(
        purchase_order=purchase_order,
        line_number=1,
        product_name="Widget A",
        quantity_ordered=10,
        unit_price=Decimal("25.00"),
        tax_rate=Decimal("8.00"),
    )
    POLineItem.objects.create(
        purchase_order=purchase_order,
        line_number=2,
        product_name="Widget B",
        quantity_ordered=5,
        unit_price=Decimal("50.00"),
        tax_rate=Decimal("8.00"),
    )
    purchase_order.refresh_from_db()
    return purchase_order
