"""EmployeePayroll model for individual employee payroll records."""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.payroll.constants import PaymentStatus


class EmployeePayroll(UUIDMixin, TimestampMixin, models.Model):
    """Stores an individual employee's payroll calculation for a specific run.

    Captures the complete breakdown of salary, attendance, earnings,
    deductions, statutory contributions, and payment details. Includes
    a salary snapshot to preserve the salary structure at processing time.
    """

    # ── Relationships ────────────────────────────────────────
    payroll_run = models.ForeignKey(
        "payroll.PayrollRun",
        on_delete=models.CASCADE,
        related_name="employee_payrolls",
        help_text="The payroll run this record belongs to.",
    )
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="employee_payrolls",
        help_text="The employee this payroll record is for.",
    )
    employee_salary = models.ForeignKey(
        "payroll.EmployeeSalary",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payroll_records",
        help_text="Salary record used for calculation.",
    )

    # ── Salary Snapshot ──────────────────────────────────────
    salary_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Frozen copy of salary structure at processing time.",
    )

    # ── Attendance Fields ────────────────────────────────────
    days_worked = models.PositiveIntegerField(
        default=0,
        help_text="Number of days the employee was present.",
    )
    days_absent = models.PositiveIntegerField(
        default=0,
        help_text="Number of absent days (paid leave like sick leave).",
    )
    unpaid_leave_days = models.PositiveIntegerField(
        default=0,
        help_text="Number of unpaid (no-pay) leave days.",
    )
    overtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total overtime hours worked.",
    )
    late_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of late arrivals.",
    )

    # ── Financial Summary ────────────────────────────────────
    basic_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Actual basic salary for this period (may be pro-rated).",
    )
    overtime_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Calculated overtime payment.",
    )
    gross_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total earnings before deductions.",
    )
    total_deductions = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of all deductions.",
    )
    net_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Final take-home salary (gross - deductions).",
    )

    # ── Statutory Contributions ──────────────────────────────
    epf_employee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Employee EPF contribution (8%).",
    )
    epf_employer = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Employer EPF contribution (12%).",
    )
    etf = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Employer ETF contribution (3%).",
    )
    paye_tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="PAYE income tax deduction.",
    )

    # ── Bank & Payment ───────────────────────────────────────
    bank_account = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of employee bank account details at processing time.",
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Transaction reference number after payment.",
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when payment was made.",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Payment status for this employee.",
    )

    # ── Verification & Notes ─────────────────────────────────
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this record has been verified.",
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Whether this record is locked (set during finalization).",
    )
    is_reversed = models.BooleanField(
        default=False,
        help_text="Whether this record has been reversed.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional notes for this employee payroll record.",
    )

    class Meta:
        ordering = ["employee"]
        unique_together = [("payroll_run", "employee")]
        indexes = [
            models.Index(fields=["payment_status"], name="idx_emppay_pmtstatus"),
        ]
        verbose_name = "Employee Payroll"
        verbose_name_plural = "Employee Payrolls"

    def __str__(self):
        return f"{self.employee} - {self.payroll_run}"

    # ── Employee Helpers ─────────────────────────────────────

    def get_employee_name(self):
        """Return the employee's full name."""
        emp = self.employee
        first = getattr(emp, "first_name", "")
        last = getattr(emp, "last_name", "")
        return f"{first} {last}".strip()

    def get_employee_code(self):
        """Return the employee's code/ID."""
        emp = self.employee
        return getattr(emp, "employee_code", "") or getattr(emp, "code", "") or str(emp.pk)

    # ── Attendance Validation ────────────────────────────────

    def validate_attendance(self):
        """Validate attendance fields are consistent."""
        errors = {}
        period = self.payroll_run.payroll_period if self.payroll_run_id else None
        if period:
            total_days = float(period.total_working_days)
            if self.days_worked + self.days_absent + self.unpaid_leave_days > total_days:
                errors["days_worked"] = (
                    "Total of days worked, absent, and unpaid leave exceeds "
                    "total working days in the period."
                )
        if self.overtime_hours < 0:
            errors["overtime_hours"] = "Overtime hours cannot be negative."
        if errors:
            raise ValidationError(errors)

    # ── Calculation Methods ──────────────────────────────────

    def calculate_net(self):
        """Calculate net salary as gross minus deductions."""
        self.net_salary = self.gross_salary - self.total_deductions
        return self.net_salary

    def validate_amounts(self):
        """Validate that financial amounts are consistent."""
        expected_net = self.gross_salary - self.total_deductions
        if self.net_salary != expected_net:
            raise ValidationError(
                f"Net salary ({self.net_salary}) does not match "
                f"gross ({self.gross_salary}) - deductions ({self.total_deductions}) "
                f"= {expected_net}"
            )
