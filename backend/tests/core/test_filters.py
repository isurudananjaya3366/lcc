"""
Tests for ``apps.core.filters`` — Group B Filter Backends (SP12).

Covers:
    * TenantFilterBackend
    * DateRangeFilterBackend
    * LCCSearchFilter
    * LCCOrderingFilter
    * IsActiveFilterBackend
    * CreatedByFilterBackend
    * ModifiedAtFilterBackend
    * BaseFilterSet

All tests use mocks / in-memory objects — no real database access required.
"""

from __future__ import annotations

import uuid
from collections import namedtuple
from datetime import date, datetime, time, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from django.utils import timezone
from rest_framework.filters import BaseFilterBackend
from rest_framework.filters import OrderingFilter as DRFOrderingFilter
from rest_framework.filters import SearchFilter as DRFSearchFilter

from apps.core.filters import (
    BaseFilterSet,
    CreatedByFilterBackend,
    DateRangeFilterBackend,
    IsActiveFilterBackend,
    LCCOrderingFilter,
    LCCSearchFilter,
    ModifiedAtFilterBackend,
    TenantFilterBackend,
)
from apps.core.filters.backends import _FALSY, _TRUTHY


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════


def _make_request(query_params: dict | None = None, user=None):
    """Return a lightweight mock DRF request."""
    request = MagicMock()
    request.query_params = query_params or {}
    if user is not None:
        request.user = user
    else:
        request.user = MagicMock(is_authenticated=True, pk=1)
    return request


def _make_view(**attrs):
    """Return a SimpleNamespace acting as a DRF view."""
    return SimpleNamespace(**attrs)


def _make_queryset(model=None, items=None):
    """
    Return a chainable mock queryset.

    The mock supports ``.filter()``, ``.none()``, and ``.model``.
    Each ``.filter()`` call returns a new mock so assertions can be
    stacked independently.
    """
    qs = MagicMock()
    if model is not None:
        qs.model = model
    else:
        qs.model = MagicMock()
    # .filter() returns itself by default for chaining.
    qs.filter.return_value = qs
    qs.none.return_value = MagicMock(spec=[])  # empty-ish queryset
    return qs


def _make_model_class(*field_names: str):
    """Create a mock model class whose ``_meta.get_field`` knows about *field_names*."""
    model = MagicMock()
    known = set(field_names)

    def _get_field(name):
        if name in known:
            return MagicMock()
        raise Exception(f"No field named '{name}'")  # noqa: TRY002

    model._meta.get_field = _get_field
    # Also set attribute-level flags for hasattr() checks.
    for fn in field_names:
        setattr(model, fn, True)
    return model


# ════════════════════════════════════════════════════════════════════════
# TenantFilterBackend
# ════════════════════════════════════════════════════════════════════════


class TestTenantFilterBackend:
    """Tests for TenantFilterBackend."""

    def setup_method(self):
        self.backend = TenantFilterBackend()

    @patch("apps.core.filters.backends.connection")
    def test_filters_by_tenant(self, mock_conn):
        """Queryset should be filtered by connection.tenant."""
        tenant = MagicMock(pk=42, schema_name="tenant_acme")
        mock_conn.tenant = tenant

        model = _make_model_class("tenant")
        qs = _make_queryset(model=model)
        view = _make_view()

        result = self.backend.filter_queryset(_make_request(), qs, view)
        qs.filter.assert_called_once_with(tenant=tenant)

    @patch("apps.core.filters.backends.connection")
    def test_no_tenant_returns_empty(self, mock_conn):
        """When no tenant on connection, return empty queryset."""
        mock_conn.tenant = None

        qs = _make_queryset()
        result = self.backend.filter_queryset(_make_request(), qs, _make_view())
        qs.none.assert_called_once()

    @patch("apps.core.filters.backends.connection")
    def test_model_without_tenant_field_skips(self, mock_conn):
        """If the model has no 'tenant' field, return queryset unfiltered."""
        mock_conn.tenant = MagicMock()
        model = _make_model_class()  # no tenant field
        qs = _make_queryset(model=model)

        result = self.backend.filter_queryset(_make_request(), qs, _make_view())
        qs.filter.assert_not_called()
        assert result is qs

    @patch("apps.core.filters.backends.connection")
    def test_custom_tenant_field_from_view(self, mock_conn):
        """View's tenant_filter_field should override default."""
        tenant = MagicMock()
        mock_conn.tenant = tenant
        model = _make_model_class("organisation")
        qs = _make_queryset(model=model)
        view = _make_view(tenant_filter_field="organisation")

        self.backend.filter_queryset(_make_request(), qs, view)
        qs.filter.assert_called_once_with(organisation=tenant)

    @patch("apps.core.filters.backends.connection")
    def test_inherits_base_filter_backend(self, mock_conn):
        """Must inherit from DRF's BaseFilterBackend."""
        assert isinstance(self.backend, BaseFilterBackend)

    @patch("apps.core.filters.backends.connection")
    def test_logs_warning_when_no_tenant(self, mock_conn):
        """Should log a warning when tenant is missing."""
        mock_conn.tenant = None
        qs = _make_queryset()

        with patch("apps.core.filters.backends.logger") as mock_logger:
            self.backend.filter_queryset(_make_request(), qs, _make_view())
            mock_logger.warning.assert_called_once()


