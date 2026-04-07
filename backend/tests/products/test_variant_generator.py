"""
Tests for the VariantGenerator service.

Covers validation, Cartesian combination generation, SKU generation,
unique SKU fallback, bulk creation, and edge cases.
"""

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.products.constants import PRODUCT_TYPES
from apps.products.models import (
    Product,
    ProductOptionConfig,
    ProductVariant,
    ProductVariantOption,
    VariantOptionType,
    VariantOptionValue,
)
from apps.products.services.variant_generator import VariantGenerator
from apps.products.services.config import (
    format_option_value_for_sku,
    validate_sku_pattern,
)

pytestmark = pytest.mark.django_db


# ════════════════════════════════════════════════════════════════════════
# Fixtures specific to generator tests
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture
def gen_product(tenant_context, category):
    """VARIABLE product configured for generation tests."""
    return Product.objects.create(
        name="Generator T-Shirt",
        category=category,
        product_type=PRODUCT_TYPES.VARIABLE,
        selling_price=Decimal("2500.00"),
        cost_price=Decimal("1500.00"),
    )


@pytest.fixture
def simple_product(tenant_context, category):
    """SIMPLE product — should fail variant generation."""
    return Product.objects.create(
        name="Simple Product",
        category=category,
        product_type=PRODUCT_TYPES.SIMPLE,
        selling_price=Decimal("1000.00"),
    )


@pytest.fixture
def size_options(tenant_context):
    """Create Size option type with S, M, L values."""
    opt_type = VariantOptionType.objects.create(
        name="Size", display_order=1
    )
    vals = []
    for idx, val in enumerate(["S", "M", "L"]):
        vals.append(
            VariantOptionValue.objects.create(
                option_type=opt_type,
                value=val,
                display_order=idx,
            )
        )
    return opt_type, vals


@pytest.fixture
def color_options(tenant_context):
    """Create Color option type with Red, Blue values."""
    opt_type = VariantOptionType.objects.create(
        name="Color", display_order=2
    )
    vals = []
    for idx, val in enumerate(["Red", "Blue"]):
        vals.append(
            VariantOptionValue.objects.create(
                option_type=opt_type,
                value=val,
                display_order=idx,
            )
        )
    return opt_type, vals


@pytest.fixture
def configured_product(gen_product, size_options, color_options):
    """Product with Size(3) x Color(2) option configs."""
    size_type, _ = size_options
    color_type, _ = color_options
    ProductOptionConfig.objects.create(
        product=gen_product, option_type=size_type, display_order=0
    )
    ProductOptionConfig.objects.create(
        product=gen_product, option_type=color_type, display_order=1
    )
    return gen_product


# ════════════════════════════════════════════════════════════════════════
# validate_combinations()
# ════════════════════════════════════════════════════════════════════════


class TestValidateCombinations:
    """Tests for VariantGenerator.validate_combinations."""

    def test_valid_configuration(self, configured_product):
        gen = VariantGenerator(configured_product)
        is_valid, error = gen.validate_combinations()
        assert is_valid is True
        assert error is None

    def test_invalid_simple_product(self, simple_product):
        gen = VariantGenerator(simple_product)
        is_valid, error = gen.validate_combinations()
        assert is_valid is False
        assert "VARIABLE" in error

    def test_no_option_configs(self, gen_product):
        gen = VariantGenerator(gen_product)
        is_valid, error = gen.validate_combinations()
        assert is_valid is False
        assert "no option configurations" in error

    def test_option_type_with_no_values(self, gen_product):
        empty_type = VariantOptionType.objects.create(
            name="Empty", display_order=1
        )
        ProductOptionConfig.objects.create(
            product=gen_product, option_type=empty_type, display_order=0
        )
        gen = VariantGenerator(gen_product)
        is_valid, error = gen.validate_combinations()
        assert is_valid is False
        assert "no values" in error

    def test_single_value_per_type_only(self, gen_product):
        """At least one type must have 2+ values."""
        single_type = VariantOptionType.objects.create(
            name="Single", display_order=1
        )
        VariantOptionValue.objects.create(
            option_type=single_type, value="Only", display_order=0
        )
        ProductOptionConfig.objects.create(
            product=gen_product,
            option_type=single_type,
            display_order=0,
        )
        gen = VariantGenerator(gen_product)
        is_valid, error = gen.validate_combinations()
        assert is_valid is False
        assert "2+" in error


# ════════════════════════════════════════════════════════════════════════
# get_combinations()
# ════════════════════════════════════════════════════════════════════════


