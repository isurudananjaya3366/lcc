"""
Comprehensive tests for the ``apps.core.pagination`` module.

All tests are database-free — they use ``RequestFactory``, mocks,
and plain Python objects so they can run in the *unit* test suite.
"""

import math
from collections import OrderedDict
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from rest_framework.pagination import (
    CursorPagination,
    LimitOffsetPagination,
    PageNumberPagination,
)
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.core.pagination import (
    LCCCursorPagination,
    LCCLimitOffsetPagination,
    NoPagination,
    StandardPagination,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

factory = APIRequestFactory()


def _drf_request(path: str = "/api/items/", query: str = "") -> Request:
    """Return a DRF ``Request`` wrapping a Django test request."""
    url = f"{path}?{query}" if query else path
    return Request(factory.get(url))


def _make_page(
    items: list,
    total: int,
    page_number: int,
    per_page: int,
):
    """
    Build a mock ``Page`` object that looks like what Django's Paginator
    produces.  This lets us test ``get_paginated_response`` without hitting
    the database.
    """
    num_pages = math.ceil(total / per_page) if per_page else 1

    paginator = MagicMock()
    paginator.count = total
    paginator.num_pages = num_pages
    paginator.per_page = per_page

    page = MagicMock()
    page.paginator = paginator
    page.number = page_number
    page.object_list = items
    page.has_next.return_value = page_number < num_pages
    page.has_previous.return_value = page_number > 1
    page.next_page_number.return_value = page_number + 1
    page.previous_page_number.return_value = page_number - 1
    return page


# ═══════════════════════════════════════════════════════════════════════
# StandardPagination
# ═══════════════════════════════════════════════════════════════════════


class TestStandardPaginationAttributes:
    """Verify class-level configuration."""

    def test_inherits_page_number_pagination(self):
        assert issubclass(StandardPagination, PageNumberPagination)

    def test_page_size_is_20(self):
        assert StandardPagination.page_size == 20

    def test_max_page_size_is_100(self):
        assert StandardPagination.max_page_size == 100

    def test_page_size_query_param(self):
        assert StandardPagination.page_size_query_param == "page_size"

    def test_instance_page_size(self):
        p = StandardPagination()
        assert p.page_size == 20

    def test_instance_max_page_size(self):
        p = StandardPagination()
        assert p.max_page_size == 100

    def test_instance_page_size_query_param(self):
        p = StandardPagination()
        assert p.page_size_query_param == "page_size"


class TestStandardPaginationResponse:
    """Test the enhanced ``get_paginated_response`` output."""

    def _response_data(self, items, total, page_number, per_page):
        paginator = StandardPagination()
        paginator.page = _make_page(items, total, page_number, per_page)
        paginator.request = _drf_request()
        resp = paginator.get_paginated_response(items)
        return resp.data

    def test_response_contains_count(self):
        data = self._response_data(list(range(20)), 150, 1, 20)
        assert data["count"] == 150

    def test_response_contains_total_pages(self):
        data = self._response_data(list(range(20)), 150, 1, 20)
        assert data["total_pages"] == 8

    def test_response_contains_current_page(self):
        data = self._response_data(list(range(20)), 150, 3, 20)
        assert data["current_page"] == 3

    def test_response_contains_page_size(self):
        data = self._response_data(list(range(20)), 150, 1, 20)
        assert data["page_size"] == 20

    def test_response_contains_results(self):
        items = [{"id": i} for i in range(5)]
        data = self._response_data(items, 5, 1, 20)
        assert data["results"] == items

    def test_response_keys(self):
        data = self._response_data([], 0, 1, 20)
        expected_keys = {
            "count",
            "next",
            "previous",
            "total_pages",
            "current_page",
            "page_size",
            "results",
        }
        assert set(data.keys()) == expected_keys

    def test_single_page_total_pages_is_one(self):
        data = self._response_data(list(range(5)), 5, 1, 20)
        assert data["total_pages"] == 1

    def test_exact_pages(self):
        """100 items / 20 per page = exactly 5 pages."""
        data = self._response_data(list(range(20)), 100, 1, 20)
        assert data["total_pages"] == 5

    def test_partial_last_page(self):
        """95 items / 20 per page = 5 pages (last page has 15 items)."""
        data = self._response_data(list(range(15)), 95, 5, 20)
        assert data["total_pages"] == 5
        assert data["current_page"] == 5

    def test_empty_queryset_count_zero(self):
        data = self._response_data([], 0, 1, 20)
        assert data["count"] == 0
        assert data["results"] == []

    def test_empty_queryset_total_pages(self):
        data = self._response_data([], 0, 1, 20)
        # math.ceil(0/20) = 0 but Django Paginator returns at least 1 page
        # Our mock uses math.ceil so it will be 0; real Django gives 1.
        assert data["total_pages"] in (0, 1)

    def test_custom_page_size_in_response(self):
        """When a client requests page_size=50, the response reflects it."""
        data = self._response_data(list(range(50)), 200, 1, 50)
        assert data["page_size"] == 50
        assert data["total_pages"] == 4

    def test_response_is_ordered_dict(self):
        """Keys should follow a predictable insertion order."""
        paginator = StandardPagination()
        paginator.page = _make_page([], 0, 1, 20)
        paginator.request = _drf_request()
        resp = paginator.get_paginated_response([])
        assert isinstance(resp.data, OrderedDict)


class TestStandardPaginationSchema:
    """Verify OpenAPI schema helper."""

    def test_get_paginated_response_schema_keys(self):
        p = StandardPagination()
        schema = p.get_paginated_response_schema({"type": "array", "items": {}})
        props = schema["properties"]
        for key in (
            "count",
            "next",
            "previous",
            "total_pages",
            "current_page",
            "page_size",
            "results",
        ):
            assert key in props, f"Missing key: {key}"

    def test_schema_type_is_object(self):
        p = StandardPagination()
        schema = p.get_paginated_response_schema({"type": "array", "items": {}})
        assert schema["type"] == "object"


# ═══════════════════════════════════════════════════════════════════════
# LCCCursorPagination
# ═══════════════════════════════════════════════════════════════════════


class TestCursorPaginationAttributes:
    """Verify class-level configuration."""

    def test_inherits_cursor_pagination(self):
        assert issubclass(LCCCursorPagination, CursorPagination)

    def test_page_size_is_20(self):
        assert LCCCursorPagination.page_size == 20

    def test_ordering_is_created_on_desc(self):
        assert LCCCursorPagination.ordering == "-created_on"

    def test_cursor_query_param(self):
        assert LCCCursorPagination.cursor_query_param == "cursor"

    def test_instance_page_size(self):
        p = LCCCursorPagination()
        assert p.page_size == 20

    def test_instance_ordering(self):
        p = LCCCursorPagination()
        assert p.ordering == "-created_on"

    def test_ordering_field_not_created_at(self):
        """Project convention is ``created_on``, not ``created_at``."""
        assert "created_at" not in LCCCursorPagination.ordering


# ═══════════════════════════════════════════════════════════════════════
# LCCLimitOffsetPagination
# ═══════════════════════════════════════════════════════════════════════


class TestLimitOffsetPaginationAttributes:
    """Verify class-level configuration."""

    def test_inherits_limit_offset_pagination(self):
        assert issubclass(LCCLimitOffsetPagination, LimitOffsetPagination)

    def test_default_limit_is_20(self):
        assert LCCLimitOffsetPagination.default_limit == 20

    def test_max_limit_is_100(self):
        assert LCCLimitOffsetPagination.max_limit == 100

    def test_instance_default_limit(self):
        p = LCCLimitOffsetPagination()
        assert p.default_limit == 20

    def test_instance_max_limit(self):
        p = LCCLimitOffsetPagination()
        assert p.max_limit == 100


class TestLimitOffsetPaginationResponse:
    """Test the enhanced ``get_paginated_response`` output."""

    def _response_data(self, items, total, limit, offset):
        paginator = LCCLimitOffsetPagination()
        paginator.count = total
        paginator.limit = limit
        paginator.offset = offset
        paginator.request = _drf_request()
        resp = paginator.get_paginated_response(items)
        return resp.data

    def test_response_contains_count(self):
        data = self._response_data(list(range(20)), 150, 20, 0)
        assert data["count"] == 150

    def test_response_contains_limit(self):
        data = self._response_data(list(range(20)), 150, 20, 0)
        assert data["limit"] == 20

    def test_response_contains_offset(self):
        data = self._response_data(list(range(20)), 150, 20, 40)
        assert data["offset"] == 40

    def test_response_contains_results(self):
        items = [{"id": i} for i in range(5)]
        data = self._response_data(items, 5, 20, 0)
        assert data["results"] == items

    def test_response_keys(self):
        data = self._response_data([], 0, 20, 0)
        expected_keys = {"count", "next", "previous", "limit", "offset", "results"}
        assert set(data.keys()) == expected_keys

    def test_empty_queryset(self):
        data = self._response_data([], 0, 20, 0)
        assert data["count"] == 0
        assert data["results"] == []

    def test_single_item(self):
        data = self._response_data([{"id": 1}], 1, 20, 0)
        assert data["count"] == 1
        assert len(data["results"]) == 1

    def test_custom_limit_reflected(self):
        data = self._response_data(list(range(50)), 200, 50, 0)
        assert data["limit"] == 50

    def test_offset_mid_dataset(self):
        data = self._response_data(list(range(20)), 200, 20, 100)
        assert data["offset"] == 100

    def test_response_is_ordered_dict(self):
        paginator = LCCLimitOffsetPagination()
        paginator.count = 0
        paginator.limit = 20
        paginator.offset = 0
        paginator.request = _drf_request()
        resp = paginator.get_paginated_response([])
        assert isinstance(resp.data, OrderedDict)


class TestLimitOffsetPaginationSchema:
    """Verify OpenAPI schema helper."""

    def test_schema_keys(self):
        p = LCCLimitOffsetPagination()
        schema = p.get_paginated_response_schema({"type": "array", "items": {}})
        props = schema["properties"]
        for key in ("count", "next", "previous", "limit", "offset", "results"):
            assert key in props, f"Missing key: {key}"


# ═══════════════════════════════════════════════════════════════════════
# NoPagination
# ═══════════════════════════════════════════════════════════════════════


class TestNoPaginationAttributes:
    """Verify class structure."""

    def test_has_paginate_queryset_method(self):
        assert hasattr(NoPagination, "paginate_queryset")

    def test_has_get_paginated_response_method(self):
        assert hasattr(NoPagination, "get_paginated_response")

    def test_is_not_subclass_of_page_number(self):
        assert not issubclass(NoPagination, PageNumberPagination)


class TestNoPaginationBehavior:
    """Test that NoPagination disables all pagination."""

    def test_paginate_queryset_returns_none(self):
        p = NoPagination()
        request = _drf_request()
        result = p.paginate_queryset([1, 2, 3], request)
        assert result is None

    def test_paginate_queryset_with_empty_list(self):
        p = NoPagination()
        request = _drf_request()
        result = p.paginate_queryset([], request)
        assert result is None

    def test_paginate_queryset_with_large_list(self):
        p = NoPagination()
        request = _drf_request()
        result = p.paginate_queryset(list(range(1000)), request)
        assert result is None

    def test_get_paginated_response_returns_data(self):
        p = NoPagination()
        items = [{"id": 1}, {"id": 2}]
        resp = p.get_paginated_response(items)
        assert resp.data == items

    def test_get_paginated_response_empty(self):
        p = NoPagination()
        resp = p.get_paginated_response([])
        assert resp.data == []

    def test_get_paginated_response_single_item(self):
        p = NoPagination()
        resp = p.get_paginated_response([{"id": 1}])
        assert resp.data == [{"id": 1}]

    def test_paginate_queryset_with_view_arg(self):
        """Accepts optional ``view`` keyword argument."""
        p = NoPagination()
        request = _drf_request()
        mock_view = MagicMock()
        result = p.paginate_queryset([1], request, view=mock_view)
        assert result is None


# ═══════════════════════════════════════════════════════════════════════
# Module exports / imports
# ═══════════════════════════════════════════════════════════════════════


class TestModuleExports:
    """Ensure the public API of the pagination package is correct."""

    def test_standard_pagination_importable(self):
        from apps.core.pagination import StandardPagination  # noqa: F811

        assert StandardPagination is not None

    def test_cursor_pagination_importable(self):
        from apps.core.pagination import LCCCursorPagination  # noqa: F811

        assert LCCCursorPagination is not None

    def test_limit_offset_importable(self):
        from apps.core.pagination import LCCLimitOffsetPagination  # noqa: F811

        assert LCCLimitOffsetPagination is not None

    def test_no_pagination_importable(self):
        from apps.core.pagination import NoPagination  # noqa: F811

        assert NoPagination is not None

    def test_all_list_contains_standard(self):
        import apps.core.pagination as mod

        assert "StandardPagination" in mod.__all__

    def test_all_list_contains_cursor(self):
        import apps.core.pagination as mod

        assert "LCCCursorPagination" in mod.__all__

    def test_all_list_contains_limit_offset(self):
        import apps.core.pagination as mod

        assert "LCCLimitOffsetPagination" in mod.__all__

    def test_all_list_contains_no_pagination(self):
        import apps.core.pagination as mod

        assert "NoPagination" in mod.__all__

    def test_all_list_has_four_entries(self):
        import apps.core.pagination as mod

        assert len(mod.__all__) == 4

    def test_module_version(self):
        import apps.core.pagination as mod

        assert mod.__version__ == "1.0.0"


# ═══════════════════════════════════════════════════════════════════════
# Edge cases & boundary values
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Boundary and edge-case scenarios."""

    # -- StandardPagination edges --

    def test_standard_single_item_response(self):
        p = StandardPagination()
        p.page = _make_page([{"id": 1}], 1, 1, 20)
        p.request = _drf_request()
        data = p.get_paginated_response([{"id": 1}]).data
        assert data["count"] == 1
        assert data["total_pages"] == 1
        assert data["current_page"] == 1

    def test_standard_boundary_page_size_equals_count(self):
        """Exactly 20 items with page_size=20 → 1 page."""
        p = StandardPagination()
        p.page = _make_page(list(range(20)), 20, 1, 20)
        p.request = _drf_request()
        data = p.get_paginated_response(list(range(20))).data
        assert data["total_pages"] == 1

    def test_standard_boundary_count_equals_max_page_size(self):
        """Exactly 100 items with page_size=100 → 1 page."""
        p = StandardPagination()
        p.page = _make_page(list(range(100)), 100, 1, 100)
        p.request = _drf_request()
        data = p.get_paginated_response(list(range(100))).data
        assert data["total_pages"] == 1
        assert data["page_size"] == 100

    # -- LimitOffset edges --

    def test_limit_offset_zero_count(self):
        p = LCCLimitOffsetPagination()
        p.count = 0
        p.limit = 20
        p.offset = 0
        p.request = _drf_request()
        data = p.get_paginated_response([]).data
        assert data["count"] == 0

    def test_limit_offset_single_item(self):
        p = LCCLimitOffsetPagination()
        p.count = 1
        p.limit = 20
        p.offset = 0
        p.request = _drf_request()
        data = p.get_paginated_response([{"id": 1}]).data
        assert data["count"] == 1
        assert len(data["results"]) == 1

    def test_limit_offset_at_max_limit(self):
        p = LCCLimitOffsetPagination()
        p.count = 500
        p.limit = 100
        p.offset = 0
        p.request = _drf_request()
        data = p.get_paginated_response(list(range(100))).data
        assert data["limit"] == 100

    # -- NoPagination edges --

    def test_no_pagination_large_payload(self):
        p = NoPagination()
        items = list(range(10_000))
        resp = p.get_paginated_response(items)
        assert len(resp.data) == 10_000

    def test_no_pagination_nested_data(self):
        p = NoPagination()
        items = [{"nested": {"key": "value"}}]
        resp = p.get_paginated_response(items)
        assert resp.data[0]["nested"]["key"] == "value"
