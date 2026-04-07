"""VendorBankAccount model for vendor banking details."""

from django.conf import settings
from django.db import models
from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.vendors.constants import BANK_VERIFICATION_CHOICES, BANK_VERIFICATION_PENDING


class VendorBankAccount(UUIDMixin, TimestampMixin, models.Model):
    """Bank account associated with a vendor for payments."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="bank_accounts",
    )
    bank_name = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200, blank=True, default="")
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    swift_code = models.CharField(max_length=11, blank=True, default="")
    branch_code = models.CharField(max_length=20, blank=True, default="")
    iban = models.CharField(max_length=34, blank=True, default="")
    currency = models.CharField(max_length=3, default="LKR")
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verification_status = models.CharField(
        max_length=20,
        choices=BANK_VERIFICATION_CHOICES,
        default=BANK_VERIFICATION_PENDING,
    )
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor_bank_accounts_created",
    )

    class Meta:
        db_table = "vendors_vendor_bank_account"
        verbose_name = "Vendor Bank Account"
        verbose_name_plural = "Vendor Bank Accounts"
        ordering = ["-is_default", "bank_name"]

    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.vendor.company_name})"
