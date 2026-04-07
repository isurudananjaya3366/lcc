"""
Shared fixtures for quote module tests.

Provides tenant-aware fixtures for testing quote models and API endpoints
against a real PostgreSQL database with proper tenant schema isolation.

Prerequisites:
    - PostgreSQL backend (DJANGO_SETTINGS_MODULE=config.settings.test_pg)
    - docker compose up db  (the lcc-postgres container must be running)
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
from rest_framework.test import APIClient

from apps.quotes.constants import QuoteStatus


TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_quotes"
TENANT_DOMAIN = "quotes.testserver"


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
            name="Quotes Test Tenant",
            slug="quotes-test",
        )
        tenant.save(verbosity=0)

        domain = DomainModel(
            tenant=tenant,
            domain=TENANT_DOMAIN,
            is_primary=True,
        )
        domain.save()

        yield tenant

        # Teardown — delete the tenant and drop the schema.
        # QuoteSettings / QuoteTemplate live in the tenant schema but
        # have CASCADE FKs back to the public Tenant table.  Django's
        # cascade collector queries them during Tenant.delete(), so the
        # tenant schema must still exist on the search_path at that
        # point.  We therefore:
        #   1. Set search_path to include the tenant schema.
        #   2. Delete the Django rows (cascade collector can find the
        #      tenant-schema tables).
        #   3. Drop the now-empty schema.
        connection.set_tenant(tenant)
        domain.delete()
        # Delete tenant row with Django cascade (schema still exists)
        from django.db.models import Model  # noqa: avoid TenantMixin.delete

        Model.delete(tenant)
        # Now drop the orphaned schema
        from django.db import connection as conn

        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_NAME)
        connection.set_schema_to_public()


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
def user(tenant_context):
    """Create and return a test user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        email=f"test-{uuid.uuid4().hex[:6]}@example.com",
        password="testpass123",
    )


@pytest.fixture
def api_client():
    """Return an unauthenticated API client with tenant host."""
    return APIClient(HTTP_HOST=TENANT_DOMAIN)


@pytest.fixture
def authed_client(user):
    """Return an authenticated API client with tenant host."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def draft_quote(tenant_context):
    """Create a draft quote."""
    from apps.quotes.models import Quote

    return Quote.objects.create(
        id=uuid.uuid4(),
        quote_number=f"QT-FIX-{uuid.uuid4().hex[:5].upper()}",
        status=QuoteStatus.DRAFT,
        issue_date=date.today(),
    )


@pytest.fixture
def sent_quote(tenant_context):
    """Create a sent quote with a public token."""
    from apps.quotes.models import Quote

    return Quote.objects.create(
        id=uuid.uuid4(),
        quote_number=f"QT-SENT-{uuid.uuid4().hex[:5].upper()}",
        status=QuoteStatus.SENT,
        issue_date=date.today(),
        public_token=uuid.uuid4(),
        valid_until=date.today() + timedelta(days=30),
    )


@pytest.fixture
def quote_with_items(draft_quote):
    """Create a draft quote with two line items."""
    from apps.quotes.models import QuoteLineItem

    QuoteLineItem.objects.create(
        quote=draft_quote,
        product_name="Product A",
        quantity=Decimal("2"),
        unit_price=Decimal("100.00"),
    )
    QuoteLineItem.objects.create(
        quote=draft_quote,
        product_name="Product B",
        quantity=Decimal("1"),
        unit_price=Decimal("50.00"),
    )
    return draft_quote
