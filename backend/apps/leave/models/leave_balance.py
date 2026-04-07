from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin


class LeaveBalance(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Tracks leave balance per employee, leave type, and calendar year.

    Stores allocation, usage, carry-forward, and encashment data.
    One record per (employee, leave_type, year) combination.
    """

    # ── Core Identification ──────────────────────────────────
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_balances",
        help_text="Employee this balance belongs to.",
    )
    leave_type = models.ForeignKey(
        "leave.LeaveType",
        on_delete=models.PROTECT,
        related_name="balances",
        help_text="Leave type for this balance.",
    )
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2100)],
        db_index=True,
        help_text="Calendar year (e.g. 2026).",
    )

    # ── Allocation ───────────────────────────────────────────
    opening_balance = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Starting balance at year start.",
    )
    allocated_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Days accrued/granted during the year.",
    )
    carried_from_previous = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Days carried over from the previous year.",
    )

    # ── Usage ────────────────────────────────────────────────
    used_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total approved leave days taken.",
    )
    pending_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Days in approval process (pending applications).",
    )
    encashed_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Days converted to cash.",
    )

    # ── Control ──────────────────────────────────────────────
    carry_forward_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="Date when carried-forward days expire.",
    )
    last_accrual_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the last accrual calculation.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this balance record is current.",
    )

    class Meta:
        verbose_name = "Leave Balance"
        verbose_name_plural = "Leave Balances"
        ordering = ["-year", "employee", "leave_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "leave_type", "year"],
                name="unique_employee_leavetype_year",
            ),
        ]
        indexes = [
            models.Index(fields=["employee", "year"], name="leave_bal_emp_year_idx"),
            models.Index(fields=["leave_type", "year", "is_active"], name="leave_bal_type_year_idx"),
            models.Index(fields=["carry_forward_expiry", "is_active"], name="leave_bal_expiry_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.employee} - {self.leave_type.name} ({self.year})"

    # ── Computed Properties ──────────────────────────────────

    @property
    def available_days(self) -> Decimal:
        """Net available days after deducting usage, pending, and encashed.

        If carry-forward days have expired, they are excluded from the total.
        """
        total = (
            self.opening_balance
            + self.allocated_days
            + self.carried_from_previous
            - self.used_days
            - self.pending_days
            - self.encashed_days
        )
        if self.is_carry_forward_expired():
            total -= self.carried_from_previous
        return max(total, Decimal("0.00"))

    # ── Query Helpers ────────────────────────────────────────

    def has_sufficient_balance(self, days_requested: Decimal) -> bool:
        return self.available_days >= Decimal(str(days_requested))

    def is_carry_forward_expired(self) -> bool:
        if not self.carry_forward_expiry:
            return False
        return timezone.now().date() > self.carry_forward_expiry

    def get_expired_carry_forward_days(self) -> Decimal:
        if self.is_carry_forward_expired():
            return self.carried_from_previous
        return Decimal("0.00")

    def can_encash_days(self, days_to_encash: Decimal) -> tuple[bool, str]:
        days_to_encash = Decimal(str(days_to_encash))
        if not self.leave_type.is_paid:
            return False, "Unpaid leave types cannot be encashed."
        if days_to_encash > self.available_days:
            return False, f"Insufficient balance. Available: {self.available_days}"
        return True, "Encashment allowed."
