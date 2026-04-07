"""
ReceiptTemplate model.

Stores customizable receipt template configurations per tenant,
including header, item display, totals, payment, footer, QR code,
and font settings. Supports template inheritance and cloning.
"""

from django.db import models

from apps.core.models import BaseModel

from ..constants import (
    FONT_SIZE_CHOICES,
    FONT_SIZE_LARGE,
    FONT_SIZE_NORMAL,
    LOGO_SIZE_CHOICES,
    LOGO_SIZE_MEDIUM,
    PAPER_SIZE_THERMAL_80MM,
    PAPER_SIZES,
    QR_CONTENT_TRANSACTION_ID,
    QR_CONTENT_TYPE_CHOICES,
    QR_POSITION_AFTER_FOOTER,
    QR_POSITION_CHOICES,
    QR_SIZE_CHOICES,
    QR_SIZE_MEDIUM,
    SEPARATOR_LENGTH_CHOICES,
    SEPARATOR_LENGTH_FULL,
    SEPARATOR_STYLE_CHOICES,
    SEPARATOR_STYLE_EQUALS,
)

DEFAULT_RETURN_POLICY = (
    "Items may be returned within 7 days of purchase "
    "with original receipt and tags attached."
)


class ReceiptTemplateManager(models.Manager):
    """Custom manager for ReceiptTemplate."""

    def get_default(self):
        """Return the default template, or the first active one."""
        template = self.filter(is_default=True, is_active=True).first()
        if template:
            return template
        return self.filter(is_active=True).first()

    def active(self):
        return self.filter(is_active=True)


