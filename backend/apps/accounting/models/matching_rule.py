"""
MatchingRule model for the accounting application.

Defines configurable rules for automatic matching of bank statement
lines to journal entries during reconciliation. Rules specify matching
criteria including amount tolerance, date range, reference matching,
and description pattern matching via regex.
"""

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.mixins import UUIDMixin


class MatchingRule(UUIDMixin, models.Model):
    """
    Configurable rule for automatic statement-to-journal matching.

    Rules are evaluated in priority order (lower number = higher priority).
    Account-specific rules take precedence over global rules (bank_account=NULL).

    Priority ranges:
        1-10:   High priority (exact matches)
        11-50:  Medium priority (fuzzy matches)
        51-100: Low priority (pattern/suggestion matches)
    """

    bank_account = models.ForeignKey(
        "accounting.BankAccount",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="matching_rules",
        help_text="NULL = global rule applying to all accounts.",
    )

    name = models.CharField(
        max_length=200,
        help_text="Human-readable rule name, e.g. 'Exact Match Same Day'.",
    )

    priority = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Rule evaluation order (1-100, lower = higher priority).",
    )

    amount_tolerance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Maximum allowed amount difference. 0 = exact match.",
    )

    date_range_days = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(365)],
        help_text="Maximum allowed date difference in days. 0 = same day.",
    )

    match_reference = models.BooleanField(
        default=False,
        help_text="If True, require exact reference/check number match.",
    )

    description_pattern = models.TextField(
        blank=True,
        default="",
        help_text="Regex pattern for description matching. Empty = skip.",
    )

    pattern_flags = models.CharField(
        max_length=10,
        blank=True,
        default="i",
        help_text="Regex flags: i=IGNORECASE, m=MULTILINE, s=DOTALL.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Controls whether this rule is used during matching.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        ordering = ["priority", "name"]
        indexes = [
            models.Index(fields=["is_active", "priority"]),
            models.Index(fields=["bank_account", "is_active"]),
        ]

    def __str__(self):
        scope = self.bank_account.account_name if self.bank_account else "Global"
        return f"{self.name} (priority={self.priority}, {scope})"

    def clean(self):
        super().clean()
        errors = {}

        if self.description_pattern:
            try:
                flags = self._get_regex_flags()
                re.compile(self.description_pattern, flags)
            except re.error as e:
                errors["description_pattern"] = f"Invalid regex pattern: {e}"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ── Regex helpers ──────────────────────────────────────────────

    def _get_regex_flags(self):
        """Convert pattern_flags string to re module flags."""
        flag_map = {
            "i": re.IGNORECASE,
            "m": re.MULTILINE,
            "s": re.DOTALL,
            "x": re.VERBOSE,
        }
        flags = 0
        for ch in (self.pattern_flags or ""):
            flags |= flag_map.get(ch, 0)
        return flags

    def get_compiled_pattern(self):
        """Return compiled regex pattern with caching."""
        if not self.description_pattern:
            return None
        cache_attr = "_compiled_pattern"
        if not hasattr(self, cache_attr):
            flags = self._get_regex_flags()
            object.__setattr__(
                self, cache_attr, re.compile(self.description_pattern, flags)
            )
        return getattr(self, cache_attr)
