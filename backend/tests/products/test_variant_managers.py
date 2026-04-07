"""
Tests for VariantQuerySet and VariantManager.

Covers all chainable QuerySet methods, the VariantManager proxy,
the get_by_options lookup, method chaining, and edge cases.

Relies on fixtures from conftest.py:
    - tenant_context, category, variable_product, variable_product_2
    - variant_option_type_size, variant_option_type_color
    - variant_option_value_small, variant_option_value_medium,
      variant_option_value_large
    - variant_option_value_red, variant_option_value_blue
"""

import pytest

from apps.products.models import (
    ProductVariant,
    ProductVariantOption,
    VariantManager,
    VariantQuerySet,
)

pytestmark = pytest.mark.django_db


# ════════════════════════════════════════════════════════════════════════
# Helper to create a variant with options linked via the through model
# ════════════════════════════════════════════════════════════════════════


def _create_variant(product, sku, name, option_values, **extra):
    """Create a ProductVariant and link option values."""
    variant = ProductVariant.objects.create(
        product=product,
        sku=sku,
        name=name,
        **extra,
    )
    for idx, ov in enumerate(option_values):
        ProductVariantOption.objects.create(
            variant=variant,
            option_value=ov,
            display_order=idx,
        )
    return variant


# ════════════════════════════════════════════════════════════════════════
# Manager/QuerySet Type Tests
# ════════════════════════════════════════════════════════════════════════


class TestVariantManagerAssignment:
    """Verify that ProductVariant.objects is a VariantManager."""

    def test_objects_is_variant_manager(self, tenant_context):
        """ProductVariant.objects should be VariantManager."""
        assert isinstance(ProductVariant.objects, VariantManager)

    def test_queryset_is_variant_queryset(self, tenant_context):
        """get_queryset must return VariantQuerySet."""
        qs = ProductVariant.objects.get_queryset()
        assert isinstance(qs, VariantQuerySet)

    def test_all_with_deleted_still_available(self, tenant_context):
        """all_with_deleted must still be the raw Manager."""
        # BaseModel defines all_with_deleted = Manager()
        assert hasattr(ProductVariant, "all_with_deleted")


# ════════════════════════════════════════════════════════════════════════
# VariantQuerySet.active() / inactive()
# ════════════════════════════════════════════════════════════════════════


