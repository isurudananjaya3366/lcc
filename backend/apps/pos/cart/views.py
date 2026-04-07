"""
POS Cart ViewSet.

Provides cart retrieval plus custom actions to add / update / remove
items, apply discounts, hold/recall carts, and void.
"""

import logging

import django_filters
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.pos.cart.models import POSCart, POSCartItem
from apps.pos.cart.serializers import (
    CartDiscountSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
    POSCartSerializer,
)
from apps.pos.cart.services.cart_service import CartService
from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    CART_STATUS_HELD,
    SESSION_STATUS_OPEN,
)

logger = logging.getLogger(__name__)


class POSCartFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr="exact")
    session = django_filters.UUIDFilter(field_name="session_id")
    customer = django_filters.UUIDFilter(field_name="customer_id")

    class Meta:
        model = POSCart
        fields = ["status", "session", "customer"]


class POSCartViewSet(viewsets.ModelViewSet):
    """
    Cart management with add / remove / discount / hold / recall / void.

    Standard CRUD plus custom actions:
      POST   /cart/{id}/add_item/
      PATCH  /cart/{id}/update_quantity/{item_id}/
      DELETE /cart/{id}/remove_item/{item_id}/
      POST   /cart/{id}/apply_discount/
      POST   /cart/{id}/apply_line_discount/{item_id}/
      POST   /cart/{id}/hold/
      POST   /cart/{id}/recall/
      POST   /cart/{id}/void/
      GET    /cart/active/
      GET    /cart/held/
    """

    queryset = POSCart.objects.select_related(
        "session", "session__terminal", "customer"
    ).prefetch_related("items__product", "items__variant")
    serializer_class = POSCartSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = POSCartFilter
    search_fields = ["reference_number"]
    ordering_fields = ["created_on", "grand_total"]
    ordering = ["-created_on"]

    # ── helpers ─────────────────────────────────────────────────────

    def _cart_response(self, cart):
        cart.refresh_from_db()
        return Response(POSCartSerializer(cart).data)

    def _get_cart_item(self, cart, item_id):
        """Resolve a cart item by UUID within the given cart."""
        try:
            return POSCartItem.objects.get(
                pk=item_id,
                cart=cart,
                is_active=True,
                is_deleted=False,
            )
        except POSCartItem.DoesNotExist:
            return None

    # ── add item ────────────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="add_item")
    def add_item(self, request, pk=None):
        from apps.products.models import Product, ProductVariant

        cart = self.get_object()
        ser = CartItemCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            product = Product.objects.get(pk=ser.validated_data["product"])
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        variant = None
        variant_id = ser.validated_data.get("variant")
        if variant_id:
            try:
                variant = ProductVariant.objects.get(pk=variant_id)
            except ProductVariant.DoesNotExist:
                return Response(
                    {"detail": "Variant not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        CartService.add_to_cart(
            cart=cart,
            product=product,
            quantity=ser.validated_data["quantity"],
            variant=variant,
        )

        logger.info("Item added to cart %s", cart.reference_number)
        return self._cart_response(cart)

    # ── update quantity ─────────────────────────────────────────────

    @action(
        detail=True,
        methods=["patch"],
        url_path=r"update_quantity/(?P<item_id>[0-9a-f-]+)",
    )
    def update_quantity(self, request, pk=None, item_id=None):
        cart = self.get_object()
        item = self._get_cart_item(cart, item_id)
        if not item:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        ser = CartItemUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        CartService.update_quantity(
            cart_item=item,
            quantity=ser.validated_data["quantity"],
        )

        return self._cart_response(cart)

    # ── remove item ─────────────────────────────────────────────────

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"remove_item/(?P<item_id>[0-9a-f-]+)",
    )
    def remove_item(self, request, pk=None, item_id=None):
        cart = self.get_object()
        item = self._get_cart_item(cart, item_id)
        if not item:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        CartService.remove_from_cart(cart_item=item)

        return self._cart_response(cart)

    # ── discounts ───────────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="apply_discount")
    def apply_discount(self, request, pk=None):
        """Apply a cart-level discount."""
        cart = self.get_object()
        ser = CartDiscountSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        CartService.apply_cart_discount(
            cart=cart,
            discount_type=ser.validated_data["discount_type"],
            discount_value=ser.validated_data["discount_value"],
            reason=ser.validated_data.get("reason", ""),
        )

        return self._cart_response(cart)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"apply_line_discount/(?P<item_id>[0-9a-f-]+)",
    )
    def apply_line_discount(self, request, pk=None, item_id=None):
        """Apply a discount to a single line item."""
        cart = self.get_object()
        item = self._get_cart_item(cart, item_id)
        if not item:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        ser = CartDiscountSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        CartService.apply_line_discount(
            cart_item=item,
            discount_type=ser.validated_data["discount_type"],
            discount_value=ser.validated_data["discount_value"],
        )

        return self._cart_response(cart)

    # ── hold / recall / void ────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="hold")
    def hold(self, request, pk=None):
        cart = self.get_object()
        CartService.hold_cart(cart, user=request.user, reason=request.data.get("reason", ""))
        return self._cart_response(cart)

    @action(detail=True, methods=["post"], url_path="recall")
    def recall(self, request, pk=None):
        cart = self.get_object()
        CartService.resume_cart(cart)
        return self._cart_response(cart)

    @action(detail=True, methods=["post"], url_path="void")
    def void(self, request, pk=None):
        cart = self.get_object()
        reason = request.data.get("reason", "")
        CartService.void_cart(cart, reason=reason)
        return self._cart_response(cart)

    # ── customer management ─────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="customer")
    def add_customer(self, request, pk=None):
        """Assign a customer to the cart."""
        cart = self.get_object()
        customer_id = request.data.get("customer")
        if not customer_id:
            return Response(
                {"detail": "Customer ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.customers.models import Customer

        try:
            customer = Customer.objects.get(pk=customer_id, is_active=True)
        except Customer.DoesNotExist:
            return Response(
                {"detail": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        cart.customer = customer
        cart.save(update_fields=["customer", "updated_on"])
        return self._cart_response(cart)

    @add_customer.mapping.delete
    def remove_customer(self, request, pk=None):
        """Remove a customer from the cart."""
        cart = self.get_object()
        cart.customer = None
        cart.save(update_fields=["customer", "updated_on"])
        return self._cart_response(cart)

    # ── cart summary / discount ─────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="summary")
    def cart_summary(self, request, pk=None):
        """Return a detailed breakdown of the cart."""
        cart = self.get_object()
        items = cart.items.select_related("product", "variant")
        return Response({
            "id": str(cart.pk),
            "status": cart.status,
            "item_count": items.count(),
            "subtotal": str(cart.subtotal),
            "discount_total": str(cart.discount_total),
            "tax_total": str(cart.tax_total),
            "grand_total": str(cart.grand_total),
            "customer": str(cart.customer) if cart.customer else None,
            "reference_number": cart.reference_number,
        })

    @action(detail=True, methods=["delete"], url_path="discount")
    def remove_discount(self, request, pk=None):
        """Clear the cart-level discount."""
        cart = self.get_object()
        if not cart.is_modifiable:
            return Response(
                {"detail": "Cart is not modifiable."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.cart_discount_type = "none"
        cart.cart_discount_value = 0
        cart.save(update_fields=["cart_discount_type", "cart_discount_value", "updated_on"])
        cart.recalculate_totals()
        return self._cart_response(cart)

    # ── convenience list actions ────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="active")
    def active_carts(self, request):
        """List active carts for the current user's open session."""
        qs = self.get_queryset().filter(
            status=CART_STATUS_ACTIVE,
            session__user=request.user,
            session__status=SESSION_STATUS_OPEN,
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                POSCartSerializer(page, many=True).data
            )
        return Response(POSCartSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="held")
    def held_carts(self, request):
        """List held carts for the current user's open session."""
        qs = self.get_queryset().filter(
            status=CART_STATUS_HELD,
            session__user=request.user,
            session__status=SESSION_STATUS_OPEN,
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                POSCartSerializer(page, many=True).data
            )
        return Response(POSCartSerializer(qs, many=True).data)
