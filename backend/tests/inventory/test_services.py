"""
Tests for stock operation services — Tasks 87 & 88.

Task 87: StockService (stock_in, stock_out, transfer, reserve, release, commit)
          and StockAdjustmentService.
Task 88: StockTakeService (create, start, record_count, complete, approval).
"""

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.inventory.stock.constants import (
    APPROVAL_APPROVED,
    APPROVAL_NOT_REQUIRED,
    APPROVAL_PENDING,
    APPROVAL_REJECTED,
    MOVEMENT_TYPE_ADJUSTMENT,
    MOVEMENT_TYPE_STOCK_IN,
    MOVEMENT_TYPE_STOCK_OUT,
    REASON_CORRECTION,
    REASON_DAMAGE,
    REASON_FOUND,
    REASON_PURCHASE,
    REASON_SALE,
    STOCK_TAKE_CANCELLED,
    STOCK_TAKE_COMPLETED,
    STOCK_TAKE_COUNTING,
    STOCK_TAKE_DRAFT,
    STOCK_TAKE_ITEM_COUNTED,
    STOCK_TAKE_ITEM_PENDING,
    STOCK_TAKE_REVIEW,
    STOCK_TAKE_SCOPE_FULL,
    VARIANCE_SIGNIFICANT_THRESHOLD,
)
from apps.inventory.stock.exceptions import (
    InsufficientStockError,
    StockOperationError,
)
from apps.inventory.stock.models.stock_level import StockLevel
from apps.inventory.stock.models.stock_movement import StockMovement
from apps.inventory.stock.models.stock_take import StockTake
from apps.inventory.stock.models.stock_take_item import StockTakeItem
from apps.inventory.stock.services.adjustment_service import StockAdjustmentService
from apps.inventory.stock.services.stock_service import StockService
from apps.inventory.stock.services.stock_take_service import StockTakeService

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════════
# Shared Fixtures
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
def user(tenant_context):
    """Create a PlatformUser for service operations."""
    from apps.platform.models.user import PlatformUser

    return PlatformUser.objects.create_user(
        email="stockuser@example.com",
        password="testpass123",
    )


@pytest.fixture
def stock_service(user):
    return StockService(user=user)


@pytest.fixture
def adjustment_service(user):
    return StockAdjustmentService(user=user)


@pytest.fixture
def stock_take_service(user):
    return StockTakeService(user=user)


@pytest.fixture
def stocked_level(product, warehouse):
    """Create a stock level with some quantity."""
    return StockLevel.objects.create(
        product=product,
        warehouse=warehouse,
        quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
        incoming_quantity=Decimal("0"),
        cost_per_unit=Decimal("500"),
    )


# ═══════════════════════════════════════════════════════════════════════
# Task 87: Test StockService
# ═══════════════════════════════════════════════════════════════════════


class TestStockIn:
    """Test stock_in operation."""

    def test_stock_in_increases_quantity(self, stock_service, product, warehouse):
        result = stock_service.stock_in(
            product=product,
            quantity=50,
            warehouse=warehouse,
            cost_per_unit=Decimal("500"),
        )
        assert result.success is True
        sl = StockLevel.objects.get(product=product, warehouse=warehouse)
        assert sl.quantity == Decimal("50")

    def test_stock_in_creates_movement(self, stock_service, product, warehouse):
        stock_service.stock_in(
            product=product,
            quantity=50,
            warehouse=warehouse,
            cost_per_unit=Decimal("500"),
        )
        movements = StockMovement.objects.filter(
            product=product,
            movement_type=MOVEMENT_TYPE_STOCK_IN,
        )
        assert movements.count() == 1
        assert movements.first().quantity == Decimal("50")

    def test_stock_in_weighted_avg_cost(self, stock_service, product, warehouse):
        # First batch: 100 @ 500
        stock_service.stock_in(
            product=product, quantity=100, warehouse=warehouse,
            cost_per_unit=Decimal("500"),
        )
        # Second batch: 100 @ 600
        stock_service.stock_in(
            product=product, quantity=100, warehouse=warehouse,
            cost_per_unit=Decimal("600"),
        )
        sl = StockLevel.objects.get(product=product, warehouse=warehouse)
        assert sl.quantity == Decimal("200")
        # WAC: (100*500 + 100*600) / 200 = 550
        assert sl.cost_per_unit == Decimal("550")

    def test_stock_in_invalid_quantity_raises(self, stock_service, product, warehouse):
        with pytest.raises(StockOperationError):
            stock_service.stock_in(
                product=product, quantity=0, warehouse=warehouse,
            )


