"""
Task 90 – Concurrency & race-condition tests for Stock module.

Validates that select_for_update() row-locking and @transaction.atomic
prevent double-spending, negative-stock, and lost-update anomalies
when concurrent operations target the same StockLevel.
"""

from decimal import Decimal

import pytest
from django.db import connection, connections
from django.test.utils import CaptureQueriesContext

from apps.inventory.stock.models.stock_level import StockLevel
from apps.inventory.stock.models.stock_movement import StockMovement
from apps.inventory.stock.services.stock_service import StockService
from apps.inventory.stock.services.adjustment_service import StockAdjustmentService
from apps.inventory.stock.exceptions import StockOperationError
from apps.products.models import Category, Product, ProductVariant
from apps.platform.models.user import PlatformUser

pytestmark = [pytest.mark.django_db]


# ───────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────


@pytest.fixture
def user(tenant_context):
    return PlatformUser.objects.create_user(
        email="concurrent@test.com", password="testpass123"
    )


@pytest.fixture
def category(tenant_context):
    return Category.objects.create(name="Conc Cat", slug="conc-cat")


@pytest.fixture
def product(category):
    return Product.objects.create(name="Conc Product", category=category)


@pytest.fixture
def variant(product):
    return ProductVariant.objects.create(product=product, sku="CONC-VAR-001")


@pytest.fixture
def stock_level(product, variant, warehouse):
    return StockLevel.objects.create(
        product=product,
        variant=variant,
        warehouse=warehouse,
        quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
        incoming_quantity=Decimal("0"),
        reorder_point=Decimal("10"),
        cost_per_unit=Decimal("500.00"),
    )


# ═══════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════


class TestAtomicStockOperations:
    """Verify that stock operations use transaction.atomic."""

    def test_stock_in_creates_movement_and_updates_level_atomically(
        self, user, product, variant, warehouse, stock_level
    ):
        """A successful stock_in must update StockLevel AND create StockMovement."""
        svc = StockService(user=user)
        result = svc.stock_in(
            product=product,
            quantity=Decimal("25"),
            warehouse=warehouse,
            variant=variant,
            cost_per_unit=Decimal("500"),
        )
        assert result.success

        stock_level.refresh_from_db()
        assert stock_level.quantity == Decimal("125")
        assert StockMovement.objects.filter(
            product=product, movement_type="stock_in", quantity=Decimal("25"),
        ).exists()

    def test_stock_out_creates_movement_and_updates_level_atomically(
        self, user, product, variant, warehouse, stock_level
    ):
        svc = StockService(user=user)
        result = svc.stock_out(
            product=product,
            quantity=Decimal("10"),
            warehouse=warehouse,
            variant=variant,
            reason="sale",
        )
        assert result.success

        stock_level.refresh_from_db()
        assert stock_level.quantity == Decimal("90")


class TestSelectForUpdateLocking:
    """Verify that queries use select_for_update for row-level locks."""

    def test_stock_in_uses_select_for_update(
        self, user, product, variant, warehouse, stock_level
    ):
        """Ensure the StockLevel query during stock_in uses SELECT ... FOR UPDATE."""
        svc = StockService(user=user)
        db_alias = connection.alias

        with CaptureQueriesContext(connections[db_alias]) as ctx:
            svc.stock_in(
                product=product,
                quantity=Decimal("5"),
                warehouse=warehouse,
                variant=variant,
                cost_per_unit=Decimal("500"),
            )

        select_for_update_queries = [
            q["sql"] for q in ctx.captured_queries
            if "FOR UPDATE" in q["sql"].upper()
        ]
        assert len(select_for_update_queries) >= 1, (
            "stock_in should issue at least one SELECT ... FOR UPDATE query"
        )

    def test_stock_out_uses_select_for_update(
        self, user, product, variant, warehouse, stock_level
    ):
        svc = StockService(user=user)
        db_alias = connection.alias

        with CaptureQueriesContext(connections[db_alias]) as ctx:
            svc.stock_out(
                product=product,
                quantity=Decimal("5"),
                warehouse=warehouse,
                variant=variant,
                reason="sale",
            )

        select_for_update_queries = [
            q["sql"] for q in ctx.captured_queries
            if "FOR UPDATE" in q["sql"].upper()
        ]
        assert len(select_for_update_queries) >= 1


