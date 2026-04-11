"""
Template service for the accounting application.

Provides operations for managing journal entry templates including
creating entries from templates and saving existing entries as templates.
"""

import logging
from decimal import Decimal, InvalidOperation

from django.db import transaction

from apps.accounting.models.enums import (
    JournalEntryType,
    JournalSource,
    TemplateCategory,
)
from apps.accounting.models.journal_entry import JournalEntry
from apps.accounting.models.journal_line import JournalEntryLine
from apps.accounting.models.journal_template import JournalEntryTemplate
from apps.accounting.validators.entry_validators import (
    validate_entry,
    validate_line_amounts,
)

logger = logging.getLogger(__name__)


class TemplateServiceError(Exception):
    """Base exception for template service errors."""


class TemplateService:
    """
    Service for journal entry template operations.

    Methods:
        get_template:          Retrieve a template by ID.
        get_template_by_name:  Find a template by name.
        list_templates:        List templates with optional category filter.
        validate_template_lines: Validate the JSON structure of template lines.
        create_from_template:  Create a journal entry from a template.
        save_as_template:      Save an existing entry as a reusable template.
    """

    @staticmethod
    def get_template(template_id):
        """
        Retrieve a template by its primary key.

        Args:
            template_id: UUID of the template.

        Returns:
            JournalEntryTemplate instance.

        Raises:
            TemplateServiceError: If template not found.
        """
        try:
            return JournalEntryTemplate.objects.get(pk=template_id)
        except JournalEntryTemplate.DoesNotExist:
            raise TemplateServiceError(
                f"Template with ID '{template_id}' not found."
            )

    @staticmethod
    def get_template_by_name(name):
        """
        Retrieve a template by name.

        Args:
            name: Exact name of the template.

        Returns:
            JournalEntryTemplate instance.

        Raises:
            TemplateServiceError: If template not found.
        """
        try:
            return JournalEntryTemplate.objects.get(name=name)
        except JournalEntryTemplate.DoesNotExist:
            raise TemplateServiceError(
                f"Template with name '{name}' not found."
            )

    @staticmethod
    def list_templates(category=None, active_only=True):
        """
        List templates with optional category filter.

        Args:
            category: TemplateCategory value to filter by (optional).
            active_only: If True (default), only return active templates.

        Returns:
            QuerySet of JournalEntryTemplate instances.
        """
        qs = JournalEntryTemplate.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        if category is not None:
            qs = qs.filter(category=category)
        return qs.order_by("name")

    @staticmethod
    def validate_template_lines(template_lines):
        """
        Validate the JSON structure of template lines.

        Ensures the template_lines dict has a ``lines`` key containing
        a list of line definitions, each with at least an ``account_code``
        and either a ``debit`` or ``credit`` value.

        Args:
            template_lines: Dict to validate.

        Returns:
            True if valid.

        Raises:
            TemplateServiceError: If structure is invalid.
        """
        if not isinstance(template_lines, dict):
            raise TemplateServiceError(
                "template_lines must be a dictionary."
            )

        lines = template_lines.get("lines")
        if not isinstance(lines, list):
            raise TemplateServiceError(
                "template_lines must have a 'lines' key containing a list."
            )

        if len(lines) < 2:
            raise TemplateServiceError(
                "Template must have at least 2 line definitions."
            )

        for idx, line_def in enumerate(lines):
            if not isinstance(line_def, dict):
                raise TemplateServiceError(
                    f"Line {idx} must be a dictionary."
                )
            if not line_def.get("account_code"):
                raise TemplateServiceError(
                    f"Line {idx} is missing 'account_code'."
                )
            debit = line_def.get("debit")
            credit = line_def.get("credit")
            if debit is None and credit is None:
                raise TemplateServiceError(
                    f"Line {idx} must have either 'debit' or 'credit'."
                )

        return True

    @staticmethod
    @transaction.atomic
    def create_from_template(
        template,
        entry_date,
        amounts=None,
        description=None,
        created_by=None,
    ):
        """
        Create a new journal entry from a template.

        Resolves template line placeholders (e.g. ``{{amount}}``) using
        the ``amounts`` dict and creates a balanced journal entry.

        Args:
            template: JournalEntryTemplate instance.
            entry_date: Transaction date for the new entry.
            amounts: Dict mapping placeholder names to Decimal values,
                     e.g. ``{"amount": Decimal("50000.00")}``.
            description: Override template description. Defaults to
                         template name.
            created_by: User creating the entry.

        Returns:
            The created JournalEntry instance.

        Raises:
            TemplateServiceError: If template lines are invalid or
                                  amount resolution fails.
        """
        amounts = amounts or {}
        lines_def = template.template_lines
        if not lines_def or not lines_def.get("lines"):
            raise TemplateServiceError(
                f"Template '{template.name}' has no line definitions."
            )

        entry = JournalEntry(
            entry_date=entry_date,
            entry_type=JournalEntryType.MANUAL,
            entry_source=JournalSource.MANUAL,
            description=description or f"From template: {template.name}",
            created_by=created_by,
        )
        entry.save()

        for idx, line_def in enumerate(lines_def["lines"]):
            account_code = line_def.get("account_code")
            if not account_code:
                raise TemplateServiceError(
                    f"Template line {idx} is missing 'account_code'."
                )

            from apps.accounting.models.account import Account

            try:
                account = Account.objects.get(code=account_code)
            except Account.DoesNotExist:
                raise TemplateServiceError(
                    f"Account with code '{account_code}' does not exist."
                )

            debit = _resolve_amount(line_def.get("debit"), amounts)
            credit = _resolve_amount(line_def.get("credit"), amounts)

            line = JournalEntryLine(
                journal_entry=entry,
                account=account,
                debit_amount=debit,
                credit_amount=credit,
                description=line_def.get("description", ""),
                sort_order=idx,
            )
            validate_line_amounts(line)
            line.save()

        _update_cached_totals(entry)
        validate_entry(entry)

        logger.info(
            "Created journal entry %s from template '%s'",
            entry.entry_number,
            template.name,
        )
        return entry

    @staticmethod
    def save_as_template(entry, name, category=None, description=None, created_by=None):
        """
        Save an existing journal entry as a reusable template.

        Extracts the line structure from the entry and stores it as a
        JSON template definition with the original amounts preserved.

        Args:
            entry: JournalEntry instance to save as template.
            name: Name for the new template.
            category: TemplateCategory value. Defaults to GENERAL.
            description: Template description.
            created_by: User creating the template.

        Returns:
            The created JournalEntryTemplate instance.
        """
        lines = []
        for line in entry.lines.select_related("account").order_by("sort_order"):
            line_def = {
                "account_code": line.account.code,
                "description": line.description,
                "debit": str(line.debit_amount) if line.debit_amount else None,
                "credit": str(line.credit_amount) if line.credit_amount else None,
            }
            lines.append(line_def)

        template = JournalEntryTemplate.objects.create(
            name=name,
            description=description or f"Created from entry {entry.entry_number}",
            template_lines={"lines": lines},
            category=category or TemplateCategory.GENERAL,
            created_by=created_by,
        )

        logger.info(
            "Saved entry %s as template '%s'",
            entry.entry_number,
            template.name,
        )
        return template


