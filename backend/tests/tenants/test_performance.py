"""
Performance tests for tenant middleware — Task 80.

SubPhase-06, Group-F: Testing & Verification (Doc 02).

Benchmarks middleware overhead for tenant resolution. Target is
under 5ms per resolution call. Tests use mocked cache and DB
to isolate middleware logic timing from I/O latency.

Run with:
    pytest backend/tests/tenants/test_performance.py -v
"""

from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory, override_settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tenant(name="perf-tenant", schema_name="perf", pk=1):
    """Create a mock Tenant object."""
    return SimpleNamespace(
        pk=pk,
        name=name,
        schema_name=schema_name,
        status="active",
        is_active=True,
    )


PERFORMANCE_TARGET_MS = 5.0
ITERATIONS = 100


# ===========================================================================
# Task 80: Performance Testing
# ===========================================================================


class TestSubdomainResolverPerformance:
    """
    Task 80: Subdomain resolver performance benchmarks.

    Verifies that subdomain resolution completes within the 5ms
    target when the cache is populated (hot path).
    """

    @patch("django.core.cache.cache")
    def test_subdomain_cache_hit_under_5ms(self, mock_cache):
        """Subdomain cache hit resolves in under 5ms average."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        tenant = _make_tenant()
        mock_cache.get.return_value = tenant
        resolver = SubdomainResolver(base_domain="lcc.example.com")

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            resolver.resolve_tenant("acme")
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS, (
            f"Subdomain cache hit took {elapsed_ms:.2f}ms "
            f"(target: <{PERFORMANCE_TARGET_MS}ms)"
        )

    @patch("django.core.cache.cache")
    def test_subdomain_cache_miss_sentinel_under_5ms(self, mock_cache):
        """Subdomain cache miss sentinel resolves in under 5ms."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        mock_cache.get.return_value = "__none__"
        resolver = SubdomainResolver(base_domain="lcc.example.com")

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            resolver.resolve_tenant("missing")
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS

    def test_reserved_subdomain_check_under_5ms(self):
        """Reserved subdomain check completes in under 5ms."""
        from apps.tenants.middleware.subdomain_resolver import SubdomainResolver

        resolver = SubdomainResolver(base_domain="lcc.example.com")

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            resolver.resolve_tenant("www")
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS


class TestCustomDomainResolverPerformance:
    """
    Task 80: Custom domain resolver performance benchmarks.

    Verifies that custom domain resolution completes within the
    5ms target when the cache is populated.
    """

    @patch("django.core.cache.cache")
    def test_custom_domain_cache_hit_under_5ms(self, mock_cache):
        """Custom domain cache hit resolves in under 5ms average."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        tenant = _make_tenant()
        mock_cache.get.return_value = tenant
        resolver = CustomDomainResolver(base_domain="lcc.example.com")

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            resolver.resolve_by_domain("shop.mybusiness.lk")
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS

    @override_settings(ALLOWED_HOSTS=["*"])
    def test_platform_domain_skip_under_5ms(self):
        """Platform domain skip completes in under 5ms."""
        from apps.tenants.middleware.domain_resolver import CustomDomainResolver

        resolver = CustomDomainResolver(base_domain="lcc.example.com")
        factory = RequestFactory()
        request = factory.get("/", HTTP_HOST="acme.lcc.example.com")

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            resolver.resolve(request)
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS


class TestHeaderResolverPerformance:
    """
    Task 80: Header resolver performance benchmarks.

    Verifies that header-based resolution path checks complete
    within the 5ms target.
    """

    def test_header_path_check_under_5ms(self):
        """Header path validation completes in under 5ms."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        paths = [
            "/api/v1/products/",
            "/mobile/v1/orders/",
            "/webhook/stripe/",
            "/dashboard/",
            "/admin/",
        ]

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            for path in paths:
                resolver.is_header_path(path)
        elapsed_ms = (time.perf_counter() - start) / (ITERATIONS * len(paths)) * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS

    def test_header_resolve_non_api_under_5ms(self):
        """Non-API path resolution skip completes in under 5ms."""
        from apps.tenants.middleware.header_resolver import HeaderResolver

        resolver = HeaderResolver()
        factory = RequestFactory()
        request = factory.get("/dashboard/")

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            resolver.resolve(request)
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS


class TestErrorHandlerPerformance:
    """
    Task 80: Error handler performance benchmarks.

    Verifies that error responses and metric tracking complete
    within the 5ms target.
    """

    def test_is_public_path_under_5ms(self):
        """Public path check completes in under 5ms."""
        from apps.tenants.middleware import is_public_path

        paths = ["/health/", "/api/v1/auth/login/", "/api/v1/products/"]

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            for path in paths:
                is_public_path(path)
        elapsed_ms = (time.perf_counter() - start) / (ITERATIONS * len(paths)) * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS

    def test_is_tenant_suspended_under_5ms(self):
        """Tenant suspended check completes in under 5ms."""
        from apps.tenants.middleware import is_tenant_suspended

        tenant = _make_tenant()

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            is_tenant_suspended(tenant)
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS

    def test_error_metrics_recording_under_5ms(self):
        """Error metric recording completes in under 5ms."""
        from apps.tenants.middleware.error_handler import (
            _record_error_metric,
            reset_error_metrics,
        )

        reset_error_metrics()

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            _record_error_metric("test_type", "test.com")
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS
        reset_error_metrics()

    def test_get_error_metrics_under_5ms(self):
        """Error metrics retrieval completes in under 5ms."""
        from apps.tenants.middleware.error_handler import (
            _record_error_metric,
            get_error_metrics,
            reset_error_metrics,
        )

        reset_error_metrics()
        for i in range(50):
            _record_error_metric(f"type_{i % 5}", f"domain{i}.com")

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            get_error_metrics()
        elapsed_ms = (time.perf_counter() - start) / ITERATIONS * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS
        reset_error_metrics()

    def test_subdomain_validation_under_5ms(self):
        """Subdomain pattern validation completes in under 5ms."""
        from apps.tenants.middleware import is_valid_subdomain

        candidates = ["acme", "my-shop", "shop123", "-bad", "BAD", "a" * 63]

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            for c in candidates:
                is_valid_subdomain(c)
        elapsed_ms = (time.perf_counter() - start) / (ITERATIONS * len(candidates)) * 1000

        assert elapsed_ms < PERFORMANCE_TARGET_MS
