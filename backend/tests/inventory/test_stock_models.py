"""
Tests for StockLevel model — Task 85.

Covers model creation, unique constraints, calculated properties,
manager methods, and validation rules.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.inventory.stock.constants import IN_STOCK, LOW_STOCK, OUT_OF_STOCK
from apps.inventory.stock.models.stock_level import StockLevel

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def category(tenant_context):
    from apps.products.models.category import Category

    return Category.objects.create(name="Electronics", slug="electronics")


@pytest.fixture
def product(category):
    from apps.products.models.product import Product

    return Product.objects.create(name="Test Phone", category=category)


@pytest.fixture
def product_2(category):
    from apps.products.models.product import Product

    return Product.objects.create(name="Test Tablet", category=category)


@pytest.fixture
def variant(product):
    from apps.products.models.product_variant import ProductVariant

    return ProductVariant.objects.create(product=product, sku="PHONE-128GB")


@pytest.fixture
def stock_level(product, warehouse):
    return StockLevel.objects.create(
        product=product,
        warehouse=warehouse,
        quantity=Decimal("100"),
        reserved_quantity=Decimal("10"),
        incoming_quantity=Decimal("20"),
        reorder_point=Decimal("15"),
        cost_per_unit=Decimal("500"),
    )


# ═══════════════════════════════════════════════════════════════════════
# Test Model Creation
# ═══════════════════════════════════════════════════════════════════════


class TestStockLevelCreation:
    """Test StockLevel model creation and defaults."""

    def test_create_basic_stock_level(self, product, warehouse):
        sl = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("50"),
        )
        assert sl.pk is not None
        assert sl.quantity == Decimal("50")

    def test_default_values(self, product, warehouse):
        sl = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
        )
        assert sl.quantity == 0
        assert sl.reserved_quantity == 0
        assert sl.incoming_quantity == 0
        assert sl.cost_per_unit == 0

    def test_automatic_timestamps(self, product, warehouse):
        sl = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
        )
        assert sl.created_on is not None
        assert sl.updated_on is not None

    def test_with_variant(self, product, variant, warehouse):
        sl = StockLevel.objects.create(
            product=product,
            variant=variant,
            warehouse=warehouse,
            quantity=Decimal("25"),
        )
        assert sl.variant == variant

    def test_with_location(self, product, warehouse, zone):
        from apps.inventory.warehouses.models import StorageLocation

        loc = StorageLocation.objects.create(
            warehouse=warehouse,
            location_type="bin",
            name="Bin-1",
            code="B001",
        )
        sl = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            location=loc,
            quantity=Decimal("30"),
        )
        assert sl.location == loc

    def test_str_representation(self, stock_level):
        text = str(stock_level)
        assert "Test Phone" in text
        assert "100" in text


# ═══════════════════════════════════════════════════════════════════════
# Test Unique Constraints
# ═══════════════════════════════════════════════════════════════════════


class TestStockLevelConstraints:
    """Test unique constraint on (product, variant, warehouse, location)."""

    def test_duplicate_raises_integrity_error(self, product, variant, warehouse, bin_loc):
        """Duplicate (product, variant, warehouse, location) raises error.

        All four fields must be non-NULL because PostgreSQL treats NULLs
        as distinct in unique constraints.
        The save() override calls full_clean() which catches uniqueness
        via Django's validate_unique before hitting the DB constraint.
        """
        StockLevel.objects.create(
            product=product,
            variant=variant,
            warehouse=warehouse,
            location=bin_loc,
            quantity=Decimal("10"),
        )
        with pytest.raises((IntegrityError, ValidationError)):
            with transaction.atomic():
                StockLevel.objects.create(
                    product=product,
                    variant=variant,
                    warehouse=warehouse,
                    location=bin_loc,
                    quantity=Decimal("20"),
                )

    def test_different_warehouses_allowed(self, product, warehouse, warehouse_2):
        sl1 = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("10"),
        )
        sl2 = StockLevel.objects.create(
            product=product,
            warehouse=warehouse_2,
            quantity=Decimal("20"),
        )
        assert sl1.pk != sl2.pk

    def test_different_variants_allowed(self, product, variant, warehouse):
        sl1 = StockLevel.objects.create(
            product=product,
            variant=None,
            warehouse=warehouse,
            quantity=Decimal("10"),
        )
        sl2 = StockLevel.objects.create(
            product=product,
            variant=variant,
            warehouse=warehouse,
            quantity=Decimal("20"),
        )
        assert sl1.pk != sl2.pk

    def test_different_products_same_warehouse(self, product, product_2, warehouse):
        sl1 = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
        )
        sl2 = StockLevel.objects.create(
            product=product_2,
            warehouse=warehouse,
        )
        assert sl1.pk != sl2.pk


# ═══════════════════════════════════════════════════════════════════════
# Test Available Quantity Property
# ═══════════════════════════════════════════════════════════════════════


class TestAvailableQuantity:
    """Test available_quantity calculation."""

    def test_available_is_quantity_minus_reserved(self, stock_level):
        # quantity=100, reserved=10
        assert stock_level.available_quantity == Decimal("90")

    def test_available_zero_reserved(self, product, warehouse):
        sl = StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("50"),
            reserved_quantity=Decimal("0"),
        )
        assert sl.available_quantity == Decimal("50")

    def test_available_returns_zero_when_reserved_exceeds_quantity(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("10"),
            reserved_quantity=Decimal("20"),
        )
        assert sl.available_quantity == Decimal("0")

    def test_projected_quantity(self, stock_level):
        # quantity=100, incoming=20, reserved=10 → 110
        assert stock_level.projected_quantity == Decimal("110")


# ═══════════════════════════════════════════════════════════════════════
# Test Stock Status Property
# ═══════════════════════════════════════════════════════════════════════


class TestStockStatus:
    """Test stock_status dynamic determination."""

    def test_in_stock(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("100"),
            reserved_quantity=Decimal("0"),
            reorder_point=Decimal("10"),
        )
        assert sl.stock_status == IN_STOCK

    def test_low_stock_at_reorder_point(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("10"),
            reserved_quantity=Decimal("0"),
            reorder_point=Decimal("10"),
        )
        assert sl.stock_status == LOW_STOCK

    def test_out_of_stock_zero_quantity(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("0"),
            reserved_quantity=Decimal("0"),
            reorder_point=Decimal("10"),
        )
        assert sl.stock_status == OUT_OF_STOCK

    def test_out_of_stock_all_reserved(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("10"),
            reserved_quantity=Decimal("10"),
            reorder_point=Decimal("5"),
        )
        assert sl.stock_status == OUT_OF_STOCK

    def test_status_display_text(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("100"),
            reserved_quantity=Decimal("0"),
            reorder_point=Decimal("10"),
        )
        assert sl.get_stock_status_display() == "In Stock"

    def test_stock_value_property(self, stock_level):
        # quantity=100, cost_per_unit=500
        assert stock_level.stock_value == Decimal("50000")


# ═══════════════════════════════════════════════════════════════════════
# Test Manager Methods
# ═══════════════════════════════════════════════════════════════════════


class TestStockLevelManager:
    """Test StockLevelManager custom methods."""

    def test_get_for_product(self, stock_level, product):
        result = StockLevel.objects.get_for_product(product)
        assert result.count() == 1
        assert result.first() == stock_level

    def test_get_total_stock(self, product, warehouse, warehouse_2):
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("40"),
        )
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse_2,
            quantity=Decimal("60"),
        )
        total = StockLevel.objects.get_total_stock(product)
        assert total == Decimal("100")

    def test_get_available_by_warehouse(self, product, warehouse, warehouse_2):
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("40"),
            reserved_quantity=Decimal("10"),
        )
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse_2,
            quantity=Decimal("60"),
            reserved_quantity=Decimal("5"),
        )
        result = StockLevel.objects.get_available_by_warehouse(product)
        assert result[warehouse] == Decimal("30")
        assert result[warehouse_2] == Decimal("55")

    def test_low_stock_items(self, product, product_2, warehouse):
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("10"),
            reserved_quantity=Decimal("0"),
            reorder_point=Decimal("15"),
        )
        StockLevel.objects.create(
            product=product_2,
            warehouse=warehouse,
            quantity=Decimal("100"),
            reserved_quantity=Decimal("0"),
            reorder_point=Decimal("10"),
        )
        low = StockLevel.objects.low_stock_items()
        assert low.count() == 1
        assert low.first().product == product

    def test_out_of_stock_items(self, product, product_2, warehouse):
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("0"),
        )
        StockLevel.objects.create(
            product=product_2,
            warehouse=warehouse,
            quantity=Decimal("50"),
        )
        oos = StockLevel.objects.out_of_stock_items()
        assert oos.count() == 1
        assert oos.first().product == product

    def test_calculate_stock_value(self, product, product_2, warehouse):
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("10"),
            cost_per_unit=Decimal("100"),
        )
        StockLevel.objects.create(
            product=product_2,
            warehouse=warehouse,
            quantity=Decimal("5"),
            cost_per_unit=Decimal("200"),
        )
        value = StockLevel.objects.calculate_stock_value(warehouse=warehouse)
        assert value == Decimal("2000")


# ═══════════════════════════════════════════════════════════════════════
# Test Validation
# ═══════════════════════════════════════════════════════════════════════


class TestStockLevelValidation:
    """Test StockLevel model validation."""

    def test_negative_quantity_fails_clean(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("-1"),
        )
        with pytest.raises(ValidationError) as exc_info:
            sl.clean()
        assert "quantity" in exc_info.value.message_dict

    def test_reserved_exceeds_quantity_fails_clean(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("10"),
            reserved_quantity=Decimal("20"),
        )
        with pytest.raises(ValidationError) as exc_info:
            sl.clean()
        assert "reserved_quantity" in exc_info.value.message_dict

    def test_negative_incoming_fails_clean(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("10"),
            incoming_quantity=Decimal("-5"),
        )
        with pytest.raises(ValidationError) as exc_info:
            sl.clean()
        assert "incoming_quantity" in exc_info.value.message_dict

    def test_valid_stock_passes_clean(self, product, warehouse):
        sl = StockLevel(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("100"),
            reserved_quantity=Decimal("10"),
            incoming_quantity=Decimal("5"),
        )
        sl.clean()  # Should not raise