class TestGetCombinations:
    """Tests for Cartesian product generation."""

    def test_two_types_cartesian_product(self, configured_product):
        gen = VariantGenerator(configured_product)
        combos = gen.get_combinations()
        # Size(3) x Color(2) = 6
        assert len(combos) == 6

    def test_single_type(self, gen_product, size_options):
        size_type, _ = size_options
        ProductOptionConfig.objects.create(
            product=gen_product, option_type=size_type, display_order=0
        )
        gen = VariantGenerator(gen_product)
        combos = gen.get_combinations()
        assert len(combos) == 3  # S, M, L

    def test_each_combo_has_correct_values(self, configured_product):
        gen = VariantGenerator(configured_product)
        combos = gen.get_combinations()
        for combo in combos:
            assert len(combo) == 2  # one Size + one Color
            # First value is from Size (display_order=1)
            assert combo[0].option_type.name == "Size"
            assert combo[1].option_type.name == "Color"

    def test_no_configs_returns_empty(self, gen_product):
        gen = VariantGenerator(gen_product)
        combos = gen.get_combinations()
        assert combos == []


# ════════════════════════════════════════════════════════════════════════
# generate_sku()
# ════════════════════════════════════════════════════════════════════════


class TestSKUGeneration:
    """Tests for SKU generation and uniqueness."""

    def test_sku_format(self, configured_product, size_options):
        _, size_vals = size_options
        gen = VariantGenerator(configured_product)
        sku = gen.generate_sku([size_vals[0]])  # S
        assert configured_product.sku in sku
        assert "S" in sku.upper()

    def test_sku_unique(self, configured_product, size_options):
        _, size_vals = size_options
        gen = VariantGenerator(configured_product)
        sku1 = gen.generate_sku([size_vals[0]])
        sku2 = gen.generate_sku([size_vals[1]])
        assert sku1 != sku2

    def test_sku_collision_fallback(
        self, configured_product, size_options
    ):
        """If base SKU is taken, appends -2, -3, etc."""
        _, size_vals = size_options
        gen = VariantGenerator(configured_product)
        base_sku = gen.generate_sku([size_vals[0]])
        # Create variant with that SKU
        ProductVariant.objects.create(
            product=configured_product, sku=base_sku
        )
        # Next generation should get base-2
        new_sku = gen.generate_sku([size_vals[0]])
        assert new_sku != base_sku
        assert new_sku.endswith("-2") or new_sku.endswith("-3")

    def test_check_sku_unique_true(self, tenant_context):
        gen = VariantGenerator.__new__(VariantGenerator)
        assert gen.check_sku_unique("NONEXISTENT-SKU") is True

    def test_check_sku_unique_false(
        self, configured_product, size_options
    ):
        _, size_vals = size_options
        ProductVariant.objects.create(
            product=configured_product, sku="TAKEN-SKU"
        )
        gen = VariantGenerator(configured_product)
        assert gen.check_sku_unique("TAKEN-SKU") is False


# ════════════════════════════════════════════════════════════════════════
# generate_variants() — full flow
# ════════════════════════════════════════════════════════════════════════


class TestGenerateVariants:
    """Tests for end-to-end variant generation."""

    def test_generate_creates_correct_count(self, configured_product):
        gen = VariantGenerator(configured_product)
        variants = gen.generate_variants()
        assert len(variants) == 6  # 3 x 2

    def test_generated_variants_have_skus(self, configured_product):
        gen = VariantGenerator(configured_product)
        variants = gen.generate_variants()
        for v in variants:
            assert v.sku != ""
            assert len(v.sku) > 0

    def test_generated_variants_have_names(self, configured_product):
        gen = VariantGenerator(configured_product)
        variants = gen.generate_variants()
        for v in variants:
            assert v.name != ""

    def test_generated_variants_have_options_linked(
        self, configured_product
    ):
        gen = VariantGenerator(configured_product)
        variants = gen.generate_variants()
        for v in variants:
            assert v.option_values.count() == 2

    def test_generated_variants_are_saved(self, configured_product):
        gen = VariantGenerator(configured_product)
        variants = gen.generate_variants()
        assert ProductVariant.objects.filter(
            product=configured_product
        ).count() == 6

    def test_generate_raises_for_simple_product(self, simple_product):
        gen = VariantGenerator(simple_product)
        with pytest.raises(ValidationError):
            gen.generate_variants()

    def test_sort_order_assigned(self, configured_product):
        gen = VariantGenerator(configured_product)
        variants = gen.generate_variants()
        orders = [v.sort_order for v in variants]
        assert orders == sorted(orders)

    def test_all_skus_unique(self, configured_product):
        gen = VariantGenerator(configured_product)
        variants = gen.generate_variants()
        skus = [v.sku for v in variants]
        assert len(skus) == len(set(skus))


