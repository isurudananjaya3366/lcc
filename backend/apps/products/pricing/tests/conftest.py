"""
Pytest fixtures for pricing production DB tests.

Provides tenant-aware fixtures for testing pricing models and services
against a real PostgreSQL database with proper tenant schema isolation.

Prerequisites:
    - PostgreSQL backend (DJANGO_SETTINGS_MODULE=config.settings.test_pg)
    - docker compose up db  (the lcc-postgres container must be running)
"""

import uuid
from decimal import Decimal

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model


TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_pricing"
TENANT_DOMAIN = "pricing.testserver"


# ═══════════════════════════════════════════════════════════════════════
# Tenant Lifecycle Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create a test tenant schema once per session.

    Uses ``django_db_blocker.unblock()`` because session-scoped fixtures
    cannot use the function-scoped ``db`` marker.  The tenant schema is
    created via TenantMixin.save() which triggers ``auto_create_schema``.
    """
    with django_db_blocker.unblock():
        # Clean up if exists from a previous (crashed) run
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Pricing Test Tenant",
            slug="pricing-test",
        )
        tenant.save(verbosity=0)

        domain = DomainModel(
            tenant=tenant,
            domain=TENANT_DOMAIN,
            is_primary=True,
        )
        domain.save()

        yield tenant

        # Teardown — switch back to public before dropping
        connection.set_schema_to_public()
        domain.delete()
        tenant.delete(force_drop=True)


@pytest.fixture
def tenant_context(setup_test_tenant, db):
    """Activate the test tenant schema for a test.

    Must be requested explicitly by tests that need tenant
    isolation.  Mock-based unit tests that do not touch the
    database should NOT request this fixture.
    """
    connection.set_tenant(setup_test_tenant)
    yield setup_test_tenant
    connection.set_schema_to_public()


# ═══════════════════════════════════════════════════════════════════════
# Common Object Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def category(tenant_context):
    """Create and return a test Category."""
    from apps.products.models import Category

    return Category.objects.create(name="Electronics", slug="electronics")


@pytest.fixture
def tax_class(tenant_context):
    """Create and return a test TaxClass."""
    from apps.products.models import TaxClass

    return TaxClass.objects.create(name="Standard VAT", rate=Decimal("15.00"))


@pytest.fixture
def product(tenant_context, category):
    """Create and return a test Product."""
    from apps.products.models import Product

    return Product.objects.create(
        name="Test Laptop",
        sku=f"LAP-{uuid.uuid4().hex[:8]}",
        category=category,
    )


@pytest.fixture
def product2(tenant_context, category):
    """Create and return a second test Product."""
    from apps.products.models import Product

    return Product.objects.create(
        name="Test Phone",
        sku=f"PHN-{uuid.uuid4().hex[:8]}",
        category=category,
    )


@pytest.fixture
def variant(tenant_context, product):
    """Create and return a test ProductVariant."""
    from apps.products.models import ProductVariant

    return ProductVariant.objects.create(
        product=product,
        sku=f"LAP-V-{uuid.uuid4().hex[:8]}",
        name="16GB RAM",
    )


@pytest.fixture
def product_price(tenant_context, product, tax_class):
    """Create and return a test ProductPrice with full fields."""
    from apps.products.pricing.models import ProductPrice

    return ProductPrice.objects.create(
        product=product,
        base_price=Decimal("250000.00"),
        cost_price=Decimal("180000.00"),
        wholesale_price=Decimal("220000.00"),
        tax_class=tax_class,
        is_taxable=True,
        is_tax_inclusive=True,
    )