class TestStockOut:
    """Test stock_out operation."""

    def test_stock_out_decreases_quantity(self, stock_service, stocked_level, product, warehouse):
        result = stock_service.stock_out(
            product=product, quantity=30, warehouse=warehouse,
        )
        assert result.success is True
        stocked_level.refresh_from_db()
        assert stocked_level.quantity == Decimal("70")

    def test_stock_out_creates_movement(self, stock_service, stocked_level, product, warehouse):
        stock_service.stock_out(
            product=product, quantity=30, warehouse=warehouse,
        )
        m = StockMovement.objects.filter(
            product=product, movement_type=MOVEMENT_TYPE_STOCK_OUT,
        ).first()
        assert m is not None
        assert m.quantity == Decimal("30")

    def test_stock_out_insufficient_raises(self, stock_service, stocked_level, product, warehouse):
        with pytest.raises(InsufficientStockError):
            stock_service.stock_out(
                product=product, quantity=200, warehouse=warehouse,
            )

    def test_stock_out_does_not_touch_reserved(self, stock_service, product, warehouse):
        StockLevel.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=Decimal("100"),
            reserved_quantity=Decimal("30"),
            cost_per_unit=Decimal("500"),
        )
        # Available = 70, try to take 60
        result = stock_service.stock_out(
            product=product, quantity=60, warehouse=warehouse,
        )
        assert result.success is True
        sl = StockLevel.objects.get(product=product, warehouse=warehouse)
        assert sl.reserved_quantity == Decimal("30")
        assert sl.quantity == Decimal("40")


class TestTransfer:
    """Test transfer operation."""

    def test_transfer_updates_both_warehouses(
        self, stock_service, stocked_level, product, warehouse, warehouse_2,
    ):
        result = stock_service.transfer(
            product=product, quantity=25,
            from_warehouse=warehouse, to_warehouse=warehouse_2,
        )
        assert result.success is True

        src = StockLevel.objects.get(product=product, warehouse=warehouse)
        dst = StockLevel.objects.get(product=product, warehouse=warehouse_2)
        assert src.quantity == Decimal("75")
        assert dst.quantity == Decimal("25")

    def test_transfer_creates_movement(
        self, stock_service, stocked_level, product, warehouse, warehouse_2,
    ):
        stock_service.transfer(
            product=product, quantity=25,
            from_warehouse=warehouse, to_warehouse=warehouse_2,
        )
        m = StockMovement.objects.filter(
            product=product,
            from_warehouse=warehouse,
            to_warehouse=warehouse_2,
        ).first()
        assert m is not None
        assert m.quantity == Decimal("25")

    def test_transfer_same_warehouse_fails(
        self, stock_service, stocked_level, product, warehouse,
    ):
        with pytest.raises(StockOperationError):
            stock_service.transfer(
                product=product, quantity=10,
                from_warehouse=warehouse, to_warehouse=warehouse,
            )

    def test_transfer_insufficient_stock_fails(
        self, stock_service, stocked_level, product, warehouse, warehouse_2,
    ):
        with pytest.raises(InsufficientStockError):
            stock_service.transfer(
                product=product, quantity=200,
                from_warehouse=warehouse, to_warehouse=warehouse_2,
            )


