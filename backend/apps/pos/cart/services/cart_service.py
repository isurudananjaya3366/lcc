from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.pos.cart.models.cart_item import MAX_CART_ITEM_QUANTITY, POSCartItem
from apps.pos.cart.models.pos_cart import POSCart
from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    CART_STATUS_HELD,
    CART_STATUS_VOIDED,
    DISCOUNT_TYPE_FIXED,
    DISCOUNT_TYPE_PERCENT,
)


class CartService:
    """Stateless service for POS cart operations."""

    @staticmethod
    def get_or_create_cart(session, customer=None):
        """Get active cart for session or create a new one."""
        cart = POSCart.objects.filter(
            session=session, status=CART_STATUS_ACTIVE
        ).first()
        if cart:
            return cart
        return POSCart.objects.create(session=session, customer=customer)

    @staticmethod
    def get_cart_by_id(cart_id):
        """Get cart by ID."""
        try:
            return POSCart.objects.get(pk=cart_id)
        except POSCart.DoesNotExist:
            return None

    @staticmethod
    def get_active_cart(session):
        """Get the active cart for a session."""
        return POSCart.objects.filter(
            session=session, status=CART_STATUS_ACTIVE
        ).first()

    @staticmethod
    @transaction.atomic
    def hold_cart(cart, user=None, reason=""):
        """Put a cart on hold with tracking info."""
        if cart.status != CART_STATUS_ACTIVE:
            raise ValidationError("Only active carts can be held.")
        cart.update_status(CART_STATUS_HELD)
        if user:
            cart.held_by = user
        if reason:
            cart.held_reason = reason
        # Generate held identifier
        session_num = getattr(cart.session, "session_number", "0")
        seq = cart.__class__.objects.filter(
            session=cart.session, status=CART_STATUS_HELD
        ).count()
        cart.held_identifier = f"HELD-{session_num}-{seq:03d}"
        cart.save(update_fields=[
            "held_by", "held_reason", "held_identifier", "updated_on"
        ])
        return True

    @staticmethod
    @transaction.atomic
    def resume_cart(cart):
        """Resume a held cart."""
        if cart.status != CART_STATUS_HELD:
            raise ValidationError("Only held carts can be resumed.")
        cart.update_status(CART_STATUS_ACTIVE)
        cart.held_by = None
        cart.held_reason = ""
        cart.held_identifier = ""
        cart.save(update_fields=[
            "held_by", "held_reason", "held_identifier", "updated_on"
        ])
        return True

    @staticmethod
    def list_held_carts(session=None, user=None):
        """List held carts for a session or user."""
        qs = POSCart.objects.filter(status=CART_STATUS_HELD)
        if session:
            qs = qs.filter(session=session)
        if user:
            qs = qs.filter(held_by=user)
        return qs.order_by("-held_at")

    @staticmethod
    @transaction.atomic
    def void_cart(cart, reason=None):
        """Void a cart."""
        if not cart.is_modifiable:
            raise ValidationError("Cart cannot be voided in its current state.")
        if reason:
            cart.notes = f"{cart.notes}\nVoid reason: {reason}".strip()
        cart.update_status(CART_STATUS_VOIDED)
        return True

    @staticmethod
    def validate_cart(cart):
        """Validate cart is ready for checkout."""
        errors = []
        if not cart.has_items:
            errors.append("Cart has no items.")
        if cart.grand_total <= 0:
            errors.append("Cart total must be greater than zero.")
        if cart.status != CART_STATUS_ACTIVE:
            errors.append(f"Cart is not active (status: {cart.status}).")

        terminal = cart.session.terminal
        if terminal.require_customer and not cart.customer:
            errors.append("Customer is required for this terminal.")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    @transaction.atomic
    def add_to_cart(cart, product, quantity=1, variant=None):
        """
        Add a product to the cart.

        If the same product+variant already exists, increments quantity.
        """
        if not cart.is_modifiable:
            raise ValidationError("Cart is not modifiable.")

        quantity = Decimal(str(quantity))
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if quantity > MAX_CART_ITEM_QUANTITY:
            raise ValidationError(
                f"Quantity cannot exceed {MAX_CART_ITEM_QUANTITY}."
            )

        # Validate product is active
        if hasattr(product, "is_active") and not product.is_active:
            raise ValidationError("Product is not active.")

        if variant and variant.product_id != product.pk:
            raise ValidationError("Variant does not belong to this product.")

        # Validate variant is active
        if variant and hasattr(variant, "is_active") and not variant.is_active:
            raise ValidationError("Product variant is not active.")

        # Check for existing item
        existing = POSCartItem.objects.filter(
            cart=cart, product=product, variant=variant
        ).first()

        if existing:
            new_qty = existing.quantity + quantity
            if new_qty > MAX_CART_ITEM_QUANTITY:
                raise ValidationError(
                    f"Total quantity cannot exceed {MAX_CART_ITEM_QUANTITY}."
                )
            existing.quantity = new_qty
            existing.calculate_line_total()
            existing.save()
            cart.recalculate_totals()
            return existing

        # Determine next line number
        max_line = (
            POSCartItem.objects.filter(cart=cart).aggregate(
                max_line=models.Max("line_number")
            )["max_line"]
            or 0
        )

        item = POSCartItem(
            cart=cart,
            product=product,
            variant=variant,
            quantity=quantity,
            line_number=max_line + 1,
        )
        item.set_prices_from_product()
        item.set_tax_from_product()
        item.save()

        cart.recalculate_totals()
        return item

    @staticmethod
    @transaction.atomic
    def update_quantity(cart_item, quantity):
        """Update item quantity. If 0, removes the item."""
        if not cart_item.cart.is_modifiable:
            raise ValidationError("Cart is not modifiable.")

        quantity = Decimal(str(quantity))

        if quantity <= 0:
            CartService.remove_from_cart(cart_item)
            return None

        if quantity > MAX_CART_ITEM_QUANTITY:
            raise ValidationError(
                f"Quantity cannot exceed {MAX_CART_ITEM_QUANTITY}."
            )

        cart_item.quantity = quantity
        cart_item.calculate_line_total()
        cart_item.save()
        cart_item.cart.recalculate_totals()
        return cart_item

    @staticmethod
    @transaction.atomic
    def remove_from_cart(cart_item):
        """Remove an item from the cart."""
        cart = cart_item.cart
        if not cart.is_modifiable:
            raise ValidationError("Cart is not modifiable.")
        cart_item.delete()
        cart.recalculate_totals()
        return True

    @staticmethod
    @transaction.atomic
    def apply_line_discount(cart_item, discount_type, discount_value, reason=None):
        """Apply discount to a specific line item."""
        if not cart_item.cart.is_modifiable:
            raise ValidationError("Cart is not modifiable.")

        if discount_type not in (DISCOUNT_TYPE_PERCENT, DISCOUNT_TYPE_FIXED):
            raise ValidationError("Invalid discount type.")

        cart_item.apply_discount(discount_type, discount_value, reason)
        cart_item.cart.recalculate_totals()
        return cart_item

    @staticmethod
    @transaction.atomic
    def apply_cart_discount(
        cart, discount_type, discount_value, reason=None, coupon_code=None
    ):
        """Apply a cart-level discount."""
        if not cart.is_modifiable:
            raise ValidationError("Cart is not modifiable.")

        if discount_type not in (DISCOUNT_TYPE_PERCENT, DISCOUNT_TYPE_FIXED):
            raise ValidationError("Invalid discount type.")

        discount_value = Decimal(str(discount_value))

        if discount_type == DISCOUNT_TYPE_PERCENT and not (
            0 <= discount_value <= 100
        ):
            raise ValidationError(
                "Percentage discount must be between 0 and 100."
            )

        if discount_type == DISCOUNT_TYPE_FIXED and discount_value > cart.subtotal:
            raise ValidationError(
                "Fixed discount cannot exceed the cart subtotal."
            )

        cart.cart_discount_type = discount_type
        cart.cart_discount_value = discount_value
        cart.cart_discount_reason = reason or ""
        cart.coupon_code = coupon_code or ""
        cart.calculate_cart_discount()
        cart.save()
        CartService.calculate_totals(cart)
        return cart

    @staticmethod
    @transaction.atomic
    def calculate_totals(cart):
        """Recalculate all cart totals from items."""
        items = cart.items.all()

        # Recalculate each item
        for item in items:
            item.calculate_line_total()
            item.save()

        # Subtotal = sum of line totals
        subtotal = sum(
            (item.line_total for item in items), Decimal("0.00")
        )
        cart.subtotal = subtotal.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Cart discount
        cart.calculate_cart_discount()

        # Line discount total
        line_discount_total = sum(
            (item.discount_amount * item.quantity for item in items),
            Decimal("0.00"),
        )

        # Total discount = line discounts + cart discount
        cart.discount_total = (
            line_discount_total + cart.cart_discount_amount
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Tax total
        cart.tax_total = sum(
            (item.tax_amount for item in items), Decimal("0.00")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Grand total = subtotal - cart_discount + tax
        cart.grand_total = (
            cart.subtotal - cart.cart_discount_amount + cart.tax_total
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        cart.save()
        return cart
