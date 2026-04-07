"""Employee bank account model for the Employees application."""

from django.conf import settings
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.employees.constants import ACCOUNT_TYPE_CHOICES, ACCOUNT_TYPE_SAVINGS


class EmployeeBankAccount(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Stores employee bank account details for payroll processing."""

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="bank_accounts",
    )

    # Bank identification
    bank_name = models.CharField(max_length=255)
    bank_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Bank code (e.g., CBSL bank code)",
    )
    branch_name = models.CharField(max_length=255, blank=True, default="")
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=255, blank=True, default="")

    # Bank codes
    swift_code = models.CharField(max_length=11, blank=True, default="", help_text="SWIFT/BIC code")
    branch_code = models.CharField(max_length=20, blank=True, default="", help_text="Bank branch code")

    # International banking
    iban = models.CharField(
        max_length=34,
        blank=True,
        default="",
        help_text="International Bank Account Number",
    )
    routing_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Bank routing number",
    )
    is_international = models.BooleanField(
        default=False,
        help_text="Whether this is an international bank account",
    )
    currency = models.CharField(
        max_length=3,
        blank=True,
        default="LKR",
        help_text="Account currency (ISO 4217 code)",
    )

    # Account type
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default=ACCOUNT_TYPE_SAVINGS,
    )

    # Primary flag
    is_primary = models.BooleanField(default=False, help_text="Primary account for salary payments")

    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_bank_accounts",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "employees_bank_account"
        verbose_name = "Employee Bank Account"
        verbose_name_plural = "Employee Bank Accounts"
        ordering = ["employee", "-is_primary"]
        indexes = [
            models.Index(fields=["employee", "is_primary"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.bank_name} ({'Primary' if self.is_primary else 'Secondary'})"

    def get_masked_account_number(self):
        """Return account number with all but last 4 digits masked."""
        if not self.account_number or len(self.account_number) <= 4:
            return self.account_number
        return "*" * (len(self.account_number) - 4) + self.account_number[-4:]

    def validate_account_number(self):
        """Basic account number validation."""
        if not self.account_number:
            return False
        cleaned = self.account_number.strip()
        return len(cleaned) >= 4 and cleaned.replace("-", "").replace(" ", "").isalnum()

    def save(self, *args, **kwargs):
        # Ensure only one primary account per employee
        if self.is_primary:
            EmployeeBankAccount.objects.filter(
                employee=self.employee,
                is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
