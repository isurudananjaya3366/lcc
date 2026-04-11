"""
Accounting enumerations module.

Defines enumeration types for the Chart of Accounts and Journal Entry
systems following double-entry bookkeeping principles. Includes account
types, categories, statuses, normal balance indicators, journal entry
types, journal entry statuses, and journal source identifiers.
"""

from django.db import models


class AccountType(models.TextChoices):
    """
    Five fundamental account types in double-entry bookkeeping.

    Accounting equation: Assets = Liabilities + Equity + (Revenue - Expenses)
    """

    ASSET = "ASSET", "Asset"
    LIABILITY = "LIABILITY", "Liability"
    EQUITY = "EQUITY", "Equity"
    REVENUE = "REVENUE", "Revenue"
    EXPENSE = "EXPENSE", "Expense"


class AccountCategory(models.TextChoices):
    """
    Sub-classification within each account type.

    CURRENT / NON_CURRENT: Assets, Liabilities
    OPERATING / NON_OPERATING: Revenue, Expenses
    OWNER_CAPITAL / RETAINED_EARNINGS: Equity
    OTHER: All types
    """

    CURRENT = "CURRENT", "Current"
    NON_CURRENT = "NON_CURRENT", "Non-Current"
    OPERATING = "OPERATING", "Operating"
    NON_OPERATING = "NON_OPERATING", "Non-Operating"
    OWNER_CAPITAL = "OWNER_CAPITAL", "Owner Capital"
    RETAINED_EARNINGS = "RETAINED_EARNINGS", "Retained Earnings"
    OTHER = "OTHER", "Other"


class AccountStatus(models.TextChoices):
    """Account lifecycle status."""

    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    ARCHIVED = "ARCHIVED", "Archived"


class NormalBalance(models.TextChoices):
    """
    Normal balance side for an account type.

    DEBIT: Assets, Expenses (increase with debits)
    CREDIT: Liabilities, Equity, Revenue (increase with credits)
    """

    DEBIT = "DEBIT", "Debit"
    CREDIT = "CREDIT", "Credit"


# ════════════════════════════════════════════════════════════════════════
# Journal Entry Enumerations (SP09)
# ════════════════════════════════════════════════════════════════════════


class JournalEntryType(models.TextChoices):
    """
    Journal entry type categorisation.

    MANUAL:    User-created entries (corrections, manual adjustments).
    AUTO:      System-generated from business transactions (sales, purchases).
    ADJUSTING: Period-end adjustments (accruals, deferrals, provisions).
    REVERSING: Auto-generated to reverse adjusting entries at period start.
    """

    MANUAL = "MANUAL", "Manual Entry"
    AUTO = "AUTO", "Auto-Generated"
    ADJUSTING = "ADJUSTING", "Adjusting Entry"
    REVERSING = "REVERSING", "Reversing Entry"


class JournalEntryStatus(models.TextChoices):
    """
    Journal entry lifecycle status.

    Workflow: DRAFT → PENDING_APPROVAL → APPROVED → POSTED → (VOID)
    """

    DRAFT = "DRAFT", "Draft"
    PENDING_APPROVAL = "PENDING_APPROVAL", "Pending Approval"
    APPROVED = "APPROVED", "Approved"
    POSTED = "POSTED", "Posted"
    VOID = "VOID", "Void"


class JournalSource(models.TextChoices):
    """
    Origin or source system of a journal entry.

    Identifies which business process generated the entry for
    source-specific reporting and reconciliation.
    """

    SALES = "SALES", "Sales"
    PURCHASE = "PURCHASE", "Purchase"
    PAYROLL = "PAYROLL", "Payroll"
    INVENTORY = "INVENTORY", "Inventory"
    BANKING = "BANKING", "Banking"
    MANUAL = "MANUAL", "Manual Entry"
    ADJUSTMENT = "ADJUSTMENT", "Adjustment"


# ════════════════════════════════════════════════════════════════════════
# Template & Recurring Enumerations (SP09 Group D)
# ════════════════════════════════════════════════════════════════════════


class TemplateCategory(models.TextChoices):
    """Category for journal entry templates."""

    GENERAL = "GENERAL", "General"
    MONTH_END = "MONTH_END", "Month-End"
    PAYROLL = "PAYROLL", "Payroll"
    DEPRECIATION = "DEPRECIATION", "Depreciation"
    ACCRUALS = "ACCRUALS", "Accruals"
    CUSTOM = "CUSTOM", "Custom"


class RecurringFrequency(models.TextChoices):
    """Frequency options for recurring journal entries."""

    DAILY = "DAILY", "Daily"
    WEEKLY = "WEEKLY", "Weekly"
    MONTHLY = "MONTHLY", "Monthly"
    QUARTERLY = "QUARTERLY", "Quarterly"
    YEARLY = "YEARLY", "Yearly"


# ════════════════════════════════════════════════════════════════════════
# Accounting Period Enumerations (SP09 Group E)
# ════════════════════════════════════════════════════════════════════════


class PeriodStatus(models.TextChoices):
    """
    Accounting period lifecycle status.

    OPEN:   Accept new entries and edits.
    CLOSED: No regular entries; adjusting entries only.
    LOCKED: No changes allowed (post year-end audit).
    """

    OPEN = "OPEN", "Open"
    CLOSED = "CLOSED", "Closed"
    LOCKED = "LOCKED", "Locked"
