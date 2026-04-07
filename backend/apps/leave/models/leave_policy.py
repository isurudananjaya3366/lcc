from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.leave.constants import PolicyScope


class LeavePolicy(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Links a LeaveType to a specific employee group with optional entitlement overrides.

    Policies can target all employees, a specific department, or a specific designation.
    Priority resolution: DESIGNATION > DEPARTMENT > ALL.
    Time-bound via effective_from / effective_to.
    """

    # ── Core ─────────────────────────────────────────────────
    name = models.CharField(
        max_length=200,
        help_text="Human-readable policy name (e.g. 'Sales Dept Annual Leave Policy').",
    )
    leave_type = models.ForeignKey(
        "leave.LeaveType",
        on_delete=models.CASCADE,
        related_name="policies",
        help_text="The leave type this policy applies to.",
    )
    days_per_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Override for the leave type's default_days_per_year. Null uses default.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this policy is currently active.",
    )

    # ── Scope (Task 15) ─────────────────────────────────────
    applies_to = models.CharField(
        max_length=20,
        choices=PolicyScope.choices,
        default=PolicyScope.ALL,
        help_text="Target group for this policy.",
    )
    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="leave_policies",
        help_text="Target department (required when applies_to=DEPARTMENT).",
    )
    designation = models.ForeignKey(
        "organization.Designation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="leave_policies",
        help_text="Target designation (required when applies_to=DESIGNATION).",
    )

    # ── Date Range (Task 16) ────────────────────────────────
    effective_from = models.DateField(
        help_text="Date from which this policy is effective.",
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        help_text="Date until which this policy is effective. Null means no expiry.",
    )

    class Meta:
        verbose_name = "Leave Policy"
        verbose_name_plural = "Leave Policies"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["leave_type"], name="leave_policy_type_idx"),
            models.Index(fields=["is_active"], name="leave_policy_active_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.leave_type.name})"

    # ── Helper Methods ───────────────────────────────────────

    def get_applicable_days(self) -> int | None:
        """Return the effective days per year, preferring the policy override."""
        if self.days_per_year is not None:
            return self.days_per_year
        return self.leave_type.default_days_per_year

    @property
    def is_currently_effective(self) -> bool:
        """Return True if the current date falls within the policy's date range."""
        today = timezone.now().date()
        if today < self.effective_from:
            return False
        if self.effective_to and today > self.effective_to:
            return False
        return True

    # ── Validation ───────────────────────────────────────────

    def clean(self) -> None:
        super().clean()

        # Date range validation
        if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
            raise ValidationError({"effective_to": "Effective end date must be after start date."})

        # Scope validation
        if self.applies_to == PolicyScope.DEPARTMENT:
            if not self.department_id:
                raise ValidationError({"department": "Department is required when policy applies to a specific department."})
            if self.designation_id:
                raise ValidationError({"designation": "Designation must be empty when policy applies to a department."})

        elif self.applies_to == PolicyScope.DESIGNATION:
            if not self.designation_id:
                raise ValidationError({"designation": "Designation is required when policy applies to a specific designation."})
            if self.department_id:
                raise ValidationError({"department": "Department must be empty when policy applies to a designation."})

        elif self.applies_to == PolicyScope.ALL:
            if self.department_id or self.designation_id:
                raise ValidationError("Department and designation must be empty when policy applies to all employees.")

    # ── Class Methods ────────────────────────────────────────

    @classmethod
    def get_applicable_policy(cls, employee, leave_type):
        """Get the highest-priority active policy for an employee and leave type.

        Priority: DESIGNATION > DEPARTMENT > ALL.
        """
        today = timezone.now().date()
        base_qs = cls.objects.filter(
            leave_type=leave_type,
            is_active=True,
            effective_from__lte=today,
        ).filter(
            models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=today),
        )

        # Priority 1: Designation
        if hasattr(employee, "designation") and employee.designation:
            policy = base_qs.filter(applies_to=PolicyScope.DESIGNATION, designation=employee.designation).first()
            if policy:
                return policy

        # Priority 2: Department
        if hasattr(employee, "department") and employee.department:
            policy = base_qs.filter(applies_to=PolicyScope.DEPARTMENT, department=employee.department).first()
            if policy:
                return policy

        # Priority 3: All employees
        return base_qs.filter(applies_to=PolicyScope.ALL).first()

    @classmethod
    def get_entitlement_days(cls, employee, leave_type) -> int | None:
        """Get leave entitlement days for an employee and leave type."""
        policy = cls.get_applicable_policy(employee, leave_type)
        if policy:
            return policy.get_applicable_days()
        return leave_type.default_days_per_year
