import logging
from datetime import date as date_type

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class ShiftSchedule(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Assigns shifts to employees or departments for specific time periods."""

    # ── Core Fields ──────────────────────────────────────────
    name = models.CharField(
        max_length=200,
        help_text="Descriptive name for this schedule.",
    )
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this schedule is currently active.",
    )
    priority = models.PositiveIntegerField(
        default=50,
        help_text="Priority for conflict resolution (higher = higher priority).",
    )

    # ── Shift Reference ─────────────────────────────────────
    shift = models.ForeignKey(
        "attendance.Shift",
        on_delete=models.PROTECT,
        related_name="schedules",
        help_text="The shift assigned by this schedule.",
    )

    # ── Employee FK (Individual Schedule) ────────────────────
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shift_schedules",
        help_text="Employee for individual schedule (null for department-wide).",
    )

    # ── Department FK (Department-wide Schedule) ─────────────
    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shift_schedules",
        help_text="Department for department-wide schedule (null for individual).",
    )

    # ── Date Range Fields ────────────────────────────────────
    effective_from = models.DateField(
        help_text="Schedule effective start date.",
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        help_text="Schedule effective end date (null = ongoing).",
    )

    # ── Recurring Schedule Fields ────────────────────────────
    is_recurring = models.BooleanField(
        default=True,
        help_text="Whether this is a recurring weekly schedule.",
    )
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    # ── Audit ────────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_shift_schedules",
    )

    class Meta:
        ordering = ["-priority", "name"]
        indexes = [
            models.Index(
                fields=["employee", "effective_from"],
                name="idx_schedule_emp_from",
            ),
            models.Index(
                fields=["department", "effective_from"],
                name="idx_schedule_dept_from",
            ),
            models.Index(fields=["is_active"], name="idx_schedule_active"),
        ]

    def __str__(self):
        target = ""
        if self.employee_id:
            target = f" → {self.employee}"
        elif self.department_id:
            target = f" → {self.department}"
        return f"{self.name}{target}"

    @property
    def is_individual(self):
        """Whether this is an individual employee schedule."""
        return self.employee_id is not None

    @property
    def is_department_wide(self):
        """Whether this is a department-wide schedule."""
        return self.department_id is not None and self.employee_id is None

    @property
    def applicable_weekdays(self):
        """Return list of applicable weekday numbers (0=Monday ... 6=Sunday)."""
        days = []
        for i, flag in enumerate(
            [
                self.monday,
                self.tuesday,
                self.wednesday,
                self.thursday,
                self.friday,
                self.saturday,
                self.sunday,
            ]
        ):
            if flag:
                days.append(i)
        return days

    def applies_on_date(self, target_date):
        """Check if this schedule applies on a given date."""
        if not self.is_active:
            return False
        if target_date < self.effective_from:
            return False
        if self.effective_to and target_date > self.effective_to:
            return False
        if self.is_recurring:
            return target_date.weekday() in self.applicable_weekdays
        return True

    def clean(self):
        super().clean()
        # Must have either employee or department (or neither for default)
        if self.employee_id and self.department_id:
            raise ValidationError(
                "A schedule cannot be assigned to both an employee and a department."
            )
        # effective_to must be after effective_from
        if self.effective_to and self.effective_to < self.effective_from:
            raise ValidationError(
                {"effective_to": "End date must be on or after start date."}
            )

    # ── Validity Helpers ─────────────────────────────────────

    def is_valid_on_date(self, check_date):
        """Check if this schedule is valid on a specific date (date range only, ignores weekday)."""
        if check_date < self.effective_from:
            return False
        if self.effective_to and check_date > self.effective_to:
            return False
        return True

    def is_currently_valid(self):
        """Check if this schedule is valid today."""
        return self.is_valid_on_date(date_type.today())

    def get_validity_period(self):
        """Return a human-readable validity period string."""
        if self.effective_to:
            return f"{self.effective_from} to {self.effective_to}"
        return f"{self.effective_from} onwards"

    def days_remaining(self):
        """Return days until effective_to, or None if open-ended."""
        if not self.effective_to:
            return None
        delta = self.effective_to - date_type.today()
        return max(delta.days, 0)

    # ── Weekday Helpers ──────────────────────────────────────

    WEEKDAY_NAMES = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
    ]
    WEEKDAY_FIELDS = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    ]

    def applies_on_weekday(self, weekday):
        """Check if schedule applies on a single weekday number (0=Mon..6=Sun)."""
        return weekday in self.applicable_weekdays

    def get_weekday_pattern(self):
        """Return list of active weekday names, e.g. ['Monday', 'Tuesday', ...]."""
        return [
            self.WEEKDAY_NAMES[i]
            for i in range(7)
            if getattr(self, self.WEEKDAY_FIELDS[i])
        ]

    def get_weekday_pattern_abbrev(self):
        """Return compact weekday string, e.g. 'Mon-Fri' or 'Mon,Wed,Fri'."""
        active = self.applicable_weekdays
        if not active:
            return "None"
        if active == list(range(7)):
            return "Every day"
        if active == list(range(5)):
            return "Mon-Fri"
        if active == [5, 6]:
            return "Sat-Sun"
        abbrevs = [self.WEEKDAY_NAMES[i][:3] for i in active]
        # Detect contiguous ranges
        if len(active) > 2 and active == list(range(active[0], active[-1] + 1)):
            return f"{self.WEEKDAY_NAMES[active[0]][:3]}-{self.WEEKDAY_NAMES[active[-1]][:3]}"
        return ", ".join(abbrevs)

    def set_weekday_pattern(self, weekdays):
        """Set weekday flags from a list of weekday numbers (0=Mon..6=Sun)."""
        for i, field in enumerate(self.WEEKDAY_FIELDS):
            setattr(self, field, i in weekdays)

    def is_weekday_pattern(self):
        """Check if schedule follows Mon-Fri pattern."""
        return self.applicable_weekdays == list(range(5))

    def is_weekend_pattern(self):
        """Check if schedule follows Sat-Sun pattern."""
        return self.applicable_weekdays == [5, 6]
