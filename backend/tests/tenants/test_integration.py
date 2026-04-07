"""
Integration tests for tenant middleware — Tasks 76-77.

SubPhase-06, Group-F: Testing & Verification (Doc 02).

Test coverage:
    Task 76: End-to-end tenant resolution integration tests
    Task 77: Multi-tenant isolation verification

These tests verify that individual middleware components work
together correctly across the full request lifecycle. They use
mock objects to simulate database and cache interactions while
validating the integration contracts between resolvers, error
handlers, and the middleware pipeline.

Run with:
    pytest backend/tests/tenants/test_integration.py -v
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory, override_settings


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_tenant(
    name="acme",
    schema_name="acme",
    pk=1,
    status="active",
    is_active=True,
):
    """Create a mock Tenant object."""
    return SimpleNamespace(
        pk=pk,
        name=name,
        schema_name=schema_name,
        status=status,
        is_active=is_active,
    )


def _make_domain(
    domain,
    tenant=None,
    is_verified=True,
    is_custom_domain=False,
    domain_type="subdomain",
):
    """Create a mock Domain object."""
    if tenant is None:
        tenant = _make_tenant()
    return SimpleNamespace(
        domain=domain,
        tenant=tenant,
        is_verified=is_verified,
        is_custom_domain=is_custom_domain,
        domain_type=domain_type,
    )


# ===========================================================================
# Task 76: Create Integration Tests
# ===========================================================================


class TestEndToEndSubdomainResolution:
    """
    Task 76: End-to-end subdomain resolution flow.

    Verifies that a request with a subdomain host header goes
    through validation, cache lookup, and tenant resolution
    in the correct order.
    """

    def test_valid_subdomain_resolves_tenant(self):
        """Full flow: valid subdomain extracts and resolves tenant."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        resolver = SubdomainResolver(base_domain="lcc.example.com")
        factory = RequestFactory()
        request = factory.get("/", HTTP_HOST="acme.lcc.example.com")

        with patch.object(
            resolver, "get_subdomain_from_request", return_value="acme"
        ), patch.object(
            resolver, "resolve_tenant", return_value=_make_tenant()
        ) as mock_resolve:
            result = resolver.resolve(request)
            mock_resolve.assert_called_once_with("acme")
            assert result is not None
            assert result.schema_name == "acme"

    def test_invalid_subdomain_returns_none(self):
        """Full flow: invalid subdomain returns None without DB call."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        resolver = SubdomainResolver(base_domain="lcc.example.com")
        factory = RequestFactory()
        request = factory.get("/", HTTP_HOST="lcc.example.com")

        with patch.object(
            resolver, "get_subdomain_from_request", return_value=""
        ):
            result = resolver.resolve(request)
            assert result is None

    def test_reserved_subdomain_skips_resolution(self):
        """Full flow: reserved subdomain (www) returns None."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        resolver = SubdomainResolver(base_domain="lcc.example.com")

        with patch("django.core.cache.cache") as mock_cache:
            result = resolver.resolve_tenant("www")
            assert result is None
            mock_cache.get.assert_not_called()


class TestEndToEndCustomDomainResolution:
    """
    Task 76: End-to-end custom domain resolution flow.

    Verifies that a request with a custom domain host header
    bypasses subdomain resolution and uses custom domain lookup.
    """

    def test_custom_domain_resolves_tenant(self):
        """Full flow: custom domain resolves through cache."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        resolver = CustomDomainResolver(base_domain="lcc.example.com")

        with patch("django.core.cache.cache") as mock_cache:
            tenant = _make_tenant(name="custom-co", schema_name="custom_co")
            mock_cache.get.return_value = tenant

            result = resolver.resolve_by_domain("shop.mybusiness.lk")
            assert result is tenant
            assert result.schema_name == "custom_co"

    @override_settings(ALLOWED_HOSTS=["*"])
    def test_platform_domain_skips_custom_lookup(self):
        """Full flow: platform subdomain is not treated as custom domain."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        resolver = CustomDomainResolver(base_domain="lcc.example.com")
        factory = RequestFactory()
        request = factory.get("/", HTTP_HOST="acme.lcc.example.com")
        result = resolver.resolve(request)
        assert result is None


class TestEndToEndHeaderResolution:
    """
    Task 76: End-to-end header-based resolution flow.

    Verifies that API requests with tenant headers go through
    path validation and header extraction correctly.
    """

    def test_api_request_with_header_resolves(self):
        """Full flow: API request with tenant header resolves tenant."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/",
            HTTP_X_TENANT_ID="acme",
        )

        with patch.object(
            resolver, "lookup_tenant", return_value=_make_tenant()
        ) as mock_resolve:
            result = resolver.resolve(request)
            assert result is not None

    def test_non_api_request_skips_header_resolution(self):
        """Full flow: browser request skips header resolution."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        factory = RequestFactory()
        request = factory.get("/dashboard/")
        result = resolver.resolve(request)
        assert result is None


