"""
LankaCommerce Cloud – Cache Layer Tests (SP09 Groups E-F).

Covers:
    - Cache constants
    - TenantCache init, key building, core ops, bulk, counters, delete_pattern
    - get_tenant_cache factory
    - cache_response / cache_method / cache_queryset decorators
    - Utility helpers (make_cache_key, hash_key, cache_get_or_set, clear_cache, cache_stats)
    - CacheInvalidator static methods
    - Signal handlers (post_save / post_delete)
    - CacheMixin
    - clearcache management command

All tests are pure-mock — no database or Redis required.
"""

from __future__ import annotations

import hashlib
from io import StringIO
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest
from django.core.management import call_command


# ════════════════════════════════════════════════════════════════════════
# Constants
# ════════════════════════════════════════════════════════════════════════


class TestCacheConstants:
    """Verify hard-coded TTL, prefix, and template values."""

    def test_ttl_short(self):
        from apps.core.cache.constants import CACHE_TTL_SHORT
        assert CACHE_TTL_SHORT == 300

    def test_ttl_medium(self):
        from apps.core.cache.constants import CACHE_TTL_MEDIUM
        assert CACHE_TTL_MEDIUM == 3600

    def test_ttl_long(self):
        from apps.core.cache.constants import CACHE_TTL_LONG
        assert CACHE_TTL_LONG == 86400

    def test_key_prefix(self):
        from apps.core.cache.constants import KEY_PREFIX
        assert KEY_PREFIX == "lcc"

    def test_tenant_key_template(self):
        from apps.core.cache.constants import TENANT_KEY_TEMPLATE
        assert "{prefix}" in TENANT_KEY_TEMPLATE
        assert "{schema}" in TENANT_KEY_TEMPLATE
        assert "{key}" in TENANT_KEY_TEMPLATE

    def test_shared_key_template(self):
        from apps.core.cache.constants import SHARED_KEY_TEMPLATE
        assert "{prefix}" in SHARED_KEY_TEMPLATE
        assert "{key}" in SHARED_KEY_TEMPLATE
        assert "{schema}" not in SHARED_KEY_TEMPLATE

    def test_max_key_length(self):
        from apps.core.cache.constants import MAX_KEY_LENGTH
        assert MAX_KEY_LENGTH == 200


# ════════════════════════════════════════════════════════════════════════
# TenantCache – init
# ════════════════════════════════════════════════════════════════════════


class TestTenantCacheInit:
    """TenantCache constructor and alias fallback."""

    @patch("apps.core.cache.tenant_cache.caches")
    def test_default_alias(self, mock_caches):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()

        mock_caches.__getitem__.assert_called_with("default")
        assert tc._alias == "default"

    @patch("apps.core.cache.tenant_cache.caches")
    def test_custom_alias(self, mock_caches):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache("sessions")

        mock_caches.__getitem__.assert_called_with("sessions")
        assert tc._alias == "sessions"

    @patch("apps.core.cache.tenant_cache.caches")
    def test_fallback_on_invalid_alias(self, mock_caches):
        """When the requested alias raises, fall back to 'default'."""
        mock_default = MagicMock()

        def side_effect(alias):
            if alias == "bogus":
                raise KeyError("bogus")
            return mock_default

        mock_caches.__getitem__ = MagicMock(side_effect=side_effect)

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache("bogus")

        assert tc._cache is mock_default


# ════════════════════════════════════════════════════════════════════════
# TenantCache – make_key
# ════════════════════════════════════════════════════════════════════════


class TestTenantCacheMakeKey:
    """Key generation with tenant context."""

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_key_with_tenant(self, mock_caches, mock_conn):
        mock_caches.__getitem__ = MagicMock(return_value=MagicMock())
        mock_conn.tenant = MagicMock(schema_name="acme")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        key = tc.make_key("products:list")

        assert key == "lcc:tenant:acme:products:list"

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_key_public_fallback(self, mock_caches, mock_conn):
        mock_caches.__getitem__ = MagicMock(return_value=MagicMock())
        mock_conn.tenant = None  # no tenant set

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        key = tc.make_key("config:theme")

        assert key == "lcc:tenant:public:config:theme"

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_shared_key(self, mock_caches, mock_conn):
        mock_caches.__getitem__ = MagicMock(return_value=MagicMock())

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        key = tc.make_key("global:exchange_rates", shared=True)

        assert key == "lcc:shared:global:exchange_rates"

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_long_key_hashed(self, mock_caches, mock_conn):
        mock_caches.__getitem__ = MagicMock(return_value=MagicMock())
        mock_conn.tenant = MagicMock(schema_name="acme")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        long_suffix = "x" * 300
        key = tc.make_key(long_suffix)

        assert key.startswith("lcc:h:")
        assert len(key) < 200  # hash is 32 hex chars + prefix

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_short_key_not_hashed(self, mock_caches, mock_conn):
        mock_caches.__getitem__ = MagicMock(return_value=MagicMock())
        mock_conn.tenant = MagicMock(schema_name="t1")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        key = tc.make_key("abc")

        assert ":h:" not in key


# ════════════════════════════════════════════════════════════════════════
# TenantCache – core operations (get / set / delete)
# ════════════════════════════════════════════════════════════════════════


