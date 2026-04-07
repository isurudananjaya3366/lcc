"""
Tests for ProductSearchService: barcode search, SKU search, name search,
combined search, variant resolution, and search history.
"""

from decimal import Decimal

import pytest

from apps.pos.constants import (
    SEARCH_METHOD_BARCODE,
    SEARCH_METHOD_COMBINED,
    SEARCH_METHOD_NAME,
    SEARCH_METHOD_SKU,
)

pytestmark = pytest.mark.django_db


# ── Barcode Search ───────────────────────────────────────────────────


class TestBarcodeSearch:
    def test_barcode_exact_match(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        result = ProductSearchService.barcode_search("8901234567890")
        assert result is not None
        assert result["barcode"] == "8901234567890"
        assert result["search_method"] == SEARCH_METHOD_BARCODE

    def test_barcode_returns_single_product(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        result = ProductSearchService.barcode_search("8901234567890")
        assert isinstance(result, dict)

    def test_barcode_with_variant(self, product_with_variant):
        from apps.pos.search.services.product_search_service import ProductSearchService

        _, variant = product_with_variant
        result = ProductSearchService.barcode_search(variant.barcode)
        assert result is not None
        assert result["variant_barcode"] == variant.barcode

    def test_barcode_not_found_returns_none(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        result = ProductSearchService.barcode_search("0000000000000")
        assert result is None

    def test_barcode_empty_string_returns_none(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        result = ProductSearchService.barcode_search("")
        assert result is None

    def test_barcode_whitespace_returns_none(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        result = ProductSearchService.barcode_search("   ")
        assert result is None

    def test_barcode_ignores_invisible_products(self, product_invisible):
        from apps.pos.search.services.product_search_service import ProductSearchService

        result = ProductSearchService.barcode_search(product_invisible.barcode)
        assert result is None


# ── SKU Search ───────────────────────────────────────────────────────


class TestSKUSearch:
    def test_sku_exact_match(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.sku_search("COKE-330", exact=True)
        assert len(results) == 1
        assert results[0]["sku"] == "COKE-330"

    def test_sku_case_insensitive(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.sku_search("coke-330", exact=True)
        assert len(results) == 1

    def test_sku_partial_match(self, product, product2):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.sku_search("3", exact=False)
        # COKE-330 contains "3"
        skus = [r["sku"] for r in results]
        assert "COKE-330" in skus

    def test_sku_no_match(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.sku_search("XYZ-999", exact=True)
        assert len(results) == 0

    def test_sku_empty_returns_empty(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.sku_search("", exact=True)
        assert results == []

    def test_sku_search_method_tag(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.sku_search("COKE-330", exact=True)
        assert results[0]["search_method"] == SEARCH_METHOD_SKU


# ── Name Search ──────────────────────────────────────────────────────


class TestNameSearch:
    def test_name_full_match(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.name_search("Coca Cola 330ml")
        assert len(results) >= 1
        assert results[0]["name"] == "Coca Cola 330ml"

    def test_name_partial_match(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.name_search("Coca")
        names = [r["name"] for r in results]
        assert "Coca Cola 330ml" in names

    def test_name_case_insensitive(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.name_search("coca cola")
        assert len(results) >= 1

    def test_name_too_short_returns_empty(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.name_search("C")
        assert results == []

    def test_name_empty_returns_empty(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.name_search("")
        assert results == []

    def test_name_no_match(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.name_search("Nonexistent Product XYZ")
        assert results == []

    def test_name_respects_limit(self, product, product2):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.name_search("p", limit=1)
        # "Pepsi 500ml" matches "p"
        assert len(results) <= 1

    def test_name_ignores_invisible_products(self, product_invisible):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.name_search("Invisible")
        assert len(results) == 0


# ── Combined Search ──────────────────────────────────────────────────


class TestCombinedSearch:
    def test_combined_barcode_first(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.combined_search("8901234567890")
        assert len(results) == 1
        assert results[0]["search_method"] == SEARCH_METHOD_COMBINED

    def test_combined_fallback_to_sku(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.combined_search("COKE-330")
        assert len(results) >= 1

    def test_combined_fallback_to_name(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.combined_search("Coca Cola")
        assert len(results) >= 1

    def test_combined_empty_returns_empty(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.combined_search("")
        assert results == []

    def test_combined_no_match_returns_empty(self, tenant_context):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.combined_search("XXXXXXXXX")
        assert results == []

    def test_combined_limits_results(self, product, product2):
        from apps.pos.search.services.product_search_service import ProductSearchService

        results = ProductSearchService.combined_search("e", limit=1)
        assert len(results) <= 1


# ── Search History ───────────────────────────────────────────────────


class TestSearchHistory:
    def test_record_search(self, terminal, cashier):
        from apps.pos.search.services.product_search_service import ProductSearchService

        ProductSearchService.record_search(
            "cola",
            result_count=2,
            terminal=terminal,
            user=cashier,
        )

        recent = list(
            ProductSearchService.get_recent_searches(
                terminal=terminal, user=cashier
            )
        )
        assert "cola" in recent

    def test_get_recent_searches_limit(self, terminal, cashier):
        from apps.pos.search.services.product_search_service import ProductSearchService

        for i in range(15):
            ProductSearchService.record_search(
                f"query_{i}",
                result_count=1,
                terminal=terminal,
                user=cashier,
            )

        recent = list(
            ProductSearchService.get_recent_searches(
                terminal=terminal, user=cashier, limit=5
            )
        )
        assert len(recent) <= 5


# ── Result Structure ─────────────────────────────────────────────────


class TestSearchResultStructure:
    def test_result_includes_required_fields(self, product):
        from apps.pos.search.services.product_search_service import ProductSearchService

        result = ProductSearchService.barcode_search(product.barcode)
        assert "id" in result
        assert "name" in result
        assert "sku" in result
        assert "barcode" in result
        assert "selling_price" in result

    def test_variant_result_includes_variant_fields(self, product_with_variant):
        from apps.pos.search.services.product_search_service import ProductSearchService

        _, variant = product_with_variant
        result = ProductSearchService.barcode_search(variant.barcode)
        assert "variant_id" in result
        assert "variant_sku" in result
        assert "variant_barcode" in result
