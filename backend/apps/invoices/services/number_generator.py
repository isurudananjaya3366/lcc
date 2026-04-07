"""
Invoice number generator.

Generates unique invoice numbers with yearly sequence reset.
Format: {PREFIX}-{YEAR}-{SEQUENCE:05d}
"""

from django.db import transaction
from django.utils import timezone

from apps.invoices.constants import InvoiceType, INVOICE_NUMBER_PREFIX


class InvoiceNumberGenerator:
    """
    Generates unique invoice numbers per type with yearly reset.

    Format by type:
        STANDARD:    INV-2026-00001
        SVAT:        SVAT-2026-00001
        CREDIT_NOTE: CN-2026-00001
        DEBIT_NOTE:  DN-2026-00001
    """

    @classmethod
    @transaction.atomic
    def get_next_number(cls, invoice_type, year=None):
        """Generate the next invoice number for the given type and year."""
        from apps.invoices.models import Invoice

        if year is None:
            year = timezone.now().year

        prefix = INVOICE_NUMBER_PREFIX.get(invoice_type, "INV")
        pattern = f"{prefix}-{year}-"

        # Lock rows for this type/year to prevent race conditions
        last_invoice = (
            Invoice.objects.select_for_update()
            .filter(
                invoice_number__startswith=pattern,
                type=invoice_type,
            )
            .order_by("-invoice_number")
            .first()
        )

        if last_invoice and last_invoice.invoice_number:
            sequence = cls._extract_sequence(last_invoice.invoice_number)
            next_seq = sequence + 1
        else:
            next_seq = 1

        return f"{prefix}-{year}-{next_seq:05d}"

    @classmethod
    def _extract_sequence(cls, invoice_number):
        """Extract the sequence number from a formatted invoice number."""
        try:
            parts = invoice_number.rsplit("-", 1)
            return int(parts[-1])
        except (ValueError, IndexError):
            return 0
