"""
Quote Number Generator

Generates unique quote numbers in the format QT-YYYY-NNNNN.
Uses database-level atomic operations for thread safety.
"""

from django.db import transaction
from django.utils import timezone


class QuoteNumberGenerator:
    """
    Generates sequential quote numbers with yearly reset.

    Format: QT-{YEAR}-{SEQUENCE:05d}
    Example: QT-2026-00001, QT-2026-00142
    """

    PREFIX = "QT"

    @classmethod
    def generate(cls) -> str:
        """
        Generate the next quote number atomically.

        Returns:
            str: Quote number like 'QT-2026-00001'
        """
        from apps.quotes.models.quote_sequence import QuoteSequence

        year = timezone.now().year

        with transaction.atomic():
            seq, _created = QuoteSequence.objects.select_for_update().get_or_create(
                year=year,
                defaults={"last_number": 0},
            )
            seq.last_number += 1
            seq.save(update_fields=["last_number"])
            next_number = seq.last_number

        return f"{cls.PREFIX}-{year}-{next_number:05d}"
