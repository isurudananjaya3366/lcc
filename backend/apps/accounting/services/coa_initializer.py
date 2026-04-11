"""
COA Initializer Service.

Handles automated chart of accounts setup for tenants, supporting
both default (from DEFAULT_ACCOUNTS) and template-based initialization.
"""

import logging
from decimal import Decimal

from django.db import transaction

from apps.accounting.data.default_accounts import DEFAULT_ACCOUNTS
from apps.accounting.models import Account, COATemplate

logger = logging.getLogger(__name__)


class COAInitializerError(Exception):
    """Base exception for COA initialization errors."""


class TenantAlreadyInitializedException(COAInitializerError):
    """Raised when the tenant already has accounts."""


class InvalidTemplateException(COAInitializerError):
    """Raised when a template is not found or inactive."""


class COAInitializerService:
    """
    Service for initializing a tenant's chart of accounts.

    Usage::

        svc = COAInitializerService()
        result = svc.create_default()
        # or
        result = svc.create_from_template(template_id)
    """

    def has_accounts(self) -> bool:
        """Return True if the current schema already has accounts."""
        return Account.objects.exists()

    # ── Public API ──────────────────────────────────────────────────

    def create_default(self, *, force: bool = False) -> dict:
        """
        Create the default chart of accounts from DEFAULT_ACCOUNTS.

        Args:
            force: If True, delete existing accounts before loading.

        Returns:
            dict with ``total`` and ``accounts_by_type`` keys.

        Raises:
            TenantAlreadyInitializedException: if accounts exist and
                *force* is False.
        """
        if self.has_accounts() and not force:
            raise TenantAlreadyInitializedException(
                "Accounts already exist. Pass force=True to replace."
            )

        with transaction.atomic():
            if force:
                self._delete_all_accounts()

            created = self._create_account_tree(DEFAULT_ACCOUNTS)

        Account.objects.rebuild()
        logger.info("Created %d default accounts.", created)
        return self._build_result(created)

    def create_from_template(self, template_id, *, force: bool = False) -> dict:
        """
        Create accounts from a COATemplate.

        Args:
            template_id: UUID of the COATemplate to use.
            force: If True, delete existing accounts before loading.

        Returns:
            dict with ``total``, ``template_name``, and
            ``accounts_by_type`` keys.

        Raises:
            InvalidTemplateException: if template not found or inactive.
            TenantAlreadyInitializedException: if accounts exist and
                *force* is False.
        """
        try:
            template = COATemplate.objects.get(pk=template_id, is_active=True)
        except COATemplate.DoesNotExist:
            raise InvalidTemplateException(
                f"Template {template_id} not found or inactive."
            )

        accounts_data = template.template_accounts
        if not accounts_data:
            raise InvalidTemplateException("Template has no account definitions.")

        if self.has_accounts() and not force:
            raise TenantAlreadyInitializedException(
                "Accounts already exist. Pass force=True to replace."
            )

        with transaction.atomic():
            if force:
                self._delete_all_accounts()

            created = self._create_account_tree(accounts_data)

        Account.objects.rebuild()
        logger.info(
            "Created %d accounts from template '%s'.",
            created,
            template.template_name,
        )
        result = self._build_result(created)
        result["template_name"] = template.template_name
        return result

    # ── Internals ───────────────────────────────────────────────────

    @staticmethod
    def _delete_all_accounts():
        """Delete all accounts leaf-first to respect PROTECT FK."""
        while Account.objects.exists():
            Account.objects.filter(children__isnull=True).delete()

    @staticmethod
    def _create_account_tree(accounts_data: list[dict]) -> int:
        """Create accounts respecting parent_code references.

        Returns the number of accounts created.
        """
        code_map: dict[str, Account] = {}
        created = 0

        for entry in accounts_data:
            parent_code = entry.get("parent_code")
            parent = code_map.get(parent_code) if parent_code else None

            account, was_created = Account.objects.get_or_create(
                code=entry["code"],
                defaults={
                    "name": entry["name"],
                    "account_type": entry["account_type"],
                    "is_header": entry.get("is_header", False),
                    "is_system": entry.get("is_system", False),
                    "description": entry.get("description", ""),
                    "parent": parent,
                    "opening_balance": Decimal(str(entry.get("opening_balance", "0.00"))),
                    "current_balance": Decimal(str(entry.get("current_balance", "0.00"))),
                },
            )
            code_map[entry["code"]] = account
            if was_created:
                created += 1

        return created

    @staticmethod
    def _build_result(total: int) -> dict:
        """Build a standard result dict with per-type counts."""
        from collections import Counter

        type_counts = Counter(
            Account.objects.values_list("account_type", flat=True)
        )
        return {
            "total": total,
            "accounts_by_type": dict(type_counts),
        }
