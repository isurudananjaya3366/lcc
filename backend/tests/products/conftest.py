"""
Pytest fixtures for products integration tests.

Provides tenant-aware fixtures for testing product models and API endpoints
against a real PostgreSQL database with proper tenant schema isolation.

Prerequisites:
    - PostgreSQL backend (DJANGO_SETTINGS_MODULE=config.settings.test_pg)
    - docker compose up db  (the lcc-postgres container must be running)
"""

from decimal import Decimal

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model


TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_products"
TENANT_DOMAIN = "products.testserver"


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
            name="Products Test Tenant",
            slug="products-test",
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

    Must be requested explicitly by tests/classes that need tenant
    isolation (e.g. integration tests).  Mock-based unit tests that
    do not touch the database should NOT request this fixture.
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
def category_2(tenant_context):
    """Create and return a second test Category."""
    from apps.products.models import Category

    return Category.objects.create(name="Clothing", slug="clothing")


@pytest.fixture
def brand(tenant_context):
    """Create and return a test Brand."""
    from apps.products.models import Brand

    return Brand.objects.create(name="Samsung", description="Electronics brand")


@pytest.fixture
def brand_2(tenant_context):
    """Create and return a second test Brand."""
    from apps.products.models import Brand

    return Brand.objects.create(name="Apple", description="Tech brand")


@pytest.fixture
def tax_class(tenant_context):
    """Create and return a test TaxClass."""
    from apps.products.models import TaxClass

    return TaxClass.objects.create(name="Standard VAT", rate=Decimal("15.00"))


@pytest.fixture
def tax_class_zero(tenant_context):
    """Create and return a zero-rated TaxClass."""
    from apps.products.models import TaxClass

    return TaxClass.objects.create(name="Zero-rated", rate=Decimal("0.00"))


@pytest.fixture
def unit_of_measure(tenant_context):
    """Create and return a test UnitOfMeasure."""
    from apps.products.models import UnitOfMeasure

    return UnitOfMeasure.objects.create(
        name="Piece", symbol="pcs", is_base_unit=True
    )


@pytest.fixture
def unit_of_measure_kg(tenant_context):
    """Create and return a kg UnitOfMeasure."""
    from apps.products.models import UnitOfMeasure

    return UnitOfMeasure.objects.create(
        name="Kilogram",
        symbol="kg",
        is_base_unit=False,
        conversion_factor=Decimal("1.0000"),
    )


@pytest.fixture
def product(tenant_context, category):
    """Create and return a test Product."""
    from apps.products.models import Product

    return Product.objects.create(name="Test Phone", category=category)


@pytest.fixture
def product_active(tenant_context, category, brand):
    """Create and return an active Product."""
    from apps.products.constants import PRODUCT_STATUS
    from apps.products.models import Product

    return Product.objects.create(
        name="Active Phone",
        category=category,
        brand=brand,
        status=PRODUCT_STATUS.ACTIVE,
        selling_price=Decimal("50000.00"),
        cost_price=Decimal("30000.00"),
    )


@pytest.fixture
def authenticated_client(tenant_context):
    """Create and return an authenticated API client."""
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient

    User = get_user_model()
    user = User.objects.create_user(
        email="test@example.com", password="testpass123"
    )
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    return client


# ═══════════════════════════════════════════════════════════════════════
# Variant Option Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def variant_option_type_size(tenant_context):
    """Create a Size variant option type."""
    from apps.products.models import VariantOptionType

    VariantOptionType.all_with_deleted.filter(slug="size").delete()
    return VariantOptionType.objects.create(
        name="Size",
        display_order=1,
    )


@pytest.fixture
def variant_option_type_color(tenant_context):
    """Create a Color variant option type with color swatch."""
    from apps.products.models import VariantOptionType

    VariantOptionType.all_with_deleted.filter(slug="color").delete()
    return VariantOptionType.objects.create(
        name="Color",
        display_order=2,
        is_color_swatch=True,
    )


@pytest.fixture
def variant_option_value_small(variant_option_type_size):
    """Create a 'Small' option value for Size."""
    from apps.products.models import VariantOptionValue

    VariantOptionValue.all_with_deleted.filter(
        option_type=variant_option_type_size, value="s"
    ).delete()
    return VariantOptionValue.objects.create(
        option_type=variant_option_type_size,
        value="s",
        display_order=1,
    )


@pytest.fixture
def variant_option_value_medium(variant_option_type_size):
    """Create a 'Medium' option value for Size."""
    from apps.products.models import VariantOptionValue

    VariantOptionValue.all_with_deleted.filter(
        option_type=variant_option_type_size, value="m"
    ).delete()
    return VariantOptionValue.objects.create(
        option_type=variant_option_type_size,
        value="m",
        display_order=2,
    )


@pytest.fixture
def variant_option_value_red(variant_option_type_color):
    """Create a 'Red' option value for Color with color code."""
    from apps.products.models import VariantOptionValue

    VariantOptionValue.all_with_deleted.filter(
        option_type=variant_option_type_color, value="red"
    ).delete()
    return VariantOptionValue.objects.create(
        option_type=variant_option_type_color,
        value="red",
        color_code="#FF0000",
        display_order=1,
    )


@pytest.fixture
def variant_option_value_large(variant_option_type_size):
    """Create a 'Large' option value for Size."""
    from apps.products.models import VariantOptionValue

    VariantOptionValue.all_with_deleted.filter(
        option_type=variant_option_type_size, value="l"
    ).delete()
    return VariantOptionValue.objects.create(
        option_type=variant_option_type_size,
        value="l",
        display_order=3,
    )


@pytest.fixture
def variant_option_value_blue(variant_option_type_color):
    """Create a 'Blue' option value for Color with color code."""
    from apps.products.models import VariantOptionValue

    VariantOptionValue.all_with_deleted.filter(
        option_type=variant_option_type_color, value="blue"
    ).delete()
    return VariantOptionValue.objects.create(
        option_type=variant_option_type_color,
        value="blue",
        color_code="#0000FF",
        display_order=2,
    )


@pytest.fixture
def variable_product(tenant_context, category):
    """Create and return a VARIABLE-type Product for variant tests."""
    from apps.products.constants import PRODUCT_TYPES
    from apps.products.models import Product

    return Product.objects.create(
        name="Classic T-Shirt",
        category=category,
        product_type=PRODUCT_TYPES.VARIABLE,
        selling_price=Decimal("2500.00"),
        cost_price=Decimal("1500.00"),
    )


@pytest.fixture
def variable_product_2(tenant_context, category):
    """Create and return a second VARIABLE-type Product."""
    from apps.products.constants import PRODUCT_TYPES
    from apps.products.models import Product

    return Product.objects.create(
        name="Polo Shirt",
        category=category,
        product_type=PRODUCT_TYPES.VARIABLE,
        selling_price=Decimal("3500.00"),
        cost_price=Decimal("2000.00"),
    )
