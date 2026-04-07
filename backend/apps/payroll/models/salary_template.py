from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class SalaryTemplate(UUIDMixin, TimestampMixin, models.Model):
    """A reusable salary structure template grouping multiple components.

    Templates can be linked to a designation and assigned to employees.
    Each template defines a set of components with default values.
    """

    name = models.CharField(
        max_length=100,
        help_text="Template name (e.g. 'Executive Package', 'Junior Staff').",
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique code for the template (e.g. 'EXEC', 'JR_STAFF').",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Description of the salary template.",
    )
    designation = models.ForeignKey(
        "organization.Designation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_templates",
        help_text="Optional designation this template is tied to.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this template is currently available.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)
