"""
POTemplate model for the purchases application.

Stores PDF template configuration for purchase order documents.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class POTemplate(UUIDMixin, TimestampMixin, models.Model):
    """Template configuration for PO PDF generation."""

    template_name = models.CharField(max_length=100, default="Default")
    is_active = models.BooleanField(default=True)

    # Company Info
    company_name = models.CharField(max_length=200, blank=True, default="")
    company_address = models.TextField(blank=True, default="")
    company_phone = models.CharField(max_length=20, blank=True, default="")
    company_email = models.EmailField(blank=True, default="")
    company_website = models.URLField(blank=True, default="")
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Company tax identification number",
    )
    logo = models.ImageField(
        upload_to="po_templates/",
        null=True,
        blank=True,
    )

    # Header / Content
    header_text = models.TextField(
        blank=True,
        default="",
        help_text="Custom text to display in the header area",
    )
    footer_text = models.TextField(blank=True, default="")

    # Styling - Colors
    primary_color = models.CharField(max_length=7, default="#000000")
    secondary_color = models.CharField(max_length=7, default="#666666")

    # Styling - Fonts
    font_family = models.CharField(max_length=50, default="Helvetica")
    font_size_header = models.PositiveIntegerField(
        default=16,
        help_text="Font size for headers (pt)",
    )
    font_size_body = models.PositiveIntegerField(
        default=10,
        help_text="Font size for body text (pt)",
    )

    # Display Options
    show_logo = models.BooleanField(default=True)
    show_line_numbers = models.BooleanField(
        default=True,
        help_text="Show line numbers in items table",
    )
    show_item_codes = models.BooleanField(
        default=True,
        help_text="Show product/SKU codes in items table",
    )
    show_tax_breakdown = models.BooleanField(
        default=True,
        help_text="Show individual tax breakdown in totals",
    )

    # Page Settings
    page_size = models.CharField(
        max_length=20,
        default="A4",
        choices=[("A4", "A4"), ("Letter", "Letter")],
    )
    paper_orientation = models.CharField(
        max_length=20,
        default="Portrait",
        choices=[("Portrait", "Portrait"), ("Landscape", "Landscape")],
    )

    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "PO Template"
        verbose_name_plural = "PO Templates"
        ordering = ["-is_default", "template_name"]

    def __str__(self):
        return self.template_name

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default template per tenant
            POTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )
        super().save(*args, **kwargs)