# ════════════════════════════════════════════════════════════════════════
# DateRangeFilterBackend
# ════════════════════════════════════════════════════════════════════════


class TestDateRangeFilterBackend:
    """Tests for DateRangeFilterBackend."""

    def setup_method(self):
        self.backend = DateRangeFilterBackend()

    def test_no_params_returns_unfiltered(self):
        qs = _make_queryset()
        result = self.backend.filter_queryset(_make_request(), qs, _make_view())
        qs.filter.assert_not_called()
        assert result is qs

    def test_date_from_only(self):
        qs = _make_queryset()
        request = _make_request({"date_from": "2026-01-01"})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once()
        call_kwargs = qs.filter.call_args[1]
        assert "created_on__gte" in call_kwargs

    def test_date_to_only(self):
        qs = _make_queryset()
        request = _make_request({"date_to": "2026-01-31"})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once()
        call_kwargs = qs.filter.call_args[1]
        assert "created_on__lte" in call_kwargs

    def test_both_date_from_and_date_to(self):
        qs = _make_queryset()
        # .filter() returns itself, so chained calls work.
        qs.filter.return_value = qs
        request = _make_request({"date_from": "2026-01-01", "date_to": "2026-01-31"})
        self.backend.filter_queryset(request, qs, _make_view())
        assert qs.filter.call_count == 2

    def test_custom_date_field_from_view(self):
        qs = _make_queryset()
        request = _make_request({"date_from": "2026-06-01"})
        view = _make_view(date_filter_field="order_date")
        self.backend.filter_queryset(request, qs, view)
        call_kwargs = qs.filter.call_args[1]
        assert "order_date__gte" in call_kwargs

    def test_invalid_date_from_ignored(self):
        qs = _make_queryset()
        request = _make_request({"date_from": "not-a-date"})
        result = self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()
        assert result is qs

    def test_invalid_date_to_ignored(self):
        qs = _make_queryset()
        request = _make_request({"date_to": "xyz"})
        result = self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()

    def test_date_from_is_start_of_day(self):
        """date_from value should be start of day (00:00:00)."""
        qs = _make_queryset()
        request = _make_request({"date_from": "2026-03-11"})
        self.backend.filter_queryset(request, qs, _make_view())
        dt = qs.filter.call_args[1]["created_on__gte"]
        assert dt.hour == 0 and dt.minute == 0 and dt.second == 0

    def test_date_to_is_end_of_day(self):
        """date_to value should be end of day (23:59:59.999999)."""
        qs = _make_queryset()
        request = _make_request({"date_to": "2026-03-11"})
        self.backend.filter_queryset(request, qs, _make_view())
        dt = qs.filter.call_args[1]["created_on__lte"]
        assert dt.hour == 23 and dt.minute == 59

    def test_default_field_is_created_on(self):
        assert self.backend.default_field == "created_on"

    def test_parse_date_none(self):
        assert DateRangeFilterBackend._parse_date(None) is None

    def test_parse_date_empty(self):
        assert DateRangeFilterBackend._parse_date("") is None

    def test_parse_date_valid(self):
        assert DateRangeFilterBackend._parse_date("2026-01-15") == date(2026, 1, 15)

    def test_parse_date_invalid(self):
        assert DateRangeFilterBackend._parse_date("31-01-2026") is None

    def test_inherits_base_filter_backend(self):
        assert isinstance(self.backend, BaseFilterBackend)


