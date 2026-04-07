"""EmployeeFamily model for the Employees application."""

from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.employees.constants import RELATIONSHIP_CHOICES


class EmployeeFamily(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Family member record for an employee.

    Tracks family details for benefits, insurance,
    and dependent management purposes.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="family_members",
        verbose_name="Employee",
        help_text="Employee this family member belongs to.",
    )

    # ── Family Member Info ──────────────────────────────────────────
    name = models.CharField(
        max_length=200,
        verbose_name="Name",
        help_text="Full name of the family member.",
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        verbose_name="Relationship",
        help_text="Relationship to the employee.",
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date of Birth",
        help_text="Family member's date of birth.",
    )
    occupation = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Occupation",
        help_text="Family member's occupation.",
    )

    # ── Dependent Flag ──────────────────────────────────────────────
    is_dependent = models.BooleanField(
        default=False,
        verbose_name="Is Dependent",
        help_text="Whether this family member is a dependent for benefits.",
    )

    # ── Contact ─────────────────────────────────────────────────────
    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Phone",
        help_text="Family member's phone number.",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Additional notes about this family member.",
    )

    class Meta:
        db_table = "employees_family"
        verbose_name = "Family Member"
        verbose_name_plural = "Family Members"
        ordering = ["employee", "relationship"]
        indexes = [
            models.Index(
                fields=["employee", "is_dependent"],
                name="idx_emp_family_dependent",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()})"
