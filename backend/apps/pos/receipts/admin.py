"""Django admin configuration for receipt models."""

from django.contrib import admin

from .models import Receipt, ReceiptTemplate


@admin.register(ReceiptTemplate)
class ReceiptTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "paper_size",
        "is_default",
        "is_system_default",
        "is_active",
        "created_on",
    )
    list_filter = ("paper_size", "is_default", "is_active", "is_system_default")
    search_fields = ("name", "description")
    readonly_fields = ("created_on", "updated_on", "template_preview")
    actions = [
        "clone_selected_templates",
        "set_as_default",
        "activate_templates",
        "deactivate_templates",
    ]

    fieldsets = (
        (None, {"fields": ("name", "paper_size", "description", "template_preview")}),
        (
            "Status",
            {"fields": ("is_active", "is_default", "is_system_default")},
        ),
        (
            "Header - Logo & Business Name",
            {
                "fields": (
                    "show_logo",
                    "logo_size",
                    "show_business_name",
                    "business_name_override",
                    "business_name_bold",
                    "business_name_uppercase",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Header - Custom Text",
            {
                "fields": (
                    "header_line_1",
                    "header_line_1_bold",
                    "header_line_1_center",
                    "header_line_2",
                    "header_line_2_bold",
                    "header_line_2_center",
                    "header_line_3",
                    "header_line_3_bold",
                    "header_line_3_center",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Address Display",
            {
                "fields": (
                    "show_address",
                    "show_phone",
                    "show_email",
                    "show_website",
                    "show_tax_number",
                    "address_separator",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Item Display",
            {
                "fields": (
                    "show_sku",
                    "show_barcode",
                    "show_category",
                    "show_unit_price",
                    "show_tax_per_item",
                    "show_discount_per_item",
                    "item_description_length",
                    "truncate_description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Totals Display",
            {
                "fields": (
                    "show_subtotal",
                    "show_tax_breakdown",
                    "show_total_tax",
                    "show_total_discount",
                    "show_savings",
                    "show_rounding",
                    "totals_separator",
                    "bold_grand_total",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Payment Display",
            {
                "fields": (
                    "show_payment_method",
                    "show_amount_tendered",
                    "show_change_given",
                    "show_balance_due",
                    "show_card_details",
                    "payment_separator",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Footer",
            {
                "fields": (
                    "footer_line_1",
                    "footer_line_1_bold",
                    "footer_line_1_center",
                    "footer_line_2",
                    "footer_line_2_bold",
                    "footer_line_2_center",
                    "footer_line_3",
                    "footer_line_3_bold",
                    "footer_line_3_center",
                    "footer_separator",
                    "show_return_policy",
                    "return_policy_text",
                    "return_policy_heading",
                    "return_policy_bold_heading",
                    "return_policy_separator",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "QR Code",
            {
                "fields": (
                    "show_qr_code",
                    "qr_content_type",
                    "qr_code_size",
                    "qr_label",
                    "qr_position",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Font & Separators",
            {
                "fields": (
                    "font_size",
                    "header_font_size",
                    "footer_font_size",
                    "use_bold_headers",
                    "separator_style",
                    "separator_length",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Template Inheritance",
            {
                "fields": (
                    "parent_template",
                    "inherits_from_parent",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.action(description="Clone selected templates")
    def clone_selected_templates(self, request, queryset):
        for template in queryset:
            template.clone_template(f"{template.name} (Copy)")
        self.message_user(
            request, f"Successfully cloned {queryset.count()} template(s)."
        )

    @admin.action(description="Set as default template")
    def set_as_default(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select exactly one template to set as default.",
                level="error",
            )
            return
        ReceiptTemplate.objects.filter(is_default=True).update(is_default=False)
        queryset.update(is_default=True)
        self.message_user(request, "Default template updated.")

    @admin.action(description="Activate selected templates")
    def activate_templates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} template(s).")

    @admin.action(description="Deactivate selected templates")
    def deactivate_templates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} template(s).")

    def template_preview(self, obj):
        """Read-only preview of template configuration summary."""
        if not obj or not obj.pk:
            return "-"
        sections = []
        if obj.show_logo:
            sections.append("Logo")
        if obj.show_business_name:
            sections.append("Business Name")
        if obj.show_address:
            sections.append("Address")
        if obj.show_qr_code:
            sections.append("QR Code")
        if obj.show_return_policy:
            sections.append("Return Policy")
        return f"{obj.paper_size} | Sections: {', '.join(sections) or 'None'}"

    template_preview.short_description = "Template Preview"


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "receipt_type",
        "cart",
        "generated_at",
        "was_printed",
        "was_emailed",
        "reprint_count",
    )
    list_filter = ("receipt_type", "generated_at")
    search_fields = ("receipt_number", "cart__reference_number")
    readonly_fields = (
        "receipt_number",
        "cart",
        "transaction_id",
        "receipt_type",
        "template",
        "generated_at",
        "printed_at",
        "emailed_at",
        "receipt_data",
        "original_receipt",
        "reprint_count",
        "generated_by",
        "created_on",
        "updated_on",
    )
    date_hierarchy = "generated_at"
    raw_id_fields = ("cart", "template", "original_receipt", "generated_by")

    fieldsets = (
        (None, {"fields": ("receipt_number", "receipt_type", "cart")}),
        (
            "Details",
            {
                "fields": (
                    "transaction_id",
                    "template",
                    "generated_by",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "generated_at",
                    "printed_at",
                    "emailed_at",
                    "created_on",
                    "updated_on",
                ),
            },
        ),
        (
            "Duplicate Info",
            {
                "fields": ("original_receipt", "reprint_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Receipt Data (JSON)",
            {
                "fields": ("receipt_data",),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
