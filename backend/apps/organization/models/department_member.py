from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.organization.constants import (
    DEFAULT_MEMBERSHIP_ROLE,
    MEMBERSHIP_ROLE_CHOICES,
)


class DepartmentMemberQuerySet(models.QuerySet):
    """Custom queryset for temporal membership queries."""

    def active(self):
        """Return only currently-active memberships."""
        return self.filter(left_date__isnull=True)

    def ended(self):
        """Return only ended memberships."""
        return self.filter(left_date__isnull=False)

    def as_of(self, target_date):
        """Return memberships that were active on *target_date*."""
        return self.filter(
            joined_date__lte=target_date,
        ).filter(
            models.Q(left_date__gte=target_date) | models.Q(left_date__isnull=True),
        )


class DepartmentMember(UUIDMixin, TimestampMixin, models.Model):
    """Track employee membership in a department with role and dates.

    Maintains a full history of department assignments so that
    transfers and role changes can be audited.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="department_memberships",
        help_text="Employee who is/was a member.",
    )
    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.CASCADE,
        related_name="members",
        help_text="Department the employee belongs/belonged to.",
    )
    role = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_ROLE_CHOICES,
        default=DEFAULT_MEMBERSHIP_ROLE,
        help_text="Role within the department (member, lead, deputy_manager).",
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the employee's primary department.",
    )
    joined_date = models.DateField(
        help_text="Date the employee joined this department.",
    )
    left_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the employee left this department (null = still active).",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional membership information.",
    )

    objects = DepartmentMemberQuerySet.as_manager()

    class Meta:
        ordering = ["-joined_date"]
        verbose_name = "Department Member"
        verbose_name_plural = "Department Members"
        indexes = [
            models.Index(fields=["employee", "department"], name="idx_dmember_emp_dept"),
            models.Index(fields=["department", "left_date"], name="idx_dmember_dept_left"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "department"],
                condition=models.Q(left_date__isnull=True),
                name="uq_active_member_per_dept",
            ),
        ]

    def __str__(self):
        status = "active" if self.left_date is None else "ended"
        return f"{self.employee} — {self.department} ({status})"

    def clean(self):
        super().clean()
        # Date consistency: left_date must be >= joined_date
        if self.left_date is not None and self.joined_date and self.left_date < self.joined_date:
            raise ValidationError(
                {"left_date": "Left date cannot be before joined date."}
            )
        # Single-primary validation: only one active primary per employee
        if self.is_primary and self.left_date is None:
            qs = DepartmentMember.objects.filter(
                employee_id=self.employee_id,
                is_primary=True,
                left_date__isnull=True,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {"is_primary": "Employee already has a primary department membership."}
                )

    @property
    def is_active(self):
        return self.left_date is None

    @property
    def duration(self):
        """Return membership duration as a timedelta."""
        end = self.left_date or date.today()
        return end - self.joined_date
