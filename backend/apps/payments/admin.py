"""Payment admin configuration."""

from django.contrib import admin

from apps.payments.models import (
    Payment,
    PaymentAllocation,
    PaymentHistory,
    PaymentMethodConfig,
    PaymentReceipt,
    PaymentSettings,
    Refund,
)


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 0
    readonly_fields = ["created_on"]


class PaymentHistoryInline(admin.TabularInline):
    model = PaymentHistory
    extra = 0
    readonly_fields = ["action", "old_value", "new_value", "changed_by", "changed_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "payment_number",
        "method",
        "status",
        "amount",
        "currency",
        "customer",
        "invoice",
        "payment_date",
        "created_on",
    ]
    list_filter = ["status", "method", "currency"]
    search_fields = ["payment_number", "reference_number", "transaction_id"]
    readonly_fields = [
        "payment_number",
        "processed_at",
        "cancelled_at",
        "amount_in_base_currency",
        "created_on",
        "updated_on",
    ]
    raw_id_fields = ["invoice", "order", "customer", "received_by", "approved_by"]
    date_hierarchy = "payment_date"
    ordering = ["-created_on"]
    inlines = [PaymentAllocationInline, PaymentHistoryInline]


@admin.register(PaymentMethodConfig)
class PaymentMethodConfigAdmin(admin.ModelAdmin):
    list_display = ["method", "display_name", "is_active", "display_order", "min_amount", "max_amount"]
    list_filter = ["is_active"]
    search_fields = ["method", "display_name"]
    ordering = ["display_order"]


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ["default_currency", "approval_threshold", "auto_complete_cash", "enable_processing_fees"]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = [
        "refund_number",
        "original_payment",
        "amount",
        "reason",
        "refund_method",
        "status",
        "created_on",
    ]
    list_filter = ["status", "reason", "refund_method"]
    search_fields = ["refund_number", "original_payment__payment_number"]
    readonly_fields = [
        "refund_number",
        "approved_at",
        "processed_at",
        "created_on",
        "updated_on",
    ]
    raw_id_fields = ["original_payment", "requested_by", "approved_by", "processed_by"]
    ordering = ["-created_on"]


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = [
        "receipt_number",
        "payment",
        "customer",
        "receipt_amount",
        "currency",
        "receipt_date",
        "is_sent",
    ]
    list_filter = ["is_sent", "currency", "payment_method"]
    search_fields = ["receipt_number", "payment__payment_number"]
    readonly_fields = [
        "receipt_number",
        "pdf_generated_at",
        "sent_at",
        "created_on",
        "updated_on",
    ]
    raw_id_fields = ["payment", "invoice", "customer", "sent_by"]
    date_hierarchy = "receipt_date"
    ordering = ["-receipt_date"]
