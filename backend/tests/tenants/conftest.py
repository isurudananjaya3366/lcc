"""
Tenant test fixtures — Task 78.

SubPhase-06, Group-F: Testing & Verification (Doc 02).

Provides reusable fixtures for tenant, domain, and middleware test
data. Fixtures use SimpleNamespace mocks so that database access is
not required for unit tests.

Usage:
    Fixtures are auto-discovered by pytest from this conftest.py.
    Import is not needed — just name the fixture as a test argument.

Run with:
    pytest backend/tests/tenants/ -v
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from django.test import RequestFactory


# ---------------------------------------------------------------------------
# Request factory
# ---------------------------------------------------------------------------


@pytest.fixture
def rf():
    """Return a Django RequestFactory instance."""
    return RequestFactory()


# ---------------------------------------------------------------------------
# Tenant fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def active_tenant():
    """Return a mock active tenant."""
    return SimpleNamespace(
        pk=1,
        name="acme",
        schema_name="acme",
        status="active",
        is_active=True,
    )


@pytest.fixture
def suspended_tenant():
    """Return a mock suspended tenant."""
    return SimpleNamespace(
        pk=2,
        name="blocked-co",
        schema_name="blocked_co",
        status="suspended",
        is_active=False,
    )


@pytest.fixture
def expired_tenant():
    """Return a mock expired tenant."""
    return SimpleNamespace(
        pk=3,
        name="old-co",
        schema_name="old_co",
        status="expired",
        is_active=False,
    )


@pytest.fixture
def public_tenant():
    """Return a mock public schema tenant."""
    return SimpleNamespace(
        pk=0,
        name="public",
        schema_name="public",
        status="active",
        is_active=True,
    )


# ---------------------------------------------------------------------------
# Domain fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def subdomain_domain(active_tenant):
    """Return a mock subdomain domain record."""
    return SimpleNamespace(
        domain="acme.lcc.example.com",
        tenant=active_tenant,
        is_verified=True,
        is_custom_domain=False,
        domain_type="subdomain",
    )


@pytest.fixture
def custom_domain(active_tenant):
    """Return a mock custom domain record."""
    return SimpleNamespace(
        domain="shop.mybusiness.lk",
        tenant=active_tenant,
        is_verified=True,
        is_custom_domain=True,
        domain_type="custom",
    )


@pytest.fixture
def unverified_domain(active_tenant):
    """Return a mock unverified custom domain record."""
    return SimpleNamespace(
        domain="pending.mybusiness.lk",
        tenant=active_tenant,
        is_verified=False,
        is_custom_domain=True,
        domain_type="custom",
    )


# ---------------------------------------------------------------------------
# Request fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_request(rf):
    """Return a mock API GET request."""
    return rf.get("/api/v1/products/", HTTP_ACCEPT="application/json")


@pytest.fixture
def browser_request(rf):
    """Return a mock browser GET request."""
    return rf.get("/dashboard/", HTTP_ACCEPT="text/html")


@pytest.fixture
def health_request(rf):
    """Return a mock health-check request."""
    return rf.get("/health/")


@pytest.fixture
def auth_request(rf):
    """Return a mock auth request."""
    return rf.get("/api/v1/auth/login/")


# ---------------------------------------------------------------------------
# Resolver fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def subdomain_resolver():
    """Return a SubdomainResolver instance."""
    from apps.tenants.middleware.subdomain_resolver import SubdomainResolver
    return SubdomainResolver(base_domain="lcc.example.com")


@pytest.fixture
def custom_domain_resolver():
    """Return a CustomDomainResolver instance."""
    from apps.tenants.middleware.domain_resolver import CustomDomainResolver
    return CustomDomainResolver(base_domain="lcc.example.com")


@pytest.fixture
def header_resolver():
    """Return a HeaderResolver instance."""
    from apps.tenants.middleware.header_resolver import HeaderResolver
    return HeaderResolver()
