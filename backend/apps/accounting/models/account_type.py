"""
AccountTypeConfig model for the accounting application.

Provides configuration and metadata for the five main account types
(Asset, Liability, Equity, Revenue, Expense) including code ranges,
normal balances, and display ordering.
"""

from django.db import models

from apps.accounting.models.enums import AccountType, NormalBalance


class AccountTypeConfig(models.Model):
    """
    System configuration for each of the five main account types.

    Defines code ranges, normal balance side, display ordering,
    and descriptive information for each account type.
    """

    type_name = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        unique=True,
        verbose_name="Account Type",
        help_text="The account type this configuration applies to.",
    )

    normal_balance = models.CharField(
        max_length=10,
        choices=NormalBalance.choices,
        verbose_name="Normal Balance",
        help_text="The normal balance side (DEBIT or CREDIT) for this account type.",
    )

    code_start = models.IntegerField(
        verbose_name="Code Range Start",
        help_text="Starting code number for accounts of this type (e.g., 1000).",
    )

    code_end = models.IntegerField(
        verbose_name="Code Range End",
        help_text="Ending code number for accounts of this type (e.g., 1999).",
    )

    display_order = models.SmallIntegerField(
        unique=True,
        verbose_name="Display Order",
        help_text="Order in which this type appears in reports and listings.",
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Detailed description of this account type.",
    )

    class Meta:
        app_label = "accounting"
        db_table = "accounting_account_type_config"
        verbose_name = "Account Type Configuration"
        verbose_name_plural = "Account Type Configurations"
        ordering = ["display_order"]
        indexes = [
            models.Index(fields=["type_name"], name="idx_atc_type_name"),
            models.Index(fields=["code_start", "code_end"], name="idx_atc_code_range"),
        ]

    def __str__(self):
        return self.get_type_name_display()
