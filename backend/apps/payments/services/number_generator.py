"""
Payment number generator service.

Generates unique payment numbers in format PAY-YYYY-NNNNN
with yearly sequence reset and tenant isolation.
"""

from django.db import transaction
from django.utils import timezone

from apps.payments.constants import PAYMENT_NUMBER_PREFIX


class PaymentNumberGenerator:
    """
    Generates unique payment numbers: PAY-YYYY-NNNNN.

    Thread-safe via select_for_update on the sequence row.
    Yearly reset — sequence restarts at 1 each calendar year.
    Tenant isolation is automatic via django-tenants schema routing.
    """

    PREFIX = PAYMENT_NUMBER_PREFIX

    @classmethod
    def generate(cls, year=None):
        """
        Generate the next payment number for the current tenant.

        Args:
            year: Override year (defaults to current year).

        Returns:
            str: Payment number in format PAY-YYYY-NNNNN.
        """
        from apps.payments.models.payment_sequence import PaymentSequence

        if year is None:
            year = timezone.now().year

        with transaction.atomic():
            seq, _ = PaymentSequence.objects.select_for_update().get_or_create(
                year=year, defaults={"last_number": 0}
            )
            seq.last_number += 1
            seq.save(update_fields=["last_number"])
            return f"{cls.PREFIX}-{year}-{seq.last_number:05d}"

    @staticmethod
    def parse_payment_number(number):
        """
        Parse a payment number into its components.

        Args:
            number: Payment number string (e.g. "PAY-2026-00042").

        Returns:
            dict: {"prefix": "PAY", "year": 2026, "sequence": 42}
        """
        parts = number.split("-")
        if len(parts) != 3:
            raise ValueError(f"Invalid payment number format: {number}")
        return {
            "prefix": parts[0],
            "year": int(parts[1]),
            "sequence": int(parts[2]),
        }

    @classmethod
    def get_current_sequence(cls, year=None):
        """
        Get the current sequence number without incrementing.

        Returns:
            int: Current last_number for the year (0 if no payments yet).
        """
        from apps.payments.models.payment_sequence import PaymentSequence

        if year is None:
            year = timezone.now().year

        try:
            seq = PaymentSequence.objects.get(year=year)
            return seq.last_number
        except PaymentSequence.DoesNotExist:
            return 0

    @classmethod
    def preview_next_number(cls, year=None):
        """
        Preview the next payment number without generating it.

        Returns:
            str: The number that would be generated next.
        """
        if year is None:
            year = timezone.now().year

        current = cls.get_current_sequence(year)
        return f"{cls.PREFIX}-{year}-{current + 1:05d}"
