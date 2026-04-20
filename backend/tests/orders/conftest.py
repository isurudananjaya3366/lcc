"""
Shared fixtures for order tests.

Provides tenant-aware fixtures for testing order models, services,
and API endpoints against a real PostgreSQL database with proper
tenant schema isolation.

Prerequisites:
    - PostgreSQL backend (DJANGO_SETTINGS_MODULE=config.settings.test_pg)
    - docker compose up db  (the lcc-postgres container must be running)
"""

import pytest
from decimal import Decimal

from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_orders"
TENANT_DOMAIN = "orders.testserver"


# ═══════════════════════════════════════════════════════════════════════
# Tenant Lifecycle Fixtures
# ═══════════════════════════════════════════════════════════════════════


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
            name="Orders Test Tenant",
            slug="orders-test",
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


# ═══════════════════════════════════════════════════════════════════════
# User Fixtures (PlatformUser uses email, no username)
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def user(tenant_context):
    """Create and return a regular user within the tenant schema."""
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_user(
        email="testuser@example.com",
        password="testpass123",  # noqa: S106
    )


@pytest.fixture
def staff_user(tenant_context):
    """Create and return a staff user within the tenant schema."""
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_user(
        email="staff@example.com",
        password="staffpass123",  # noqa: S106
        is_staff=True,
    )


# ═══════════════════════════════════════════════════════════════════════
# Data Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def order_data():
    """Basic order creation data."""
    return {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "customer_phone": "+94771234567",
        "source": "manual",
        "currency": "LKR",
        "notes": "Test order",
    }


@pytest.fixture
def line_item_data():
    """Basic line item data."""
    return {
        "item_name": "Test Product",
        "item_sku": "TP-001",
        "quantity_ordered": Decimal("2"),
        "unit_price": Decimal("1500.00"),
        "original_price": Decimal("1500.00"),
        "is_taxable": True,
        "tax_rate": Decimal("18.00"),
    }


# ═══════════════════════════════════════════════════════════════════════
# Factory Fixtures (tenant-aware)
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def create_order(tenant_context):
    """Factory fixture to create an Order instance."""
    def _create_order(**kwargs):
        from apps.orders.models import Order
        from apps.orders.constants import OrderStatus, OrderSource

        defaults = {
            "order_number": f"ORD-TEST-{Order.objects.count() + 1:04d}",
            "status": OrderStatus.PENDING,
            "source": OrderSource.MANUAL,
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "currency": "LKR",
            "subtotal": Decimal("0"),
            "total_amount": Decimal("0"),
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)

    return _create_order


@pytest.fixture
def create_line_item(tenant_context):
    """Factory fixture to create an OrderLineItem instance."""
    def _create_line_item(order, **kwargs):
        from apps.orders.models import OrderLineItem

        defaults = {
            "item_name": "Test Product",
            "item_sku": "TP-001",
            "quantity_ordered": Decimal("2"),
            "unit_price": Decimal("1500.00"),
            "original_price": Decimal("1500.00"),
            "is_taxable": True,
            "tax_rate": Decimal("18.00"),
        }
        defaults.update(kwargs)
        item = OrderLineItem(order=order, **defaults)
        item.recalculate()
        item.save()
        return item

    return _create_line_item


@pytest.fixture
def sample_order(create_order):
    """A simple order in PENDING status."""
    return create_order()


@pytest.fixture
def confirmed_order(create_order):
    """An order in CONFIRMED status."""
    from apps.orders.constants import OrderStatus
    return create_order(status=OrderStatus.CONFIRMED)


@pytest.fixture
def delivered_order(create_order, create_line_item):
    """An order in DELIVERED status with fulfilled line items."""
    from apps.orders.constants import OrderStatus
    from django.utils import timezone

    order = create_order(
        status=OrderStatus.DELIVERED,
        delivered_at=timezone.now(),
        subtotal=Decimal("3000.00"),
        total_amount=Decimal("3540.00"),
    )
    create_line_item(
        order,
        quantity_ordered=Decimal("2"),
        quantity_fulfilled=Decimal("2"),
        unit_price=Decimal("1500.00"),
    )
    return order
