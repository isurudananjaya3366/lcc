"""
Account model for the accounting application.

Defines the Account model which represents entries in the chart
of accounts using MPTT for hierarchical tree structure. Each account
has a unique code, a type (asset, liability, equity, revenue, expense),
and a name. Accounts support parent-child hierarchy via TreeForeignKey.
"""

from decimal import Decimal

from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from apps.accounting.constants import ACCOUNT_TYPE_CHOICES
from apps.accounting.models.enums import (
    AccountCategory,
    AccountStatus,
    AccountType,
    NormalBalance,
)
from apps.core.mixins import TimestampMixin, UUIDMixin


class Account(UUIDMixin, TimestampMixin, MPTTModel):
    """
    Chart of accounts entry with MPTT hierarchy.

    Represents a single account in the chart of accounts used
    for double-entry bookkeeping. Uses MPTT for efficient tree
    traversal, ancestor/descendant queries, and balance aggregation.
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

    # ── Account Type (CharField for backward compat) ────────────────
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

    # ── Account Type Config FK ──────────────────────────────────────
    account_type_config = models.ForeignKey(
        "accounting.AccountTypeConfig",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="accounts",
        verbose_name="Account Type Configuration",
        help_text="Link to the account type configuration for code range and balance rules.",
    )

    # ── Account Category ────────────────────────────────────────────
    category = models.CharField(
        max_length=30,
        choices=AccountCategory.choices,
        default=AccountCategory.OTHER,
        db_index=True,
        verbose_name="Category",
        help_text="Sub-classification within the account type.",
    )

    # ── Account Status ──────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        db_index=True,
        verbose_name="Status",
        help_text="Account lifecycle status.",
    )

    # ── Parent Account (MPTT TreeForeignKey) ────────────────────────
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
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
        help_text="Whether this is a system-generated account that cannot be deleted.",
    )
    is_header = models.BooleanField(
        default=False,
        verbose_name="Header Account",
        help_text="Header/summary accounts group child accounts and cannot hold transactions.",
    )

    # ── Currency ────────────────────────────────────────────────────
    currency = models.CharField(
        max_length=3,
        default="LKR",
        verbose_name="Currency",
        help_text="ISO 4217 currency code. Defaults to LKR (Sri Lankan Rupee).",
    )

    # ── Balance Fields ──────────────────────────────────────────────
    opening_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Opening Balance",
        help_text="Initial balance when the account was created or at fiscal year start.",
    )
    current_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Current Balance",
        help_text="Cached current balance, updated by journal entries.",
    )

    class MPTTMeta:
        order_insertion_by = ["code"]

    class Meta:
        app_label = "accounting"
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
            models.Index(
                fields=["status"],
                name="idx_account_status",
            ),
            models.Index(
                fields=["tree_id", "lft"],
                name="idx_account_tree",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(code__regex=r"^\d{4,}$"),
                name="chk_account_code_numeric",
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

    @property
    def full_path(self):
        """Return full account path from root to self."""
        ancestors = self.get_ancestors(include_self=True)
        return " > ".join(a.name for a in ancestors)

    def recalculate_balance(self):
        """Recalculate current_balance from journal entries."""
        from apps.accounting.models.journal import JournalEntry

        entries = JournalEntry.objects.filter(
            account=self, status="posted"
        ).aggregate(
            total_debit=models.Sum("debit"),
            total_credit=models.Sum("credit"),
        )
        total_debit = entries["total_debit"] or Decimal("0.00")
        total_credit = entries["total_credit"] or Decimal("0.00")

        if self.is_debit_normal:
            self.current_balance = (
                self.opening_balance + total_debit - total_credit
            )
        else:
            self.current_balance = (
                self.opening_balance + total_credit - total_debit
            )
        self.save(update_fields=["current_balance", "updated_on"])
