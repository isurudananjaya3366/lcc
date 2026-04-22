"""
Pytest fixtures for attributes integration tests.

Provides tenant-aware fixtures for testing attribute models and API endpoints
against a real PostgreSQL database with proper tenant schema isolation.

Prerequisites:
    - PostgreSQL backend (DJANGO_SETTINGS_MODULE=config.settings.test_pg)
    - docker compose up db  (the lcc-postgres container must be running)
"""

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_attrs"
TENANT_DOMAIN = "attrs.testserver"


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
                DomainModel.objects.get_or_create(
                    domain=TENANT_DOMAIN,
                    defaults={"tenant": tenant, "is_primary": True},
                )
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
            name="Attributes Test Tenant",
            slug="attrs-test",
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


@pytest.fixture(autouse=True)
def tenant_context(setup_test_tenant, db):
    """Activate the test tenant schema for each test.

    This is ``autouse=True`` so every test in this directory
    automatically runs inside the tenant schema.  The ``db`` dependency
    ensures pytest-django's transaction wrapper is active.
    """
    connection.set_tenant(setup_test_tenant)
    yield setup_test_tenant
    connection.set_schema_to_public()


# ═══════════════════════════════════════════════════════════════════════
# AttributeGroup Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def attribute_group(tenant_context):
    """Create and return a test AttributeGroup."""
    from apps.attributes.models import AttributeGroup

    return AttributeGroup.objects.create(
        name="Technical Specifications",
        description="Technical spec attributes",
        display_order=1,
    )


@pytest.fixture
def attribute_group_2(tenant_context):
    """Create and return a second test AttributeGroup."""
    from apps.attributes.models import AttributeGroup

    return AttributeGroup.objects.create(
        name="Dimensions",
        description="Size and weight attributes",
        display_order=2,
    )


# ═══════════════════════════════════════════════════════════════════════
# Attribute Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def text_attribute(tenant_context, attribute_group):
    """Create and return a TEXT type Attribute."""
    from apps.attributes.models import Attribute

    return Attribute.objects.create(
        name="Brand",
        group=attribute_group,
        attribute_type="text",
        is_required=True,
        is_filterable=True,
        is_searchable=True,
        display_order=1,
    )


@pytest.fixture
def number_attribute(tenant_context, attribute_group):
    """Create and return a NUMBER type Attribute."""
    from apps.attributes.models import Attribute

    return Attribute.objects.create(
        name="Weight",
        group=attribute_group,
        attribute_type="number",
        unit="kg",
        is_required=False,
        is_filterable=True,
        min_value=0,
        max_value=1000,
        display_order=2,
    )


@pytest.fixture
def select_attribute(tenant_context, attribute_group):
    """Create and return a SELECT type Attribute."""
    from apps.attributes.models import Attribute

    return Attribute.objects.create(
        name="Color",
        group=attribute_group,
        attribute_type="select",
        is_required=True,
        is_filterable=True,
        display_order=3,
    )


# ═══════════════════════════════════════════════════════════════════════
# AttributeOption Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def attribute_options(tenant_context, select_attribute):
    """Create and return three AttributeOptions for the select attribute."""
    from apps.attributes.models import AttributeOption

    red = AttributeOption.objects.create(
        attribute=select_attribute,
        value="red",
        label="Red",
        color_code="#FF0000",
        display_order=1,
        is_default=True,
    )
    blue = AttributeOption.objects.create(
        attribute=select_attribute,
        value="blue",
        label="Blue",
        color_code="#0000FF",
        display_order=2,
    )
    green = AttributeOption.objects.create(
        attribute=select_attribute,
        value="green",
        label="Green",
        color_code="#00FF00",
        display_order=3,
    )
    return [red, blue, green]


# ═══════════════════════════════════════════════════════════════════════
# Category Fixtures (for M2M relationship testing)
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def category(tenant_context):
    """Create and return a test Category for M2M testing."""
    from apps.products.models import Category

    return Category.objects.create(
        name="Electronics",
    )


@pytest.fixture
def child_category(tenant_context, category):
    """Create and return a child category under Electronics."""
    from apps.products.models import Category

    return Category.objects.create(
        name="Laptops",
        parent=category,
    )


# ═══════════════════════════════════════════════════════════════════════
# Auth Fixtures (tenant-scoped)
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def auth_user(tenant_context):
    """Create and return an authenticated user within tenant context.

    PlatformUser uses email as the primary identifier, not username.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()  # noqa: N806
    return User.objects.create_user(
        email="testattrs@example.com",
        password="testpass123",  # noqa: S106
    )


@pytest.fixture
def auth_api_client(auth_user):
    """Return an authenticated DRF API client with tenant HTTP_HOST."""
    from rest_framework.test import APIClient

    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=auth_user)
    return client
