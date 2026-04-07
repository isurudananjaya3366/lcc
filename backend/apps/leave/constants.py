"""Constants for the Leave Management app.

Defines leave type categories, gender restrictions, policy scopes,
and other constants aligned with Sri Lankan labor law requirements.
"""

from django.db import models


# ──────────────────────────────────────────────────────────────
# Leave Type Category Choices
# ──────────────────────────────────────────────────────────────
class LeaveTypeCategory(models.TextChoices):
    """Categories for leave types aligned with Sri Lankan labor law."""

    ANNUAL = "ANNUAL", "Annual Leave"
    CASUAL = "CASUAL", "Casual Leave"
    SICK = "SICK", "Sick Leave"
    MATERNITY = "MATERNITY", "Maternity Leave"
    PATERNITY = "PATERNITY", "Paternity Leave"
    NO_PAY = "NO_PAY", "No-Pay Leave"
    OTHER = "OTHER", "Other"


# ──────────────────────────────────────────────────────────────
# Gender Restriction Choices
# ──────────────────────────────────────────────────────────────
class GenderRestriction(models.TextChoices):
    """Gender restrictions for leave types."""

    ALL = "ALL", "All Genders"
    MALE = "MALE", "Male Only"
    FEMALE = "FEMALE", "Female Only"


# ──────────────────────────────────────────────────────────────
# Policy Scope Choices
# ──────────────────────────────────────────────────────────────
class PolicyScope(models.TextChoices):
    """Scope options for leave policies."""

    ALL = "ALL", "All Employees"
    DEPARTMENT = "DEPARTMENT", "Specific Department"
    DESIGNATION = "DESIGNATION", "Specific Designation"


# ──────────────────────────────────────────────────────────────
# Accrual Method Choices
# ──────────────────────────────────────────────────────────────
class AccrualMethod(models.TextChoices):
    """Methods for leave accrual calculation."""

    ANNUAL_GRANT = "annual_grant", "Annual Grant"
    MONTHLY = "monthly_accrual", "Monthly Accrual"
    PRO_RATA = "pro_rata", "Pro-Rata"


# ──────────────────────────────────────────────────────────────
# Leave Request Status Choices
# ──────────────────────────────────────────────────────────────
class LeaveRequestStatus(models.TextChoices):
    """Status workflow for leave requests."""

    DRAFT = "DRAFT", "Draft"
    PENDING = "PENDING", "Pending Approval"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"
    RECALLED = "RECALLED", "Recalled"


# ──────────────────────────────────────────────────────────────
# Half-Day Type Choices
# ──────────────────────────────────────────────────────────────
class HalfDayType(models.TextChoices):
    """Half-day leave period options."""

    FIRST_HALF = "FIRST_HALF", "First Half"
    SECOND_HALF = "SECOND_HALF", "Second Half"


# ──────────────────────────────────────────────────────────────
# Holiday Type Choices
# ──────────────────────────────────────────────────────────────
class HolidayType(models.TextChoices):
    """Types of holidays."""

    PUBLIC = "PUBLIC", "Public Holiday"
    BANK = "BANK", "Bank Holiday"
    COMPANY = "COMPANY", "Company Holiday"
    OPTIONAL = "OPTIONAL", "Optional Holiday"


# ──────────────────────────────────────────────────────────────
# Holiday Scope Choices
# ──────────────────────────────────────────────────────────────
class HolidayScope(models.TextChoices):
    """Scope for holiday applicability."""

    ALL = "ALL", "All Employees"
    DEPARTMENT = "DEPARTMENT", "Department Only"
    LOCATION = "LOCATION", "Location Only"