class ReceiptTemplate(BaseModel):
    """
    Customizable receipt template configuration.

    Controls the visual layout, content visibility, and formatting
    of generated receipts. Each tenant can have multiple templates
    with one designated as default.

    Supports inheritance from a parent template and cloning.
    """

    # ── Core Fields (Task 04) ────────────────────────────────────────
    name = models.CharField(max_length=100)
    paper_size = models.CharField(
        max_length=10,
        choices=PAPER_SIZES,
        default=PAPER_SIZE_THERMAL_80MM,
    )
    is_default = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    # ── Header Configuration (Task 05) ──────────────────────────────
    show_logo = models.BooleanField(default=True)
    logo_size = models.CharField(
        max_length=10,
        choices=LOGO_SIZE_CHOICES,
        default=LOGO_SIZE_MEDIUM,
    )
    business_name_override = models.CharField(
        max_length=200, blank=True, null=True
    )
    show_business_name = models.BooleanField(default=True)
    business_name_bold = models.BooleanField(default=True)
    business_name_uppercase = models.BooleanField(default=False)

    # ── Header Text Fields (Task 06) ────────────────────────────────
    header_line_1 = models.CharField(max_length=200, blank=True, null=True)
    header_line_2 = models.CharField(max_length=200, blank=True, null=True)
    header_line_3 = models.CharField(max_length=200, blank=True, null=True)
    header_line_1_bold = models.BooleanField(default=False)
    header_line_2_bold = models.BooleanField(default=False)
    header_line_3_bold = models.BooleanField(default=False)
    header_line_1_center = models.BooleanField(default=True)
    header_line_2_center = models.BooleanField(default=True)
    header_line_3_center = models.BooleanField(default=True)

    # ── Address Display Settings (Task 07) ──────────────────────────
    show_address = models.BooleanField(default=True)
    show_phone = models.BooleanField(default=True)
    show_email = models.BooleanField(default=True)
    show_website = models.BooleanField(default=False)
    show_tax_number = models.BooleanField(default=True)
    address_separator = models.BooleanField(default=True)

    # ── Item Display Settings (Task 08) ─────────────────────────────
    show_sku = models.BooleanField(default=False)
    show_barcode = models.BooleanField(default=False)
    show_category = models.BooleanField(default=False)
    show_tax_per_item = models.BooleanField(default=False)
    show_discount_per_item = models.BooleanField(default=True)
    item_description_length = models.PositiveIntegerField(default=30)
    truncate_description = models.BooleanField(default=True)
    show_unit_price = models.BooleanField(default=True)

    # ── Totals Display Settings (Task 09) ───────────────────────────
    show_subtotal = models.BooleanField(default=True)
    show_tax_breakdown = models.BooleanField(default=True)
    show_total_tax = models.BooleanField(default=True)
    show_total_discount = models.BooleanField(default=True)
    show_savings = models.BooleanField(default=False)
    show_rounding = models.BooleanField(default=False)
    totals_separator = models.BooleanField(default=True)
    bold_grand_total = models.BooleanField(default=True)

    # ── Payment Display Settings (Task 10) ──────────────────────────
    show_payment_method = models.BooleanField(default=True)
    show_amount_tendered = models.BooleanField(default=True)
    show_change_given = models.BooleanField(default=True)
    show_balance_due = models.BooleanField(default=False)
    show_card_details = models.BooleanField(default=False)
    payment_separator = models.BooleanField(default=True)

    # ── Footer Configuration (Task 11) ──────────────────────────────
    footer_line_1 = models.CharField(max_length=200, blank=True, null=True)
    footer_line_2 = models.CharField(max_length=200, blank=True, null=True)
    footer_line_3 = models.CharField(max_length=200, blank=True, null=True)
    footer_line_1_bold = models.BooleanField(default=False)
    footer_line_2_bold = models.BooleanField(default=False)
    footer_line_3_bold = models.BooleanField(default=False)
    footer_line_1_center = models.BooleanField(default=True)
    footer_line_2_center = models.BooleanField(default=True)
    footer_line_3_center = models.BooleanField(default=True)
    footer_separator = models.BooleanField(default=True)

    # ── Return Policy (Task 12) ─────────────────────────────────────
    show_return_policy = models.BooleanField(default=False)
    return_policy_text = models.TextField(
        blank=True, null=True, default=DEFAULT_RETURN_POLICY
    )
    return_policy_heading = models.CharField(
        max_length=100, blank=True, null=True
    )
    return_policy_bold_heading = models.BooleanField(default=True)
    return_policy_separator = models.BooleanField(default=True)

    # ── QR Code Settings (Task 13) ──────────────────────────────────
    show_qr_code = models.BooleanField(default=False)
    qr_content_type = models.CharField(
        max_length=20,
        choices=QR_CONTENT_TYPE_CHOICES,
        default=QR_CONTENT_TRANSACTION_ID,
    )
    qr_code_size = models.CharField(
        max_length=10,
        choices=QR_SIZE_CHOICES,
        default=QR_SIZE_MEDIUM,
    )
    qr_label = models.CharField(max_length=100, blank=True, null=True)
    qr_position = models.CharField(
        max_length=20,
        choices=QR_POSITION_CHOICES,
        default=QR_POSITION_AFTER_FOOTER,
    )

    # ── Font Settings (Task 14) ─────────────────────────────────────
    font_size = models.CharField(
        max_length=10,
        choices=FONT_SIZE_CHOICES,
        default=FONT_SIZE_NORMAL,
    )
    header_font_size = models.CharField(
        max_length=10,
        choices=FONT_SIZE_CHOICES,
        default=FONT_SIZE_LARGE,
    )
    footer_font_size = models.CharField(
        max_length=10,
        choices=FONT_SIZE_CHOICES,
        default=FONT_SIZE_NORMAL,
    )
    use_bold_headers = models.BooleanField(default=True)
    separator_style = models.CharField(
        max_length=10,
        choices=SEPARATOR_STYLE_CHOICES,
        default=SEPARATOR_STYLE_EQUALS,
    )
    separator_length = models.CharField(
        max_length=10,
        choices=SEPARATOR_LENGTH_CHOICES,
        default=SEPARATOR_LENGTH_FULL,
    )

    # ── Template Inheritance (Task 15) ──────────────────────────────
    parent_template = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="child_templates",
    )
    is_system_default = models.BooleanField(default=False)
    inherits_from_parent = models.BooleanField(default=True)

    objects = ReceiptTemplateManager()
    all_with_deleted = models.Manager()

    class Meta(BaseModel.Meta):
        db_table = "pos_receipt_template"
        verbose_name = "Receipt Template"
        verbose_name_plural = "Receipt Templates"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_paper_size_display()})"

    def save(self, *args, **kwargs):
        # Ensure only one default template per tenant
        if self.is_default:
            ReceiptTemplate.objects.filter(is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)
        # Ensure only one system default
        if self.is_system_default:
            ReceiptTemplate.objects.filter(is_system_default=True).exclude(
                pk=self.pk
            ).update(is_system_default=False)
        # Prevent circular inheritance
        if self.parent_template:
            self._validate_no_circular_inheritance()
        super().save(*args, **kwargs)

    def _validate_no_circular_inheritance(self):
        """Ensure no circular reference in parent chain."""
        visited = {self.pk}
        parent = self.parent_template
        while parent is not None:
            if parent.pk in visited:
                raise ValueError("Circular template inheritance detected.")
            visited.add(parent.pk)
            parent = parent.parent_template

    def get_effective_value(self, field_name):
        """
        Get the effective value for a field, traversing the inheritance chain.

        If this template's field is None/empty and inherits_from_parent is True,
        returns the parent's value instead.
        """
        value = getattr(self, field_name, None)
        if value is not None and value != "":
            return value
        if self.inherits_from_parent and self.parent_template:
            return self.parent_template.get_effective_value(field_name)
        return value

    def get_inherited_fields(self):
        """Return a dict of all field values, resolving inheritance."""
        fields = {}
        for field in self._meta.concrete_fields:
            if field.attname not in ("id", "parent_template_id"):
                fields[field.attname] = self.get_effective_value(
                    field.attname
                )
        return fields

    def clone_template(self, new_name):
        """Create a duplicate of this template with a new name."""
        clone = ReceiptTemplate()
        for field in self._meta.concrete_fields:
            if field.attname not in (
                "id",
                "created_on",
                "updated_on",
            ):
                setattr(clone, field.attname, getattr(self, field.attname))
        clone.pk = None
        clone.name = new_name
        clone.is_default = False
        clone.is_system_default = False
        clone.save()
        return clone
