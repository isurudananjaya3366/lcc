"""
Store API views for the LankaCommerce webstore.

Provides public read-only endpoints for product listing, detail,
related products, reviews, and category listing. Also provides
a public order submission endpoint for the checkout flow.
"""

from datetime import timedelta
from decimal import Decimal

from django.db import models as django_models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.orders.constants import OrderSource, OrderStatus
from apps.orders.models.order import Order
from apps.orders.models.order_item import OrderLineItem
from apps.products.models import Category, Product

from .serializers import (
    StoreCategorySerializer,
    StoreOrderCreateSerializer,
    StoreProductSerializer,
)

# ─── Order Submission ────────────────────────────────────────────────────────


class StoreOrderCreateView(generics.CreateAPIView):
    """
    POST /api/v1/store/orders/

    Public endpoint for the storefront checkout to submit a new order.
    Creates an Order + OrderLineItems and returns a confirmation payload.
    No authentication required (guest checkout supported).
    """

    permission_classes = [AllowAny]
    serializer_class = StoreOrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        contact = data["contactInfo"]
        shipping = data["shippingAddress"]
        items = data["items"]

        # ── Calculate totals ─────────────────────────────────────────
        subtotal = sum(
            Decimal(str(item["price"])) * item["quantity"] for item in items
        )

        # ── Generate order number ────────────────────────────────────
        order_number = self._generate_order_number()

        # ── Create Order ─────────────────────────────────────────────
        order = Order.objects.create(
            order_number=order_number,
            source=OrderSource.WEBSTORE,
            is_guest_order=True,
            status=OrderStatus.PENDING,
            customer_name=(
                f"{contact['firstName']} {contact['lastName']}".strip()
            ),
            customer_email=contact["email"],
            customer_phone=contact["phone"],
            shipping_address={
                "province": shipping["province"],
                "district": shipping["district"],
                "city": shipping["city"],
                "address1": shipping["address1"],
                "address2": shipping.get("address2", ""),
                "landmark": shipping.get("landmark", ""),
                "postalCode": shipping.get("postalCode", ""),
                "country": "Sri Lanka",
            },
            shipping_method=data["shippingMethodId"],
            payment_method=data["paymentMethod"],
            subtotal=subtotal,
            total_amount=subtotal,
        )

        # ── Create Line Items ─────────────────────────────────────────
        for position, item in enumerate(items, start=1):
            OrderLineItem.objects.create(
                order=order,
                position=position,
                item_name=item["name"],
                item_sku=item["sku"],
                unit_price=Decimal(str(item["price"])),
                quantity_ordered=Decimal(str(item["quantity"])),
                line_total=Decimal(str(item["price"])) * item["quantity"],
                currency="LKR",
            )

        # ── Estimated delivery (5 business days) ─────────────────────
        estimated_delivery = (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        return Response(
            {
                "orderId": str(order.id),
                "orderNumber": order.order_number,
                "status": order.status,
                "total": float(order.total_amount),
                "currency": "LKR",
                "estimatedDelivery": estimated_delivery,
                "createdAt": order.created_on.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _generate_order_number() -> str:
        """Generate a unique order number using OrderSettings if available."""
        try:
            from apps.orders.models.settings import OrderSettings

            settings_obj = OrderSettings.objects.first()
            if settings_obj:
                return settings_obj.get_next_order_number()
        except Exception:
            pass

        # Fallback: LCC-YYYY-NNNNN format
        year = timezone.now().year
        seq = Order.objects.filter(order_date__year=year).count() + 1
        return f"LCC-{year}-{seq:05d}"


class StoreProductViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = StoreProductSerializer
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "sku", "brand__name"]
    ordering_fields = ["selling_price", "name", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        qs = (
            Product.objects.filter(
                is_webstore_visible=True,
                status="active",
            )
            .select_related("category", "brand")
            .prefetch_related("images", "variants__option_values__option_type")
        )

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)

        min_price = self.request.query_params.get("min_price")
        if min_price:
            qs = qs.filter(selling_price__gte=min_price)

        max_price = self.request.query_params.get("max_price")
        if max_price:
            qs = qs.filter(selling_price__lte=max_price)

        if self.request.query_params.get("featured") == "true":
            qs = qs.filter(featured=True)

        if self.request.query_params.get("on_sale") == "true":
            qs = qs.filter(mrp__isnull=False).filter(
                selling_price__lt=django_models.F("mrp")
            )

        return qs

    @action(detail=True, methods=["get"], url_path="related")
    def related(self, request, slug=None):
        product = self.get_object()
        limit = min(int(request.query_params.get("limit", 4)), 20)
        related_qs = (
            Product.objects.filter(
                is_webstore_visible=True,
                status="active",
                category=product.category,
            )
            .exclude(pk=product.pk)
            .select_related("category")
            .prefetch_related("images")[:limit]
        )
        serializer = self.get_serializer(related_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="reviews")
    def reviews(self, request, slug=None):
        # Reviews model not yet implemented — return empty paginated response
        return Response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )


class StoreCategoryViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = StoreCategorySerializer
    lookup_field = "slug"
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by("name")
