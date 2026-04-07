"""Constants for the Payroll Management app.

Defines salary component types, calculation methods, categories,
and other constants for Sri Lankan payroll compliance.
"""

from django.db import models


class ComponentType(models.TextChoices):
    """Salary component type classification."""

    EARNING = "EARNING", "Earning"
    DEDUCTION = "DEDUCTION", "Deduction"
    EMPLOYER_CONTRIBUTION = "EMPLOYER_CONTRIBUTION", "Employer Contribution"


class CalculationType(models.TextChoices):
    """Calculation method for salary components."""

    FIXED = "FIXED", "Fixed Amount"
    PERCENTAGE_OF_BASIC = "PERCENTAGE_OF_BASIC", "Percentage of Basic Salary"
    PERCENTAGE_OF_GROSS = "PERCENTAGE_OF_GROSS", "Percentage of Gross Salary"
    FORMULA = "FORMULA", "Formula-based"


class ComponentCategory(models.TextChoices):
    """Category classification for salary components."""

    BASIC = "BASIC", "Basic Salary"
    ALLOWANCE = "ALLOWANCE", "Allowance"
    BONUS = "BONUS", "Bonus"
    STATUTORY = "STATUTORY", "Statutory"
    LOAN = "LOAN", "Loan Deduction"
    TAX = "TAX", "Tax"
    OTHER = "OTHER", "Other"


class SalaryChangeReason(models.TextChoices):
    """Reasons for salary revision."""

    ANNUAL_INCREMENT = "ANNUAL_INCREMENT", "Annual Increment"
    PROMOTION = "PROMOTION", "Promotion"
    TRANSFER = "TRANSFER", "Transfer"
    RESTRUCTURE = "RESTRUCTURE", "Restructuring"
    CORRECTION = "CORRECTION", "Correction"
    OTHER = "OTHER", "Other"


class PayrollStatus(models.TextChoices):
    """Status choices for payroll periods and payroll runs."""

    DRAFT = "DRAFT", "Draft"
    PROCESSING = "PROCESSING", "Processing"
    PROCESSED = "PROCESSED", "Processed"
    PENDING_APPROVAL = "PENDING_APPROVAL", "Pending Approval"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    FINALIZED = "FINALIZED", "Finalized"
    REVERSED = "REVERSED", "Reversed"


class PaymentStatus(models.TextChoices):
    """Payment status for individual employee payroll records."""

    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    FAILED = "FAILED", "Failed"
    ON_HOLD = "ON_HOLD", "On Hold"


class LineType(models.TextChoices):
    """Type classification for payroll line items."""

    EARNING = "EARNING", "Earning"
    DEDUCTION = "DEDUCTION", "Deduction"
    EMPLOYER_CONTRIBUTION = "EMPLOYER_CONTRIBUTION", "Employer Contribution"
    ADJUSTMENT = "ADJUSTMENT", "Adjustment"


class HistoryAction(models.TextChoices):
    """Action types for payroll audit history."""

    CREATED = "CREATED", "Created"
    PROCESSED = "PROCESSED", "Processed"
    SUBMITTED = "SUBMITTED", "Submitted for Approval"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    FINALIZED = "FINALIZED", "Finalized"
    REVERSED = "REVERSED", "Reversed"
    CORRECTED = "CORRECTED", "Correction Applied"
    PAID = "PAID", "Marked as Paid"
    BANK_FILE_GENERATED = "BANK_FILE_GENERATED", "Bank File Generated"
