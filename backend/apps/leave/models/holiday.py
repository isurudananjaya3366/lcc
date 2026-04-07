"""Holiday model for the Leave Management app.

Manages public holidays, bank holidays, company holidays,
and optional holidays with recurring support.
"""

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.leave.constants import HolidayScope, HolidayType


class Holiday(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Holiday definition with scope and recurrence support.

    Recurring holidays act as templates (year=null, is_recurring=True).
    Instances are generated per year from templates.
    """

    # ── Core Fields ──────────────────────────────────────────
    name = models.CharField(max_length=200)
    date = models.DateField()
    holiday_type = models.CharField(
        max_length=20,
        choices=HolidayType.choices,
        default=HolidayType.PUBLIC,
    )
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # ── Scope Fields ─────────────────────────────────────────
    applies_to = models.CharField(
        max_length=20,
        choices=HolidayScope.choices,
        default=HolidayScope.ALL,
    )
    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="holidays",
    )
    location = models.CharField(max_length=100, null=True, blank=True)

    # ── Recurrence Fields ────────────────────────────────────
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="RRULE format (RFC 5545).",
    )
    year = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"], name="idx_holiday_date"),
            models.Index(fields=["is_active"], name="idx_holiday_active"),
            models.Index(fields=["applies_to"], name="idx_holiday_scope"),
            models.Index(
                fields=["department", "date"],
                name="idx_holiday_dept_date",
            ),
            models.Index(
                fields=["is_recurring"], name="idx_holiday_recurring"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.date}) [{self.get_holiday_type_display()}]"

    def clean(self):
        super().clean()
        errors = {}

        if self.applies_to == HolidayScope.ALL:
            if self.department_id:
                errors["department"] = (
                    "Department must be empty when applies_to is ALL."
                )
            if self.location:
                errors["location"] = (
                    "Location must be empty when applies_to is ALL."
                )

        elif self.applies_to == HolidayScope.DEPARTMENT:
            if not self.department_id:
                errors["department"] = (
                    "Department is required when applies_to is DEPARTMENT."
                )
            if self.location:
                errors["location"] = (
                    "Location must be empty when applies_to is DEPARTMENT."
                )

        elif self.applies_to == HolidayScope.LOCATION:
            if self.department_id:
                errors["department"] = (
                    "Department must be empty when applies_to is LOCATION."
                )
            if not self.location:
                errors["location"] = (
                    "Location is required when applies_to is LOCATION."
                )

        if errors:
            raise ValidationError(errors)

    @classmethod
    def generate_instances_for_year(cls, year):
        """Generate holiday instances for a year from recurring templates.

        Creates new Holiday records from templates (is_recurring=True, year=null).
        Sets is_recurring=False and year=target_year on generated instances.

        Args:
            year: Target year for instance generation.

        Returns:
            List of created Holiday instances.
        """
        templates = cls.objects.filter(
            is_recurring=True,
            year__isnull=True,
            is_active=True,
            is_deleted=False,
        )
        created = []
        for template in templates:
            new_date = template.date.replace(year=year)
            instance, was_created = cls.objects.get_or_create(
                name=template.name,
                date=new_date,
                defaults={
                    "holiday_type": template.holiday_type,
                    "description": template.description,
                    "is_active": True,
                    "applies_to": template.applies_to,
                    "department": template.department,
                    "location": template.location,
                    "is_recurring": False,
                    "year": year,
                },
            )
            if was_created:
                created.append(instance)
        return created
