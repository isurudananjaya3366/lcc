"""Purchases admin configuration."""

from django.contrib import admin

from apps.purchases.models.purchase_order import PurchaseOrder
from apps.purchases.models.po_line_item import POLineItem
from apps.purchases.models.po_history import POHistory
from apps.purchases.models.po_settings import POSettings
from apps.purchases.models.goods_receipt import GoodsReceipt
from apps.purchases.models.grn_line_item import GRNLineItem
from apps.purchases.models.po_template import POTemplate


class POLineItemInline(admin.TabularInline):
    """Inline admin for PO line items."""

    model = POLineItem
    extra = 0
    readonly_fields = ["line_total", "tax_amount"]


class POHistoryInline(admin.TabularInline):
    """Inline admin for PO history entries."""

    model = POHistory
    extra = 0
    readonly_fields = [
        "changed_by", "change_type", "old_status", "new_status",
        "description", "changes", "created_on",
    ]
    can_delete = False


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin configuration for PurchaseOrder."""

    list_display = [
        "po_number",
        "vendor",
        "status",
        "order_date",
        "total",
        "payment_status",
        "created_on",
    ]
    list_filter = ["status", "payment_status", "order_date"]
    search_fields = ["po_number", "vendor__company_name", "vendor_reference"]
    readonly_fields = ["po_number", "created_on", "updated_on"]
    date_hierarchy = "order_date"
    inlines = [POLineItemInline, POHistoryInline]


@admin.register(POSettings)
class POSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for POSettings."""

    list_display = [
        "po_number_prefix",
        "default_currency",
        "requires_approval_above",
        "auto_send_email",
    ]


class GRNLineItemInline(admin.TabularInline):
    """Inline admin for GRN line items."""

    model = GRNLineItem
    extra = 0
    readonly_fields = ["quantity_received", "quantity_rejected", "condition"]


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    """Admin configuration for GoodsReceipt."""

    list_display = [
        "grn_number",
        "purchase_order",
        "received_by",
        "received_at",
        "inspection_status",
    ]
    list_filter = ["inspection_status"]
    search_fields = ["grn_number", "purchase_order__po_number"]
    readonly_fields = ["grn_number", "received_at", "created_on", "updated_on"]
    inlines = [GRNLineItemInline]


@admin.register(POTemplate)
class POTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for POTemplate."""

    list_display = ["template_name", "company_name", "is_default"]
    list_filter = ["is_default"]