# ════════════════════════════════════════════════════════════════════════
# LCCSearchFilter
# ════════════════════════════════════════════════════════════════════════


class TestLCCSearchFilter:
    """Tests for LCCSearchFilter."""

    def setup_method(self):
        self.backend = LCCSearchFilter()

    def test_inherits_drf_search_filter(self):
        assert isinstance(self.backend, DRFSearchFilter)

    def test_search_param_is_search(self):
        assert self.backend.search_param == "search"

    def test_is_instance_of_base_filter_backend(self):
        assert isinstance(self.backend, BaseFilterBackend)

    def test_has_filter_queryset_method(self):
        assert callable(getattr(self.backend, "filter_queryset", None))

    def test_get_search_fields_returns_none_without_view_attr(self):
        """If view has no search_fields, get_search_fields returns None."""
        view = _make_view()
        # DRF's get_search_fields will return None if view doesn't define it
        result = self.backend.get_search_fields(view, _make_request())
        assert result is None

    def test_get_search_fields_returns_view_fields(self):
        view = _make_view(search_fields=["name", "^sku"])
        result = self.backend.get_search_fields(view, _make_request())
        assert result == ["name", "^sku"]


# ════════════════════════════════════════════════════════════════════════
# LCCOrderingFilter
# ════════════════════════════════════════════════════════════════════════


class TestLCCOrderingFilter:
    """Tests for LCCOrderingFilter."""

    def setup_method(self):
        self.backend = LCCOrderingFilter()

    def test_inherits_drf_ordering_filter(self):
        assert isinstance(self.backend, DRFOrderingFilter)

    def test_ordering_param_is_ordering(self):
        assert self.backend.ordering_param == "ordering"

    def test_is_instance_of_base_filter_backend(self):
        assert isinstance(self.backend, BaseFilterBackend)

    def test_has_filter_queryset_method(self):
        assert callable(getattr(self.backend, "filter_queryset", None))

    def test_get_default_ordering_returns_view_ordering(self):
        view = _make_view(ordering=["-created_on"])
        result = self.backend.get_default_ordering(view)
        assert result == ["-created_on"]

    def test_get_default_ordering_returns_none_without_attr(self):
        view = _make_view()
        result = self.backend.get_default_ordering(view)
        assert result is None


# ════════════════════════════════════════════════════════════════════════
# IsActiveFilterBackend
# ════════════════════════════════════════════════════════════════════════


class TestIsActiveFilterBackend:
    """Tests for IsActiveFilterBackend."""

    def setup_method(self):
        self.backend = IsActiveFilterBackend()

    def test_no_param_returns_unfiltered(self):
        qs = _make_queryset()
        result = self.backend.filter_queryset(_make_request(), qs, _make_view())
        qs.filter.assert_not_called()
        assert result is qs

    @pytest.mark.parametrize("value", ["true", "True", "TRUE", "1", "yes", "Yes"])
    def test_truthy_values(self, value):
        model = _make_model_class("is_active")
        qs = _make_queryset(model=model)
        request = _make_request({"is_active": value})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once_with(is_active=True)

    @pytest.mark.parametrize("value", ["false", "False", "FALSE", "0", "no", "No"])
    def test_falsy_values(self, value):
        model = _make_model_class("is_active")
        qs = _make_queryset(model=model)
        request = _make_request({"is_active": value})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once_with(is_active=False)

    def test_invalid_value_returns_unfiltered(self):
        model = _make_model_class("is_active")
        qs = _make_queryset(model=model)
        request = _make_request({"is_active": "maybe"})
        result = self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()
        assert result is qs

    def test_model_without_is_active_skips(self):
        model = MagicMock(spec=[])  # No is_active attribute
        qs = _make_queryset(model=model)
        request = _make_request({"is_active": "true"})
        result = self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()

    def test_inherits_base_filter_backend(self):
        assert isinstance(self.backend, BaseFilterBackend)

    def test_whitespace_in_param(self):
        """Leading/trailing whitespace should be stripped."""
        model = _make_model_class("is_active")
        qs = _make_queryset(model=model)
        request = _make_request({"is_active": "  true  "})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once_with(is_active=True)


