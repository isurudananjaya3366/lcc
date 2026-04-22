"""
Pytest fixtures for POS module integration tests.

Provides tenant-aware fixtures for testing POS terminal, session, cart,
search, and payment functionality against a real PostgreSQL database
with proper tenant schema isolation.

Prerequisites:
    - PostgreSQL backend (DJANGO_SETTINGS_MODULE=config.settings.test_pg)
    - docker compose up db  (the lcc-postgres container must be running)
"""

from decimal import Decimal

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

# Import receipt fixtures so pytest discovers them
from tests.pos.conftest_receipts import *  # noqa: F401,F403

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_pos"
TENANT_DOMAIN = "pos.testserver"


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
            name="POS Test Tenant",
            slug="pos-test",
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
# User Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def cashier(tenant_context):
    """Create a cashier user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_user(
        email="cashier@testpos.com",
        password="testpass123",  # noqa: S106
    )


@pytest.fixture
def manager_user(tenant_context):
    """Create a manager user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_user(
        email="manager@testpos.com",
        password="managerpass123",  # noqa: S106
        is_staff=True,
    )


@pytest.fixture
def cashier2(tenant_context):
    """Create a second cashier user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_user(
        email="cashier2@testpos.com",
        password="testpass123",  # noqa: S106
    )


# ═══════════════════════════════════════════════════════════════════════
# Warehouse Fixture
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def warehouse(tenant_context):
    """Create an active warehouse for terminals."""
    from apps.inventory.warehouses.models import Warehouse

    return Warehouse.objects.create(
        name="Colombo POS Store",
        code="WH-POS-01",
        warehouse_type="main",
        address_line_1="100 Galle Road",
        city="Colombo",
        district="colombo",
        phone="+94112345678",
        status="active",
    )


# ═══════════════════════════════════════════════════════════════════════
# POS Terminal Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def terminal(warehouse):
    """Create an active POS terminal."""
    from apps.pos.terminal.models import POSTerminal

    return POSTerminal.objects.create(
        name="Main Checkout",
        code="T001",
        warehouse=warehouse,
        location="Ground Floor",
        status="active",
    )


@pytest.fixture
def terminal2(warehouse):
    """Create a second POS terminal."""
    from apps.pos.terminal.models import POSTerminal

    return POSTerminal.objects.create(
        name="Express Checkout",
        code="T002",
        warehouse=warehouse,
        location="Ground Floor",
        status="active",
    )


@pytest.fixture
def inactive_terminal(warehouse):
    """Create an inactive POS terminal."""
    from apps.pos.terminal.models import POSTerminal

    return POSTerminal.objects.create(
        name="Disabled Terminal",
        code="T099",
        warehouse=warehouse,
        location="Storage",
        status="inactive",
    )


# ═══════════════════════════════════════════════════════════════════════
# POS Session Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def session(terminal, cashier):
    """Create and open a POS session."""
    from apps.pos.terminal.models import POSSession

    session_number = POSSession.generate_session_number(terminal)
    sess = POSSession(
        terminal=terminal,
        user=cashier,
        session_number=session_number,
        opening_cash_amount=Decimal("10000.00"),
    )
    sess.open_session()
    return sess


@pytest.fixture
def closed_session(terminal2, cashier2):
    """Create a closed POS session."""
    from apps.pos.terminal.models import POSSession

    session_number = POSSession.generate_session_number(terminal2)
    sess = POSSession(
        terminal=terminal2,
        user=cashier2,
        session_number=session_number,
        opening_cash_amount=Decimal("5000.00"),
    )
    sess.open_session()
    sess.close_session(actual_cash_amount=Decimal("5000.00"))
    return sess


# ═══════════════════════════════════════════════════════════════════════
# Product Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def product_category(tenant_context):
    """Create a test product category."""
    from apps.products.models import Category

    return Category.objects.create(name="Beverages", slug="beverages")


@pytest.fixture
def product(tenant_context, product_category):
    """Create a test product."""
    from apps.products.models import Product

    return Product.objects.create(
        name="Coca Cola 330ml",
        sku="COKE-330",
        barcode="8901234567890",
        selling_price=Decimal("150.00"),
        cost_price=Decimal("100.00"),
        category=product_category,
        is_pos_visible=True,
        status="active",
    )


@pytest.fixture
def product2(tenant_context, product_category):
    """Create a second test product."""
    from apps.products.models import Product

    return Product.objects.create(
        name="Pepsi 500ml",
        sku="PEPSI-500",
        barcode="8901234567891",
        selling_price=Decimal("200.00"),
        cost_price=Decimal("130.00"),
        category=product_category,
        is_pos_visible=True,
        status="active",
    )


@pytest.fixture
def product_invisible(tenant_context, product_category):
    """Create a product not visible in POS."""
    from apps.products.models import Product

    return Product.objects.create(
        name="Invisible Item",
        sku="INVIS-001",
        barcode="8901234500001",
        selling_price=Decimal("500.00"),
        cost_price=Decimal("300.00"),
        category=product_category,
        is_pos_visible=False,
        status="active",
    )


@pytest.fixture
def product_with_variant(tenant_context, product_category):
    """Create a product with a variant."""
    from apps.products.models import Product, ProductVariant

    prod = Product.objects.create(
        name="T-Shirt",
        sku="TSHIRT-001",
        barcode="8901234500010",
        selling_price=Decimal("1500.00"),
        cost_price=Decimal("800.00"),
        category=product_category,
        is_pos_visible=True,
        status="active",
    )
    variant = ProductVariant.objects.create(
        product=prod,
        sku="TSHIRT-001-BLU-M",
        barcode="8901234500011",
    )
    return prod, variant


# ═══════════════════════════════════════════════════════════════════════
# Customer Fixture
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def customer(tenant_context):
    """Create a test customer."""
    from apps.customers.models import Customer

    return Customer.objects.create(
        first_name="Saman",
        last_name="Perera",
        email="saman@example.com",
        phone="+94771234567",
    )


# ═══════════════════════════════════════════════════════════════════════
# Cart Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def cart(session):
    """Create an active cart for the session."""
    from apps.pos.cart.services.cart_service import CartService

    return CartService.get_or_create_cart(session)


@pytest.fixture
def cart_with_items(cart, product, product2):
    """Create a cart with two items."""
    from apps.pos.cart.services.cart_service import CartService

    CartService.add_to_cart(cart, product, quantity=2)
    CartService.add_to_cart(cart, product2, quantity=1)
    cart.refresh_from_db()
    return cart


# ═══════════════════════════════════════════════════════════════════════
# Quick Button Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def quick_button_group(terminal, product):
    """Create a quick button group with a button."""
    from apps.pos.search.models import QuickButton, QuickButtonGroup

    group = QuickButtonGroup.objects.create(
        name="Popular Drinks",
        code="popular-drinks",
        is_active=True,
        display_order=1,
    )
    QuickButton.objects.create(
        group=group,
        product=product,
        label="Coke",
        row=0,
        column=0,
        is_active=True,
    )
    return group


# ═══════════════════════════════════════════════════════════════════════
# API Client Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def api_client():
    """Return a DRF API test client."""
    from rest_framework.test import APIClient

    return APIClient(HTTP_HOST=TENANT_DOMAIN)


@pytest.fixture
def authenticated_client(api_client, cashier):
    """Return an API client authenticated as cashier."""
    api_client.force_authenticate(user=cashier)
    return api_client


@pytest.fixture
def manager_client(api_client, manager_user):
    """Return an API client authenticated as manager."""
    api_client.force_authenticate(user=manager_user)
    return api_client
