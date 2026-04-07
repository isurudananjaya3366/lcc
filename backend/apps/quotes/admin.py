from django.contrib import admin

from apps.quotes.models import (
    Quote,
    QuoteHistory,
    QuoteLineItem,
    QuoteSequence,
    QuoteSettings,
    QuoteTemplate,
)


class QuoteLineItemInline(admin.TabularInline):
    model = QuoteLineItem
    extra = 0
    readonly_fields = ["discount_amount", "tax_amount", "line_total"]
    fields = [
        "position", "product_name", "quantity", "unit_of_measure",
        "unit_price", "discount_type", "discount_value", "discount_amount",
        "is_taxable", "tax_rate", "tax_amount", "line_total",
    ]


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = [
        "quote_number",
        "status",
        "customer",
        "guest_name",
        "total",
        "currency",
        "issue_date",
        "valid_until",
        "revision_number",
        "created_on",
    ]
    list_filter = ["status", "currency", "issue_date", "is_latest_revision"]
    search_fields = ["quote_number", "title", "guest_name", "guest_email"]
    readonly_fields = ["quote_number", "created_on", "updated_on"]
    ordering = ["-created_on"]
    inlines = [QuoteLineItemInline]


@admin.register(QuoteSequence)
class QuoteSequenceAdmin(admin.ModelAdmin):
    list_display = ["year", "last_number"]
    readonly_fields = ["year", "last_number"]


@admin.register(QuoteHistory)
class QuoteHistoryAdmin(admin.ModelAdmin):
    list_display = ["quote", "event_type", "user", "timestamp"]
    list_filter = ["event_type"]
    readonly_fields = ["quote", "event_type", "user", "timestamp", "old_values", "new_values", "notes"]
    ordering = ["-timestamp"]


@admin.register(QuoteSettings)
class QuoteSettingsAdmin(admin.ModelAdmin):
    list_display = ["tenant", "default_validity_days", "auto_expire_enabled"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(QuoteTemplate)
class QuoteTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "tenant", "is_default", "is_active", "theme", "page_size", "created_at"]
    list_filter = ["is_default", "is_active", "theme", "page_size"]
    search_fields = ["name", "business_name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("tenant", "name", "description", "is_default", "is_active")}),
        ("Header", {"fields": (
            "logo", "show_logo", "business_name", "business_address",
            "business_city", "business_postal_code", "business_country",
            "show_business_address", "phone_number", "email_address",
            "website", "show_contact_info",
            "company_registration_number", "tax_registration_number",
        )}),
        ("Styling", {"fields": (
            "primary_color", "secondary_color", "accent_color", "text_color",
            "header_font", "body_font", "font_size", "theme",
            "show_borders", "show_grid_lines", "line_spacing",
        )}),
        ("Content", {"fields": (
            "footer_text", "show_footer", "footer_alignment",
            "terms_and_conditions", "show_terms", "terms_title",
            "default_thank_you_message", "default_payment_instructions",
            "validity_message_template",
            "show_signature_line", "signature_label",
            "authorized_person_name", "authorized_person_title",
        )}),
        ("Layout", {"fields": (
            "page_size", "page_orientation",
            "margin_top", "margin_bottom", "margin_left", "margin_right",
            "layout_options",
        )}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
