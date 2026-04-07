"""
Tests for StockMovement model — Task 86.

Covers movement creation, type validation, quantity validation,
reversal functionality, reference linking, and manager methods.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.inventory.stock.constants import (
    MOVEMENT_TYPE_ADJUSTMENT,
    MOVEMENT_TYPE_STOCK_IN,
    MOVEMENT_TYPE_STOCK_OUT,
    MOVEMENT_TYPE_TRANSFER,
    REASON_CORRECTION,
    REASON_PURCHASE,
    REASON_SALE,
    REASON_TRANSFER,
    REFERENCE_TYPE_ORDER,
)
from apps.inventory.stock.models.stock_movement import StockMovement

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
def user(tenant_context):
    """Create a PlatformUser for FK assignment on movements."""
    from apps.platform.models.user import PlatformUser

    return PlatformUser.objects.create_user(
        email="testuser@example.com",
        password="testpass123",
    )


@pytest.fixture
def movement_in(product, warehouse, user):
    return StockMovement.objects.create(
        product=product,
        to_warehouse=warehouse,
        movement_type=MOVEMENT_TYPE_STOCK_IN,
        quantity=Decimal("50"),
        reason=REASON_PURCHASE,
        cost_per_unit=Decimal("500"),
        created_by=user,
    )


@pytest.fixture
def movement_out(product, warehouse, user):
    return StockMovement.objects.create(
        product=product,
        from_warehouse=warehouse,
        movement_type=MOVEMENT_TYPE_STOCK_OUT,
        quantity=Decimal("10"),
        reason=REASON_SALE,
        cost_per_unit=Decimal("500"),
        created_by=user,
    )


# ═══════════════════════════════════════════════════════════════════════
# Test Movement Creation
# ═══════════════════════════════════════════════════════════════════════


class TestStockMovementCreation:
    """Test creating different movement types."""

    def test_create_stock_in(self, movement_in):
        assert movement_in.pk is not None
        assert movement_in.movement_type == MOVEMENT_TYPE_STOCK_IN
        assert movement_in.quantity == Decimal("50")
        assert movement_in.to_warehouse is not None
        assert movement_in.from_warehouse is None

    def test_create_stock_out(self, movement_out):
        assert movement_out.movement_type == MOVEMENT_TYPE_STOCK_OUT
        assert movement_out.from_warehouse is not None
        assert movement_out.to_warehouse is None

    def test_create_transfer(self, product, warehouse, warehouse_2, user):
        m = StockMovement.objects.create(
            product=product,
            from_warehouse=warehouse,
            to_warehouse=warehouse_2,
            movement_type=MOVEMENT_TYPE_TRANSFER,
            quantity=Decimal("25"),
            reason=REASON_TRANSFER,
            cost_per_unit=Decimal("500"),
            created_by=user,
        )
        assert m.from_warehouse == warehouse
        assert m.to_warehouse == warehouse_2

    def test_create_adjustment(self, product, warehouse, user):
        m = StockMovement.objects.create(
            product=product,
            to_warehouse=warehouse,
            movement_type=MOVEMENT_TYPE_ADJUSTMENT,
            quantity=Decimal("5"),
            reason=REASON_CORRECTION,
            cost_per_unit=Decimal("500"),
            created_by=user,
        )
        assert m.movement_type == MOVEMENT_TYPE_ADJUSTMENT

    def test_timestamps_set(self, movement_in):
        assert movement_in.created_on is not None
        assert movement_in.movement_date is not None

    def test_user_tracking(self, movement_in, user):
        assert movement_in.created_by == user

    def test_str_representation(self, movement_in):
        text = str(movement_in)
        assert "Test Phone" in text
        assert "50" in text

    def test_total_cost_property(self, movement_in):
        # quantity=50, cost=500 → 25000
        assert movement_in.total_cost == Decimal("25000")


# ═══════════════════════════════════════════════════════════════════════
# Test Movement Type Validation
# ═══════════════════════════════════════════════════════════════════════


class TestMovementTypeValidation:
    """Test warehouse field validation by movement type."""

    def test_stock_in_requires_to_warehouse(self, product):
        m = StockMovement(
            product=product,
            movement_type=MOVEMENT_TYPE_STOCK_IN,
            quantity=Decimal("10"),
        )
        with pytest.raises(ValidationError) as exc_info:
            m.clean()
        assert "to_warehouse" in exc_info.value.message_dict

    def test_stock_out_requires_from_warehouse(self, product):
        m = StockMovement(
            product=product,
            movement_type=MOVEMENT_TYPE_STOCK_OUT,
            quantity=Decimal("10"),
        )
        with pytest.raises(ValidationError) as exc_info:
            m.clean()
        assert "from_warehouse" in exc_info.value.message_dict

    def test_transfer_requires_both_warehouses(self, product, warehouse):
        m = StockMovement(
            product=product,
            from_warehouse=warehouse,
            movement_type=MOVEMENT_TYPE_TRANSFER,
            quantity=Decimal("10"),
        )
        with pytest.raises(ValidationError) as exc_info:
            m.clean()
        assert "to_warehouse" in exc_info.value.message_dict

    def test_transfer_same_warehouse_fails(self, product, warehouse):
        m = StockMovement(
            product=product,
            from_warehouse=warehouse,
            to_warehouse=warehouse,
            movement_type=MOVEMENT_TYPE_TRANSFER,
            quantity=Decimal("10"),
        )
        with pytest.raises(ValidationError) as exc_info:
            m.clean()
        assert "to_warehouse" in exc_info.value.message_dict

    def test_adjustment_requires_warehouse(self, product):
        m = StockMovement(
            product=product,
            movement_type=MOVEMENT_TYPE_ADJUSTMENT,
            quantity=Decimal("10"),
        )
        with pytest.raises(ValidationError) as exc_info:
            m.clean()
        assert "from_warehouse" in exc_info.value.message_dict


# ═══════════════════════════════════════════════════════════════════════
# Test Quantity Validation
# ═══════════════════════════════════════════════════════════════════════


class TestQuantityValidation:
    """Test quantity validation in clean()."""

    def test_zero_quantity_fails(self, product, warehouse):
        m = StockMovement(
            product=product,
            to_warehouse=warehouse,
            movement_type=MOVEMENT_TYPE_STOCK_IN,
            quantity=Decimal("0"),
        )
        with pytest.raises(ValidationError) as exc_info:
            m.clean()
        assert "quantity" in exc_info.value.message_dict

    def test_negative_quantity_fails(self, product, warehouse):
        m = StockMovement(
            product=product,
            to_warehouse=warehouse,
            movement_type=MOVEMENT_TYPE_STOCK_IN,
            quantity=Decimal("-5"),
        )
        with pytest.raises(ValidationError) as exc_info:
            m.clean()
        assert "quantity" in exc_info.value.message_dict


# ═══════════════════════════════════════════════════════════════════════
# Test Movement Reversal
# ═══════════════════════════════════════════════════════════════════════


class TestMovementReversal:
    """Test reverse() method for creating reversal movements."""

    def test_reverse_stock_in(self, movement_in, user):
        reversal = movement_in.reverse(reason="Wrong receipt", user=user)

        assert reversal.pk is not None
        assert reversal.movement_type == MOVEMENT_TYPE_STOCK_OUT
        assert reversal.quantity == movement_in.quantity
        assert reversal.original_movement == movement_in
        assert reversal.reason == REASON_CORRECTION

        movement_in.refresh_from_db()
        assert movement_in.is_reversed is True
        assert movement_in.reversed_by == user

    def test_reverse_stock_out(self, movement_out, user):
        reversal = movement_out.reverse(reason="Customer cancelled", user=user)

        assert reversal.movement_type == MOVEMENT_TYPE_STOCK_IN
        assert reversal.quantity == movement_out.quantity

    def test_double_reversal_prevented(self, movement_in, user):
        movement_in.reverse(reason="First reversal", user=user)
        with pytest.raises(ValidationError):
            movement_in.reverse(reason="Second attempt", user=user)

    def test_reversal_links(self, movement_in, user):
        reversal = movement_in.reverse(reason="Error", user=user)

        movement_in.refresh_from_db()
        assert movement_in.reversed_by == user
        assert movement_in.reversed_at is not None
        assert movement_in.reversal_reason == "Error"


# ═══════════════════════════════════════════════════════════════════════
# Test Reference Linking
# ═══════════════════════════════════════════════════════════════════════


class TestReferenceLinks:
    """Test reference fields on movements."""

    def test_reference_fields(self, product, warehouse, user):
        m = StockMovement.objects.create(
            product=product,
            from_warehouse=warehouse,
            movement_type=MOVEMENT_TYPE_STOCK_OUT,
            quantity=Decimal("5"),
            reason=REASON_SALE,
            reference_type=REFERENCE_TYPE_ORDER,
            reference_id="ORD-001",
            reference_number="ORD-001",
            created_by=user,
        )
        assert m.reference_type == REFERENCE_TYPE_ORDER
        assert m.reference_id == "ORD-001"

    def test_query_by_reference(self, product, warehouse, user):
        StockMovement.objects.create(
            product=product,
            from_warehouse=warehouse,
            movement_type=MOVEMENT_TYPE_STOCK_OUT,
            quantity=Decimal("5"),
            reason=REASON_SALE,
            reference_type=REFERENCE_TYPE_ORDER,
            reference_id="ORD-002",
            created_by=user,
        )
        result = StockMovement.objects.by_reference(REFERENCE_TYPE_ORDER, "ORD-002")
        assert result.count() == 1


# ═══════════════════════════════════════════════════════════════════════
# Test Manager Methods
# ═══════════════════════════════════════════════════════════════════════


class TestStockMovementManager:
    """Test StockMovementManager methods."""

    def test_by_type(self, movement_in, movement_out):
        stock_ins = StockMovement.objects.by_type(MOVEMENT_TYPE_STOCK_IN)
        assert stock_ins.count() == 1
        assert stock_ins.first() == movement_in

    def test_for_product(self, movement_in, product):
        result = StockMovement.objects.for_product(product)
        assert movement_in in result

    def test_for_warehouse(self, movement_in, warehouse):
        result = StockMovement.objects.for_warehouse(warehouse)
        assert movement_in in result

    def test_recent(self, movement_in, movement_out):
        recent = StockMovement.objects.recent(days=1)
        assert len(recent) == 2

    def test_by_date_range(self, movement_in):
        now = timezone.now()
        start = now.replace(hour=0, minute=0, second=0)
        end = now.replace(hour=23, minute=59, second=59)
        result = StockMovement.objects.by_date_range(start, end)
        assert movement_in in result
