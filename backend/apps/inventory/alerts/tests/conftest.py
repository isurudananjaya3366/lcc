"""Shared fixtures for alerts tests — tenant-aware."""

import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
from rest_framework.test import APIClient

from apps.inventory.alerts.models import GlobalStockSettings


User = get_user_model()
TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

SCHEMA_NAME = "test_alerts"
TENANT_DOMAIN = "alerts.testserver"


# ── Tenant lifecycle ──────────────────────────────────────────────


@pytest.fixture(scope="session")
def setup_test_tenant(django_db_setup, django_db_blocker):
    """Create a test tenant schema once per session."""
    with django_db_blocker.unblock():
        if TenantModel.objects.filter(schema_name=SCHEMA_NAME).exists():
            t = TenantModel.objects.get(schema_name=SCHEMA_NAME)
            t.delete(force_drop=True)

        tenant = TenantModel(
            schema_name=SCHEMA_NAME,
            name="Alerts Test Tenant",
            slug="alerts-test",
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
        domain.delete()
        tenant.delete(force_drop=True)


@pytest.fixture
def tenant_context(setup_test_tenant, db):
    """Activate the test tenant schema for a test."""
    connection.set_tenant(setup_test_tenant)
    yield setup_test_tenant
    connection.set_schema_to_public()


# ── Auth fixtures ─────────────────────────────────────────────────


@pytest.fixture
def user(tenant_context):
    return User.objects.create_user(
        email="alerts-test@example.com",
        password="testpass123",
    )


@pytest.fixture
def api_client():
    return APIClient(HTTP_HOST=TENANT_DOMAIN)


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


# ── Global settings ───────────────────────────────────────────────


@pytest.fixture
def global_settings(tenant_context):
    settings, _ = GlobalStockSettings.objects.get_or_create(
        defaults={
            "default_low_threshold": Decimal("10.000"),
            "default_reorder_point": Decimal("15.000"),
            "default_reorder_qty": Decimal("50.000"),
            "enable_auto_reorder": False,
        }
    )
    return settings
