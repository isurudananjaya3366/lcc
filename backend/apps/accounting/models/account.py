"""
Account model for the accounting application.

Defines the Account model which represents entries in the chart
of accounts. Each account has a unique code, a type (asset,
liability, equity, revenue, expense), and a name. Accounts
support a parent hierarchy for sub-accounts.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.accounting.constants import ACCOUNT_TYPE_CHOICES


class Account(UUIDMixin, TimestampMixin, models.Model):
    """
    Chart of accounts entry.

    Represents a single account in the chart of accounts used
    for double-entry bookkeeping. Accounts are categorised by
    type (asset, liability, equity, revenue, expense) and
    identified by a unique code within the tenant.

    Fields:
        code: Unique account code (e.g. 1000, 2100, 4000).
        name: Human-readable account name.
        account_type: Category of the account.
        parent: Optional parent account for sub-account hierarchy.
        description: Optional description of account purpose.
        is_active: Whether the account is currently in use.
        is_system: Whether this is a system-generated account.
    """

    # ── Account Code ────────────────────────────────────────────────
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Account Code",
        help_text=(
            "Unique account code within the tenant. "
            "Standard chart of accounts numbering (e.g. 1000, 2100)."
        ),
    )

    # ── Name ────────────────────────────────────────────────────────
    name = models.CharField(
        max_length=200,
        verbose_name="Account Name",
        help_text="Human-readable account name.",
    )

    # ── Account Type ────────────────────────────────────────────────
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        db_index=True,
        verbose_name="Account Type",
        help_text=(
            "Category of account: asset, liability, equity, "
            "revenue, or expense. Determines reporting position."
        ),
    )

    # ── Parent Account ──────────────────────────────────────────────
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent Account",
        help_text="Parent account for sub-account hierarchy.",
    )

    # ── Description ─────────────────────────────────────────────────
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Optional description of the account's purpose.",
    )

    # ── Flags ───────────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether the account is currently in use.",
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name="System Account",
        help_text="Whether this is a system-generated account.",
    )

    class Meta:
        db_table = "accounting_account"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ["code"]
        indexes = [
            models.Index(
                fields=["account_type", "is_active"],
                name="idx_account_type_active",
            ),
            models.Index(
                fields=["code"],
                name="idx_account_code",
            ),
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def is_debit_normal(self):
        """Return True if this account type normally carries a debit balance."""
        return self.account_type in ("asset", "expense")

    @property
    def is_credit_normal(self):
        """Return True if this account type normally carries a credit balance."""
        return self.account_type in ("liability", "equity", "revenue")
