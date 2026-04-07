"""
Unit tests for tenant middleware — Tasks 69-75.

SubPhase-06, Group-F: Testing & Verification (Doc 01).

Test coverage:
    Task 69: Middleware initialization and flow (TestMiddleware)
    Task 70: Subdomain resolution scenarios (TestSubdomainResolution)
    Task 71: Custom domain resolution and verification (TestCustomDomainResolution)
    Task 72: Header-based tenant resolution (TestHeaderResolution)
    Task 73: Public schema fallback paths (TestPublicFallback)
    Task 74: Suspended tenant access handling (TestSuspendedTenant)
    Task 75: Cache usage and invalidation (TestCacheBehavior)

Run with:
    pytest backend/tests/tenants/test_middleware.py -v
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory, override_settings


# ---------------------------------------------------------------------------
# Shared mock helpers
# ---------------------------------------------------------------------------

def _make_tenant(
    name: str = "acme",
    schema_name: str = "acme",
    pk: int = 1,
    status: str = "active",
    is_active: bool = True,
):
    """Create a mock Tenant object."""
    tenant = SimpleNamespace(
        pk=pk,
        name=name,
        schema_name=schema_name,
        status=status,
        is_active=is_active,
    )
    return tenant


def _make_domain(
    domain: str,
    tenant=None,
    is_verified: bool = True,
    is_custom_domain: bool = False,
    domain_type: str = "subdomain",
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
# Task 69: Create Middleware Tests — TestMiddleware
# ===========================================================================


@pytest.mark.django_db
class TestMiddleware:
    """
    Task 69: Middleware initialization and request flow.

    Covers request attributes, context switching, and initialization.
    """

    def test_middleware_class_exists(self):
        """LCCTenantMiddleware class can be imported."""
        from apps.tenants.middleware import LCCTenantMiddleware
        assert LCCTenantMiddleware is not None

    def test_middleware_inherits_tenant_main(self):
        """LCCTenantMiddleware extends TenantMainMiddleware."""
        from apps.tenants.middleware import LCCTenantMiddleware
        from django_tenants.middleware.main import TenantMainMiddleware
        assert issubclass(LCCTenantMiddleware, TenantMainMiddleware)

    def test_middleware_init_stores_get_response(self):
        """__init__ stores the get_response callable."""
        from apps.tenants.middleware import LCCTenantMiddleware
        mock_response = MagicMock()
        with patch.object(
            LCCTenantMiddleware.__bases__[0], "__init__", return_value=None
        ):
            mw = LCCTenantMiddleware(mock_response)
            assert mw.get_response is mock_response

    def test_middleware_has_process_request(self):
        """process_request method exists on the middleware."""
        from apps.tenants.middleware import LCCTenantMiddleware
        assert hasattr(LCCTenantMiddleware, "process_request")

    def test_middleware_has_call_method(self):
        """__call__ method exists on the middleware."""
        from apps.tenants.middleware import LCCTenantMiddleware
        assert hasattr(LCCTenantMiddleware, "__call__")

    def test_process_request_injects_attributes(self):
        """process_request injects request.tenant and request.schema_name."""
        from apps.tenants.middleware import LCCTenantMiddleware

        factory = RequestFactory()
        request = factory.get("/")

        mock_tenant = _make_tenant()

        with patch.object(
            LCCTenantMiddleware.__bases__[0],
            "__init__",
            return_value=None,
        ), patch.object(
            LCCTenantMiddleware.__bases__[0],
            "process_request",
            return_value=None,
        ), patch(
            "django.db.connection"
        ) as mock_conn:
            mock_conn.tenant = mock_tenant
            mock_conn.schema_name = "acme"

            mw = LCCTenantMiddleware(MagicMock())
            mw.process_request(request)

            assert request.tenant is mock_tenant
            assert request.schema_name == "acme"

    def test_process_request_handles_no_tenant(self):
        """process_request handles None tenant gracefully."""
        from apps.tenants.middleware import LCCTenantMiddleware

        factory = RequestFactory()
        request = factory.get("/")

        with patch.object(
            LCCTenantMiddleware.__bases__[0],
            "__init__",
            return_value=None,
        ), patch.object(
            LCCTenantMiddleware.__bases__[0],
            "process_request",
            return_value=None,
        ), patch(
            "django.db.connection"
        ) as mock_conn:
            mock_conn.tenant = None
            mock_conn.schema_name = None

            mw = LCCTenantMiddleware(MagicMock())
            mw.process_request(request)

            assert request.tenant is None
            assert request.schema_name is None


# ===========================================================================
# Task 70: Test Subdomain Resolution — TestSubdomainResolution
# ===========================================================================


class TestSubdomainResolution:
    """
    Task 70: Subdomain resolution scenarios.

    Covers valid subdomains, reserved subdomains, invalid subdomains,
    and the SUBDOMAIN_PATTERN regex.
    """

    def test_subdomain_pattern_valid_simple(self):
        """Valid simple subdomain matches."""
        from apps.tenants.middleware import SUBDOMAIN_PATTERN
        assert SUBDOMAIN_PATTERN.match("acme")

    def test_subdomain_pattern_valid_with_hyphens(self):
        """Valid subdomain with hyphens matches."""
        from apps.tenants.middleware import SUBDOMAIN_PATTERN
        assert SUBDOMAIN_PATTERN.match("my-company")

    def test_subdomain_pattern_valid_with_numbers(self):
        """Valid subdomain with numbers matches."""
        from apps.tenants.middleware import SUBDOMAIN_PATTERN
        assert SUBDOMAIN_PATTERN.match("shop123")

    def test_subdomain_pattern_rejects_leading_hyphen(self):
        """Subdomain with leading hyphen is rejected."""
        from apps.tenants.middleware import SUBDOMAIN_PATTERN
        assert SUBDOMAIN_PATTERN.match("-acme") is None

    def test_subdomain_pattern_rejects_trailing_hyphen(self):
        """Subdomain with trailing hyphen is rejected."""
        from apps.tenants.middleware import SUBDOMAIN_PATTERN
        assert SUBDOMAIN_PATTERN.match("acme-") is None

    def test_subdomain_pattern_rejects_uppercase(self):
        """Uppercase letters are rejected (must be lowercase)."""
        from apps.tenants.middleware import SUBDOMAIN_PATTERN
        assert SUBDOMAIN_PATTERN.match("ACME") is None

    def test_subdomain_pattern_rejects_dots(self):
        """Dots in subdomain are rejected."""
        from apps.tenants.middleware import SUBDOMAIN_PATTERN
        assert SUBDOMAIN_PATTERN.match("acme.corp") is None

    def test_subdomain_pattern_rejects_underscores(self):
        """Underscores in subdomain are rejected."""
        from apps.tenants.middleware import SUBDOMAIN_PATTERN
        assert SUBDOMAIN_PATTERN.match("acme_corp") is None

    def test_is_valid_subdomain_valid(self):
        """is_valid_subdomain returns True for valid strings."""
        from apps.tenants.middleware import is_valid_subdomain
        assert is_valid_subdomain("acme") is True
        assert is_valid_subdomain("my-shop") is True
        assert is_valid_subdomain("a") is True

    def test_is_valid_subdomain_invalid(self):
        """is_valid_subdomain returns False for invalid strings."""
        from apps.tenants.middleware import is_valid_subdomain
        assert is_valid_subdomain("") is False
        assert is_valid_subdomain("-bad") is False
        assert is_valid_subdomain("BAD") is False

    @patch("django.core.cache.cache")
    def test_resolver_returns_none_for_reserved(self, mock_cache):
        """Reserved subdomains return None without DB lookup."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        resolver = SubdomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_tenant("www")
        assert result is None
        # Should not hit cache for reserved subdomain
        mock_cache.get.assert_not_called()

    def test_resolver_returns_none_for_empty(self):
        """Empty subdomain returns None."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        resolver = SubdomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_tenant("")
        assert result is None

    @patch("django.core.cache.cache")
    def test_resolver_cache_hit(self, mock_cache):
        """Cached tenant is returned without DB query."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        tenant = _make_tenant(name="cached-co")
        mock_cache.get.return_value = tenant

        resolver = SubdomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_tenant("cached")
        assert result is tenant

    @patch("django.core.cache.cache")
    def test_resolver_cache_miss_sentinel(self, mock_cache):
        """Cache miss sentinel returns None without DB query."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        mock_cache.get.return_value = "__none__"

        resolver = SubdomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_tenant("missing")
        assert result is None

    def test_resolve_method_calls_get_subdomain_from_request(self):
        """resolve() delegates to get_subdomain_from_request + resolve_tenant."""
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


# ===========================================================================
# Task 71: Test Custom Domain Resolution — TestCustomDomainResolution
# ===========================================================================


class TestCustomDomainResolution:
    """
    Task 71: Custom domain resolution and verification.

    Covers verified domains, unverified domains, missing domains,
    and platform domain bypass.
    """

    def test_resolver_class_exists(self):
        """CustomDomainResolver class can be imported."""
        from apps.tenants.middleware import CustomDomainResolver
        assert CustomDomainResolver is not None

    def test_resolver_has_resolve_method(self):
        """CustomDomainResolver has a resolve method."""
        from apps.tenants.middleware import CustomDomainResolver
        assert hasattr(CustomDomainResolver, "resolve")

    def test_resolver_has_resolve_by_domain(self):
        """CustomDomainResolver has a resolve_by_domain method."""
        from apps.tenants.middleware import CustomDomainResolver
        assert hasattr(CustomDomainResolver, "resolve_by_domain")

    @override_settings(ALLOWED_HOSTS=["*"])
    def test_platform_domain_is_skipped(self):
        """Platform base domains are not resolved as custom domains."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        resolver = CustomDomainResolver(base_domain="lcc.example.com")
        factory = RequestFactory()
        request = factory.get("/", HTTP_HOST="acme.lcc.example.com")
        result = resolver.resolve(request)
        assert result is None

    @patch("django.core.cache.cache")
    def test_cache_hit_returns_tenant(self, mock_cache):
        """Cached custom domain returns tenant."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        tenant = _make_tenant(name="custom-co")
        mock_cache.get.return_value = tenant

        resolver = CustomDomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_by_domain("shop.mybusiness.lk")
        assert result is tenant

    @patch("django.core.cache.cache")
    def test_cache_miss_sentinel_returns_none(self, mock_cache):
        """Cache miss sentinel returns None."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        mock_cache.get.return_value = "__none__"

        resolver = CustomDomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_by_domain("missing.example.com")
        assert result is None

    def test_empty_domain_returns_none(self):
        """Empty domain string returns None."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        resolver = CustomDomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_by_domain("")
        assert result is None

    def test_invalidate_custom_domain_cache_callable(self):
        """invalidate_custom_domain_cache is importable and callable."""
        from apps.tenants.middleware import invalidate_custom_domain_cache
        assert callable(invalidate_custom_domain_cache)

    @patch("django.core.cache.cache")
    def test_invalidate_deletes_cache_key(self, mock_cache):
        """invalidate_custom_domain_cache deletes the correct cache key."""
        from apps.tenants.middleware import invalidate_custom_domain_cache

        invalidate_custom_domain_cache("shop.mybusiness.lk")
        mock_cache.delete.assert_called_once()
        call_arg = mock_cache.delete.call_args[0][0]
        assert "shop.mybusiness.lk" in call_arg


# ===========================================================================
# Task 72: Test Header Resolution — TestHeaderResolution
# ===========================================================================


class TestHeaderResolution:
    """
    Task 72: Header-based tenant resolution.

    Covers allowed/disallowed paths, header extraction,
    and authentication expectations.
    """

    def test_resolver_class_exists(self):
        """HeaderResolver class can be imported."""
        from apps.tenants.middleware import HeaderResolver
        assert HeaderResolver is not None

    def test_resolver_has_resolve_method(self):
        """HeaderResolver has a resolve method."""
        from apps.tenants.middleware import HeaderResolver
        assert hasattr(HeaderResolver, "resolve")

    def test_is_header_path_api(self):
        """API paths are allowed for header resolution."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        assert resolver.is_header_path("/api/v1/products/") is True

    def test_is_header_path_mobile(self):
        """Mobile paths are allowed for header resolution."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        assert resolver.is_header_path("/mobile/v1/orders/") is True

    def test_is_header_path_webhook(self):
        """Webhook paths are allowed for header resolution."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        assert resolver.is_header_path("/webhook/stripe/") is True

    def test_is_header_path_rejects_browser(self):
        """Browser paths are rejected for header resolution."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        assert resolver.is_header_path("/dashboard/") is False

    def test_is_header_path_rejects_admin(self):
        """Admin paths are rejected for header resolution."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        assert resolver.is_header_path("/admin/") is False

    def test_is_header_path_empty(self):
        """Empty path returns False."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        assert resolver.is_header_path("") is False

    def test_resolve_skips_non_api_path(self):
        """resolve() returns None for non-API paths."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        factory = RequestFactory()
        request = factory.get("/dashboard/")
        result = resolver.resolve(request)
        assert result is None

    def test_resolve_returns_none_without_header(self):
        """resolve() returns None when no tenant header is present."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        factory = RequestFactory()
        request = factory.get("/api/v1/products/")
        result = resolver.resolve(request)
        assert result is None

    def test_invalidate_header_cache_callable(self):
        """invalidate_header_cache is importable and callable."""
        from apps.tenants.middleware import invalidate_header_cache
        assert callable(invalidate_header_cache)

    @patch("django.core.cache.cache")
    def test_invalidate_deletes_cache_key(self, mock_cache):
        """invalidate_header_cache deletes the correct cache key."""
        from apps.tenants.middleware import invalidate_header_cache

        invalidate_header_cache("acme-corp")
        mock_cache.delete.assert_called_once()
        call_arg = mock_cache.delete.call_args[0][0]
        assert "acme-corp" in call_arg


# ===========================================================================
# Task 73: Test Public Fallback — TestPublicFallback
# ===========================================================================


class TestPublicFallback:
    """
    Task 73: Public schema fallback paths.

    Covers public schema path detection and expected schema usage.
    """

    def test_is_public_path_auth(self):
        """Auth path is public."""
        from apps.tenants.middleware import is_public_path
        assert is_public_path("/api/v1/auth/login/") is True

    def test_is_public_path_register(self):
        """Register path is public."""
        from apps.tenants.middleware import is_public_path
        assert is_public_path("/api/v1/register/") is True

    def test_is_public_path_plans(self):
        """Plans path is public."""
        from apps.tenants.middleware import is_public_path
        assert is_public_path("/api/v1/plans/") is True

    def test_is_public_path_health(self):
        """Health check path is public."""
        from apps.tenants.middleware import is_public_path
        assert is_public_path("/health/") is True

    def test_is_public_path_metrics(self):
        """Metrics path is public."""
        from apps.tenants.middleware import is_public_path
        assert is_public_path("/metrics/") is True

    def test_is_public_path_products_is_not_public(self):
        """Products path is NOT public."""
        from apps.tenants.middleware import is_public_path
        assert is_public_path("/api/v1/products/") is False

    def test_is_public_path_dashboard_is_not_public(self):
        """Dashboard path is NOT public."""
        from apps.tenants.middleware import is_public_path
        assert is_public_path("/dashboard/") is False

    def test_is_public_path_empty(self):
        """Empty path returns False."""
        from apps.tenants.middleware import is_public_path
        assert is_public_path("") is False

    def test_get_public_schema_paths_returns_list(self):
        """get_public_schema_paths returns a list."""
        from apps.tenants.middleware.error_handler import get_public_schema_paths
        result = get_public_schema_paths()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_public_paths_contain_auth(self):
        """Default public paths include auth."""
        from apps.tenants.middleware.error_handler import get_public_schema_paths
        paths = get_public_schema_paths()
        assert any("/auth/" in p for p in paths)


# ===========================================================================
# Task 74: Test Suspended Tenant — TestSuspendedTenant
# ===========================================================================


class TestSuspendedTenant:
    """
    Task 74: Suspended tenant access handling.

    Covers 403 responses, template usage, and status detection.
    """

    def test_is_tenant_suspended_true(self):
        """Suspended tenant is detected."""
        from apps.tenants.middleware import is_tenant_suspended
        tenant = _make_tenant(status="suspended")
        assert is_tenant_suspended(tenant) is True

    def test_is_tenant_suspended_false_for_active(self):
        """Active tenant is not suspended."""
        from apps.tenants.middleware import is_tenant_suspended
        tenant = _make_tenant(status="active")
        assert is_tenant_suspended(tenant) is False

    def test_is_tenant_suspended_false_for_none(self):
        """None tenant returns False."""
        from apps.tenants.middleware import is_tenant_suspended
        assert is_tenant_suspended(None) is False

    def test_tenant_suspended_api_returns_403(self):
        """API request to suspended tenant returns 403 JSON."""
        from apps.tenants.middleware import tenant_suspended

        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        tenant = _make_tenant(status="suspended")
        response = tenant_suspended(request, tenant)
        assert response.status_code == 403

    def test_tenant_suspended_api_json_format(self):
        """Suspended API response has correct JSON structure."""
        import json
        from apps.tenants.middleware import tenant_suspended

        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        tenant = _make_tenant(status="suspended")
        response = tenant_suspended(request, tenant)
        body = json.loads(response.content)
        assert body["error"] == "tenant_suspended"
        assert "detail" in body

    def test_tenant_suspended_browser_returns_403(self):
        """Browser request to suspended tenant returns 403."""
        from apps.tenants.middleware import tenant_suspended

        factory = RequestFactory()
        request = factory.get("/dashboard/", HTTP_ACCEPT="text/html")
        tenant = _make_tenant(status="suspended")
        response = tenant_suspended(request, tenant)
        assert response.status_code == 403

    def test_tenant_not_found_api_returns_404(self):
        """API request to unknown tenant returns 404 JSON."""
        from apps.tenants.middleware import tenant_not_found

        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        response = tenant_not_found(request, hostname="unknown.example.com")
        assert response.status_code == 404

    def test_tenant_not_found_api_json_format(self):
        """Not-found API response has correct JSON structure."""
        import json
        from apps.tenants.middleware import tenant_not_found

        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        response = tenant_not_found(request, hostname="unknown.example.com")
        body = json.loads(response.content)
        assert body["error"] == "tenant_not_found"
        assert "detail" in body

    def test_get_tenant_status_active(self):
        """get_tenant_status returns 'active' for active tenants."""
        from apps.tenants.middleware import get_tenant_status
        tenant = _make_tenant(status="active")
        assert get_tenant_status(tenant) == "active"

    def test_get_tenant_status_suspended(self):
        """get_tenant_status returns 'suspended' for suspended tenants."""
        from apps.tenants.middleware import get_tenant_status
        tenant = _make_tenant(status="suspended")
        assert get_tenant_status(tenant) == "suspended"

    def test_get_tenant_status_expired(self):
        """get_tenant_status returns 'expired' for expired tenants."""
        from apps.tenants.middleware import get_tenant_status
        tenant = _make_tenant(status="expired")
        assert get_tenant_status(tenant) == "expired"

    def test_get_tenant_status_none(self):
        """get_tenant_status returns 'not_found' for None."""
        from apps.tenants.middleware import get_tenant_status
        assert get_tenant_status(None) == "not_found"

    def test_is_tenant_expired_true(self):
        """Expired tenant is detected."""
        from apps.tenants.middleware import is_tenant_expired
        tenant = _make_tenant(status="expired")
        assert is_tenant_expired(tenant) is True

    def test_is_tenant_expired_false_for_active(self):
        """Active tenant is not expired."""
        from apps.tenants.middleware import is_tenant_expired
        tenant = _make_tenant(status="active")
        assert is_tenant_expired(tenant) is False

    def test_tenant_expired_api_returns_403(self):
        """API request to expired tenant returns 403 JSON."""
        from apps.tenants.middleware import tenant_expired
        from apps.tenants.middleware.error_handler import reset_error_metrics

        reset_error_metrics()
        factory = RequestFactory()
        request = factory.get(
            "/api/v1/products/", HTTP_ACCEPT="application/json"
        )
        tenant = _make_tenant(status="expired")
        response = tenant_expired(request, tenant)
        assert response.status_code == 403


# ===========================================================================
# Task 75: Test Cache Behavior — TestCacheBehavior
# ===========================================================================


class TestCacheBehavior:
    """
    Task 75: Cache usage and invalidation.

    Covers cache hit, miss, invalidation, and TTL expectations.
    """

    @patch("django.core.cache.cache")
    def test_subdomain_cache_hit(self, mock_cache):
        """Subdomain resolver returns cached tenant on cache hit."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        tenant = _make_tenant()
        mock_cache.get.return_value = tenant

        resolver = SubdomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_tenant("acme")
        assert result is tenant
        mock_cache.set.assert_not_called()

    @patch("django.core.cache.cache")
    def test_subdomain_cache_miss_sentinel(self, mock_cache):
        """Subdomain resolver returns None for miss sentinel."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        mock_cache.get.return_value = "__none__"

        resolver = SubdomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_tenant("missing")
        assert result is None

    @patch("django.core.cache.cache")
    def test_custom_domain_cache_hit(self, mock_cache):
        """Custom domain resolver returns cached tenant on cache hit."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        tenant = _make_tenant()
        mock_cache.get.return_value = tenant

        resolver = CustomDomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_by_domain("shop.example.com")
        assert result is tenant

    @patch("django.core.cache.cache")
    def test_custom_domain_cache_miss_sentinel(self, mock_cache):
        """Custom domain resolver returns None for miss sentinel."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        mock_cache.get.return_value = "__none__"

        resolver = CustomDomainResolver(base_domain="lcc.example.com")
        result = resolver.resolve_by_domain("missing.example.com")
        assert result is None

    @patch("django.core.cache.cache")
    def test_subdomain_invalidation(self, mock_cache):
        """invalidate_subdomain_cache calls cache.delete."""
        from apps.tenants.middleware.subdomain_resolver import (
            SubdomainResolver,
            invalidate_subdomain_cache,
        )

        with patch(
            "apps.tenants.middleware.subdomain_resolver.SubdomainResolver"
        ) as MockResolver:
            mock_instance = MagicMock()
            mock_instance.get_subdomain.return_value = "acme"
            MockResolver.return_value = mock_instance

            invalidate_subdomain_cache("acme.lcc.example.com")

    @patch("django.core.cache.cache")
    def test_custom_domain_invalidation(self, mock_cache):
        """invalidate_custom_domain_cache calls cache.delete."""
        from apps.tenants.middleware import invalidate_custom_domain_cache

        invalidate_custom_domain_cache("shop.mybusiness.lk")
        mock_cache.delete.assert_called_once()

    @patch("django.core.cache.cache")
    def test_header_cache_invalidation(self, mock_cache):
        """invalidate_header_cache calls cache.delete."""
        from apps.tenants.middleware import invalidate_header_cache

        invalidate_header_cache("acme-corp")
        mock_cache.delete.assert_called_once()

    def test_error_metrics_reset(self):
        """Error metrics can be reset."""
        from apps.tenants.middleware import get_error_metrics, reset_error_metrics

        reset_error_metrics()
        metrics = get_error_metrics()
        assert metrics["total"] == 0

    def test_error_metrics_track_counts(self):
        """Error metrics track counts by type."""
        from apps.tenants.middleware.error_handler import (
            _record_error_metric,
            get_error_metrics,
            reset_error_metrics,
        )

        reset_error_metrics()
        _record_error_metric("tenant_not_found", "test.com")
        _record_error_metric("tenant_not_found", "test.com")
        _record_error_metric("tenant_suspended", "other.com")

        metrics = get_error_metrics()
        assert metrics["total"] == 3
        assert metrics["by_type"]["tenant_not_found"] == 2
        assert metrics["by_type"]["tenant_suspended"] == 1
        reset_error_metrics()

    def test_error_metrics_track_by_domain(self):
        """Error metrics track counts by domain."""
        from apps.tenants.middleware.error_handler import (
            _record_error_metric,
            get_error_metrics,
            reset_error_metrics,
        )

        reset_error_metrics()
        _record_error_metric("tenant_not_found", "abuse.com")
        _record_error_metric("tenant_not_found", "abuse.com")

        metrics = get_error_metrics()
        assert "abuse.com" in metrics["by_domain"]
        assert metrics["by_domain"]["abuse.com"]["tenant_not_found"] == 2
        reset_error_metrics()
