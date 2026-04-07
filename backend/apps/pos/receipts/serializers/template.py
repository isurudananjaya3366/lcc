"""
ReceiptTemplate serializers — Task 70, 76.

Serializers for ReceiptTemplate model CRUD, clone, preview, and usage endpoints.
"""

from rest_framework import serializers

from apps.pos.receipts.models import ReceiptTemplate


class ReceiptTemplateListSerializer(serializers.ModelSerializer):
    """Compact template for list views."""

    receipt_count = serializers.SerializerMethodField()
    paper_size_display = serializers.CharField(
        source="get_paper_size_display", read_only=True
    )

    class Meta:
        model = ReceiptTemplate
        fields = [
            "id",
            "name",
            "paper_size",
            "paper_size_display",
            "is_default",
            "is_system_default",
            "description",
            "receipt_count",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "is_system_default",
            "receipt_count",
            "created_on",
            "updated_on",
        ]

    def get_receipt_count(self, obj):
        return obj.receipts.count()


class ReceiptTemplateDetailSerializer(serializers.ModelSerializer):
    """Full template detail with all configuration fields."""

    paper_size_display = serializers.CharField(
        source="get_paper_size_display", read_only=True
    )
    parent_template_name = serializers.SerializerMethodField()
    child_count = serializers.SerializerMethodField()

    class Meta:
        model = ReceiptTemplate
        fields = [
            # Core
            "id",
            "name",
            "paper_size",
            "paper_size_display",
            "is_default",
            "is_system_default",
            "description",
            # Header
            "show_logo",
            "logo_size",
            "business_name_override",
            "show_business_name",
            "business_name_bold",
            "business_name_uppercase",
            "header_line_1",
            "header_line_2",
            "header_line_3",
            "header_line_1_bold",
            "header_line_2_bold",
            "header_line_3_bold",
            # Address
            "show_address",
            "show_phone",
            "show_email",
            "show_website",
            "show_tax_number",
            "address_separator",
            # Items
            "show_sku",
            "show_barcode",
            "show_category",
            "show_tax_per_item",
            "show_discount_per_item",
            "item_description_length",
            "truncate_description",
            "show_unit_price",
            # Totals
            "show_subtotal",
            "show_tax_breakdown",
            "show_total_tax",
            "show_total_discount",
            "show_savings",
            "show_rounding",
            "totals_separator",
            "bold_grand_total",
            # Payment
            "show_payment_method",
            "show_amount_tendered",
            "show_change_given",
            "show_balance_due",
            "show_card_details",
            "payment_separator",
            # Footer
            "footer_line_1",
            "footer_line_2",
            "footer_line_3",
            "footer_line_1_bold",
            "footer_line_2_bold",
            "footer_line_3_bold",
            "footer_line_1_center",
            "footer_line_2_center",
            "footer_line_3_center",
            "footer_separator",
            "return_policy_text",
            # QR
            "show_qr_code",
            "qr_content_type",
            "qr_code_size",
            "qr_label",
            "qr_position",
            # Font
            "font_size",
            "header_font_size",
            "footer_font_size",
            "use_bold_headers",
            "separator_style",
            "separator_length",
            # Inheritance
            "parent_template",
            "parent_template_name",
            "inherits_from_parent",
            "child_count",
            # Meta
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "is_system_default",
            "parent_template_name",
            "child_count",
            "created_on",
            "updated_on",
        ]

    def get_parent_template_name(self, obj):
        if obj.parent_template:
            return obj.parent_template.name
        return None

    def get_child_count(self, obj):
        return obj.child_templates.count()

    def validate_name(self, value):
        """Ensure template name is unique within the tenant."""
        qs = ReceiptTemplate.objects.filter(name=value, is_active=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A template with this name already exists."
            )
        return value


# ── Action Serializers ──────────────────────────────────────────


class TemplateCloneSerializer(serializers.Serializer):
    """Request schema for cloning a template."""

    new_name = serializers.CharField(
        max_length=100,
        help_text="Name for the cloned template",
    )

    def validate_new_name(self, value):
        if ReceiptTemplate.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError(
                "A template with this name already exists."
            )
        return value


class TemplatePreviewSerializer(serializers.Serializer):
    """Request schema for previewing a template."""

    format = serializers.ChoiceField(
        choices=["html", "pdf", "thermal"],
        default="html",
    )