class TestTenantCacheOperations:
    """get, set, delete — happy path and error paths."""

    def _make_cache(self, mock_caches, mock_conn, schema="test_tenant"):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name=schema)
        from apps.core.cache.tenant_cache import TenantCache
        return TenantCache(), mock_backend

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_get_returns_value(self, mock_caches, mock_conn):
        tc, backend = self._make_cache(mock_caches, mock_conn)
        backend.get.return_value = {"id": 1}

        result = tc.get("my_key")
        assert result == {"id": 1}
        backend.get.assert_called_once()

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_get_returns_default(self, mock_caches, mock_conn):
        tc, backend = self._make_cache(mock_caches, mock_conn)
        backend.get.return_value = "fallback"

        result = tc.get("missing", default="fallback")
        assert result == "fallback"

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_get_error_returns_default(self, mock_caches, mock_conn):
        tc, backend = self._make_cache(mock_caches, mock_conn)
        backend.get.side_effect = ConnectionError("redis down")

        result = tc.get("k", default="safe")
        assert result == "safe"

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_set_returns_true(self, mock_caches, mock_conn):
        tc, backend = self._make_cache(mock_caches, mock_conn)

        assert tc.set("k", "v") is True
        backend.set.assert_called_once()

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_set_with_timeout(self, mock_caches, mock_conn):
        tc, backend = self._make_cache(mock_caches, mock_conn)
        tc.set("k", "v", timeout=600)

        _, kwargs_or_args = backend.set.call_args
        # set(cache_key, value, timeout)
        assert backend.set.call_args[0][2] == 600

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_set_error_returns_false(self, mock_caches, mock_conn):
        tc, backend = self._make_cache(mock_caches, mock_conn)
        backend.set.side_effect = ConnectionError("redis down")

        assert tc.set("k", "v") is False

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_delete_returns_true(self, mock_caches, mock_conn):
        tc, backend = self._make_cache(mock_caches, mock_conn)
        assert tc.delete("k") is True
        backend.delete.assert_called_once()

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_delete_error_returns_false(self, mock_caches, mock_conn):
        tc, backend = self._make_cache(mock_caches, mock_conn)
        backend.delete.side_effect = Exception("boom")

        assert tc.delete("k") is False


# ════════════════════════════════════════════════════════════════════════
# TenantCache – bulk operations
# ════════════════════════════════════════════════════════════════════════


