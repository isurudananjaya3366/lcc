"""
Django admin registration for Orders module.
"""

from django.contrib import admin

from apps.orders.models import Order
from apps.orders.models.order_item import OrderLineItem
from apps.orders.models.history import OrderHistory
from apps.orders.models.fulfillment import Fulfillment
from apps.orders.models.fulfillment_item import FulfillmentLineItem
from apps.orders.models.order_return import OrderReturn
from apps.orders.models.settings import OrderSettings


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    extra = 0
    readonly_fields = ("id", "created_on")
    fields = (
        "item_name", "item_sku", "quantity_ordered",
        "unit_price", "total_price", "status",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number", "status", "customer_name",
        "total_amount", "payment_status", "created_on",
    )
    list_filter = ("status", "source", "payment_status", "currency", "is_draft", "is_locked")
    search_fields = ("order_number", "customer_name", "customer_email")
    readonly_fields = ("id", "order_number", "created_on", "updated_on")
    ordering = ("-created_on",)
    inlines = [OrderLineItemInline]


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "event_type", "actor", "created_on")
    list_filter = ("event_type",)
    readonly_fields = ("id", "created_on")
    ordering = ("-created_on",)


@admin.register(Fulfillment)
class FulfillmentAdmin(admin.ModelAdmin):
    list_display = (
        "fulfillment_number", "order", "status",
        "carrier", "tracking_number", "created_on",
    )
    list_filter = ("status", "carrier")
    search_fields = ("fulfillment_number", "tracking_number")
    readonly_fields = ("id", "created_on", "updated_on")
    ordering = ("-created_on",)


@admin.register(OrderReturn)
class OrderReturnAdmin(admin.ModelAdmin):
    list_display = (
        "return_number", "order", "status", "reason",
        "refund_amount", "requested_at",
    )
    list_filter = ("status", "reason", "refund_method")
    search_fields = ("return_number",)
    readonly_fields = ("id", "created_on", "updated_on")
    ordering = ("-requested_at",)


@admin.register(OrderSettings)
class OrderSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "order_number_prefix", "default_currency", "tax_inclusive_pricing")
    readonly_fields = ("id", "created_on", "updated_on")
