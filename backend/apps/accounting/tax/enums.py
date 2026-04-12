"""
Tax-related enumerations for Sri Lankan tax compliance.

Defines standardized choices for tax types, filing periods, and
filing statuses used across the tax reporting module.
"""

from django.db import models


class TaxType(models.TextChoices):
    """Sri Lankan tax types handled by the system."""

    VAT = "vat", "Value Added Tax (VAT)"
    PAYE = "paye", "Pay As You Earn (PAYE)"
    EPF = "epf", "Employees Provident Fund (EPF)"
    ETF = "etf", "Employees Trust Fund (ETF)"
    WHT = "wht", "Withholding Tax (WHT)"


class TaxPeriod(models.TextChoices):
    """Tax filing frequency types."""

    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"
    ANNUAL = "annual", "Annual"


class FilingStatus(models.TextChoices):
    """Tax filing lifecycle statuses."""

    PENDING = "pending", "Pending"
    GENERATED = "generated", "Generated"
    FILED = "filed", "Filed"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
