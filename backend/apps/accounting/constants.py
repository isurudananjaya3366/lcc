"""
Accounting constants module.

Defines choices, types, and other constants used across
the accounting application models.
"""

# ════════════════════════════════════════════════════════════════════════
# Account Type Choices
# ════════════════════════════════════════════════════════════════════════

ACCOUNT_TYPE_ASSET = "asset"
ACCOUNT_TYPE_LIABILITY = "liability"
ACCOUNT_TYPE_EQUITY = "equity"
ACCOUNT_TYPE_REVENUE = "revenue"
ACCOUNT_TYPE_EXPENSE = "expense"

ACCOUNT_TYPE_CHOICES = [
    (ACCOUNT_TYPE_ASSET, "Asset"),
    (ACCOUNT_TYPE_LIABILITY, "Liability"),
    (ACCOUNT_TYPE_EQUITY, "Equity"),
    (ACCOUNT_TYPE_REVENUE, "Revenue"),
    (ACCOUNT_TYPE_EXPENSE, "Expense"),
]


# ════════════════════════════════════════════════════════════════════════
# Journal Entry Status Choices
# ════════════════════════════════════════════════════════════════════════

ENTRY_STATUS_DRAFT = "draft"
ENTRY_STATUS_POSTED = "posted"
ENTRY_STATUS_REVERSED = "reversed"

ENTRY_STATUS_CHOICES = [
    (ENTRY_STATUS_DRAFT, "Draft"),
    (ENTRY_STATUS_POSTED, "Posted"),
    (ENTRY_STATUS_REVERSED, "Reversed"),
]

# Default journal entry status
DEFAULT_ENTRY_STATUS = ENTRY_STATUS_DRAFT
