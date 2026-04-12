"""
Financial report enumerations.

Defines report type and period enumerations for the financial
reporting system.
"""

from django.db import models


class ReportType(models.TextChoices):
    """
    Supported financial report types.

    Each type corresponds to a standard financial statement
    or reporting format used in accounting.
    """

    TRIAL_BALANCE = "TRIAL_BALANCE", "Trial Balance"
    PROFIT_LOSS = "PROFIT_LOSS", "Profit & Loss Statement"
    BALANCE_SHEET = "BALANCE_SHEET", "Balance Sheet"
    CASH_FLOW = "CASH_FLOW", "Cash Flow Statement"
    GENERAL_LEDGER = "GENERAL_LEDGER", "General Ledger"


class ReportPeriod(models.TextChoices):
    """
    Supported reporting period types.

    Sri Lankan fiscal year runs April 1 to March 31.
    Quarters: Q1 Apr-Jun, Q2 Jul-Sep, Q3 Oct-Dec, Q4 Jan-Mar.
    """

    MONTHLY = "MONTHLY", "Monthly"
    QUARTERLY = "QUARTERLY", "Quarterly"
    YEARLY = "YEARLY", "Yearly"
    CUSTOM = "CUSTOM", "Custom Date Range"


class DetailLevel(models.TextChoices):
    """Controls the granularity of report output."""

    SUMMARY = "SUMMARY", "Summary"
    DETAIL = "DETAIL", "Detailed"


class ComparisonType(models.TextChoices):
    """Type of comparison period for variance analysis."""

    PRIOR_PERIOD = "PRIOR_PERIOD", "Prior Period"
    PRIOR_YEAR = "PRIOR_YEAR", "Prior Year"
    CUSTOM = "CUSTOM", "Custom"