# ════════════════════════════════════════════════════════════════════════
# config.py utility functions
# ════════════════════════════════════════════════════════════════════════


class TestConfigUtilities:
    """Tests for SKU config utility functions."""

    def test_format_option_value_basic(self):
        assert format_option_value_for_sku("medium") == "MEDIUM"

    def test_format_option_value_strips_spaces(self):
        assert format_option_value_for_sku("light blue") == "LIGHTBLUE"

    def test_format_option_value_truncation(self):
        long_val = "A" * 50
        result = format_option_value_for_sku(long_val)
        assert len(result) <= 20

    def test_validate_sku_pattern_valid(self):
        result = validate_sku_pattern("{product_sku}-{options}")
        assert result is True

    def test_validate_sku_pattern_invalid(self):
        result = validate_sku_pattern("{something_else}")
        assert result is False


# ════════════════════════════════════════════════════════════════════════
# 3-option-type and signal tests (audit gap fix)
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture
def material_options(tenant_context):
    """Create Material option type with Cotton, Polyester values."""
    opt_type = VariantOptionType.objects.create(
        name="Material", display_order=3
    )
    vals = []
    for idx, val in enumerate(["Cotton", "Polyester"]):
        vals.append(
            VariantOptionValue.objects.create(
                option_type=opt_type,
                value=val,
                display_order=idx,
            )
        )
    return opt_type, vals


@pytest.fixture
def three_option_product(
    gen_product, size_options, color_options, material_options
):
    """Product with Size(3) x Color(2) x Material(2) option configs."""
    size_type, _ = size_options
    color_type, _ = color_options
    material_type, _ = material_options
    ProductOptionConfig.objects.create(
        product=gen_product, option_type=size_type, display_order=0
    )
    ProductOptionConfig.objects.create(
        product=gen_product, option_type=color_type, display_order=1
    )
    ProductOptionConfig.objects.create(
        product=gen_product, option_type=material_type, display_order=2
    )
    return gen_product


class TestThreeOptionTypes:
    """Tests with 3 option types producing 12 combinations."""

    def test_three_types_combination_count(self, three_option_product):
        gen = VariantGenerator(three_option_product)
        combos = gen.get_combinations()
        assert len(combos) == 12  # 3 * 2 * 2

    def test_three_types_generate_all(self, three_option_product):
        gen = VariantGenerator(three_option_product)
        variants = gen.generate_variants()
        assert len(variants) == 12
        assert ProductVariant.objects.filter(
            product=three_option_product
        ).count() == 12

    def test_three_types_each_variant_has_3_options(
        self, three_option_product
    ):
        gen = VariantGenerator(three_option_product)
        variants = gen.generate_variants()
        for v in variants:
            assert v.variant_options.count() == 3

    def test_three_types_sku_contains_all_options(
        self, three_option_product
    ):
        gen = VariantGenerator(three_option_product)
        variants = gen.generate_variants()
        for v in variants:
            # SKU should contain 3 option codes separated by '-'
            parts = v.sku.split("-")
            assert len(parts) >= 4  # product_sku-OPT1-OPT2-OPT3

    def test_three_types_all_skus_unique(self, three_option_product):
        gen = VariantGenerator(three_option_product)
        variants = gen.generate_variants()
        skus = [v.sku for v in variants]
        assert len(skus) == len(set(skus))


class TestSignals:
    """Tests for product variant signal handlers."""

    def test_pre_save_generates_name_on_update(
        self, configured_product, size_options, color_options
    ):
        """Pre-save signal generates name when variant is re-saved."""
        _, size_vals = size_options
        _, color_vals = color_options
        variant = ProductVariant.objects.create(
            product=configured_product,
            sku="SIG-TEST-1",
        )
        ProductVariantOption.objects.create(
            variant=variant, option_value=size_vals[0], display_order=0
        )
        ProductVariantOption.objects.create(
            variant=variant, option_value=color_vals[0], display_order=1
        )
        variant.name = ""
        variant.save()
        variant.refresh_from_db()
        assert variant.name  # should be auto-generated

    def test_pre_save_preserves_manual_name(self, configured_product):
        """Pre-save signal does not overwrite manually set name."""
        variant = ProductVariant.objects.create(
            product=configured_product,
            sku="SIG-TEST-2",
            name="Custom Name",
        )
        variant.save()
        variant.refresh_from_db()
        assert variant.name == "Custom Name"
