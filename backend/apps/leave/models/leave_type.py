import re

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.leave.constants import GenderRestriction, LeaveTypeCategory


class LeaveType(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Defines a type of leave available in the system.

    Each tenant can configure leave types that comply with Sri Lankan labor laws
    and company-specific policies. Stores configuration for entitlement, eligibility,
    restrictions, and UI display.
    """

    # ── Core Identification ──────────────────────────────────
    name = models.CharField(
        max_length=100,
        help_text="Human-readable leave type name (e.g. 'Annual Leave').",
    )
    code = models.CharField(
        max_length=10,
        help_text="Short uppercase code (e.g. 'AL'). Unique per tenant.",
    )
    category = models.CharField(
        max_length=20,
        choices=LeaveTypeCategory.choices,
        help_text="Leave category aligned with Sri Lankan labor law.",
    )

    # ── Description & UI ─────────────────────────────────────
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed description, rules, and usage guidelines.",
    )
    color = models.CharField(
        max_length=7,
        default="#2196F3",
        help_text="Hex color code for calendar/UI display (e.g. '#4CAF50').",
    )

    # ── Entitlement Configuration ────────────────────────────
    default_days_per_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Default annual entitlement in days. Can be overridden by policy.",
    )
    max_consecutive_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum consecutive days allowed in a single stretch.",
    )
    max_days_per_request = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum days allowed per leave request.",
    )

    # ── Flags ────────────────────────────────────────────────
    is_paid = models.BooleanField(
        default=True,
        help_text="Whether this leave type is paid.",
    )
    requires_document = models.BooleanField(
        default=False,
        help_text="Whether supporting documents are required.",
    )
    document_after_days = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive days after which a document is required.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this leave type is available for new applications.",
    )
    allow_half_day = models.BooleanField(
        default=True,
        help_text="Whether half-day leave is allowed for this type.",
    )

    # ── Eligibility & Restrictions ───────────────────────────
    applicable_gender = models.CharField(
        max_length=10,
        choices=GenderRestriction.choices,
        default=GenderRestriction.ALL,
        help_text="Gender restriction for this leave type.",
    )
    min_service_months = models.PositiveIntegerField(
        default=0,
        help_text="Minimum months of service required for eligibility.",
    )
    min_notice_days = models.PositiveIntegerField(
        default=0,
        help_text="Minimum days of advance notice required before leave start.",
    )

    class Meta:
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["category"], name="leave_type_category_idx"),
            models.Index(fields=["is_active"], name="leave_type_active_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def clean(self) -> None:
        super().clean()

        # Uppercase code
        if self.code:
            self.code = self.code.upper()

        # Validate hex color
        if self.color and not re.match(r"^#[0-9A-Fa-f]{6}$", self.color):
            raise ValidationError({"color": "Color must be a valid hex code (e.g. '#4CAF50')."})

        # Category-specific gender validation
        if self.category == LeaveTypeCategory.MATERNITY and self.applicable_gender != GenderRestriction.FEMALE:
            raise ValidationError(
                {"applicable_gender": "Maternity leave must be restricted to Female only (legal requirement)."}
            )
        if self.category == LeaveTypeCategory.PATERNITY and self.applicable_gender != GenderRestriction.MALE:
            raise ValidationError(
                {"applicable_gender": "Paternity leave must be restricted to Male only (legal requirement)."}
            )
