"""
Shared fixtures for customer module tests.

Provides tenant-aware fixtures for testing customer models, services,
and API endpoints against a real PostgreSQL database with proper
tenant schema isolation.

Prerequisites:
    - PostgreSQL backend (DJANGO_SETTINGS_MODULE=config.settings.test_pg)
    - docker compose up db  (the lcc-postgres container must be running)
"""

import uuid

import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
from rest_framework.test import APIClient


TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_customers"
TENANT_DOMAIN = "customers.testserver"


# ═══════════════════════════════════════════════════════════════════════
# Tenant Lifecycle Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create a test tenant schema once per session."""
    with django_db_blocker.unblock():
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Customers Test Tenant",
            slug="customers-test",
        )
        tenant.save(verbosity=0)

        domain = DomainModel(
            tenant=tenant,
            domain=TENANT_DOMAIN,
            is_primary=True,
        )
        domain.save()

        yield tenant

        # Teardown
        connection.set_tenant(tenant)
        domain.delete()
        from django.db.models import Model

        Model.delete(tenant)
        from django.db import connection as conn

        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_NAME)
        connection.set_schema_to_public()


@pytest.fixture(autouse=True)
def tenant_context(setup_test_tenant, db):
    """Activate the test tenant schema for every test automatically."""
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
def api_client(user):
    """Authenticated API client with tenant host header."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    client._user = user
    return client