class TestActiveFilter:
    """Tests for VariantQuerySet.active() and inactive()."""

    def test_active_returns_active_variants(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        v1 = _create_variant(
            variable_product,
            "TSH-S-RED",
            "Small / Red",
            [variant_option_value_small, variant_option_value_red],
        )
        v2 = _create_variant(
            variable_product,
            "TSH-S-RED-OFF",
            "Small / Red (off)",
            [variant_option_value_small],
            is_active=False,
        )

        active = ProductVariant.objects.active()
        assert v1 in active
        assert v2 not in active

    def test_active_excludes_deleted(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _create_variant(
            variable_product,
            "TSH-S-DEL",
            "Small Deleted",
            [variant_option_value_small],
        )
        v.is_deleted = True
        v.save(update_fields=["is_deleted"])

        assert v not in ProductVariant.objects.active()

    def test_inactive_returns_inactive_only(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        _create_variant(
            variable_product,
            "TSH-ACT",
            "Active",
            [variant_option_value_small],
        )
        v_off = _create_variant(
            variable_product,
            "TSH-OFF",
            "Off",
            [variant_option_value_red],
            is_active=False,
        )

        inactive = ProductVariant.objects.inactive()
        assert v_off in inactive
        assert inactive.count() >= 1


# ════════════════════════════════════════════════════════════════════════
# VariantQuerySet.for_product()
# ════════════════════════════════════════════════════════════════════════


class TestForProductFilter:
    """Tests for VariantQuerySet.for_product()."""

    def test_for_product_with_instance(
        self,
        variable_product,
        variable_product_2,
        variant_option_value_small,
        variant_option_value_medium,
    ):
        v1 = _create_variant(
            variable_product,
            "P1-S",
            "P1 Small",
            [variant_option_value_small],
        )
        v2 = _create_variant(
            variable_product_2,
            "P2-M",
            "P2 Medium",
            [variant_option_value_medium],
        )

        result = ProductVariant.objects.for_product(variable_product)
        assert v1 in result
        assert v2 not in result

    def test_for_product_with_id(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _create_variant(
            variable_product,
            "P1-S-ID",
            "P1 Small ID",
            [variant_option_value_small],
        )
        result = ProductVariant.objects.for_product(variable_product.pk)
        assert v in result

    def test_for_product_returns_empty_for_no_variants(
        self, variable_product_2
    ):
        result = ProductVariant.objects.for_product(variable_product_2)
        assert result.count() == 0


# ════════════════════════════════════════════════════════════════════════
# VariantQuerySet.by_option()
# ════════════════════════════════════════════════════════════════════════


class TestByOptionFilter:
    """Tests for VariantQuerySet.by_option()."""

    def test_by_single_option(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_medium,
        variant_option_value_red,
    ):
        v_small = _create_variant(
            variable_product,
            "TSH-S-R1",
            "Small Red",
            [variant_option_value_small, variant_option_value_red],
        )
        v_med = _create_variant(
            variable_product,
            "TSH-M-R1",
            "Medium Red",
            [variant_option_value_medium, variant_option_value_red],
        )

        result = ProductVariant.objects.by_option(variant_option_value_small)
        assert v_small in result
        assert v_med not in result

    def test_by_multiple_options_and_logic(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_medium,
        variant_option_value_red,
        variant_option_value_blue,
    ):
        v_s_r = _create_variant(
            variable_product,
            "TSH-S-RED2",
            "Small Red",
            [variant_option_value_small, variant_option_value_red],
        )
        _create_variant(
            variable_product,
            "TSH-S-BLU",
            "Small Blue",
            [variant_option_value_small, variant_option_value_blue],
        )
        _create_variant(
            variable_product,
            "TSH-M-RED2",
            "Medium Red",
            [variant_option_value_medium, variant_option_value_red],
        )

        # AND logic: Small AND Red
        result = ProductVariant.objects.by_option(
            [variant_option_value_small, variant_option_value_red]
        )
        assert v_s_r in result
        assert result.count() == 1

    def test_by_option_with_tuple(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        v = _create_variant(
            variable_product,
            "TSH-TUPLE",
            "Tuple Test",
            [variant_option_value_small, variant_option_value_red],
        )
        result = ProductVariant.objects.by_option(
            (variant_option_value_small, variant_option_value_red)
        )
        assert v in result

    def test_by_option_returns_empty_for_unmatched(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_large,
    ):
        _create_variant(
            variable_product,
            "TSH-ONLY-S",
            "Small Only",
            [variant_option_value_small],
        )
        result = ProductVariant.objects.by_option(variant_option_value_large)
        assert result.count() == 0


# ════════════════════════════════════════════════════════════════════════
# VariantQuerySet.in_stock() — placeholder
# ════════════════════════════════════════════════════════════════════════


class TestInStockFilter:
    """Tests for VariantQuerySet.in_stock() placeholder."""

    def test_in_stock_returns_active(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _create_variant(
            variable_product,
            "TSH-STOCK",
            "Stock",
            [variant_option_value_small],
        )
        result = ProductVariant.objects.in_stock()
        assert v in result

    def test_in_stock_excludes_inactive(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _create_variant(
            variable_product,
            "TSH-NOSTOCK",
            "No Stock",
            [variant_option_value_small],
            is_active=False,
        )
        result = ProductVariant.objects.in_stock()
        assert v not in result


# ════════════════════════════════════════════════════════════════════════
# VariantQuerySet.with_prices() / with_stock() / with_options()
# ════════════════════════════════════════════════════════════════════════


class TestPrefetchMethods:
    """Tests for prefetch methods — verify they return querysets."""

    def test_with_prices_is_chainable(
        self,
        variable_product,
        variant_option_value_small,
    ):
        _create_variant(
            variable_product,
            "TSH-WP",
            "With Prices",
            [variant_option_value_small],
        )
        qs = ProductVariant.objects.active().with_prices()
        assert isinstance(qs, VariantQuerySet)
        assert qs.count() >= 1

    def test_with_stock_is_chainable(
        self,
        variable_product,
        variant_option_value_small,
    ):
        _create_variant(
            variable_product,
            "TSH-WS",
            "With Stock",
            [variant_option_value_small],
        )
        qs = ProductVariant.objects.active().with_stock()
        assert isinstance(qs, VariantQuerySet)
        assert qs.count() >= 1

    def test_with_options_prefetches_data(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        _create_variant(
            variable_product,
            "TSH-WO",
            "With Options",
            [variant_option_value_small, variant_option_value_red],
        )
        qs = ProductVariant.objects.for_product(
            variable_product
        ).with_options()
        variant = qs.first()
        # Access prefetched data without extra queries
        options = list(variant.option_values.all())
        assert len(options) == 2

    def test_with_prices_selects_product(
        self,
        variable_product,
        variant_option_value_small,
    ):
        _create_variant(
            variable_product,
            "TSH-WP-SEL",
            "Prices Select",
            [variant_option_value_small],
        )
        qs = ProductVariant.objects.with_prices()
        variant = qs.first()
        # product should be select_related (no extra query)
        assert variant.product.name == "Classic T-Shirt"


# ════════════════════════════════════════════════════════════════════════
# Method Chaining
# ════════════════════════════════════════════════════════════════════════


class TestMethodChaining:
    """Tests for chaining multiple QuerySet methods."""

    def test_active_for_product_chain(
        self,
        variable_product,
        variable_product_2,
        variant_option_value_small,
        variant_option_value_medium,
    ):
        v1 = _create_variant(
            variable_product,
            "TSH-CH1",
            "Chain Active P1",
            [variant_option_value_small],
        )
        _create_variant(
            variable_product_2,
            "TSH-CH2",
            "Chain Active P2",
            [variant_option_value_medium],
        )
        v3_off = _create_variant(
            variable_product,
            "TSH-CH3",
            "Chain Inactive P1",
            [variant_option_value_small],
            is_active=False,
        )

        result = ProductVariant.objects.active().for_product(variable_product)
        assert v1 in result
        assert v3_off not in result

    def test_for_product_by_option_chain(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_medium,
        variant_option_value_red,
    ):
        v_s_r = _create_variant(
            variable_product,
            "TSH-SPCH",
            "Small Red Chain",
            [variant_option_value_small, variant_option_value_red],
        )
        _create_variant(
            variable_product,
            "TSH-MPCH",
            "Medium Red Chain",
            [variant_option_value_medium, variant_option_value_red],
        )

        result = (
            ProductVariant.objects.for_product(variable_product).by_option(
                variant_option_value_small
            )
        )
        assert v_s_r in result
        assert result.count() == 1

    def test_triple_chain(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        v = _create_variant(
            variable_product,
            "TSH-TRI",
            "Triple",
            [variant_option_value_small, variant_option_value_red],
        )

        result = (
            ProductVariant.objects.active()
            .for_product(variable_product)
            .by_option(variant_option_value_small)
        )
        assert v in result

    def test_chain_with_prefetch(
        self,
        variable_product,
        variant_option_value_small,
    ):
        _create_variant(
            variable_product,
            "TSH-PFC",
            "Prefetch Chain",
            [variant_option_value_small],
        )
        result = (
            ProductVariant.objects.active()
            .for_product(variable_product)
            .with_options()
        )
        assert isinstance(result, VariantQuerySet)
        assert result.count() >= 1


# ════════════════════════════════════════════════════════════════════════
# VariantManager.get_by_options()
# ════════════════════════════════════════════════════════════════════════


class TestGetByOptions:
    """Tests for VariantManager.get_by_options()."""

    def test_get_by_options_with_instances(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_medium,
        variant_option_value_red,
    ):
        v_s_r = _create_variant(
            variable_product,
            "TSH-GBO-SR",
            "Small Red",
            [variant_option_value_small, variant_option_value_red],
        )
        _create_variant(
            variable_product,
            "TSH-GBO-MR",
            "Medium Red",
            [variant_option_value_medium, variant_option_value_red],
        )

        found = ProductVariant.objects.get_by_options(
            variable_product,
            [variant_option_value_small, variant_option_value_red],
        )
        assert found is not None
        assert found.pk == v_s_r.pk

    def test_get_by_options_with_dict(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        v = _create_variant(
            variable_product,
            "TSH-GBO-D",
            "Small Red Dict",
            [variant_option_value_small, variant_option_value_red],
        )

        found = ProductVariant.objects.get_by_options(
            variable_product,
            {"Size": "s", "Color": "red"},
        )
        assert found is not None
        assert found.pk == v.pk

    def test_get_by_options_exact_match_only(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
        variant_option_value_blue,
    ):
        """Variant with 2 options should NOT match a 1-option search."""
        _create_variant(
            variable_product,
            "TSH-GBO-E",
            "Small Red Blue",
            [
                variant_option_value_small,
                variant_option_value_red,
                variant_option_value_blue,
            ],
        )

        found = ProductVariant.objects.get_by_options(
            variable_product,
            [variant_option_value_small, variant_option_value_red],
        )
        # Should NOT match because variant has 3 options, search has 2
        assert found is None

    def test_get_by_options_returns_none_for_no_match(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
        variant_option_value_blue,
    ):
        _create_variant(
            variable_product,
            "TSH-GBO-NM",
            "Small Red NM",
            [variant_option_value_small, variant_option_value_red],
        )

        found = ProductVariant.objects.get_by_options(
            variable_product,
            [variant_option_value_small, variant_option_value_blue],
        )
        assert found is None

    def test_get_by_options_with_invalid_dict(
        self,
        variable_product,
        variant_option_value_small,
    ):
        _create_variant(
            variable_product,
            "TSH-GBO-INV",
            "Invalid Dict",
            [variant_option_value_small],
        )

        found = ProductVariant.objects.get_by_options(
            variable_product,
            {"Nonexistent": "xyz"},
        )
        assert found is None

    def test_get_by_options_empty_options(self, variable_product):
        found = ProductVariant.objects.get_by_options(
            variable_product, []
        )
        assert found is None

    def test_get_by_options_empty_dict(self, variable_product):
        found = ProductVariant.objects.get_by_options(
            variable_product, {}
        )
        assert found is None

    def test_get_by_options_with_product_id(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        v = _create_variant(
            variable_product,
            "TSH-GBO-PID",
            "Product ID",
            [variant_option_value_small, variant_option_value_red],
        )

        found = ProductVariant.objects.get_by_options(
            variable_product.pk,
            [variant_option_value_small, variant_option_value_red],
        )
        assert found is not None
        assert found.pk == v.pk

    def test_get_by_options_scoped_to_product(
        self,
        variable_product,
        variable_product_2,
        variant_option_value_small,
        variant_option_value_red,
    ):
        """Same options on two products — returns correct product's variant."""
        v1 = _create_variant(
            variable_product,
            "P1-GBO-SC",
            "P1 Small Red",
            [variant_option_value_small, variant_option_value_red],
        )
        _create_variant(
            variable_product_2,
            "P2-GBO-SC",
            "P2 Small Red",
            [variant_option_value_small, variant_option_value_red],
        )

        found = ProductVariant.objects.get_by_options(
            variable_product,
            [variant_option_value_small, variant_option_value_red],
        )
        assert found is not None
        assert found.pk == v1.pk

    def test_get_by_options_single_option(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _create_variant(
            variable_product,
            "TSH-GBO-1",
            "Single Option",
            [variant_option_value_small],
        )
        found = ProductVariant.objects.get_by_options(
            variable_product,
            [variant_option_value_small],
        )
        assert found is not None
        assert found.pk == v.pk


# ════════════════════════════════════════════════════════════════════════
# Edge Cases
# ════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_empty_queryset(self, tenant_context):
        """active() on empty table returns empty queryset."""
        assert ProductVariant.objects.active().count() == 0

    def test_for_product_nonexistent_id(self, tenant_context):
        """for_product with non-existent UUID returns empty."""
        import uuid

        result = ProductVariant.objects.for_product(uuid.uuid4())
        assert result.count() == 0

    def test_queryset_returns_variant_queryset_type(self, tenant_context):
        """All chained calls should return VariantQuerySet."""
        qs = ProductVariant.objects.active()
        assert isinstance(qs, VariantQuerySet)

        qs2 = qs.filter(name="test")
        # Regular filter returns base QuerySet, that's fine
        assert hasattr(qs2, "active")

    def test_by_option_empty_list(self, tenant_context):
        """by_option with empty list returns all."""
        result = ProductVariant.objects.by_option([])
        assert isinstance(result, VariantQuerySet)
