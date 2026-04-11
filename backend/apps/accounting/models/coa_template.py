"""
COATemplate model for industry-specific chart of accounts templates.

Stores reusable account structures that can be applied when
initializing a new tenant's chart of accounts.
"""

from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class IndustryType(models.TextChoices):
    """Industry categories for COA templates."""

    RETAIL = "RETAIL", "Retail Business"
    SERVICE = "SERVICE", "Service Company"
    MANUFACTURING = "MANUFACTURING", "Manufacturing"
    RESTAURANT = "RESTAURANT", "Restaurant / Hospitality"
    PROFESSIONAL = "PROFESSIONAL", "Professional Services"
    CONSTRUCTION = "CONSTRUCTION", "Construction"
    NONPROFIT = "NONPROFIT", "Non-Profit Organization"
    ECOMMERCE = "ECOMMERCE", "E-Commerce"


class COATemplate(UUIDMixin, TimestampMixin, models.Model):
    """
    Industry-specific chart of accounts template.

    Each template stores a JSON array of account definitions that can
    be loaded via :class:`COAInitializerService` when setting up a
    new tenant.
    """

    # ── Template Name ───────────────────────────────────────────────
    template_name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Template Name",
        help_text="Unique name for this COA template.",
    )

    # ── Industry Category ───────────────────────────────────────────
    industry = models.CharField(
        max_length=50,
        choices=IndustryType.choices,
        db_index=True,
        verbose_name="Industry",
        help_text="Industry category for this template.",
    )

    # ── Template Accounts (JSON) ────────────────────────────────────
    template_accounts = models.JSONField(
        default=list,
        verbose_name="Template Accounts",
        help_text="JSON array of account definitions.",
    )

    # ── Description ─────────────────────────────────────────────────
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Detailed description of this template.",
    )

    # ── Status ──────────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this template is available for use.",
    )

    class Meta:
        app_label = "accounting"
        db_table = "accounting_coa_template"
        verbose_name = "COA Template"
        verbose_name_plural = "COA Templates"
        ordering = ["template_name"]

    def __str__(self):
        return self.template_name

    @property
    def account_count(self):
        """Return number of accounts in the template."""
        if isinstance(self.template_accounts, list):
            return len(self.template_accounts)
        return 0

    def get_accounts_by_type(self, account_type: str) -> list[dict]:
        """Return accounts filtered by type."""
        return [
            a for a in self.template_accounts
            if a.get("account_type") == account_type
        ]

    def get_root_accounts(self) -> list[dict]:
        """Return accounts with no parent."""
        return [
            a for a in self.template_accounts
            if a.get("parent_code") is None
        ]