# ════════════════════════════════════════════════════════════════════════
# CreatedByFilterBackend
# ════════════════════════════════════════════════════════════════════════


class TestCreatedByFilterBackend:
    """Tests for CreatedByFilterBackend."""

    def setup_method(self):
        self.backend = CreatedByFilterBackend()

    def test_no_param_returns_unfiltered(self):
        qs = _make_queryset()
        result = self.backend.filter_queryset(_make_request(), qs, _make_view())
        qs.filter.assert_not_called()
        assert result is qs

    def test_created_by_me_authenticated(self):
        user = MagicMock(is_authenticated=True, pk=7)
        model = _make_model_class("created_by")
        qs = _make_queryset(model=model)
        request = _make_request({"created_by": "me"}, user=user)
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once_with(created_by=user)

    def test_created_by_me_case_insensitive(self):
        user = MagicMock(is_authenticated=True, pk=7)
        model = _make_model_class("created_by")
        qs = _make_queryset(model=model)
        request = _make_request({"created_by": "ME"}, user=user)
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once_with(created_by=user)

    def test_created_by_me_anonymous_returns_empty(self):
        user = MagicMock(is_authenticated=False)
        model = _make_model_class("created_by")
        qs = _make_queryset(model=model)
        request = _make_request({"created_by": "me"}, user=user)
        result = self.backend.filter_queryset(request, qs, _make_view())
        qs.none.assert_called_once()

    def test_created_by_user_id(self):
        model = _make_model_class("created_by")
        qs = _make_queryset(model=model)
        request = _make_request({"created_by": "42"})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once_with(created_by_id=42)

    def test_created_by_invalid_id_passes_through(self):
        """Non-integer, non-'me' value is passed as a string PK (e.g. UUID)."""
        model = _make_model_class("created_by")
        qs = _make_queryset(model=model)
        request = _make_request({"created_by": "abc-uuid"})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once_with(created_by_id="abc-uuid")

    def test_model_without_created_by_skips(self):
        model = MagicMock(spec=[])  # No created_by
        qs = _make_queryset(model=model)
        request = _make_request({"created_by": "me"})
        result = self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()

    def test_inherits_base_filter_backend(self):
        assert isinstance(self.backend, BaseFilterBackend)

    def test_created_by_me_with_whitespace(self):
        user = MagicMock(is_authenticated=True, pk=7)
        model = _make_model_class("created_by")
        qs = _make_queryset(model=model)
        request = _make_request({"created_by": "  Me  "}, user=user)
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once_with(created_by=user)

    def test_created_by_none_user(self):
        """If request.user is None for 'me', return empty."""
        model = _make_model_class("created_by")
        qs = _make_queryset(model=model)
        request = _make_request({"created_by": "me"})
        request.user = None
        result = self.backend.filter_queryset(request, qs, _make_view())
        qs.none.assert_called_once()


# ════════════════════════════════════════════════════════════════════════
# ModifiedAtFilterBackend
# ════════════════════════════════════════════════════════════════════════


