"""
JournalEntryTemplate model for the accounting application.

Stores reusable journal entry patterns with line item definitions
in JSON format, enabling quick creation of common entries like
monthly rent, depreciation, or recurring expenses.
"""

from django.conf import settings
from django.db import models

from apps.accounting.models.enums import TemplateCategory
from apps.core.mixins import UUIDMixin


def _default_template_lines():
    """Default value for template_lines JSONField."""
    return {"lines": []}


class JournalEntryTemplate(UUIDMixin, models.Model):
    """
    Reusable journal entry template.

    Stores a named entry pattern with line item definitions in JSON
    format. Templates can be used to create new journal entries
    quickly and can be linked to recurring entry schedules.

    JSON Structure for template_lines:
        {
          "lines": [
            {
              "account_code": "5300",
              "description": "Monthly Office Rent",
              "debit": "{{amount}}",
              "credit": null
            },
            {
              "account_code": "1110",
              "description": "Bank Payment",
              "debit": null,
              "credit": "{{amount}}"
            }
          ]
        }
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Template Name",
        help_text="Descriptive name for the template (e.g. 'Monthly Rent Payment').",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Detailed description of the template's purpose and usage.",
    )

    template_lines = models.JSONField(
        default=_default_template_lines,
        verbose_name="Template Lines",
        help_text="JSON structure defining the entry line items with account codes and amounts.",
    )

    category = models.CharField(
        max_length=20,
        choices=TemplateCategory.choices,
        default=TemplateCategory.GENERAL,
        db_index=True,
        verbose_name="Category",
        help_text="Template category for organisation and filtering.",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this template is available for use.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_templates_created",
        verbose_name="Created By",
        help_text="User who created this template.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        db_table = "accounting_journal_entry_template"
        verbose_name = "Journal Entry Template"
        verbose_name_plural = "Journal Entry Templates"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["category"],
                name="idx_jet_category",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
