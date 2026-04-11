"""
BankAccount model for the accounting application.

Stores bank account configuration for reconciliation, including
bank details, GL account linkage, currency, and reconciliation
tracking fields.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.accounting.constants import ACCOUNT_TYPE_ASSET, ACCOUNT_TYPE_LIABILITY
from apps.accounting.models.enums import BankAccountType
from apps.core.mixins import UUIDMixin


class BankAccount(UUIDMixin, models.Model):
    """
    Bank account configuration for reconciliation.

    Links a physical bank account to a GL account in the Chart of
    Accounts for statement import and reconciliation.

    Validation rules:
        - CHECKING/SAVINGS/CASH must link to Asset GL accounts.
        - CREDIT_CARD must link to Liability GL accounts.
    """

    account_name = models.CharField(
        max_length=100,
        verbose_name="Account Name",
        help_text="Descriptive name for the bank account (e.g., 'BOC Business').",
    )

    account_number = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Account Number",
        help_text="Bank account number.",
    )

    bank_name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Bank Name",
        help_text="Name of the bank (e.g., 'Bank of Ceylon').",
    )

    branch_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Branch Name",
        help_text="Branch name (optional).",
    )

    branch_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Branch Code",
        help_text="Branch code (optional).",
    )

    account_type = models.CharField(
        max_length=20,
        choices=BankAccountType.choices,
        default=BankAccountType.CHECKING,
        db_index=True,
        verbose_name="Account Type",
        help_text="Type of bank account.",
    )

    gl_account = models.ForeignKey(
        "accounting.Account",
        on_delete=models.PROTECT,
        related_name="bank_accounts",
        verbose_name="GL Account",
        help_text="Linked General Ledger account from the Chart of Accounts.",
    )

    currency = models.CharField(
        max_length=3,
        default="LKR",
        db_index=True,
        verbose_name="Currency",
        help_text="ISO 4217 currency code (e.g., 'LKR', 'USD').",
    )

    last_reconciled_date = models.DateField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Last Reconciled Date",
        help_text="Date of the last completed reconciliation.",
    )

    last_reconciled_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Last Reconciled Balance",
        help_text="Balance at the last completed reconciliation.",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Whether this bank account is active for reconciliation.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bank_accounts_created",
        verbose_name="Created By",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bank_accounts_updated",
        verbose_name="Updated By",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = "accounting_bank_account"
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        ordering = ["bank_name", "account_name"]
        indexes = [
            models.Index(
                fields=["bank_name", "account_number"],
                name="idx_bank_acct_lookup",
            ),
        ]

    def __str__(self):
        return f"{self.account_name} ({self.bank_name} - {self.account_number})"

    def clean(self):
        """Validate GL account type matches bank account type."""
        super().clean()
        if self.gl_account_id:
            gl = self.gl_account
            asset_types = {
                BankAccountType.CHECKING,
                BankAccountType.SAVINGS,
                BankAccountType.CASH,
            }
            if self.account_type in asset_types:
                if gl.account_type != ACCOUNT_TYPE_ASSET:
                    raise ValidationError(
                        {
                            "gl_account": (
                                f"{self.get_account_type_display()} accounts must be "
                                f"linked to Asset GL accounts."
                            )
                        }
                    )
            elif self.account_type == BankAccountType.CREDIT_CARD:
                if gl.account_type != ACCOUNT_TYPE_LIABILITY:
                    raise ValidationError(
                        {
                            "gl_account": (
                                "Credit Card accounts must be linked to "
                                "Liability GL accounts."
                            )
                        }
                    )

    def save(self, *args, **kwargs):
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)