class TestModifiedAtFilterBackend:
    """Tests for ModifiedAtFilterBackend."""

    def setup_method(self):
        self.backend = ModifiedAtFilterBackend()

    def test_no_params_returns_unfiltered(self):
        qs = _make_queryset()
        result = self.backend.filter_queryset(_make_request(), qs, _make_view())
        qs.filter.assert_not_called()
        assert result is qs

    def test_modified_after_only(self):
        qs = _make_queryset()
        request = _make_request({"modified_after": "2026-02-01"})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once()
        assert "updated_on__gte" in qs.filter.call_args[1]

    def test_modified_before_only(self):
        qs = _make_queryset()
        request = _make_request({"modified_before": "2026-02-28"})
        self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_called_once()
        assert "updated_on__lte" in qs.filter.call_args[1]

    def test_both_modified_params(self):
        qs = _make_queryset()
        qs.filter.return_value = qs
        request = _make_request({
            "modified_after": "2026-02-01",
            "modified_before": "2026-02-28",
        })
        self.backend.filter_queryset(request, qs, _make_view())
        assert qs.filter.call_count == 2

    def test_invalid_date_ignored(self):
        qs = _make_queryset()
        request = _make_request({"modified_after": "nope"})
        result = self.backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()

    def test_custom_field_from_view(self):
        qs = _make_queryset()
        request = _make_request({"modified_after": "2026-01-01"})
        view = _make_view(modified_filter_field="last_change")
        self.backend.filter_queryset(request, qs, view)
        assert "last_change__gte" in qs.filter.call_args[1]

    def test_default_field_is_updated_on(self):
        assert self.backend.default_field == "updated_on"

    def test_inherits_base_filter_backend(self):
        assert isinstance(self.backend, BaseFilterBackend)

    def test_parse_date_none(self):
        assert ModifiedAtFilterBackend._parse_date(None) is None

    def test_parse_date_valid(self):
        assert ModifiedAtFilterBackend._parse_date("2026-06-15") == date(2026, 6, 15)

    def test_parse_date_invalid(self):
        assert ModifiedAtFilterBackend._parse_date("15/06/2026") is None

    def test_modified_after_is_start_of_day(self):
        qs = _make_queryset()
        request = _make_request({"modified_after": "2026-03-11"})
        self.backend.filter_queryset(request, qs, _make_view())
        dt = qs.filter.call_args[1]["updated_on__gte"]
        assert dt.hour == 0 and dt.minute == 0

    def test_modified_before_is_end_of_day(self):
        qs = _make_queryset()
        request = _make_request({"modified_before": "2026-03-11"})
        self.backend.filter_queryset(request, qs, _make_view())
        dt = qs.filter.call_args[1]["updated_on__lte"]
        assert dt.hour == 23 and dt.minute == 59


# ════════════════════════════════════════════════════════════════════════
# BaseFilterSet
# ════════════════════════════════════════════════════════════════════════


class TestBaseFilterSet:
    """Tests for BaseFilterSet."""

    def test_inherits_from_filterset(self):
        from django_filters import FilterSet
        assert issubclass(BaseFilterSet, FilterSet)

    def test_has_is_active_filter(self):
        assert "is_active" in BaseFilterSet.declared_filters

    def test_has_created_after_filter(self):
        assert "created_after" in BaseFilterSet.declared_filters

    def test_has_created_before_filter(self):
        assert "created_before" in BaseFilterSet.declared_filters

    def test_has_modified_after_filter(self):
        assert "modified_after" in BaseFilterSet.declared_filters

    def test_has_modified_before_filter(self):
        assert "modified_before" in BaseFilterSet.declared_filters

    def test_is_active_field_name(self):
        f = BaseFilterSet.declared_filters["is_active"]
        assert f.field_name == "is_active"

    def test_created_after_uses_created_on(self):
        f = BaseFilterSet.declared_filters["created_after"]
        assert f.field_name == "created_on"
        assert f.lookup_expr == "gte"

    def test_created_before_uses_created_on(self):
        f = BaseFilterSet.declared_filters["created_before"]
        assert f.field_name == "created_on"
        assert f.lookup_expr == "lte"

    def test_modified_after_uses_updated_on(self):
        f = BaseFilterSet.declared_filters["modified_after"]
        assert f.field_name == "updated_on"
        assert f.lookup_expr == "gte"

    def test_modified_before_uses_updated_on(self):
        f = BaseFilterSet.declared_filters["modified_before"]
        assert f.field_name == "updated_on"
        assert f.lookup_expr == "lte"

    def test_declared_filters_count(self):
        """BaseFilterSet should declare exactly 5 common filters."""
        assert len(BaseFilterSet.declared_filters) == 5

    def test_meta_fields_empty(self):
        """Meta.fields should be empty (abstract base)."""
        assert BaseFilterSet.Meta.fields == []