class TestReserve:
    """Test reserve_stock operation."""

    def test_reserve_increases_reserved(self, stock_service, stocked_level, product, warehouse):
        result = stock_service.reserve_stock(
            product=product, quantity=20, warehouse=warehouse,
        )
        assert result.success is True
        stocked_level.refresh_from_db()
        assert stocked_level.reserved_quantity == Decimal("20")

    def test_reserve_decreases_available(self, stock_service, stocked_level, product, warehouse):
        stock_service.reserve_stock(
            product=product, quantity=20, warehouse=warehouse,
        )
        stocked_level.refresh_from_db()
        assert stocked_level.available_quantity == Decimal("80")

    def test_reserve_insufficient_fails(self, stock_service, stocked_level, product, warehouse):
        with pytest.raises(InsufficientStockError):
            stock_service.reserve_stock(
                product=product, quantity=200, warehouse=warehouse,
            )


class TestRelease:
    """Test release_stock operation."""

    def test_release_decreases_reserved(self, stock_service, product, warehouse):
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), reserved_quantity=Decimal("30"),
            cost_per_unit=Decimal("500"),
        )
        result = stock_service.release_stock(
            product=product, quantity=10, warehouse=warehouse,
        )
        assert result.success is True
        sl = StockLevel.objects.get(product=product, warehouse=warehouse)
        assert sl.reserved_quantity == Decimal("20")

    def test_release_more_than_reserved_fails(self, stock_service, product, warehouse):
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), reserved_quantity=Decimal("10"),
            cost_per_unit=Decimal("500"),
        )
        with pytest.raises(StockOperationError):
            stock_service.release_stock(
                product=product, quantity=50, warehouse=warehouse,
            )


class TestCommitReserved:
    """Test commit_reserved operation."""

    def test_commit_decreases_both(self, stock_service, product, warehouse):
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), reserved_quantity=Decimal("30"),
            cost_per_unit=Decimal("500"),
        )
        result = stock_service.commit_reserved(
            product=product, quantity=20, warehouse=warehouse,
        )
        assert result.success is True
        sl = StockLevel.objects.get(product=product, warehouse=warehouse)
        assert sl.quantity == Decimal("80")
        assert sl.reserved_quantity == Decimal("10")

    def test_commit_non_reserved_fails(self, stock_service, product, warehouse):
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), reserved_quantity=Decimal("5"),
            cost_per_unit=Decimal("500"),
        )
        with pytest.raises(StockOperationError):
            stock_service.commit_reserved(
                product=product, quantity=20, warehouse=warehouse,
            )


# ═══════════════════════════════════════════════════════════════════════
# Task 87: Test StockAdjustmentService
# ═══════════════════════════════════════════════════════════════════════


class TestAdjustment:
    """Test adjustment operations."""

    def test_adjust_up(self, adjustment_service, product, warehouse):
        result = adjustment_service.adjust_up(
            product=product, quantity=25, warehouse=warehouse,
            reason=REASON_FOUND, cost_per_unit=Decimal("500"),
        )
        assert result.success is True
        sl = StockLevel.objects.get(product=product, warehouse=warehouse)
        assert sl.quantity == Decimal("25")

    def test_adjust_down(self, adjustment_service, product, warehouse):
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), cost_per_unit=Decimal("500"),
        )
        result = adjustment_service.adjust_down(
            product=product, quantity=15, warehouse=warehouse,
            reason=REASON_DAMAGE,
        )
        assert result.success is True
        sl = StockLevel.objects.get(product=product, warehouse=warehouse)
        assert sl.quantity == Decimal("85")

    def test_adjustment_creates_movement(self, adjustment_service, product, warehouse):
        adjustment_service.adjust_up(
            product=product, quantity=25, warehouse=warehouse,
            reason=REASON_FOUND,
        )
        m = StockMovement.objects.filter(
            product=product, movement_type=MOVEMENT_TYPE_ADJUSTMENT,
        ).first()
        assert m is not None

    def test_requires_authorization_large_value(self, adjustment_service):
        # 200 * 1 = 200 > threshold of 100
        assert adjustment_service.requires_authorization(200) is True

    def test_no_authorization_small_value(self, adjustment_service):
        # 5 * 1 = 5 < threshold of 100
        assert adjustment_service.requires_authorization(5) is False


