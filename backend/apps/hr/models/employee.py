"""
Employee model for the HR application.

Defines the Employee model which stores staff records within a
tenant schema. Each employee links to a user account, has a role
for access control, contact information, and an activity status.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.hr.constants import (
    DEFAULT_EMPLOYEE_ROLE,
    DEFAULT_EMPLOYEE_STATUS,
    EMPLOYEE_ROLE_CHOICES,
    EMPLOYEE_STATUS_CHOICES,
    EMPLOYEE_STATUS_ACTIVE,
    EMPLOYEE_STATUS_SUSPENDED,
)


class Employee(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Tenant staff member record.

    Represents an employee within a tenant organisation. Links to
    a user account for authentication, assigns a role for access
    control, and tracks contact details and employment status.

    Fields:
        user: One-to-one FK to the tenant user account.
        employee_number: Unique employee identifier within tenant.
        first_name: Employee's first name.
        last_name: Employee's last name.
        role: Staff access level (admin, manager, cashier, etc.).
        email: Work email address.
        phone: Primary phone number (+94 XX XXX XXXX).
        mobile: Mobile phone number (+94 XX XXX XXXX).
        date_of_birth: Employee's date of birth.
        hire_date: Date the employee joined.
        termination_date: Date the employee left (if applicable).
        department: Department or team name.
        position: Job title or position.
        status: Current employment status.
        notes: Additional notes about the employee.
    """

    # ── User FK ─────────────────────────────────────────────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
        verbose_name="User Account",
        help_text=(
            "The user account linked to this employee. "
            "Tenant user is defined in the platform app."
        ),
    )

    # ── Employee Number ─────────────────────────────────────────────
    employee_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Employee Number",
        help_text="Unique employee identifier within the tenant.",
    )

    # ── Name Fields ─────────────────────────────────────────────────
    first_name = models.CharField(
        max_length=100,
        verbose_name="First Name",
        help_text="Employee's first name.",
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Last Name",
        help_text="Employee's last name.",
    )

    # ── Role ────────────────────────────────────────────────────────
    role = models.CharField(
        max_length=20,
        choices=EMPLOYEE_ROLE_CHOICES,
        default=DEFAULT_EMPLOYEE_ROLE,
        db_index=True,
        verbose_name="Role",
        help_text=(
            "Staff access level. Maps to permissions: "
            "admin (full), manager (management), cashier (POS), "
            "warehouse (inventory), accountant (accounting)."
        ),
    )

    # ── Contact Fields ──────────────────────────────────────────────
    email = models.EmailField(
        max_length=254,
        blank=True,
        default="",
        verbose_name="Work Email",
        help_text="Employee's work email address.",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Phone",
        help_text="Primary phone number. Format: +94 XX XXX XXXX.",
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Mobile",
        help_text="Mobile phone number. Format: +94 XX XXX XXXX.",
    )

    # ── Employment Dates ────────────────────────────────────────────
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date of Birth",
        help_text="Employee's date of birth.",
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Hire Date",
        help_text="Date the employee joined the organisation.",
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Termination Date",
        help_text="Date the employee left (if applicable).",
    )

    # ── Department & Position ───────────────────────────────────────
    department = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Department",
        help_text="Department or team name.",
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Position",
        help_text="Job title or position.",
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=EMPLOYEE_STATUS_CHOICES,
        default=DEFAULT_EMPLOYEE_STATUS,
        db_index=True,
        verbose_name="Status",
        help_text="Current employment status. Affects system access.",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Additional notes about this employee.",
    )

    class Meta:
        db_table = "hr_employee"
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(
                fields=["role", "status"],
                name="idx_employee_role_status",
            ),
            models.Index(
                fields=["last_name", "first_name"],
                name="idx_employee_name",
            ),
            models.Index(
                fields=["status"],
                name="idx_employee_status",
            ),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.employee_number})"

    @property
    def full_name(self):
        """Return the employee's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self):
        """Return True if the employee is currently active."""
        return self.status == EMPLOYEE_STATUS_ACTIVE

    @property
    def is_suspended(self):
        """Return True if the employee is suspended."""
        return self.status == EMPLOYEE_STATUS_SUSPENDED

    @property
    def is_terminated(self):
        """Return True if the employee has a termination date."""
        return self.termination_date is not None
