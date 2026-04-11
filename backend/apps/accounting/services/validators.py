"""
Account Validator and archive helper.

Centralises validation rules and soft-archive logic for accounts.
"""

import logging

from django.core.exceptions import ValidationError

from apps.accounting.models import Account
from apps.accounting.models.enums import AccountStatus
from apps.accounting.models.journal import LegacyJournalEntry

logger = logging.getLogger(__name__)

# Code range per account type (inclusive bounds).
CODE_RANGES: dict[str, tuple[int, int]] = {
    "asset": (1000, 1999),
    "liability": (2000, 2999),
    "equity": (3000, 3999),
    "revenue": (4000, 4999),
    "expense": (5000, 5999),
}


class AccountValidator:
    """
    Validates Account business rules.

    All public methods raise ``ValidationError`` on failure and
    return ``True`` on success.
    """

    # ── Code format ─────────────────────────────────────────────────

    @staticmethod
    def validate_code_format(code: str) -> bool:
        """Code must be a numeric string of at least 4 digits."""
        if not code or not code.isdigit() or len(code) < 4:
            raise ValidationError(
                f"Account code must be a numeric string of at least "
                f"4 digits. Got: '{code}'."
            )
        return True

    # ── Code uniqueness ─────────────────────────────────────────────

    @staticmethod
    def validate_code_unique(code: str, exclude_id=None) -> bool:
        """Code must be unique within the current schema."""
        qs = Account.objects.filter(code=code)
        if exclude_id is not None:
            qs = qs.exclude(pk=exclude_id)
        if qs.exists():
            raise ValidationError(
                f"Account code '{code}' already exists."
            )
        return True

    # ── Code range ──────────────────────────────────────────────────

    @staticmethod
    def validate_code_range(code: str, account_type: str) -> bool:
        """Verify that *code* falls inside the range for *account_type*."""
        code_int = int(code)
        range_tuple = CODE_RANGES.get(account_type)
        if range_tuple is None:
            raise ValidationError(
                f"Unknown account type: '{account_type}'."
            )
        low, high = range_tuple
        if not (low <= code_int <= high):
            raise ValidationError(
                f"Account code {code} invalid for type '{account_type}'. "
                f"Must be between {low} and {high}."
            )
        return True

    # ── Account type ────────────────────────────────────────────────

    @staticmethod
    def validate_account_type(account_type: str) -> bool:
        """Must be one of the known account types."""
        if account_type not in CODE_RANGES:
            raise ValidationError(
                f"Invalid account type: '{account_type}'."
            )
        return True

    # ── Deletion ────────────────────────────────────────────────────

    @staticmethod
    def validate_can_delete(account_id) -> bool:
        """
        Returns True when the account may be hard-deleted.

        Raises ``ValidationError`` if:
        * It is a system account.
        * It has child accounts.
        * It has journal entries.
        """
        account = Account.objects.get(pk=account_id)

        if account.is_system:
            raise ValidationError(
                f"Cannot delete system account {account.code} "
                f"({account.name})."
            )

        child_count = account.get_children().count()
        if child_count:
            raise ValidationError(
                f"Cannot delete account {account.code} because it has "
                f"{child_count} child account(s). Delete children first."
            )

        entry_count = LegacyJournalEntry.objects.filter(account=account).count()
        if entry_count:
            raise ValidationError(
                f"Cannot delete account {account.code} ({account.name}) "
                f"with {entry_count} journal entries. "
                f"Archive the account instead."
            )

        return True

    # ── Archive / soft-delete ───────────────────────────────────────

    @staticmethod
    def archive_account(account_id, *, archive_children: bool = False) -> Account:
        """
        Soft-archive an account by setting its status to ARCHIVED.

        Args:
            account_id: PK of the account.
            archive_children: If True, recursively archive child accounts.

        Returns:
            The updated Account instance.
        """
        account = Account.objects.get(pk=account_id)

        if account.status == AccountStatus.ARCHIVED:
            logger.warning("Account %s is already archived.", account.code)
            return account

        children = account.get_children().filter(status=AccountStatus.ACTIVE)
        if children.exists() and not archive_children:
            raise ValidationError(
                f"Account {account.code} has {children.count()} active "
                f"child account(s). Pass archive_children=True to "
                f"archive them as well."
            )

        if archive_children:
            for child in children:
                AccountValidator.archive_account(
                    child.pk, archive_children=True
                )

        account.status = AccountStatus.ARCHIVED
        account.is_active = False
        account.save(update_fields=["status", "is_active", "updated_on"])
        logger.info("Archived account %s (%s).", account.code, account.name)
        return account
