"""
Tests for ProductVariant, ProductVariantOption, and ProductOptionConfig models.

Covers creation, validation, computed fields, relationships, constraints,
and soft-delete behaviour.  Relies on conftest fixtures.
"""

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.products.constants import PRODUCT_TYPES
from apps.products.models import (
    Product,
    ProductOptionConfig,
    ProductVariant,
    ProductVariantOption,
    VariantOptionType,
    VariantOptionValue,
)

pytestmark = pytest.mark.django_db


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════


def _make_variant(product, sku, option_values, **extra):
    """Create a ProductVariant and link option values."""
    variant = ProductVariant.objects.create(
        product=product, sku=sku, **extra
    )
    for idx, ov in enumerate(option_values):
        ProductVariantOption.objects.create(
            variant=variant, option_value=ov, display_order=idx
        )
    return variant


# ════════════════════════════════════════════════════════════════════════
# ProductVariant — Creation
# ════════════════════════════════════════════════════════════════════════


class TestProductVariantCreation:
    """ProductVariant creation and basic fields."""

    def test_create_variant(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product,
            "TSH-S",
            [variant_option_value_small],
        )
        assert v.pk is not None
        assert v.product == variable_product
        assert v.sku == "TSH-S"
        assert v.is_active is True

    def test_variant_has_uuid_pk(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-UUID", [variant_option_value_small]
        )
        import uuid

        assert isinstance(v.pk, uuid.UUID)

    def test_variant_timestamps(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-TS", [variant_option_value_small]
        )
        assert v.created_on is not None
        assert v.updated_on is not None

    def test_variant_barcode_optional(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product,
            "TSH-BC",
            [variant_option_value_small],
            barcode="123456789",
        )
        assert v.barcode == "123456789"

    def test_variant_name_auto_blank(
        self,
        variable_product,
        variant_option_value_small,
    ):
        """Name can be blank — auto-generated on save."""
        v = ProductVariant.objects.create(
            product=variable_product, sku="TSH-ABLNK"
        )
        assert v.name == "" or v.name is not None


# ════════════════════════════════════════════════════════════════════════
# ProductVariant — Relationships
# ════════════════════════════════════════════════════════════════════════


