from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class DepartmentHead(UUIDMixin, TimestampMixin, models.Model):
    """Track department heads with full appointment history.

    Separate from DepartmentMember to distinguish leadership roles,
    support acting/interim heads, and record appointment details.
    """

    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.CASCADE,
        related_name="heads",
        help_text="Department this head record belongs to.",
    )
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="head_positions",
        help_text="Employee serving as department head.",
    )
    is_acting = models.BooleanField(
        default=False,
        help_text="Whether this is an acting/interim head.",
    )
    start_date = models.DateField(
        help_text="Date the head tenure began.",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the head tenure ended (null = currently serving).",
    )
    appointed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="department_head_appointments",
        help_text="User who made the appointment.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional appointment notes.",
    )

    class Meta:
        ordering = ["department", "-start_date"]
        verbose_name = "Department Head"
        verbose_name_plural = "Department Heads"
        indexes = [
            models.Index(
                fields=["department", "end_date"],
                name="idx_dhead_dept_end",
            ),
        ]

    def __str__(self):
        suffix = " (Acting)" if self.is_acting else ""
        end = self.end_date or "present"
        return f"{self.employee} — {self.department}{suffix} ({self.start_date} to {end})"

    @property
    def is_current(self):
        return self.end_date is None
