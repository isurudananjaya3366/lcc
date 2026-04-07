"""PayslipTemplate model for tenant-specific payslip PDF configuration."""

import re

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class PaperSize(models.TextChoices):
    """Paper size options for PDF generation."""

    A4 = "A4", "A4 (210mm × 297mm)"
    LETTER = "LETTER", "US Letter (8.5\" × 11\")"


class PayslipTemplate(UUIDMixin, TimestampMixin, models.Model):
    """Tenant-specific payslip PDF template configuration.

    Each tenant has one template controlling company branding,
    statutory details, footer text, color scheme, and display
    preferences for generated payslip PDFs.
    """

    # ── Tenant Relationship ──────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is currently in use.",
    )
    internal_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes about this template configuration.",
    )

    # ── Company Details ──────────────────────────────────────
    company_name = models.CharField(
        max_length=200,
        help_text="Company name displayed on payslip header.",
    )
    company_logo = models.ImageField(
        upload_to="payslip_templates/logos/",
        blank=True,
        null=True,
        help_text="Company logo for payslip header (PNG/JPG, max 2MB).",
    )
    company_address = models.TextField(
        help_text="Company address displayed on payslip header.",
    )
    company_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Company phone (e.g. +94 11 234 5678).",
    )
    company_email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        help_text="HR contact email for payslip queries.",
    )

    # ── Statutory Registration ───────────────────────────────
    epf_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Employees' Provident Fund registration number.",
    )
    etf_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Employees' Trust Fund registration number.",
    )

    # ── Footer ───────────────────────────────────────────────
    footer_text = models.TextField(
        blank=True,
        null=True,
        help_text="General footer text (contact info, portal links).",
    )
    disclaimer_text = models.TextField(
        blank=True,
        null=True,
        help_text="Legal disclaimer / confidentiality notice.",
    )
    show_footer = models.BooleanField(
        default=True,
        help_text="Display footer section on payslip.",
    )
    show_disclaimer = models.BooleanField(
        default=True,
        help_text="Display disclaimer section on payslip.",
    )

    # ── Style & Display ──────────────────────────────────────
    paper_size = models.CharField(
        max_length=10,
        choices=PaperSize.choices,
        default=PaperSize.A4,
        help_text="Paper size for PDF generation.",
    )
    primary_color = models.CharField(
        max_length=7,
        default="#2C3E50",
        help_text="Hex color for headers/accents (e.g. #2C3E50).",
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#7F8C8D",
        help_text="Hex color for subheadings/borders (e.g. #7F8C8D).",
    )
    show_employer_contributions = models.BooleanField(
        default=False,
        help_text="Show employer EPF/ETF contributions on payslip.",
    )
    show_ytd = models.BooleanField(
        default=True,
        help_text="Show year-to-date totals for earnings/deductions.",
    )
    show_bank_details = models.BooleanField(
        default=True,
        help_text="Show employee bank account details on payslip.",
    )

    class Meta:
        app_label = "payslip"
        verbose_name = "Payslip Template"
        verbose_name_plural = "Payslip Templates"

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"Payslip Template ({status})"

    def clean(self):
        """Validate hex color format."""
        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")
        if self.primary_color and not hex_pattern.match(self.primary_color):
            raise ValidationError(
                {"primary_color": "Must be a valid hex color (e.g. #2C3E50)."}
            )
        if self.secondary_color and not hex_pattern.match(self.secondary_color):
            raise ValidationError(
                {"secondary_color": "Must be a valid hex color (e.g. #7F8C8D)."}
            )
