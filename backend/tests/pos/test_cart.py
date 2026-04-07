"""
Tests for cart operations: creation, add/update/remove items,
line and cart discounts, total calculations, and cart state management.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    CART_STATUS_HELD,
    CART_STATUS_VOIDED,
    DISCOUNT_TYPE_FIXED,
    DISCOUNT_TYPE_PERCENT,
)

pytestmark = pytest.mark.django_db


# ── Cart Creation ────────────────────────────────────────────────────


class TestCartCreation:
    def test_create_cart_with_session(self, cart, session):
        assert cart.pk is not None
        assert cart.session == session
        assert cart.status == CART_STATUS_ACTIVE

    def test_cart_reference_auto_generated(self, cart):
        assert cart.reference_number is not None
        assert len(cart.reference_number) > 0

    def test_cart_totals_initialize_to_zero(self, cart):
        assert cart.subtotal == Decimal("0.00")
        assert cart.discount_total == Decimal("0.00")
        assert cart.tax_total == Decimal("0.00")
        assert cart.grand_total == Decimal("0.00")

    def test_get_or_create_returns_existing_active_cart(self, cart, session):
        from apps.pos.cart.services.cart_service import CartService

        same_cart = CartService.get_or_create_cart(session)
        assert same_cart.pk == cart.pk

    def test_cart_with_customer(self, session, customer):
        from apps.pos.cart.services.cart_service import CartService

        c = CartService.get_or_create_cart(session, customer=customer)
        assert c.customer == customer


# ── Add to Cart ──────────────────────────────────────────────────────


class TestAddToCart:
    def test_add_product_to_cart(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=1)
        assert item.pk is not None
        assert item.product == product
        assert item.quantity == Decimal("1")

    def test_add_product_with_quantity(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=3)
        assert item.quantity == Decimal("3")

    def test_add_product_with_variant(self, cart, product_with_variant):
        from apps.pos.cart.services.cart_service import CartService

        prod, variant = product_with_variant
        item = CartService.add_to_cart(cart, prod, quantity=1, variant=variant)
        assert item.variant == variant

    def test_add_sets_price_from_product(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=1)
        assert item.original_price == product.selling_price
        assert item.unit_price == product.selling_price

    def test_add_increments_quantity_if_exists(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        CartService.add_to_cart(cart, product, quantity=2)
        item = CartService.add_to_cart(cart, product, quantity=3)
        assert item.quantity == Decimal("5")

    def test_add_calculates_line_total(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=2)
        assert item.line_total == product.selling_price * 2

    def test_add_updates_cart_totals(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        CartService.add_to_cart(cart, product, quantity=2)
        cart.refresh_from_db()
        assert cart.subtotal > Decimal("0.00")

    def test_add_zero_quantity_raises(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        with pytest.raises(ValidationError, match="greater than zero"):
            CartService.add_to_cart(cart, product, quantity=0)

    def test_add_negative_quantity_raises(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        with pytest.raises(ValidationError, match="greater than zero"):
            CartService.add_to_cart(cart, product, quantity=-1)

    def test_add_variant_wrong_product_raises(self, cart, product, product_with_variant):
        from apps.pos.cart.services.cart_service import CartService

        _, variant = product_with_variant  # variant belongs to different product
        with pytest.raises(ValidationError, match="does not belong"):
            CartService.add_to_cart(cart, product, variant=variant)


# ── Update Quantity ──────────────────────────────────────────────────


class TestUpdateQuantity:
    def test_update_quantity_success(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=1)
        updated = CartService.update_quantity(item, 5)
        assert updated.quantity == Decimal("5")

    def test_update_recalculates_line_total(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=1)
        CartService.update_quantity(item, 3)
        item.refresh_from_db()
        assert item.line_total == product.selling_price * 3

    def test_update_quantity_zero_removes_item(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.cart.models import POSCartItem

        item = CartService.add_to_cart(cart, product, quantity=1)
        item_pk = item.pk
        result = CartService.update_quantity(item, 0)
        assert result is None
        assert not POSCartItem.objects.filter(pk=item_pk).exists()

    def test_update_updates_cart_totals(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=1)
        CartService.update_quantity(item, 5)
        cart.refresh_from_db()
        assert cart.subtotal == product.selling_price * 5


# ── Remove from Cart ─────────────────────────────────────────────────


class TestRemoveFromCart:
    def test_remove_item_success(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.cart.models import POSCartItem

        item = CartService.add_to_cart(cart, product, quantity=1)
        item_pk = item.pk
        CartService.remove_from_cart(item)
        assert not POSCartItem.objects.filter(pk=item_pk).exists()

    def test_remove_updates_cart_totals(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        item = cart_with_items.items.first()
        CartService.remove_from_cart(item)
        cart_with_items.refresh_from_db()
        # Should still have the second item's total
        assert cart_with_items.items.count() == 1

    def test_remove_only_specified_item(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        initial_count = cart_with_items.items.count()
        item = cart_with_items.items.first()
        CartService.remove_from_cart(item)
        assert cart_with_items.items.count() == initial_count - 1


# ── Line Discounts ───────────────────────────────────────────────────


class TestLineDiscount:
    def test_apply_percentage_discount(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=2)
        CartService.apply_line_discount(item, DISCOUNT_TYPE_PERCENT, Decimal("10"))
        item.refresh_from_db()
        assert item.discount_type == DISCOUNT_TYPE_PERCENT
        assert item.discount_value == Decimal("10")
        assert item.discount_amount > Decimal("0.00")

    def test_apply_fixed_discount(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=1)
        CartService.apply_line_discount(item, DISCOUNT_TYPE_FIXED, Decimal("20"))
        item.refresh_from_db()
        assert item.discount_type == DISCOUNT_TYPE_FIXED
        assert item.discount_amount == Decimal("20.00")

    def test_invalid_discount_type_raises(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=1)
        with pytest.raises(ValidationError, match="Invalid discount type"):
            CartService.apply_line_discount(item, "bogus", Decimal("10"))

    def test_discount_updates_cart_totals(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        item = CartService.add_to_cart(cart, product, quantity=2)
        cart.refresh_from_db()
        original_total = cart.grand_total

        CartService.apply_line_discount(item, DISCOUNT_TYPE_PERCENT, Decimal("50"))
        cart.refresh_from_db()
        assert cart.grand_total < original_total


# ── Cart-Level Discount ──────────────────────────────────────────────


class TestCartDiscount:
    def test_apply_cart_percentage_discount(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        CartService.apply_cart_discount(
            cart_with_items, DISCOUNT_TYPE_PERCENT, Decimal("10")
        )
        cart_with_items.refresh_from_db()
        assert cart_with_items.cart_discount_type == DISCOUNT_TYPE_PERCENT
        assert cart_with_items.cart_discount_value == Decimal("10")
        assert cart_with_items.cart_discount_amount > Decimal("0.00")

    def test_apply_cart_fixed_discount(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        CartService.apply_cart_discount(
            cart_with_items, DISCOUNT_TYPE_FIXED, Decimal("50")
        )
        cart_with_items.refresh_from_db()
        assert cart_with_items.cart_discount_amount == Decimal("50.00")

    def test_cart_discount_with_coupon_code(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        CartService.apply_cart_discount(
            cart_with_items,
            DISCOUNT_TYPE_PERCENT,
            Decimal("15"),
            coupon_code="SAVE15",
        )
        cart_with_items.refresh_from_db()
        assert cart_with_items.coupon_code == "SAVE15"

    def test_cart_discount_invalid_type_raises(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        with pytest.raises(ValidationError, match="Invalid discount type"):
            CartService.apply_cart_discount(
                cart_with_items, "invalid", Decimal("10")
            )

    def test_percentage_over_100_raises(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        with pytest.raises(ValidationError, match="between 0 and 100"):
            CartService.apply_cart_discount(
                cart_with_items, DISCOUNT_TYPE_PERCENT, Decimal("150")
            )

    def test_fixed_exceeding_subtotal_raises(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        with pytest.raises(ValidationError, match="exceed"):
            CartService.apply_cart_discount(
                cart_with_items, DISCOUNT_TYPE_FIXED, Decimal("99999")
            )


# ── Calculate Totals ─────────────────────────────────────────────────


class TestCalculateTotals:
    def test_empty_cart_totals_zero(self, cart):
        assert cart.subtotal == Decimal("0.00")
        assert cart.grand_total == Decimal("0.00")

    def test_single_item_totals(self, cart, product):
        from apps.pos.cart.services.cart_service import CartService

        CartService.add_to_cart(cart, product, quantity=2)
        cart.refresh_from_db()
        assert cart.subtotal == product.selling_price * 2

    def test_multiple_items_totals(self, cart_with_items):
        # cart_with_items: 2 x Coke(150) + 1 x Pepsi(200)
        expected_subtotal = Decimal("150.00") * 2 + Decimal("200.00")
        assert cart_with_items.subtotal == expected_subtotal

    def test_totals_after_discount(self, cart_with_items):
        from apps.pos.cart.services.cart_service import CartService

        original = cart_with_items.grand_total
        CartService.apply_cart_discount(
            cart_with_items, DISCOUNT_TYPE_PERCENT, Decimal("10")
        )
        cart_with_items.refresh_from_db()
        assert cart_with_items.grand_total < original


# ── Cart State Management ────────────────────────────────────────────


class TestCartStateManagement:
    def test_hold_cart(self, cart):
        from apps.pos.cart.services.cart_service import CartService

        CartService.hold_cart(cart)
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_HELD

    def test_resume_held_cart(self, cart):
        from apps.pos.cart.services.cart_service import CartService

        CartService.hold_cart(cart)
        CartService.resume_cart(cart)
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_ACTIVE

    def test_hold_non_active_raises(self, cart):
        from apps.pos.cart.services.cart_service import CartService

        CartService.hold_cart(cart)
        with pytest.raises(ValidationError, match="Only active"):
            CartService.hold_cart(cart)

    def test_resume_non_held_raises(self, cart):
        from apps.pos.cart.services.cart_service import CartService

        with pytest.raises(ValidationError, match="Only held"):
            CartService.resume_cart(cart)

    def test_void_cart(self, cart):
        from apps.pos.cart.services.cart_service import CartService

        CartService.void_cart(cart, reason="Customer left")
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_VOIDED

    def test_void_cart_with_reason(self, cart):
        from apps.pos.cart.services.cart_service import CartService

        CartService.void_cart(cart, reason="Wrong items")
        cart.refresh_from_db()
        assert "Wrong items" in cart.notes

    def test_voided_cart_not_modifiable(self, cart):
        from apps.pos.cart.services.cart_service import CartService

        CartService.void_cart(cart)
        assert cart.is_modifiable is False