# ═══════════════════════════════════════════════════════════════════════
# Task 88: Test StockTakeService
# ═══════════════════════════════════════════════════════════════════════


class TestStockTakeCreation:
    """Test stock take creation."""

    def test_create_stock_take(self, stock_take_service, warehouse):
        result = stock_take_service.create_stock_take(
            warehouse=warehouse,
            name="Q4 Count",
            scope=STOCK_TAKE_SCOPE_FULL,
        )
        assert result.success is True
        st = StockTake.objects.get(pk=result.data["stock_take_id"])
        assert st.status == STOCK_TAKE_DRAFT
        assert st.name == "Q4 Count"

    def test_reference_generated(self, stock_take_service, warehouse):
        result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Count 1",
        )
        st = StockTake.objects.get(pk=result.data["stock_take_id"])
        assert st.reference.startswith("ST-")

    def test_sequential_references(self, stock_take_service, warehouse):
        r1 = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Count 1",
        )
        r2 = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Count 2",
        )
        st1 = StockTake.objects.get(pk=r1.data["stock_take_id"])
        st2 = StockTake.objects.get(pk=r2.data["stock_take_id"])
        # Second reference number should be greater
        assert st2.reference > st1.reference


class TestStockTakeStart:
    """Test starting a stock take (populating items)."""

    def test_start_populates_items(self, stock_take_service, product, warehouse):
        # Create stock level
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("50"), cost_per_unit=Decimal("500"),
        )
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Start Test",
        )
        st_id = create_result.data["stock_take_id"]

        result = stock_take_service.start_stock_take(st_id)
        assert result.success is True
        assert result.data["items_created"] == 1

        st = StockTake.objects.get(pk=st_id)
        assert st.status == STOCK_TAKE_COUNTING
        assert st.total_items == 1
        assert st.started_at is not None

    def test_start_captures_expected_quantity(self, stock_take_service, product, warehouse):
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("75"), cost_per_unit=Decimal("300"),
        )
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Qty Test",
        )
        stock_take_service.start_stock_take(create_result.data["stock_take_id"])

        item = StockTakeItem.objects.first()
        assert item.expected_quantity == Decimal("75")
        assert item.cost_per_unit == Decimal("300")
        assert item.status == STOCK_TAKE_ITEM_PENDING

    def test_start_multiple_products(
        self, stock_take_service, product, product_2, warehouse,
    ):
        StockLevel.objects.create(
            product=product, warehouse=warehouse, quantity=Decimal("50"),
        )
        StockLevel.objects.create(
            product=product_2, warehouse=warehouse, quantity=Decimal("30"),
        )
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Multi Test",
        )
        result = stock_take_service.start_stock_take(
            create_result.data["stock_take_id"]
        )
        assert result.data["items_created"] == 2