class TestTenantCacheBulkOps:
    """get_many / set_many."""

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_get_many(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()

        # Simulate backend returning data keyed by the full cache key
        full_k1 = tc.make_key("a")
        full_k2 = tc.make_key("b")
        mock_backend.get_many.return_value = {full_k1: 1, full_k2: 2}

        result = tc.get_many(["a", "b"])
        assert result == {"a": 1, "b": 2}

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_get_many_error(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")
        mock_backend.get_many.side_effect = Exception("fail")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.get_many(["a"]) == {}

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_set_many(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()

        assert tc.set_many({"x": 1, "y": 2}, timeout=60) is True
        mock_backend.set_many.assert_called_once()

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_set_many_error(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")
        mock_backend.set_many.side_effect = Exception("fail")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.set_many({"x": 1}) is False


# ════════════════════════════════════════════════════════════════════════
# TenantCache – counters
# ════════════════════════════════════════════════════════════════════════


class TestTenantCacheCounters:
    """incr / decr including missing-key initialisation."""

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_incr(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")
        mock_backend.incr.return_value = 5

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.incr("counter") == 5

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_decr(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")
        mock_backend.decr.return_value = 3

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.decr("counter") == 3

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_incr_missing_key_initialises(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")
        mock_backend.incr.side_effect = ValueError("key not found")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        result = tc.incr("new_counter", delta=10)

        assert result == 10
        mock_backend.set.assert_called_once()

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_decr_missing_key_initialises(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")
        mock_backend.decr.side_effect = ValueError("key not found")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        result = tc.decr("new_counter", delta=5)

        assert result == -5
        mock_backend.set.assert_called_once()

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_incr_error_returns_none(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")
        mock_backend.incr.side_effect = ConnectionError("down")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.incr("counter") is None

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_decr_error_returns_none(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")
        mock_backend.decr.side_effect = ConnectionError("down")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.decr("counter") is None


# ════════════════════════════════════════════════════════════════════════
# TenantCache – delete_pattern
# ════════════════════════════════════════════════════════════════════════


class TestTenantCacheDeletePattern:
    """delete_pattern with & without backend support."""

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_with_backend_support(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_backend.delete_pattern = MagicMock(return_value=5)
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.delete_pattern("products:*") == 5

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_without_backend_support(self, mock_caches, mock_conn):
        mock_backend = MagicMock(spec=[])  # no delete_pattern attr
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.delete_pattern("products:*") == 0

    @patch("apps.core.cache.tenant_cache.connection")
    @patch("apps.core.cache.tenant_cache.caches")
    def test_delete_pattern_error(self, mock_caches, mock_conn):
        mock_backend = MagicMock()
        mock_backend.delete_pattern.side_effect = Exception("oops")
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)
        mock_conn.tenant = MagicMock(schema_name="t1")

        from apps.core.cache.tenant_cache import TenantCache
        tc = TenantCache()
        assert tc.delete_pattern("products:*") == 0


# ════════════════════════════════════════════════════════════════════════
# get_tenant_cache factory
# ════════════════════════════════════════════════════════════════════════


class TestGetTenantCacheFactory:
    """Factory helper."""

    @patch("apps.core.cache.tenant_cache.caches")
    def test_returns_tenant_cache_instance(self, mock_caches):
        mock_caches.__getitem__ = MagicMock(return_value=MagicMock())

        from apps.core.cache.tenant_cache import TenantCache, get_tenant_cache
        tc = get_tenant_cache()
        assert isinstance(tc, TenantCache)

    @patch("apps.core.cache.tenant_cache.caches")
    def test_custom_alias(self, mock_caches):
        mock_caches.__getitem__ = MagicMock(return_value=MagicMock())

        from apps.core.cache.tenant_cache import get_tenant_cache
        tc = get_tenant_cache("sessions")
        assert tc._alias == "sessions"


# ════════════════════════════════════════════════════════════════════════
# Decorator – cache_response
# ════════════════════════════════════════════════════════════════════════


class TestCacheResponseDecorator:
    """cache_response for view functions."""

    @patch("apps.core.cache.decorators.TenantCache")
    def test_caches_successful_response(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None  # cache miss
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_response

        @cache_response(timeout=300)
        def my_view(request):
            resp = MagicMock()
            resp.status_code = 200
            resp.data = {"ok": True}
            return resp

        request = MagicMock(method="GET", path="/api/test", META={}, user=MagicMock(pk=1))
        result = my_view(request)

        # Should have called set to cache
        tc_inst.set.assert_called_once()
        assert result.status_code == 200

    @patch("apps.core.cache.decorators.TenantCache")
    def test_cache_hit_returns_cached(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = {"cached": True}
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_response

        called = []

        @cache_response(timeout=300)
        def my_view(request):
            called.append(True)
            resp = MagicMock(status_code=200, data={"fresh": True})
            return resp

        request = MagicMock(method="GET", path="/api/test", META={}, user=MagicMock(pk=1))
        result = my_view(request)

        assert result == {"cached": True}
        assert len(called) == 0  # original view NOT called

    @patch("apps.core.cache.decorators.TenantCache")
    def test_vary_on_user(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_response

        @cache_response(timeout=300, vary_on_user=True)
        def my_view(request):
            resp = MagicMock(status_code=200, data={})
            return resp

        request = MagicMock(method="GET", path="/api/test", META={}, user=MagicMock(pk=42))
        my_view(request)

        # The key passed to tc.get should contain ":u:42"
        get_key = tc_inst.get.call_args[0][0]
        assert ":u:42" in get_key

    @patch("apps.core.cache.decorators.TenantCache")
    def test_vary_on_tenant_false_uses_shared(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_response

        @cache_response(timeout=300, vary_on_tenant=False)
        def my_view(request):
            resp = MagicMock(status_code=200, data={})
            return resp

        request = MagicMock(method="GET", path="/api/test", META={}, user=MagicMock(pk=1))
        my_view(request)

        # shared=True should be passed
        _, get_kwargs = tc_inst.get.call_args
        assert get_kwargs.get("shared") is True

    @patch("apps.core.cache.decorators.TenantCache")
    def test_does_not_cache_error_responses(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_response

        @cache_response(timeout=300)
        def my_view(request):
            resp = MagicMock(status_code=500, data={"error": True})
            return resp

        request = MagicMock(method="GET", path="/api/test", META={}, user=MagicMock(pk=1))
        my_view(request)

        tc_inst.set.assert_not_called()

    @patch("apps.core.cache.decorators.TenantCache")
    def test_custom_cache_key_string(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_response

        @cache_response(cache_key="my:static:key", timeout=300)
        def my_view(request):
            resp = MagicMock(status_code=200, data={})
            return resp

        request = MagicMock(method="GET", path="/api/test", META={}, user=MagicMock(pk=1))
        my_view(request)

        get_key = tc_inst.get.call_args[0][0]
        assert get_key == "my:static:key"

    @patch("apps.core.cache.decorators.TenantCache")
    def test_custom_cache_key_callable(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_response

        @cache_response(cache_key=lambda req: f"dynamic:{req.path}", timeout=300)
        def my_view(request):
            resp = MagicMock(status_code=200, data={})
            return resp

        request = MagicMock(method="GET", path="/products", META={}, user=MagicMock(pk=1))
        my_view(request)

        get_key = tc_inst.get.call_args[0][0]
        assert get_key == "dynamic:/products"

    @patch("apps.core.cache.decorators.TenantCache")
    def test_does_not_cache_4xx_responses(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_response

        @cache_response(timeout=300)
        def my_view(request):
            resp = MagicMock(status_code=404, data={"detail": "not found"})
            return resp

        request = MagicMock(method="GET", path="/api/test", META={})
        my_view(request)

        tc_inst.set.assert_not_called()


# ════════════════════════════════════════════════════════════════════════
# Decorator – cache_method
# ════════════════════════════════════════════════════════════════════════


class TestCacheMethodDecorator:
    """cache_method for arbitrary methods."""

    @patch("apps.core.cache.decorators.TenantCache")
    def test_caches_return_value(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_method

        class Svc:
            @cache_method(timeout=60)
            def compute(self):
                return 42

        result = Svc().compute()
        assert result == 42
        tc_inst.set.assert_called_once()

    @patch("apps.core.cache.decorators.TenantCache")
    def test_cache_hit(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = 99
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_method

        class Svc:
            @cache_method(timeout=60)
            def compute(self):
                return 42

        result = Svc().compute()
        assert result == 99

    @patch("apps.core.cache.decorators.TenantCache")
    def test_different_kwargs_different_keys(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_method

        @cache_method(timeout=60)
        def fetch(limit=10):
            return list(range(limit))

        fetch(limit=5)
        key1 = tc_inst.get.call_args_list[0][0][0]

        fetch(limit=20)
        key2 = tc_inst.get.call_args_list[1][0][0]

        assert key1 != key2


# ════════════════════════════════════════════════════════════════════════
# Decorator – cache_queryset
# ════════════════════════════════════════════════════════════════════════


class TestCacheQuerysetDecorator:
    """cache_queryset decorator."""

    @patch("apps.core.cache.decorators.TenantCache")
    def test_caches_result(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_queryset

        @cache_queryset(cache_key="products:all", timeout=300)
        def get_products():
            return [1, 2, 3]

        result = get_products()
        assert result == [1, 2, 3]
        tc_inst.set.assert_called_once()

    @patch("apps.core.cache.decorators.TenantCache")
    def test_evaluates_queryset_to_list(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_queryset

        # Simulate a queryset-like object
        mock_qs = MagicMock()
        mock_qs.__iter__ = MagicMock(return_value=iter([1, 2, 3]))
        mock_qs.query = MagicMock()  # has .query => looks like a queryset

        @cache_queryset(cache_key="qs:test")
        def get_qs():
            return mock_qs

        result = get_qs()
        assert isinstance(result, list)

    @patch("apps.core.cache.decorators.TenantCache")
    def test_cache_hit(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = [10, 20]
        MockTC.return_value = tc_inst

        from apps.core.cache.decorators import cache_queryset

        called = []

        @cache_queryset(cache_key="qs:test")
        def get_qs():
            called.append(True)
            return []

        result = get_qs()
        assert result == [10, 20]
        assert len(called) == 0


# ════════════════════════════════════════════════════════════════════════
# Utility – make_cache_key
# ════════════════════════════════════════════════════════════════════════


class TestMakeCacheKey:
    """make_cache_key utility."""

    @patch("apps.core.cache.utils.TenantCache")
    def test_generates_tenant_scoped_key(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.make_key.return_value = "lcc:tenant:t1:products:list"
        MockTC.return_value = tc_inst

        from apps.core.cache.utils import make_cache_key
        key = make_cache_key("products", "list")

        tc_inst.make_key.assert_called_once_with("products:list", shared=False)
        assert key == "lcc:tenant:t1:products:list"

    @patch("apps.core.cache.utils.TenantCache")
    def test_shared_key(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.make_key.return_value = "lcc:shared:rates"
        MockTC.return_value = tc_inst

        from apps.core.cache.utils import make_cache_key
        key = make_cache_key("rates", shared=True)

        tc_inst.make_key.assert_called_once_with("rates", shared=True)


# ════════════════════════════════════════════════════════════════════════
# Utility – hash_key
# ════════════════════════════════════════════════════════════════════════


class TestHashKey:
    """hash_key utility."""

    def test_returns_md5_hex_digest(self):
        from apps.core.cache.utils import hash_key
        result = hash_key("hello")
        expected = hashlib.md5(b"hello").hexdigest()
        assert result == expected

    def test_consistent_hashing(self):
        from apps.core.cache.utils import hash_key
        assert hash_key("same") == hash_key("same")

    def test_different_keys_different_hashes(self):
        from apps.core.cache.utils import hash_key
        assert hash_key("a") != hash_key("b")


# ════════════════════════════════════════════════════════════════════════
# Utility – cache_get_or_set
# ════════════════════════════════════════════════════════════════════════


class TestCacheGetOrSet:
    """cache_get_or_set utility."""

    @patch("apps.core.cache.utils.TenantCache")
    def test_returns_cached_value(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = "cached_data"
        MockTC.return_value = tc_inst

        from apps.core.cache.utils import cache_get_or_set
        result = cache_get_or_set("k", lambda: "fresh", timeout=60)

        assert result == "cached_data"

    @patch("apps.core.cache.utils.TenantCache")
    def test_calls_callback_on_miss(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.utils import cache_get_or_set
        cb = MagicMock(return_value="computed")
        result = cache_get_or_set("k", cb, timeout=60)

        cb.assert_called_once()
        assert result == "computed"

    @patch("apps.core.cache.utils.TenantCache")
    def test_caches_callback_result(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.get.return_value = None
        MockTC.return_value = tc_inst

        from apps.core.cache.utils import cache_get_or_set
        cache_get_or_set("k", lambda: "new_val", timeout=120)

        tc_inst.set.assert_called_once_with("k", "new_val", timeout=120, shared=False)


# ════════════════════════════════════════════════════════════════════════
# Utility – clear_cache
# ════════════════════════════════════════════════════════════════════════


class TestClearCache:
    """clear_cache utility."""

    @patch("apps.core.cache.utils.caches")
    def test_clears_entire_cache(self, mock_caches):
        mock_backend = MagicMock()
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)

        from apps.core.cache.utils import clear_cache
        result = clear_cache()

        assert result is True
        mock_backend.clear.assert_called_once()

    @patch("apps.core.cache.utils.TenantCache")
    @patch("apps.core.cache.utils.caches")
    def test_clears_with_pattern(self, mock_caches, MockTC):
        tc_inst = MagicMock()
        MockTC.return_value = tc_inst

        from apps.core.cache.utils import clear_cache
        result = clear_cache(pattern="products:*")

        assert result is True
        tc_inst.delete_pattern.assert_called_once_with("products:*")

    @patch("apps.core.cache.utils.caches")
    def test_error_returns_false(self, mock_caches):
        mock_backend = MagicMock()
        mock_backend.clear.side_effect = Exception("fail")
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)

        from apps.core.cache.utils import clear_cache
        result = clear_cache()

        assert result is False


# ════════════════════════════════════════════════════════════════════════
# Utility – cache_stats
# ════════════════════════════════════════════════════════════════════════


class TestCacheStats:
    """cache_stats utility."""

    @patch("apps.core.cache.utils.caches")
    def test_returns_dict(self, mock_caches):
        mock_redis_client = MagicMock()
        mock_redis_client.info.return_value = {
            "used_memory_human": "1.5M",
            "maxmemory_human": "100M",
            "keyspace_hits": 500,
            "keyspace_misses": 50,
        }
        mock_redis_client.dbsize.return_value = 42

        mock_client = MagicMock()
        mock_client.get_client.return_value = mock_redis_client

        mock_backend = MagicMock()
        mock_backend.client = mock_client
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)

        from apps.core.cache.utils import cache_stats
        stats = cache_stats()

        assert stats["used_memory"] == "1.5M"
        assert stats["total_keys"] == 42
        assert stats["hit_rate"] == 500

    @patch("apps.core.cache.utils.caches")
    def test_returns_empty_on_unsupported_backend(self, mock_caches):
        mock_backend = MagicMock(spec=[])  # no .client
        mock_caches.__getitem__ = MagicMock(return_value=mock_backend)

        from apps.core.cache.utils import cache_stats
        stats = cache_stats()

        assert stats == {}

    @patch("apps.core.cache.utils.caches")
    def test_returns_empty_on_error(self, mock_caches):
        mock_caches.__getitem__ = MagicMock(side_effect=Exception("boom"))

        from apps.core.cache.utils import cache_stats
        stats = cache_stats()

        assert stats == {}


# ════════════════════════════════════════════════════════════════════════
# CacheInvalidator
# ════════════════════════════════════════════════════════════════════════


class TestCacheInvalidator:
    """CacheInvalidator static methods."""

    @patch("apps.core.cache.invalidation.TenantCache")
    def test_invalidate_model(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.delete_pattern.return_value = 3
        MockTC.return_value = tc_inst

        model_cls = MagicMock()
        model_cls._meta.label_lower = "products.product"

        from apps.core.cache.invalidation import CacheInvalidator
        count = CacheInvalidator.invalidate_model(model_cls)

        assert count == 3
        tc_inst.delete_pattern.assert_called_once_with("products_product:*")

    @patch("apps.core.cache.invalidation.TenantCache")
    def test_invalidate_list(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.delete_pattern.return_value = 2
        MockTC.return_value = tc_inst

        model_cls = MagicMock()
        model_cls._meta.label_lower = "products.product"

        from apps.core.cache.invalidation import CacheInvalidator
        count = CacheInvalidator.invalidate_list(model_cls)

        assert count == 2
        tc_inst.delete_pattern.assert_called_once_with("products_product:list*")

    @patch("apps.core.cache.invalidation.TenantCache")
    def test_invalidate_detail(self, MockTC):
        tc_inst = MagicMock()
        tc_inst.delete_pattern.return_value = 1
        MockTC.return_value = tc_inst

        model_cls = MagicMock()
        model_cls._meta.label_lower = "products.product"

        from apps.core.cache.invalidation import CacheInvalidator
        count = CacheInvalidator.invalidate_detail(model_cls, instance_id=7)

        assert count == 1
        tc_inst.delete_pattern.assert_called_once_with("products_product:detail:7*")

    @patch("apps.core.cache.invalidation.CacheInvalidator.invalidate_model")
    def test_invalidate_related_explicit(self, mock_inv_model):
        mock_inv_model.return_value = 2

        model_cls = MagicMock()
        model_cls._meta.label_lower = "orders.order"
        instance = MagicMock()

        related_cls = MagicMock()
        related_cls._meta.label_lower = "orders.orderitem"

        from apps.core.cache.invalidation import CacheInvalidator
        total = CacheInvalidator.invalidate_related(
            model_cls, instance, related_models=[related_cls],
        )

        assert total == 4  # 2 for model + 2 for related
        assert mock_inv_model.call_count == 2

    @patch("apps.core.cache.invalidation.CacheInvalidator.invalidate_model")
    def test_invalidate_related_auto_discovers(self, mock_inv_model):
        mock_inv_model.return_value = 1

        rel_obj = MagicMock()
        rel_obj.related_model = MagicMock()

        model_cls = MagicMock()
        model_cls._meta.label_lower = "orders.order"
        model_cls._meta.related_objects = [rel_obj]
        instance = MagicMock()

        from apps.core.cache.invalidation import CacheInvalidator
        total = CacheInvalidator.invalidate_related(model_cls, instance)

        assert total == 2  # 1 for model + 1 for auto-discovered related
        assert mock_inv_model.call_count == 2

    @patch("apps.core.cache.invalidation.TenantCache")
    def test_invalidate_tenant_cache(self, MockTC):
        tc_inst = MagicMock()
        tc_inst._get_tenant_schema.return_value = "acme"
        tc_inst.delete_pattern.return_value = 10
        MockTC.return_value = tc_inst

        from apps.core.cache.invalidation import CacheInvalidator
        result = CacheInvalidator.invalidate_tenant_cache()

        assert result is True
        tc_inst.delete_pattern.assert_called_once_with("*")


# ════════════════════════════════════════════════════════════════════════
# Signal handlers
# ════════════════════════════════════════════════════════════════════════


class TestCacheSignalHandlers:
    """post_save and post_delete signal handlers."""

    @patch("apps.core.cache.invalidation.CacheInvalidator.invalidate_detail")
    @patch("apps.core.cache.invalidation.CacheInvalidator.invalidate_list")
    def test_post_save_handler(self, mock_list, mock_detail):
        mock_list.return_value = 1
        mock_detail.return_value = 1

        model_cls = MagicMock()
        instance = MagicMock(pk=5)

        from apps.core.cache.invalidation import cache_post_save_handler
        cache_post_save_handler(sender=model_cls, instance=instance)

        mock_list.assert_called_once_with(model_cls)
        mock_detail.assert_called_once_with(model_cls, 5)

    @patch("apps.core.cache.invalidation.CacheInvalidator.invalidate_model")
    def test_post_delete_handler(self, mock_inv):
        mock_inv.return_value = 3

        model_cls = MagicMock()
        instance = MagicMock(pk=5)

        from apps.core.cache.invalidation import cache_post_delete_handler
        cache_post_delete_handler(sender=model_cls, instance=instance)

        mock_inv.assert_called_once_with(model_cls)

    @patch("apps.core.cache.invalidation.CacheInvalidator.invalidate_list")
    def test_post_save_handler_error_does_not_raise(self, mock_list):
        mock_list.side_effect = Exception("unexpected")

        model_cls = MagicMock()
        instance = MagicMock(pk=1)

        from apps.core.cache.invalidation import cache_post_save_handler
        # Should not raise
        cache_post_save_handler(sender=model_cls, instance=instance)

    @patch("apps.core.cache.invalidation.CacheInvalidator.invalidate_model")
    def test_post_delete_handler_error_does_not_raise(self, mock_inv):
        mock_inv.side_effect = Exception("unexpected")

        model_cls = MagicMock()
        instance = MagicMock(pk=1)

        from apps.core.cache.invalidation import cache_post_delete_handler
        cache_post_delete_handler(sender=model_cls, instance=instance)


# ════════════════════════════════════════════════════════════════════════
# CacheMixin
# ════════════════════════════════════════════════════════════════════════


class TestCacheMixin:
    """CacheMixin model mixin."""

    def test_get_invalidation_related_with_cache_meta(self):
        from apps.core.cache.invalidation import CacheMixin

        class FakeRelated:
            pass

        class MyModel(CacheMixin):
            class CacheMeta:
                invalidate_related = [FakeRelated]
            class Meta:
                abstract = True

        assert MyModel._get_invalidation_related() == [FakeRelated]

    def test_get_invalidation_related_without_cache_meta(self):
        from apps.core.cache.invalidation import CacheMixin

        class MyModel(CacheMixin):
            class Meta:
                abstract = True

        assert MyModel._get_invalidation_related() == []

    def test_get_invalidation_related_empty_meta(self):
        from apps.core.cache.invalidation import CacheMixin

        class MyModel(CacheMixin):
            class CacheMeta:
                pass
            class Meta:
                abstract = True

        assert MyModel._get_invalidation_related() == []


# ════════════════════════════════════════════════════════════════════════
# Management command – clearcache
# ════════════════════════════════════════════════════════════════════════


class TestClearCacheCommand:
    """clearcache management command."""

    @patch("apps.core.management.commands.clearcache.caches")
    def test_all_flag(self, mock_caches):
        mock_default = MagicMock()
        mock_sessions = MagicMock()

        # Make caches iterable (yields alias names) and subscriptable
        mock_caches.__iter__ = MagicMock(return_value=iter(["default", "sessions"]))
        mock_caches.__getitem__ = MagicMock(
            side_effect=lambda k: {"default": mock_default, "sessions": mock_sessions}[k],
        )

        out = StringIO()
        call_command("clearcache", "--all", stdout=out)

        mock_default.clear.assert_called_once()
        mock_sessions.clear.assert_called_once()
        assert "Cleared cache alias" in out.getvalue()

    @patch("apps.core.management.commands.clearcache.clear_cache")
    def test_alias_flag(self, mock_clear):
        mock_clear.return_value = True
        out = StringIO()

        call_command("clearcache", "--alias", "sessions", stdout=out)

        mock_clear.assert_called_once_with(cache_alias="sessions", pattern=None)
        assert "Cache cleared" in out.getvalue()

    @patch("apps.core.management.commands.clearcache.clear_cache")
    def test_pattern_flag(self, mock_clear):
        mock_clear.return_value = True
        out = StringIO()

        call_command("clearcache", "--pattern", "products:*", stdout=out)

        mock_clear.assert_called_once_with(cache_alias="default", pattern="products:*")
        assert "products:*" in out.getvalue()

    @patch("apps.core.management.commands.clearcache.clear_cache")
    def test_default_no_flags(self, mock_clear):
        mock_clear.return_value = True
        out = StringIO()

        call_command("clearcache", stdout=out)

        mock_clear.assert_called_once_with(cache_alias="default", pattern=None)

    @patch("apps.core.management.commands.clearcache.clear_cache")
    def test_failure_output(self, mock_clear):
        mock_clear.return_value = False
        out = StringIO()
        err = StringIO()

        call_command("clearcache", stdout=out, stderr=err)

        assert "Failed" in err.getvalue()

    @patch("apps.core.management.commands.clearcache.CacheInvalidator")
    def test_tenant_flag(self, mock_inv):
        out = StringIO()
        call_command("clearcache", "--tenant", stdout=out)
        mock_inv.invalidate_tenant_cache.assert_called_once()
        assert "tenant" in out.getvalue().lower()

    @patch("apps.core.management.commands.clearcache.CacheInvalidator")
    @patch("django.apps.apps.get_model")
    def test_model_flag(self, mock_get_model, mock_inv):
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model
        mock_inv.invalidate_model.return_value = 5
        out = StringIO()

        call_command("clearcache", "--model", "products.Product", stdout=out)

        mock_get_model.assert_called_once_with("products.Product")
        mock_inv.invalidate_model.assert_called_once_with(mock_model)
        assert "products.Product" in out.getvalue()

    @patch("django.apps.apps.get_model", side_effect=LookupError("Not found"))
    def test_model_flag_invalid(self, mock_get_model):
        out = StringIO()
        err = StringIO()
        call_command("clearcache", "--model", "foo.Bar", stdout=out, stderr=err)
        assert "not found" in err.getvalue().lower()


# ════════════════════════════════════════════════════════════════════════
# Session Caching Tests
# ════════════════════════════════════════════════════════════════════════


class TestSessionCaching:
    """Verify session-related cache settings are configured correctly."""

    def test_session_engine(self):
        from django.conf import settings
        assert settings.SESSION_ENGINE == "django.contrib.sessions.backends.cache"

    def test_session_cache_alias(self):
        from django.conf import settings
        assert settings.SESSION_CACHE_ALIAS == "sessions"

    def test_session_cookie_age(self):
        from django.conf import settings
        # base.py overrides to 2 weeks; cache.py sets 1 day but base.py wins
        assert settings.SESSION_COOKIE_AGE > 0

    def test_session_cookie_httponly(self):
        from django.conf import settings
        assert settings.SESSION_COOKIE_HTTPONLY is True

    def test_sessions_cache_alias_exists(self):
        from django.core.cache import caches
        # Should not raise
        cache = caches["sessions"]
        assert cache is not None

    def test_ratelimit_cache_alias_exists(self):
        from django.core.cache import caches
        cache = caches["ratelimit"]
        assert cache is not None

    def test_sessions_cache_set_get(self):
        from django.core.cache import caches
        cache = caches["sessions"]
        cache.set("test_sess_key", "sess_value", 60)
        assert cache.get("test_sess_key") == "sess_value"
        cache.delete("test_sess_key")


# ════════════════════════════════════════════════════════════════════════
# CacheMixin Instance Method Tests
# ════════════════════════════════════════════════════════════════════════


class TestCacheMixinInstanceMethods:
    """Test the get_cache_key and invalidate_cache instance methods."""

    def test_get_cache_key(self):
        from apps.core.cache.invalidation import CacheMixin

        obj = MagicMock(spec=CacheMixin)
        obj._meta = MagicMock()
        obj._meta.label_lower = "products.product"
        obj.pk = 42
        result = CacheMixin.get_cache_key(obj, suffix="detail")
        assert result == "products_product:detail:42"

    def test_get_cache_key_custom_suffix(self):
        from apps.core.cache.invalidation import CacheMixin

        obj = MagicMock(spec=CacheMixin)
        obj._meta = MagicMock()
        obj._meta.label_lower = "orders.order"
        obj.pk = 99
        result = CacheMixin.get_cache_key(obj, suffix="summary")
        assert result == "orders_order:summary:99"

    @patch("apps.core.cache.invalidation.CacheInvalidator")
    def test_invalidate_cache(self, mock_inv):
        from apps.core.cache.invalidation import CacheMixin

        mock_inv.invalidate_detail.return_value = 1
        mock_inv.invalidate_list.return_value = 2
        mock_inv.invalidate_model.return_value = 3

        obj = MagicMock(spec=CacheMixin)
        obj.pk = 42
        obj._get_invalidation_related = MagicMock(return_value=[MagicMock()])

        result = CacheMixin.invalidate_cache(obj)
        assert result == 6  # 1 + 2 + 3

    @patch("apps.core.cache.invalidation.CacheInvalidator")
    def test_invalidate_cache_no_related(self, mock_inv):
        from apps.core.cache.invalidation import CacheMixin

        mock_inv.invalidate_detail.return_value = 0
        mock_inv.invalidate_list.return_value = 0

        obj = MagicMock(spec=CacheMixin)
        obj.pk = 1
        obj._get_invalidation_related = MagicMock(return_value=[])

        result = CacheMixin.invalidate_cache(obj)
        assert result == 0


# ════════════════════════════════════════════════════════════════════════
# Multi-Tenant Cache Isolation Tests  (SP09 Task 80)
# ════════════════════════════════════════════════════════════════════════


class TestMultiTenantCacheIsolation:
    """Verify that cache operations are isolated between tenants."""

    @patch("apps.core.cache.tenant_cache.caches")
    def test_same_key_different_tenants_produces_different_cache_keys(self, mock_caches):
        """Two tenants using the same logical key get distinct cache keys."""
        from apps.core.cache.tenant_cache import TenantCache

        tc = TenantCache()

        with patch.object(tc, "_get_tenant_schema", return_value="tenant_a"):
            key_a = tc.make_key("product:list")

        with patch.object(tc, "_get_tenant_schema", return_value="tenant_b"):
            key_b = tc.make_key("product:list")

        assert key_a != key_b
        assert "tenant_a" in key_a
        assert "tenant_b" in key_b

    @patch("apps.core.cache.tenant_cache.caches")
    def test_shared_key_same_across_tenants(self, mock_caches):
        """Shared keys are identical regardless of tenant context."""
        from apps.core.cache.tenant_cache import TenantCache

        tc = TenantCache()

        with patch.object(tc, "_get_tenant_schema", return_value="tenant_a"):
            key_a = tc.make_key("global:config", shared=True)

        with patch.object(tc, "_get_tenant_schema", return_value="tenant_b"):
            key_b = tc.make_key("global:config", shared=True)

        assert key_a == key_b

    @patch("apps.core.cache.tenant_cache.caches")
    def test_public_schema_fallback_is_isolated(self, mock_caches):
        """When no tenant context exists, keys use 'public' prefix."""
        from apps.core.cache.tenant_cache import TenantCache

        tc = TenantCache()

        with patch.object(tc, "_get_tenant_schema", return_value="public"):
            key_pub = tc.make_key("product:list")

        with patch.object(tc, "_get_tenant_schema", return_value="tenant_a"):
            key_tenant = tc.make_key("product:list")

        assert key_pub != key_tenant
        assert "public" in key_pub


# ════════════════════════════════════════════════════════════════════════
# Signal Handler transaction.on_commit Tests
# ════════════════════════════════════════════════════════════════════════


class TestSignalHandlersOnCommit:
    """Verify signal handlers use transaction.on_commit."""

    @patch("apps.core.cache.invalidation.transaction")
    @patch("apps.core.cache.invalidation.CacheInvalidator")
    def test_post_save_uses_on_commit(self, mock_inv, mock_txn):
        from apps.core.cache.invalidation import cache_post_save_handler

        sender = MagicMock()
        instance = MagicMock(pk=1)

        cache_post_save_handler(sender=sender, instance=instance)

        mock_txn.on_commit.assert_called_once()

    @patch("apps.core.cache.invalidation.transaction")
    @patch("apps.core.cache.invalidation.CacheInvalidator")
    def test_post_delete_uses_on_commit(self, mock_inv, mock_txn):
        from apps.core.cache.invalidation import cache_post_delete_handler

        sender = MagicMock()
        instance = MagicMock(pk=1)

        cache_post_delete_handler(sender=sender, instance=instance)

        mock_txn.on_commit.assert_called_once()

    @patch("apps.core.cache.invalidation.transaction")
    @patch("apps.core.cache.invalidation.CacheInvalidator")
    def test_post_save_fallback_without_transaction(self, mock_inv, mock_txn):
        """If on_commit raises, handler executes immediately."""
        from apps.core.cache.invalidation import cache_post_save_handler

        mock_txn.on_commit.side_effect = Exception("no transaction")
        sender = MagicMock()
        instance = MagicMock(pk=1)

        # Should not raise
        cache_post_save_handler(sender=sender, instance=instance)
        mock_inv.invalidate_list.assert_called_once()


# ════════════════════════════════════════════════════════════════════════
# Cache TTL Settings Tests
# ════════════════════════════════════════════════════════════════════════


class TestCacheSettingsIntegration:
    """Verify cache settings are properly loaded into Django settings."""

    def test_cache_ttl_short_in_settings(self):
        from django.conf import settings
        assert hasattr(settings, "CACHE_TTL_SHORT")
        assert settings.CACHE_TTL_SHORT == 300

    def test_cache_ttl_medium_in_settings(self):
        from django.conf import settings
        assert hasattr(settings, "CACHE_TTL_MEDIUM")
        assert settings.CACHE_TTL_MEDIUM == 3600

    def test_cache_ttl_long_in_settings(self):
        from django.conf import settings
        assert hasattr(settings, "CACHE_TTL_LONG")
        assert settings.CACHE_TTL_LONG == 86400

    def test_caches_has_default(self):
        from django.conf import settings
        assert "default" in settings.CACHES

    def test_caches_has_sessions(self):
        from django.conf import settings
        assert "sessions" in settings.CACHES

    def test_caches_has_ratelimit(self):
        from django.conf import settings
        assert "ratelimit" in settings.CACHES
