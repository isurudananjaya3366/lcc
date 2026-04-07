"""
Invoice balance recalculation — accounts for credit/debit notes.
"""

from decimal import Decimal

from django.db import transaction

from apps.invoices.constants import InvoiceStatus, InvoiceType, TERMINAL_STATES


class InvoiceBalanceService:
    """Recalculates invoice balance considering credit/debit note adjustments."""

    @classmethod
    @transaction.atomic
    def recalculate_balance(cls, invoice_id):
        """
        Recalculate balance for an invoice considering:
        - Direct payments (amount_paid)
        - Applied credit notes (reduce balance)
        - Applied debit notes (increase balance)
        """
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.select_for_update().get(id=invoice_id)

        # Sum issued credit notes
        credit_total = Decimal("0.00")
        for cn in invoice.adjustment_invoices.filter(
            type=InvoiceType.CREDIT_NOTE, is_deleted=False,
        ).exclude(status__in=[InvoiceStatus.CANCELLED, InvoiceStatus.VOID, InvoiceStatus.DRAFT]):
            credit_total += cn.total

        # Sum issued debit notes
        debit_total = Decimal("0.00")
        for dn in invoice.adjustment_invoices.filter(
            type=InvoiceType.DEBIT_NOTE, is_deleted=False,
        ).exclude(status__in=[InvoiceStatus.CANCELLED, InvoiceStatus.VOID, InvoiceStatus.DRAFT]):
            debit_total += dn.total

        effective_total = invoice.total + debit_total
        effective_paid = invoice.amount_paid + credit_total
        invoice.balance_due = max(effective_total - effective_paid, Decimal("0.00"))
        invoice.save(update_fields=["balance_due"])
        return invoice
