"""Invoice admin configuration."""

from django.contrib import admin

from apps.invoices.models import Invoice, InvoiceHistory, InvoiceLineItem, InvoiceSettings
from apps.invoices.models.invoice_template import InvoiceTemplate


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    readonly_fields = ["discount_amount", "tax_amount", "line_total"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "type",
        "status",
        "customer_name",
        "total",
        "balance_due",
        "currency",
        "issue_date",
        "due_date",
        "created_on",
    ]
    list_filter = ["status", "type", "tax_scheme", "currency"]
    search_fields = ["invoice_number", "customer_name", "customer_email"]
    readonly_fields = [
        "invoice_number",
        "subtotal",
        "discount_amount",
        "tax_amount",
        "total",
        "amount_paid",
        "balance_due",
        "base_currency_total",
        "tax_breakdown",
        "pdf_generated_at",
        "created_on",
        "updated_on",
    ]
    inlines = [InvoiceLineItemInline]
    date_hierarchy = "created_on"


@admin.register(InvoiceHistory)
class InvoiceHistoryAdmin(admin.ModelAdmin):
    list_display = ["invoice", "action", "old_status", "new_status", "user", "created_on"]
    list_filter = ["action"]
    readonly_fields = ["invoice", "action", "old_status", "new_status", "user", "notes", "metadata", "created_on"]


@admin.register(InvoiceSettings)
class InvoiceSettingsAdmin(admin.ModelAdmin):
    list_display = ["tenant", "default_due_days", "default_payment_terms"]


@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "tenant", "is_active", "is_default"]
    list_filter = ["is_active", "is_default"]