class TestRecordCount:
    """Test recording counts on stock take items."""

    @pytest.fixture
    def active_stock_take(self, stock_take_service, product, warehouse):
        """Create and start a stock take with one item."""
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), cost_per_unit=Decimal("500"),
        )
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Count Test",
        )
        st_id = create_result.data["stock_take_id"]
        stock_take_service.start_stock_take(st_id)
        return StockTake.objects.get(pk=st_id)

    def test_record_count_updates_item(self, stock_take_service, active_stock_take, user):
        item = active_stock_take.items.first()
        result = stock_take_service.record_count(
            stock_take_item_id=item.pk,
            counted_quantity=95,
            user=user,
        )
        assert result.success is True

        item.refresh_from_db()
        assert item.counted_quantity == Decimal("95")
        assert item.status == STOCK_TAKE_ITEM_COUNTED
        assert item.counted_by == user
        assert item.counted_at is not None

    def test_record_count_calculates_variance(self, stock_take_service, active_stock_take, user):
        item = active_stock_take.items.first()
        stock_take_service.record_count(
            stock_take_item_id=item.pk,
            counted_quantity=90,
            user=user,
        )
        item.refresh_from_db()
        assert item.variance_quantity == Decimal("-10")
        assert item.variance_value == Decimal("-5000")

    def test_high_variance_flags_recount(self, stock_take_service, active_stock_take, user):
        item = active_stock_take.items.first()
        # Count much less than expected — variance > 10%
        stock_take_service.record_count(
            stock_take_item_id=item.pk,
            counted_quantity=80,
            user=user,
        )
        item.refresh_from_db()
        assert abs(item.variance_percentage) > VARIANCE_SIGNIFICANT_THRESHOLD
        assert item.requires_recount is True

    def test_locked_item_raises(self, stock_take_service, active_stock_take, user):
        item = active_stock_take.items.first()
        item.is_locked = True
        item.save()

        with pytest.raises(StockOperationError, match="locked"):
            stock_take_service.record_count(
                stock_take_item_id=item.pk,
                counted_quantity=100,
                user=user,
            )


class TestStockTakeComplete:
    """Test completing a stock take with adjustments."""

    @pytest.fixture
    def reviewed_stock_take(self, stock_take_service, product, warehouse, user):
        """Create a stock take that's been counted and reviewed."""
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), cost_per_unit=Decimal("500"),
        )
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Complete Test",
        )
        st_id = create_result.data["stock_take_id"]
        stock_take_service.start_stock_take(st_id)

        item = StockTakeItem.objects.filter(
            stock_take_id=st_id,
        ).first()
        stock_take_service.record_count(
            stock_take_item_id=item.pk,
            counted_quantity=95,
            user=user,
        )
        stock_take_service.submit_for_review(st_id)
        return StockTake.objects.get(pk=st_id)

    def test_complete_creates_adjustments(
        self, stock_take_service, reviewed_stock_take, user,
    ):
        result = stock_take_service.complete_stock_take(
            stock_take_id=reviewed_stock_take.pk,
            user=user,
        )
        assert result.success is True
        assert result.data["adjustments_created"] == 1

    def test_complete_updates_stock_level(
        self, stock_take_service, reviewed_stock_take, product, warehouse, user,
    ):
        stock_take_service.complete_stock_take(
            stock_take_id=reviewed_stock_take.pk,
            user=user,
        )
        sl = StockLevel.objects.get(product=product, warehouse=warehouse)
        # Original 100, variance -5 → 95
        assert sl.quantity == Decimal("95")

    def test_complete_sets_status(
        self, stock_take_service, reviewed_stock_take, user,
    ):
        stock_take_service.complete_stock_take(
            stock_take_id=reviewed_stock_take.pk,
            user=user,
        )
        reviewed_stock_take.refresh_from_db()
        assert reviewed_stock_take.status == STOCK_TAKE_COMPLETED
        assert reviewed_stock_take.completed_at is not None
        assert reviewed_stock_take.completed_by == user


