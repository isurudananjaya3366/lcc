"""Admin configuration for the Vendor Bills application."""

from django.contrib import admin

from apps.vendor_bills.models import (
    BillHistory,
    BillLineItem,
    BillSettings,
    MatchingResult,
    PaymentSchedule,
    VendorBill,
    VendorPayment,
)


class BillLineItemInline(admin.TabularInline):
    model = BillLineItem
    extra = 0
    readonly_fields = ["tax_amount", "line_total"]


@admin.register(VendorBill)
class VendorBillAdmin(admin.ModelAdmin):
    """Admin for VendorBill model."""

    list_display = [
        "bill_number",
        "vendor",
        "status",
        "bill_date",
        "due_date",
        "total",
        "amount_paid",
        "is_matched",
    ]
    list_filter = ["status", "is_matched", "payment_terms"]
    search_fields = ["bill_number", "vendor_invoice_number"]
    readonly_fields = ["bill_number", "created_on", "updated_on"]
    date_hierarchy = "bill_date"
    inlines = [BillLineItemInline]


@admin.register(BillLineItem)
class BillLineItemAdmin(admin.ModelAdmin):
    list_display = ["vendor_bill", "line_number", "item_description", "quantity", "billed_price", "line_total"]
    list_filter = ["vendor_bill__status"]
    search_fields = ["item_description", "vendor_sku"]


@admin.register(MatchingResult)
class MatchingResultAdmin(admin.ModelAdmin):
    list_display = ["vendor_bill", "bill_line", "match_status", "is_within_tolerance"]
    list_filter = ["match_status", "is_within_tolerance"]


@admin.register(BillHistory)
class BillHistoryAdmin(admin.ModelAdmin):
    list_display = ["vendor_bill", "change_type", "changed_by", "created_on"]
    list_filter = ["change_type"]
    readonly_fields = ["created_on"]
    date_hierarchy = "created_on"


@admin.register(BillSettings)
class BillSettingsAdmin(admin.ModelAdmin):
    list_display = ["tenant", "bill_number_prefix", "require_approval", "approval_threshold"]


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ["payment_number", "vendor", "amount", "payment_date", "payment_method", "status"]
    list_filter = ["status", "payment_method", "is_advance"]
    search_fields = ["payment_number", "reference", "transaction_id"]
    readonly_fields = ["payment_number", "created_on", "updated_on"]
    date_hierarchy = "payment_date"


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ["vendor_bill", "scheduled_date", "amount", "status", "reminder_sent"]
    list_filter = ["status", "reminder_sent"]
    date_hierarchy = "scheduled_date"
