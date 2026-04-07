"""EmergencyContact model for the Employees application."""

from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.employees.constants import RELATIONSHIP_CHOICES


class EmergencyContact(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Emergency contact information for an employee.

    Supports multiple contacts per employee with priority ordering.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
        verbose_name="Employee",
        help_text="Employee this emergency contact belongs to.",
    )

    # ── Contact Information ─────────────────────────────────────────
    name = models.CharField(
        max_length=200,
        verbose_name="Contact Name",
        help_text="Full name of the emergency contact.",
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        verbose_name="Relationship",
        help_text="Relationship to the employee.",
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Phone Number",
        help_text="Contact phone number.",
    )
    email = models.EmailField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Email",
        help_text="Contact email address (optional).",
    )

    # ── Priority ────────────────────────────────────────────────────
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name="Priority",
        help_text="Contact priority (1 = highest).",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Additional notes about this contact.",
    )

    class Meta:
        db_table = "employees_emergency_contact"
        verbose_name = "Emergency Contact"
        verbose_name_plural = "Emergency Contacts"
        ordering = ["employee", "priority"]
        indexes = [
            models.Index(
                fields=["employee", "priority"],
                name="idx_emp_emergency_priority",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()})"