def _resolve_amount(value, amounts):
    """
    Resolve a template line amount value.

    Handles:
        - None / null → Decimal("0")
        - Numeric string → Decimal(value)
        - Placeholder ``{{name}}`` → looked up in amounts dict
    """
    if value is None:
        return Decimal("0")

    if isinstance(value, (int, float)):
        return Decimal(str(value))

    value_str = str(value).strip()

    if value_str.startswith("{{") and value_str.endswith("}}"):
        key = value_str[2:-2].strip()
        if key not in amounts:
            raise TemplateServiceError(
                f"Missing amount for placeholder '{{{{{key}}}}}'."
            )
        resolved = amounts[key]
        if not isinstance(resolved, Decimal):
            resolved = Decimal(str(resolved))
        return resolved

    try:
        return Decimal(value_str)
    except InvalidOperation:
        raise TemplateServiceError(
            f"Cannot resolve template amount: '{value_str}'."
        )


def _update_cached_totals(entry):
    """Recalculate and save the cached total_debit and total_credit."""
    from django.db.models import Sum

    totals = entry.lines.aggregate(
        total_debit=Sum("debit_amount"),
        total_credit=Sum("credit_amount"),
    )
    entry.total_debit = totals["total_debit"] or Decimal("0")
    entry.total_credit = totals["total_credit"] or Decimal("0")
    entry.save(update_fields=["total_debit", "total_credit"])