class TestSubmitForReview:
    """Test submit_for_review workflow."""

    @pytest.fixture
    def counted_stock_take(self, stock_take_service, product, warehouse, user):
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), cost_per_unit=Decimal("500"),
        )
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Review Test",
        )
        st_id = create_result.data["stock_take_id"]
        stock_take_service.start_stock_take(st_id)
        item = StockTakeItem.objects.filter(stock_take_id=st_id).first()
        stock_take_service.record_count(
            stock_take_item_id=item.pk,
            counted_quantity=100,
            user=user,
        )
        return StockTake.objects.get(pk=st_id)

    def test_submit_changes_status(self, stock_take_service, counted_stock_take):
        result = stock_take_service.submit_for_review(counted_stock_take.pk)
        assert result.success is True

        counted_stock_take.refresh_from_db()
        assert counted_stock_take.status == STOCK_TAKE_REVIEW

    def test_no_significant_variance_no_approval_needed(
        self, stock_take_service, counted_stock_take,
    ):
        result = stock_take_service.submit_for_review(counted_stock_take.pk)
        assert result.data["approval_status"] == APPROVAL_NOT_REQUIRED


class TestApprovalWorkflow:
    """Test approve/reject stock take workflows."""

    @pytest.fixture
    def review_stock_take(self, stock_take_service, product, warehouse, user):
        """Stock take with significant variance in REVIEW status."""
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), cost_per_unit=Decimal("500"),
        )
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Approval Test",
        )
        st_id = create_result.data["stock_take_id"]
        stock_take_service.start_stock_take(st_id)

        item = StockTakeItem.objects.filter(stock_take_id=st_id).first()
        # Very big variance to trigger approval
        stock_take_service.record_count(
            stock_take_item_id=item.pk,
            counted_quantity=50,
            user=user,
        )
        stock_take_service.submit_for_review(st_id)
        return StockTake.objects.get(pk=st_id)

    def test_significant_variance_requires_approval(self, review_stock_take):
        assert review_stock_take.approval_status == APPROVAL_PENDING

    def test_approve_stock_take(self, stock_take_service, review_stock_take, user):
        result = stock_take_service.approve_stock_take(
            review_stock_take.pk, approver=user,
        )
        assert result.success is True
        review_stock_take.refresh_from_db()
        assert review_stock_take.approval_status == APPROVAL_APPROVED
        assert review_stock_take.approved_by == user

    def test_reject_stock_take(self, stock_take_service, review_stock_take, user):
        result = stock_take_service.reject_stock_take(
            review_stock_take.pk, approver=user, reason="Needs recount",
        )
        assert result.success is True
        review_stock_take.refresh_from_db()
        assert review_stock_take.approval_status == APPROVAL_REJECTED
        # Rejection reverts to COUNTING
        assert review_stock_take.status == STOCK_TAKE_COUNTING


class TestCancelStockTake:
    """Test cancelling a stock take."""

    def test_cancel_draft(self, stock_take_service, warehouse):
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Cancel Test",
        )
        st_id = create_result.data["stock_take_id"]
        result = stock_take_service.cancel_stock_take(st_id)
        assert result.success is True

        st = StockTake.objects.get(pk=st_id)
        assert st.status == STOCK_TAKE_CANCELLED
        assert st.cancelled_at is not None

    def test_cancel_completed_fails(self, stock_take_service, product, warehouse, user):
        StockLevel.objects.create(
            product=product, warehouse=warehouse,
            quantity=Decimal("100"), cost_per_unit=Decimal("500"),
        )
        create_result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Cancel Fail Test",
        )
        st_id = create_result.data["stock_take_id"]
        stock_take_service.start_stock_take(st_id)

        item = StockTakeItem.objects.filter(stock_take_id=st_id).first()
        stock_take_service.record_count(
            stock_take_item_id=item.pk, counted_quantity=100, user=user,
        )
        stock_take_service.submit_for_review(st_id)
        stock_take_service.complete_stock_take(st_id, user=user)

        with pytest.raises(StockOperationError):
            stock_take_service.cancel_stock_take(st_id)


class TestBlindCount:
    """Test blind count mode."""

    def test_blind_count_flag(self, stock_take_service, warehouse):
        result = stock_take_service.create_stock_take(
            warehouse=warehouse, name="Blind Count",
            is_blind_count=True,
        )
        st = StockTake.objects.get(pk=result.data["stock_take_id"])
        assert st.is_blind_count is True