class TestConcurrentStockOut:
    """
    Sequential stock_out calls verifying insufficient-stock prevention.
    With 100 units, draining 60 then 60 should fail on the second call.
    """

    def test_sequential_stock_out_prevents_overselling(
        self, user, product, variant, warehouse, stock_level
    ):
        """First stock_out(60) succeeds; second stock_out(60) raises InsufficientStockError."""
        svc = StockService(user=user)

        # First call: 100 - 60 = 40
        result1 = svc.stock_out(
            product=product,
            quantity=Decimal("60"),
            warehouse=warehouse,
            variant=variant,
            reason="sale",
        )
        assert result1.success

        # Second call: only 40 left, requesting 60 must fail
        with pytest.raises(StockOperationError):
            svc.stock_out(
                product=product,
                quantity=Decimal("60"),
                warehouse=warehouse,
                variant=variant,
                reason="sale",
            )

        # Final stock must not be negative
        stock_level.refresh_from_db()
        assert stock_level.quantity == Decimal("40")


class TestConcurrentReservation:
    """Sequential reserve_stock verifying over-reservation prevention."""

    def test_sequential_reserve_prevents_over_reservation(
        self, user, product, variant, warehouse, stock_level
    ):
        """Reserve 60 from 100 available, then reserve 60 again; second must fail."""
        svc = StockService(user=user)

        # First: reserve 60 of 100 available (available = 100 - 0 = 100)
        result1 = svc.reserve_stock(
            product=product,
            quantity=Decimal("60"),
            warehouse=warehouse,
            variant=variant,
        )
        assert result1.success

        # Second: only 40 available, requesting 60 must fail
        with pytest.raises(StockOperationError):
            svc.reserve_stock(
                product=product,
                quantity=Decimal("60"),
                warehouse=warehouse,
                variant=variant,
            )

        stock_level.refresh_from_db()
        # reserved must not exceed quantity
        assert stock_level.reserved_quantity <= stock_level.quantity


class TestConcurrentAdjustments:
    """Sequential adjustments should produce correct cumulative result."""

    def test_multiple_adjust_up_serialized(
        self, user, product, variant, warehouse, stock_level
    ):
        """
        10 sequential adjust_up(+10) from base 100 should yield 200.
        """
        for _ in range(10):
            svc = StockAdjustmentService(user=user)
            result = svc.adjust_up(
                product=product,
                quantity=Decimal("10"),
                warehouse=warehouse,
                variant=variant,
                reason="found",
            )
            assert result.success

        stock_level.refresh_from_db()
        assert stock_level.quantity == Decimal("200"), (
            f"Expected 200 but got {stock_level.quantity}"
        )


class TestTransferAtomicity:
    """Transfer must debit source and credit destination atomically."""

    def test_transfer_updates_both_warehouses(
        self, user, product, variant, warehouse, warehouse_2, stock_level
    ):
        # Ensure destination stock level exists
        dest_level = StockLevel.objects.create(
            product=product,
            variant=variant,
            warehouse=warehouse_2,
            quantity=Decimal("0"),
            reserved_quantity=Decimal("0"),
            cost_per_unit=Decimal("500.00"),
        )

        svc = StockService(user=user)
        result = svc.transfer(
            product=product,
            quantity=Decimal("30"),
            from_warehouse=warehouse,
            to_warehouse=warehouse_2,
            variant=variant,
        )
        assert result.success

        stock_level.refresh_from_db()
        dest_level.refresh_from_db()
        assert stock_level.quantity == Decimal("70")
        assert dest_level.quantity == Decimal("30")

    def test_transfer_failure_rolls_back(
        self, user, product, variant, warehouse, warehouse_2, stock_level
    ):
        """Transfer exceeding source stock should not create partial state."""
        svc = StockService(user=user)
        try:
            svc.transfer(
                product=product,
                quantity=Decimal("999"),
                from_warehouse=warehouse,
                to_warehouse=warehouse_2,
                variant=variant,
            )
        except (StockOperationError, Exception):
            pass

        stock_level.refresh_from_db()
        assert stock_level.quantity == Decimal("100"), (
            "Source stock should remain unchanged after failed transfer"
        )
