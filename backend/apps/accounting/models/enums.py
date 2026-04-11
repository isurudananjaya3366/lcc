"""
Accounting enumerations module.

Defines enumeration types for the Chart of Accounts system following
double-entry bookkeeping principles. Includes account types, categories,
statuses, and normal balance indicators.
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
