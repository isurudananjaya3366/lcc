"""
Pytest fixtures for warehouse/inventory integration tests.

Provides tenant-aware fixtures for testing warehouse models and API endpoints
against a real PostgreSQL database with proper tenant schema isolation.

Prerequisites:
    - PostgreSQL backend (DJANGO_SETTINGS_MODULE=config.settings.test_pg)
    - docker compose up db  (the lcc-postgres container must be running)
"""

from datetime import time
from decimal import Decimal

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model


TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_inventory"
TENANT_DOMAIN = "inventory.testserver"


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
            name="Inventory Test Tenant",
            slug="inventory-test",
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
# Warehouse Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def warehouse(tenant_context):
    """Create and return an active warehouse."""
    from apps.inventory.warehouses.models import Warehouse

    return Warehouse.objects.create(
        name="Colombo Main",
        code="WH-CMB-01",
        warehouse_type="main",
        address_line_1="123 Galle Road",
        city="Colombo",
        district="colombo",
        phone="+94112345678",
        status="active",
    )


@pytest.fixture
def warehouse_2(tenant_context):
    """Create and return a second active warehouse."""
    from apps.inventory.warehouses.models import Warehouse

    return Warehouse.objects.create(
        name="Kandy Distribution",
        code="WH-KDY-01",
        warehouse_type="distribution",
        address_line_1="45 Peradeniya Road",
        city="Kandy",
        district="kandy",
        phone="+94812345678",
        status="active",
    )


@pytest.fixture
def warehouse_inactive(tenant_context):
    """Create and return an inactive warehouse."""
    from apps.inventory.warehouses.models import Warehouse

    return Warehouse.objects.create(
        name="Galle Returns",
        code="WH-GLE-01",
        warehouse_type="returns",
        address_line_1="10 Matara Road",
        city="Galle",
        district="galle",
        phone="+94912345678",
        status="inactive",
    )


# ═══════════════════════════════════════════════════════════════════════
# Storage Location Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def zone(warehouse):
    """Create a root zone location."""
    from apps.inventory.warehouses.models import StorageLocation

    return StorageLocation.objects.create(
        warehouse=warehouse,
        location_type="zone",
        name="Zone A",
        code="ZA",
    )


@pytest.fixture
def aisle(warehouse, zone):
    """Create an aisle under zone."""
    from apps.inventory.warehouses.models import StorageLocation

    return StorageLocation.objects.create(
        warehouse=warehouse,
        parent=zone,
        location_type="aisle",
        name="Aisle 1",
        code="ZA-A01",
    )


@pytest.fixture
def rack(warehouse, aisle):
    """Create a rack under aisle."""
    from apps.inventory.warehouses.models import StorageLocation

    return StorageLocation.objects.create(
        warehouse=warehouse,
        parent=aisle,
        location_type="rack",
        name="Rack 1",
        code="ZA-A01-R01",
    )


@pytest.fixture
def shelf(warehouse, rack):
    """Create a shelf under rack."""
    from apps.inventory.warehouses.models import StorageLocation

    return StorageLocation.objects.create(
        warehouse=warehouse,
        parent=rack,
        location_type="shelf",
        name="Shelf 1",
        code="ZA-A01-R01-S01",
    )


@pytest.fixture
def bin_loc(warehouse, shelf):
    """Create a bin under shelf."""
    from apps.inventory.warehouses.models import StorageLocation

    return StorageLocation.objects.create(
        warehouse=warehouse,
        parent=shelf,
        location_type="bin",
        name="Bin 1",
        code="ZA-A01-R01-S01-B01",
    )


# ═══════════════════════════════════════════════════════════════════════
# Zone & Route Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def warehouse_zone(warehouse):
    """Create a warehouse zone."""
    from apps.inventory.warehouses.models import WarehouseZone

    return WarehouseZone.objects.create(
        warehouse=warehouse,
        purpose="storage",
        code="ZN-01",
        name="General Storage",
    )


@pytest.fixture
def transfer_route(warehouse, warehouse_2):
    """Create a transfer route between two warehouses."""
    from apps.inventory.warehouses.models import TransferRoute

    return TransferRoute.objects.create(
        source_warehouse=warehouse,
        destination_warehouse=warehouse_2,
        transit_days=2,
        estimated_cost=Decimal("1000.00"),
        cost_per_kg=Decimal("50.00"),
        cost_per_m3=Decimal("200.00"),
    )


# ═══════════════════════════════════════════════════════════════════════
# Capacity Fixture
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def warehouse_capacity(warehouse):
    """Create a warehouse capacity record."""
    from apps.inventory.warehouses.models import WarehouseCapacity

    return WarehouseCapacity.objects.create(
        warehouse=warehouse,
        max_item_capacity=1000,
        max_weight_capacity=Decimal("50000.00"),
        max_volume_capacity=Decimal("5000.00"),
        current_item_count=450,
        current_weight=Decimal("22500.00"),
        current_volume=Decimal("2250.00"),
    )


# ═══════════════════════════════════════════════════════════════════════
# Auth Fixture
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def authenticated_client(tenant_context):
    """Create and return an authenticated API client."""
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient

    User = get_user_model()
    user = User.objects.create_user(
        email="warehouse-test@example.com",
        password="testpass123",
    )
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    return client