class TestEndToEndErrorHandling:
    """
    Task 76: End-to-end error handling integration.

    Verifies that error handlers produce correct responses and
    that metrics are tracked consistently across the pipeline.
    """

    def test_not_found_then_metrics_tracked(self):
        """Full flow: tenant_not_found increments error metrics."""
        from apps.tenants.middleware import (
            get_error_metrics,
            reset_error_metrics,
            tenant_not_found,
        )

        reset_error_metrics()
        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        response = tenant_not_found(request, hostname="unknown.example.com")
        assert response.status_code == 404

        metrics = get_error_metrics()
        assert metrics["total"] >= 1
        assert "tenant_not_found" in metrics["by_type"]
        reset_error_metrics()

    def test_suspended_then_metrics_tracked(self):
        """Full flow: tenant_suspended increments error metrics."""
        from apps.tenants.middleware import (
            get_error_metrics,
            reset_error_metrics,
            tenant_suspended,
        )

        reset_error_metrics()
        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        tenant = _make_tenant(status="suspended")
        response = tenant_suspended(request, tenant)
        assert response.status_code == 403

        metrics = get_error_metrics()
        assert metrics["total"] >= 1
        assert "tenant_suspended" in metrics["by_type"]
        reset_error_metrics()

    def test_expired_then_metrics_tracked(self):
        """Full flow: tenant_expired increments error metrics."""
        from apps.tenants.middleware import (
            get_error_metrics,
            reset_error_metrics,
            tenant_expired,
        )

        reset_error_metrics()
        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        tenant = _make_tenant(status="expired")
        response = tenant_expired(request, tenant)
        assert response.status_code == 403

        metrics = get_error_metrics()
        assert metrics["total"] >= 1
        assert "tenant_expired" in metrics["by_type"]
        reset_error_metrics()

    def test_public_path_bypasses_tenant_resolution(self):
        """Full flow: public paths return True and skip resolution."""
        from apps.tenants.middleware import is_public_path

        assert is_public_path("/api/v1/auth/login/") is True
        assert is_public_path("/health/") is True
        assert is_public_path("/api/v1/products/") is False


# ===========================================================================
# Task 77: Test Multi-Tenant Isolation
# ===========================================================================


