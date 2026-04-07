"""EmployeeAddress model for the Employees application."""

from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.employees.constants import (
    ADDRESS_TYPE_CHOICES,
    ADDRESS_TYPE_PERMANENT,
    PROVINCE_CHOICES,
)


class EmployeeAddress(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Employee address record.

    Supports multiple address types (permanent, temporary, work)
    with Sri Lanka-specific province and district fields.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="Employee",
        help_text="Employee this address belongs to.",
    )

    # ── Address Type ────────────────────────────────────────────────
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default=ADDRESS_TYPE_PERMANENT,
        verbose_name="Address Type",
        help_text="Type of address (permanent, temporary, work).",
    )

    # ── Address Fields ──────────────────────────────────────────────
    line1 = models.CharField(
        max_length=255,
        verbose_name="Address Line 1",
        help_text="Street address or house number.",
    )
    line2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Address Line 2",
        help_text="Apartment, suite, or additional address info.",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="City",
        help_text="City or town name.",
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        default="",
        verbose_name="Postal Code",
        help_text="Postal/zip code.",
    )

    # ── Sri Lanka Specific ──────────────────────────────────────────
    province = models.CharField(
        max_length=30,
        choices=PROVINCE_CHOICES,
        blank=True,
        default="",
        verbose_name="Province",
        help_text="Sri Lanka province.",
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="District",
        help_text="District within the province.",
    )

    # ── Flags ───────────────────────────────────────────────────────
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Primary Address",
        help_text="Whether this is the primary address.",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Additional notes about this address.",
    )

    class Meta:
        db_table = "employees_address"
        verbose_name = "Employee Address"
        verbose_name_plural = "Employee Addresses"
        ordering = ["employee", "-is_primary", "address_type"]
        indexes = [
            models.Index(
                fields=["employee", "address_type"],
                name="idx_emp_addr_type",
            ),
        ]

    def __str__(self):
        return f"{self.get_address_type_display()} - {self.city}"
