"""
Double-entry bookkeeping validators for journal entries.

Provides validation functions that enforce accounting rules:
    - Balance validation (debits == credits)
    - Non-zero entry totals
    - Minimum line count (>= 2)
    - Positive, exclusive debit/credit amounts per line
    - Active account validation
    - Open period validation
"""

from decimal import Decimal

from django.core.exceptions import ValidationError

MINIMUM_LINES = 2


def validate_entry_balance(entry):
    """
    Validate that total debits equal total credits across all lines.

    Raises:
        ValidationError: If sum of debit_amount != sum of credit_amount.
    """
    lines = entry.lines.all()
    total_debit = sum(line.debit_amount for line in lines)
    total_credit = sum(line.credit_amount for line in lines)

    if total_debit != total_credit:
        diff = abs(total_debit - total_credit)
        raise ValidationError(
            f"Entry does not balance. Total debits ({total_debit}) "
            f"!= total credits ({total_credit}). Difference: ₨{diff}"
        )


def validate_entry_not_zero(entry):
    """
    Validate that the entry has non-zero totals.

    Raises:
        ValidationError: If total debit and total credit are both zero.
    """
    lines = entry.lines.all()
    total_debit = sum(line.debit_amount for line in lines)
    total_credit = sum(line.credit_amount for line in lines)

    if total_debit == Decimal("0") and total_credit == Decimal("0"):
        raise ValidationError("Journal entry cannot have zero totals.")


def validate_entry_minimum_lines(entry):
    """
    Validate that the entry has at least MINIMUM_LINES (2) lines.

    Raises:
        ValidationError: If line count is less than MINIMUM_LINES.
    """
    line_count = entry.lines.count()
    if line_count < MINIMUM_LINES:
        raise ValidationError(
            f"Journal entry must have at least {MINIMUM_LINES} lines. "
            f"Found {line_count}."
        )


def validate_line_amounts(line):
    """
    Validate that a line has positive amounts and uses either
    debit or credit exclusively (not both).

    Raises:
        ValidationError: If amounts are negative or both populated.
    """
    if line.debit_amount < 0:
        raise ValidationError("Debit amount cannot be negative.")
    if line.credit_amount < 0:
        raise ValidationError("Credit amount cannot be negative.")
    if line.debit_amount > 0 and line.credit_amount > 0:
        raise ValidationError(
            "A line cannot have both debit and credit amounts. "
            "Use separate lines for debit and credit."
        )
    if line.debit_amount == 0 and line.credit_amount == 0:
        raise ValidationError(
            "A line must have either a debit or credit amount."
        )


def validate_line_accounts_active(entry):
    """
    Validate that all accounts referenced by entry lines are active.

    Raises:
        ValidationError: If any line references an inactive account.
    """
    lines = entry.lines.select_related("account").all()
    inactive = [
        line.account.code
        for line in lines
        if not line.account.is_active
    ]
    if inactive:
        codes = ", ".join(inactive)
        raise ValidationError(
            f"The following accounts are inactive and cannot be used "
            f"in journal entries: {codes}"
        )


def validate_entry_period(entry):
    """
    Validate that the entry date falls within an open accounting period.

    Attempts to check against AccountingPeriod model if it exists.
    If AccountingPeriod is not yet available (pre-SP09 Group E),
    validation is skipped.

    Raises:
        ValidationError: If entry date is in a closed or locked period.
    """
    try:
        from apps.accounting.models.accounting_period import AccountingPeriod
    except ImportError:
        return

    period = AccountingPeriod.objects.filter(
        start_date__lte=entry.entry_date,
        end_date__gte=entry.entry_date,
    ).first()

    if period is None:
        return

    if period.status != "OPEN":
        raise ValidationError(
            f"Cannot create entries for {entry.entry_date}. "
            f"The accounting period ({period}) is {period.status}."
        )


def validate_entry(entry):
    """
    Run all entry-level validations.

    Raises:
        ValidationError: If any validation fails.
    """
    validate_entry_minimum_lines(entry)
    validate_entry_not_zero(entry)
    validate_entry_balance(entry)
    validate_line_accounts_active(entry)
    validate_entry_period(entry)
