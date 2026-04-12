"""
Tax configuration model.

Stores tenant-specific tax registration details and filing preferences
for Sri Lankan tax compliance (VAT, PAYE, EPF, ETF, WHT).
"""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from apps.core.mixins import UUIDMixin

from ..tax.enums import TaxPeriod

# ── Validators ──────────────────────────────────────────────────────
vat_number_validator = RegexValidator(
    regex=r"^\d{9}-7000$",
    message="VAT number must be in format XXXXXXXXX-7000 (9 digits, hyphen, 7000).",
)

epf_number_validator = RegexValidator(
    regex=r"^E/\d{6}$",
    message="EPF number must be in format E/XXXXXX (E/ prefix followed by 6 digits).",
)

etf_number_validator = RegexValidator(
    regex=r"^\d{6}$",
    message="ETF number must be a 6-digit numeric sequence.",
)

tin_number_validator = RegexValidator(
    regex=r"^\d{9}$",
    message="TIN must be a 9-digit numeric sequence.",
)


class TaxConfiguration(UUIDMixin, models.Model):
    """
    Tenant-specific tax registration details and filing preferences.

    Each tenant has one TaxConfiguration storing their VAT, EPF, ETF
    registration numbers, employer TIN, and VAT filing frequency.
    """

    # ── VAT Registration ────────────────────────────────────────────
    vat_registration_no = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[vat_number_validator],
        verbose_name="VAT Registration Number",
        help_text="VAT registration number issued by IRD (format: XXXXXXXXX-7000).",
    )
    is_svat_registered = models.BooleanField(
        default=False,
        verbose_name="SVAT Registered",
        help_text="Whether the business is registered under Simplified VAT scheme.",
    )
    vat_filing_period = models.CharField(
        max_length=20,
        choices=TaxPeriod.choices,
        blank=True,
        null=True,
        verbose_name="VAT Filing Period",
        help_text="VAT filing frequency: Monthly (>75M turnover) or Quarterly (SVAT 12M-75M).",
    )

    # ── Payroll Tax Registration ────────────────────────────────────
    epf_registration_no = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[epf_number_validator],
        verbose_name="EPF Registration Number",
        help_text="EPF registration number issued by Central Bank (format: E/XXXXXX).",
    )
    etf_registration_no = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[etf_number_validator],
        verbose_name="ETF Registration Number",
        help_text="ETF registration number issued by ETF Board (6-digit numeric).",
    )

    # ── Employer Identification ─────────────────────────────────────
    tin_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[tin_number_validator],
        verbose_name="Tax Identification Number (TIN)",
        help_text="Employer TIN issued by Inland Revenue Department (9-digit numeric).",
    )

    # ── Timestamps ──────────────────────────────────────────────────
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_tax_configuration"
        verbose_name = "Tax Configuration"
        verbose_name_plural = "Tax Configurations"
        ordering = ["-created_at"]

    def __str__(self):
        parts = []
        if self.vat_registration_no:
            parts.append(f"VAT: {self.vat_registration_no}")
        if self.tin_number:
            parts.append(f"TIN: {self.tin_number}")
        return " | ".join(parts) if parts else f"Tax Config #{str(self.id)[:8]}"

    def clean(self):
        super().clean()
        if self.vat_registration_no and not self.vat_filing_period:
            raise ValidationError(
                {"vat_filing_period": "VAT filing period is required for VAT-registered businesses."}
            )
