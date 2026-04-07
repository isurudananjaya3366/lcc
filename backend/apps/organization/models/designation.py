from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.organization.constants import (
    DEFAULT_DESIGNATION_LEVEL,
    DEFAULT_DESIGNATION_STATUS,
    DESIGNATION_LEVEL_CHOICES,
    DESIGNATION_LEVEL_MANAGER,
    DESIGNATION_LEVEL_ORDER,
    DESIGNATION_STATUS_ACTIVE,
    DESIGNATION_STATUS_CHOICES,
)


class DesignationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=DESIGNATION_STATUS_ACTIVE)


class Designation(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Job title / position within the organisation.

    Each designation has a seniority level, optional department link,
    salary range, and a ``reports_to`` self-FK for the designation
    hierarchy.
    """

    objects = DesignationQuerySet.as_manager()

    # ── Core Fields ─────────────────────────────────────────────────
    title = models.CharField(
        max_length=100,
        help_text="Job title, e.g. 'Software Engineer'.",
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique designation code, e.g. 'SE'.",
    )
    status = models.CharField(
        max_length=20,
        choices=DESIGNATION_STATUS_CHOICES,
        default=DEFAULT_DESIGNATION_STATUS,
        db_index=True,
        help_text="Whether this designation is active.",
    )

    # ── Level ───────────────────────────────────────────────────────
    level = models.CharField(
        max_length=20,
        choices=DESIGNATION_LEVEL_CHOICES,
        default=DEFAULT_DESIGNATION_LEVEL,
        db_index=True,
        help_text="Seniority level (entry → executive).",
    )

    # ── Description ─────────────────────────────────────────────────
    description = models.TextField(
        blank=True,
        default="",
        help_text="Position overview and summary.",
    )
    responsibilities = models.TextField(
        blank=True,
        default="",
        help_text="Key duties and accountabilities.",
    )

    # ── Department Link (optional) ──────────────────────────────────
    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="designations",
        help_text="Department this designation belongs to (null = org-wide).",
    )

    # ── Salary Range ────────────────────────────────────────────────
    min_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Minimum salary for this position.",
    )
    max_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum salary for this position.",
    )
    currency = models.CharField(
        max_length=3,
        default="LKR",
        help_text="ISO 4217 currency code for salary.",
    )

    # ── Requirements ────────────────────────────────────────────────
    qualifications = models.TextField(
        blank=True,
        default="",
        help_text="Educational and professional qualifications required.",
    )
    experience_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum years of experience required.",
    )

    # ── Reporting ───────────────────────────────────────────────────
    reports_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
        help_text="Superior designation this position reports to.",
    )

    # ── Manager Flag ────────────────────────────────────────────────
    is_manager = models.BooleanField(
        default=False,
        help_text="Whether this designation has managerial authority.",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Designation"
        verbose_name_plural = "Designations"
        indexes = [
            models.Index(fields=["code"], name="idx_desig_code"),
            models.Index(fields=["status"], name="idx_desig_status"),
            models.Index(fields=["level"], name="idx_desig_level"),
            models.Index(fields=["title"], name="idx_desig_title"),
            models.Index(fields=["department"], name="idx_desig_dept"),
            models.Index(fields=["is_manager"], name="idx_desig_manager"),
            models.Index(fields=["department", "status"], name="idx_desig_dept_status"),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.code:
            self.code = self.code.upper()
        if (
            self.min_salary is not None
            and self.max_salary is not None
            and self.max_salary < self.min_salary
        ):
            raise ValidationError(
                {"max_salary": "Maximum salary must be >= minimum salary."}
            )

    @property
    def level_rank(self):
        """Numeric rank of this designation's level."""
        return DESIGNATION_LEVEL_ORDER.get(self.level, 0)
