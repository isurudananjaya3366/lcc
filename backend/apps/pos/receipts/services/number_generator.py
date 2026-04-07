"""
ReceiptNumberGenerator — generates unique sequential receipt numbers.

Task 33: Format  REC-YYYYMMDD-NNNNN  with daily reset.
"""

import logging

from django.db import transaction
from django.utils import timezone

from apps.pos.receipts.services.exceptions import ReceiptNumberGenerationError

logger = logging.getLogger(__name__)


class ReceiptNumberGenerator:
    """
    Generates unique, sequential receipt numbers.

    Format: REC-YYYYMMDD-NNNNN
    - Daily sequence reset
    - Tenant isolation via schema
    - Thread-safe (select_for_update)
    """

    PREFIX = "REC"
    SEQUENCE_LENGTH = 5
    MAX_SEQUENCE = 99999
    MAX_RETRIES = 5

    def generate(self):
        """
        Generate next receipt number.

        Returns:
            str: e.g. ``REC-20260122-00042``

        Raises:
            ReceiptNumberGenerationError: on failure after retries.
        """
        attempts = 0

        while attempts < self.MAX_RETRIES:
            try:
                current_date = timezone.now().date()
                sequence = self._get_next_sequence(current_date)
                receipt_number = self._format_receipt_number(current_date, sequence)

                if self._verify_unique(receipt_number):
                    return receipt_number

                attempts += 1
                logger.warning(
                    "Receipt number conflict: %s, retry %d/%d",
                    receipt_number,
                    attempts,
                    self.MAX_RETRIES,
                )
            except ReceiptNumberGenerationError:
                raise
            except Exception as e:
                attempts += 1
                logger.error(
                    "Error generating receipt number: %s, retry %d/%d",
                    e,
                    attempts,
                    self.MAX_RETRIES,
                )

        raise ReceiptNumberGenerationError(
            f"Failed to generate unique receipt number after {self.MAX_RETRIES} attempts"
        )

    # ── internals ─────────────────────────────────────────────

    def _get_next_sequence(self, date):
        from apps.pos.receipts.models import ReceiptSequence

        with transaction.atomic():
            seq, _created = ReceiptSequence.objects.select_for_update().get_or_create(
                date=date,
                defaults={"current_sequence": 0},
            )
            seq.current_sequence += 1

            if seq.current_sequence > self.MAX_SEQUENCE:
                raise ReceiptNumberGenerationError(
                    f"Sequence overflow for date {date}: "
                    f"exceeded maximum of {self.MAX_SEQUENCE}"
                )

            seq.save(update_fields=["current_sequence", "updated_on"])
            return seq.current_sequence

    def _format_receipt_number(self, date, sequence):
        date_str = date.strftime("%Y%m%d")
        seq_str = str(sequence).zfill(self.SEQUENCE_LENGTH)
        return f"{self.PREFIX}-{date_str}-{seq_str}"

    def _verify_unique(self, receipt_number):
        from apps.pos.receipts.models import Receipt

        return not Receipt.objects.filter(receipt_number=receipt_number).exists()