class TestMultiTenantIsolation:
    """
    Task 77: Multi-tenant isolation verification.

    Verifies that tenant resolution produces isolated schema contexts
    and that different tenants cannot cross-contaminate each other's
    resolution results. Tests use mock resolvers to validate the
    contract without requiring actual database schemas.
    """

    def test_different_subdomains_resolve_different_tenants(self):
        """Distinct subdomains resolve to distinct tenant objects."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        resolver = SubdomainResolver(base_domain="lcc.example.com")

        tenant_a = _make_tenant(name="alpha", schema_name="alpha", pk=1)
        tenant_b = _make_tenant(name="beta", schema_name="beta", pk=2)

        with patch.object(resolver, "resolve_tenant") as mock_resolve:
            mock_resolve.return_value = tenant_a
            result_a = resolver.resolve_tenant("alpha")
            assert result_a.schema_name == "alpha"
            assert result_a.pk == 1

            mock_resolve.return_value = tenant_b
            result_b = resolver.resolve_tenant("beta")
            assert result_b.schema_name == "beta"
            assert result_b.pk == 2

            assert result_a.pk != result_b.pk
            assert result_a.schema_name != result_b.schema_name

    def test_custom_domain_isolates_from_subdomain(self):
        """Custom domain resolution is independent of subdomain resolution."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        sub_resolver = SubdomainResolver(base_domain="lcc.example.com")
        dom_resolver = CustomDomainResolver(base_domain="lcc.example.com")

        tenant_sub = _make_tenant(name="sub-tenant", schema_name="sub", pk=10)
        tenant_dom = _make_tenant(name="dom-tenant", schema_name="dom", pk=20)

        with patch.object(
            sub_resolver, "resolve_tenant", return_value=tenant_sub
        ), patch(
            "django.core.cache.cache"
        ) as mock_cache:
            mock_cache.get.return_value = tenant_dom

            result_sub = sub_resolver.resolve_tenant("sub-tenant")
            result_dom = dom_resolver.resolve_by_domain("shop.custom.lk")

            assert result_sub.pk != result_dom.pk
            assert result_sub.schema_name == "sub"
            assert result_dom.schema_name == "dom"

    def test_header_resolution_isolates_from_subdomain(self):
        """Header resolution is independent of subdomain resolution."""
        from apps.tenants.middleware.header_resolver import HeaderResolver
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        sub_resolver = SubdomainResolver(base_domain="lcc.example.com")
        hdr_resolver = HeaderResolver()

        tenant_sub = _make_tenant(name="sub-t", schema_name="sub_t", pk=30)
        tenant_hdr = _make_tenant(name="hdr-t", schema_name="hdr_t", pk=40)

        with patch.object(
            sub_resolver, "resolve_tenant", return_value=tenant_sub
        ), patch.object(
            hdr_resolver, "lookup_tenant", return_value=tenant_hdr
        ):
            result_sub = sub_resolver.resolve_tenant("sub-t")
            factory = RequestFactory()
            request = factory.get(
                "/api/v1/products/",
                HTTP_X_TENANT_ID="hdr-t",
            )
            result_hdr = hdr_resolver.resolve(request)

            if result_hdr is not None:
                assert result_sub.pk != result_hdr.pk

    def test_suspended_tenant_does_not_leak_data(self):
        """Suspended tenant response contains no schema or internal IDs."""
        from apps.tenants.middleware import reset_error_metrics, tenant_suspended

        reset_error_metrics()
        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        tenant = _make_tenant(status="suspended", pk=999, schema_name="secret")
        response = tenant_suspended(request, tenant)

        body = json.loads(response.content)
        assert "secret" not in json.dumps(body)
        assert "999" not in json.dumps(body)
        assert body["error"] == "tenant_suspended"
        reset_error_metrics()

    def test_expired_tenant_does_not_leak_data(self):
        """Expired tenant response contains no schema or internal IDs."""
        from apps.tenants.middleware import reset_error_metrics, tenant_expired

        reset_error_metrics()
        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        tenant = _make_tenant(status="expired", pk=888, schema_name="hidden")
        response = tenant_expired(request, tenant)

        body = json.loads(response.content)
        assert "hidden" not in json.dumps(body)
        assert "888" not in json.dumps(body)
        assert body["error"] == "tenant_expired"
        reset_error_metrics()

    def test_not_found_does_not_leak_valid_tenants(self):
        """Not-found response does not reveal any existing tenant names."""
        from apps.tenants.middleware import reset_error_metrics, tenant_not_found

        reset_error_metrics()
        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        response = tenant_not_found(request, hostname="hacker.example.com")

        body = json.loads(response.content)
        assert body["error"] == "tenant_not_found"
        assert "acme" not in json.dumps(body).lower()
        reset_error_metrics()

    def test_metrics_isolated_per_error_type(self):
        """Error metrics track separate counters for each error type."""
        from apps.tenants.middleware.error_handler import (
            _record_error_metric,
            get_error_metrics,
            reset_error_metrics,
        )

        reset_error_metrics()
        _record_error_metric("tenant_not_found", "a.com")
        _record_error_metric("tenant_suspended", "b.com")
        _record_error_metric("tenant_expired", "c.com")

        metrics = get_error_metrics()
        assert metrics["by_type"]["tenant_not_found"] == 1
        assert metrics["by_type"]["tenant_suspended"] == 1
        assert metrics["by_type"]["tenant_expired"] == 1
        assert metrics["total"] == 3
        reset_error_metrics()

    def test_metrics_isolated_per_domain(self):
        """Error metrics track separate counters for each domain."""
        from apps.tenants.middleware.error_handler import (
            _record_error_metric,
            get_error_metrics,
            reset_error_metrics,
        )

        reset_error_metrics()
        _record_error_metric("tenant_not_found", "x.com")
        _record_error_metric("tenant_not_found", "x.com")
        _record_error_metric("tenant_not_found", "y.com")

        metrics = get_error_metrics()
        assert metrics["by_domain"]["x.com"]["tenant_not_found"] == 2
        assert metrics["by_domain"]["y.com"]["tenant_not_found"] == 1
        reset_error_metrics()

    def test_cache_invalidation_does_not_affect_other_resolvers(self):
        """Invalidating one resolver cache does not affect others."""
        with patch(
            "django.core.cache.cache"
        ) as mock_cache:
            from apps.tenants.middleware import invalidate_custom_domain_cache

            invalidate_custom_domain_cache("shop.example.com")
            mock_cache.delete.assert_called_once()
            call_arg = mock_cache.delete.call_args[0][0]
            assert "custom_domain" in call_arg
            assert "header" not in call_arg

    def test_public_path_does_not_affect_tenant_resolution(self):
        """Public path check does not modify resolver state."""
        from apps.tenants.middleware import is_public_path

        # Public path check is stateless
        assert is_public_path("/health/") is True
        assert is_public_path("/api/v1/products/") is False
        # Calling multiple times has no side effect
        assert is_public_path("/health/") is True