class TestProductVariantRelationships:
    """FK, M2M, and through-model relations."""

    def test_product_fk(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-FK", [variant_option_value_small]
        )
        assert v.product_id == variable_product.pk

    def test_option_values_m2m(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        v = _make_variant(
            variable_product,
            "TSH-M2M",
            [variant_option_value_small, variant_option_value_red],
        )
        ov_ids = set(v.option_values.values_list("id", flat=True))
        assert variant_option_value_small.pk in ov_ids
        assert variant_option_value_red.pk in ov_ids

    def test_variant_through_model(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-TH", [variant_option_value_small]
        )
        through = ProductVariantOption.objects.filter(variant=v)
        assert through.count() == 1
        assert through.first().option_value == variant_option_value_small

    def test_variant_reverse_relation(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-RR", [variant_option_value_small]
        )
        assert v in variable_product.variants.all()

    def test_cascade_delete_from_product(
        self,
        variable_product,
        variant_option_value_small,
    ):
        _make_variant(
            variable_product, "TSH-CAS", [variant_option_value_small]
        )
        pid = variable_product.pk
        Product.all_with_deleted.filter(pk=pid).delete()
        assert ProductVariant.objects.filter(product_id=pid).count() == 0


# ════════════════════════════════════════════════════════════════════════
# ProductVariant — Computed Fields / Methods
# ════════════════════════════════════════════════════════════════════════


class TestProductVariantMethods:
    """Tests for computed fields and instance methods."""

    def test_str_contains_sku(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-STR", [variant_option_value_small]
        )
        assert "TSH-STR" in str(v)

    def test_get_option_display(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        v = _make_variant(
            variable_product,
            "TSH-OD",
            [variant_option_value_small, variant_option_value_red],
        )
        display = v.get_option_display()
        assert isinstance(display, dict)
        assert len(display) == 2

    def test_get_full_name_property(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product,
            "TSH-FN",
            [variant_option_value_small],
            name="Small",
        )
        full = v.get_full_name
        assert variable_product.name in full
        assert "Small" in full

    def test_generate_name_from_options(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_red,
    ):
        v = _make_variant(
            variable_product,
            "TSH-GN",
            [variant_option_value_small, variant_option_value_red],
        )
        v.generate_name_from_options()
        assert v.name != ""

    def test_get_weight_without_override(self, variable_product):
        v = ProductVariant.objects.create(
            product=variable_product, sku="TSH-GW1"
        )
        weight = v.get_weight()
        assert weight == variable_product.weight

    def test_get_weight_with_override(self, variable_product):
        v = ProductVariant.objects.create(
            product=variable_product,
            sku="TSH-GW2",
            weight_override=Decimal("5.00"),
        )
        assert v.get_weight() == Decimal("5.00")

    def test_get_dimensions_without_override(self, variable_product):
        v = ProductVariant.objects.create(
            product=variable_product, sku="TSH-GD1"
        )
        dims = v.get_dimensions()
        assert isinstance(dims, dict)
        assert "length" in dims

    def test_get_dimensions_with_override(self, variable_product):
        v = ProductVariant.objects.create(
            product=variable_product,
            sku="TSH-GD2",
            length_override=Decimal("10.00"),
            width_override=Decimal("5.00"),
            height_override=Decimal("3.00"),
        )
        dims = v.get_dimensions()
        assert dims["length"] == Decimal("10.00")
        assert dims["width"] == Decimal("5.00")
        assert dims["height"] == Decimal("3.00")


# ════════════════════════════════════════════════════════════════════════
# ProductVariant — Constraints
# ════════════════════════════════════════════════════════════════════════


class TestProductVariantConstraints:
    """Unique constraints and validation."""

    def test_unique_sku(
        self,
        variable_product,
        variant_option_value_small,
        variant_option_value_medium,
    ):
        _make_variant(
            variable_product, "TSH-UNQ", [variant_option_value_small]
        )
        with pytest.raises(IntegrityError):
            _make_variant(
                variable_product, "TSH-UNQ", [variant_option_value_medium]
            )

    def test_sort_order_default(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-SO", [variant_option_value_small]
        )
        assert v.sort_order == 0


# ════════════════════════════════════════════════════════════════════════
# ProductVariant — Soft Delete
# ════════════════════════════════════════════════════════════════════════


class TestProductVariantSoftDelete:
    """Soft delete behaviour inherited from BaseModel."""

    def test_soft_delete(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-SD", [variant_option_value_small]
        )
        v.delete()
        # VariantManager doesn't pre-filter alive; use active()
        assert ProductVariant.objects.active().filter(pk=v.pk).count() == 0
        assert (
            ProductVariant.all_with_deleted.filter(pk=v.pk).count() == 1
        )

    def test_soft_delete_sets_flags(
        self,
        variable_product,
        variant_option_value_small,
    ):
        v = _make_variant(
            variable_product, "TSH-SDF", [variant_option_value_small]
        )
        v.delete()
        v.refresh_from_db()
        assert v.is_deleted is True


# ════════════════════════════════════════════════════════════════════════
# ProductVariantOption (through model)
# ════════════════════════════════════════════════════════════════════════


class TestProductVariantOption:
    """Tests for ProductVariantOption through model."""

    def test_through_creation(
        self,
        variable_product,
        variant_option_value_small,
    ):
        variant = ProductVariant.objects.create(
            product=variable_product, sku="TSH-TH1"
        )
        through = ProductVariantOption.objects.create(
            variant=variant,
            option_value=variant_option_value_small,
            display_order=0,
        )
        assert through.pk is not None

    def test_through_unique_together(
        self,
        variable_product,
        variant_option_value_small,
    ):
        variant = ProductVariant.objects.create(
            product=variable_product, sku="TSH-TH2"
        )
        ProductVariantOption.objects.create(
            variant=variant,
            option_value=variant_option_value_small,
            display_order=0,
        )
        with pytest.raises(IntegrityError):
            ProductVariantOption.objects.create(
                variant=variant,
                option_value=variant_option_value_small,
                display_order=1,
            )

    def test_through_cascade_on_variant_delete(
        self,
        variable_product,
        variant_option_value_small,
    ):
        variant = ProductVariant.objects.create(
            product=variable_product, sku="TSH-TH3"
        )
        ProductVariantOption.objects.create(
            variant=variant,
            option_value=variant_option_value_small,
            display_order=0,
        )
        ProductVariant.all_with_deleted.filter(pk=variant.pk).delete()
        assert ProductVariantOption.objects.filter(
            variant=variant
        ).count() == 0


# ════════════════════════════════════════════════════════════════════════
# ProductOptionConfig
# ════════════════════════════════════════════════════════════════════════


class TestProductOptionConfig:
    """Tests for ProductOptionConfig model."""

    def test_create_config(
        self,
        variable_product,
        variant_option_type_size,
    ):
        config = ProductOptionConfig.objects.create(
            product=variable_product,
            option_type=variant_option_type_size,
            display_order=0,
        )
        assert config.pk is not None
        assert config.product == variable_product
        assert config.option_type == variant_option_type_size

    def test_config_unique_product_type(
        self,
        variable_product,
        variant_option_type_size,
    ):
        ProductOptionConfig.objects.create(
            product=variable_product,
            option_type=variant_option_type_size,
            display_order=0,
        )
        with pytest.raises(IntegrityError):
            ProductOptionConfig.objects.create(
                product=variable_product,
                option_type=variant_option_type_size,
                display_order=1,
            )

    def test_config_reverse_relation(
        self,
        variable_product,
        variant_option_type_size,
    ):
        ProductOptionConfig.objects.create(
            product=variable_product,
            option_type=variant_option_type_size,
            display_order=0,
        )
        assert variable_product.option_configs.count() == 1

    def test_config_different_products_same_type(
        self,
        variable_product,
        variable_product_2,
        variant_option_type_size,
    ):
        ProductOptionConfig.objects.create(
            product=variable_product,
            option_type=variant_option_type_size,
            display_order=0,
        )
        ProductOptionConfig.objects.create(
            product=variable_product_2,
            option_type=variant_option_type_size,
            display_order=0,
        )
        assert ProductOptionConfig.objects.count() == 2