# ════════════════════════════════════════════════════════════════════════
# Module-level / import / __all__ tests
# ════════════════════════════════════════════════════════════════════════


class TestModuleExports:
    """Verify that the public API surface is correct."""

    def test_all_backends_importable(self):
        from apps.core.filters import (
            CreatedByFilterBackend,
            DateRangeFilterBackend,
            IsActiveFilterBackend,
            LCCOrderingFilter,
            LCCSearchFilter,
            ModifiedAtFilterBackend,
            TenantFilterBackend,
        )
        assert TenantFilterBackend is not None
        assert DateRangeFilterBackend is not None
        assert LCCSearchFilter is not None
        assert LCCOrderingFilter is not None
        assert IsActiveFilterBackend is not None
        assert CreatedByFilterBackend is not None
        assert ModifiedAtFilterBackend is not None

    def test_base_filterset_importable(self):
        from apps.core.filters import BaseFilterSet
        assert BaseFilterSet is not None

    def test_all_list_contains_all_exports(self):
        import apps.core.filters as mod
        expected = {
            "TenantFilterBackend",
            "DateRangeFilterBackend",
            "LCCSearchFilter",
            "LCCOrderingFilter",
            "IsActiveFilterBackend",
            "CreatedByFilterBackend",
            "ModifiedAtFilterBackend",
            "BaseFilterSet",
        }
        assert set(mod.__all__) == expected

    def test_version_defined(self):
        import apps.core.filters as mod
        assert hasattr(mod, "__version__")
        assert mod.__version__ == "1.0.0"


# ════════════════════════════════════════════════════════════════════════
# Edge cases & integration-style scenarios
# ════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Miscellaneous edge-case tests."""

    def test_truthy_set_contents(self):
        assert _TRUTHY == frozenset({"true", "1", "yes"})

    def test_falsy_set_contents(self):
        assert _FALSY == frozenset({"false", "0", "no"})

    @patch("apps.core.filters.backends.connection")
    def test_tenant_filter_with_none_connection_attr(self, mock_conn):
        """connection object without .tenant attribute should be safe."""
        del mock_conn.tenant  # simulate missing attribute
        qs = _make_queryset()
        backend = TenantFilterBackend()
        result = backend.filter_queryset(_make_request(), qs, _make_view())
        qs.none.assert_called_once()

    def test_date_range_empty_string_params(self):
        qs = _make_queryset()
        request = _make_request({"date_from": "", "date_to": ""})
        backend = DateRangeFilterBackend()
        result = backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()

    def test_is_active_empty_string_ignored(self):
        """Empty string for is_active should not match truthy/falsy."""
        qs = _make_queryset()
        request = _make_request({"is_active": ""})
        backend = IsActiveFilterBackend()
        result = backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()

    def test_created_by_empty_string_returns_unfiltered(self):
        qs = _make_queryset()
        request = _make_request({"created_by": ""})
        backend = CreatedByFilterBackend()
        result = backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()

    def test_modified_at_empty_string_params(self):
        qs = _make_queryset()
        request = _make_request({"modified_after": "", "modified_before": ""})
        backend = ModifiedAtFilterBackend()
        result = backend.filter_queryset(request, qs, _make_view())
        qs.filter.assert_not_called()

    def test_multiple_backends_can_be_chained(self):
        """Ensure backends can be instantiated and called in sequence."""
        backends = [
            IsActiveFilterBackend(),
            DateRangeFilterBackend(),
            ModifiedAtFilterBackend(),
        ]
        qs = _make_queryset(model=_make_model_class("is_active"))
        request = _make_request({"is_active": "true", "date_from": "2026-01-01"})
        view = _make_view()
        for b in backends:
            qs = b.filter_queryset(request, qs, view)
        # At least is_active and date_from should have caused filter calls.
        # (The mock returns itself, so chaining works.)

    def test_search_filter_class_name(self):
        assert LCCSearchFilter.__name__ == "LCCSearchFilter"

    def test_ordering_filter_class_name(self):
        assert LCCOrderingFilter.__name__ == "LCCOrderingFilter"
