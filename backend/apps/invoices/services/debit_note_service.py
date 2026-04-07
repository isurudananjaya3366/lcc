"""
Debit note service — creation and application of debit notes.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.invoices.constants import DebitNoteReason, InvoiceStatus, InvoiceType
from apps.invoices.exceptions import InvoiceError

logger = logging.getLogger(__name__)


class DebitNoteService:
    """Service for debit note operations."""

    @classmethod
    @transaction.atomic
    def create_debit_note(
        cls, original_invoice_id, reason, amount=None, items=None,
        reason_notes="", user=None,
        # Legacy aliases
        line_items_data=None, notes=None,
    ):
        """
        Create a debit note linked to an original invoice.

        Args:
            original_invoice_id: UUID of the original invoice.
            reason: DebitNoteReason value.
            amount: Optional total debit amount (for simple single-item debit).
            items: List of line item dicts (for itemized debit).
            reason_notes: Detailed explanation.
            user: User creating the debit note.
            line_items_data: Legacy alias for items.
            notes: Legacy alias for reason_notes.

        If amount is provided without items, a single line item is created.
        """
        from apps.invoices.models import Invoice, InvoiceLineItem
        from apps.invoices.services.calculation_service import InvoiceCalculationService
        from apps.invoices.services.number_generator import InvoiceNumberGenerator

        # Support legacy parameter names
        if items is None and line_items_data is not None:
            items = line_items_data
        if notes is not None and not reason_notes:
            reason_notes = notes

        # Validate reason
        valid_reasons = {r.value for r in DebitNoteReason}
        reason_val = reason.value if hasattr(reason, "value") else reason
        if reason_val not in valid_reasons:
            raise InvoiceError(f"Invalid debit note reason: {reason_val}")

        original = Invoice.objects.select_for_update().get(id=original_invoice_id)

        if original.status in {InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED, InvoiceStatus.VOID}:
            raise InvoiceError(
                f"Cannot create debit note for invoice in {original.status} status."
            )

        debit_note = Invoice(
            type=InvoiceType.DEBIT_NOTE,
            status=InvoiceStatus.ISSUED,
            related_invoice=original,
            customer=original.customer,
            customer_name=original.customer_name,
            customer_email=original.customer_email,
            customer_phone=original.customer_phone,
            customer_address=original.customer_address,
            business_name=original.business_name,
            business_address=original.business_address,
            business_phone=original.business_phone,
            business_email=original.business_email,
            business_website=original.business_website,
            business_registration_number=original.business_registration_number,
            vat_registration_number=original.vat_registration_number,
            svat_number=original.svat_number,
            tax_scheme=original.tax_scheme,
            currency=original.currency,
            exchange_rate=original.exchange_rate,
            currency_symbol=original.currency_symbol,
            notes=reason_notes,
            external_reference=original.invoice_number or "",
            issue_date=timezone.now().date(),
            created_by=user,
        )
        # Generate debit note number
        debit_note.invoice_number = InvoiceNumberGenerator.get_next_number(
            InvoiceType.DEBIT_NOTE
        )
        debit_note.save()

        if items:
            # Itemized charges
            for idx, item_data in enumerate(items):
                InvoiceLineItem.objects.create(
                    invoice=debit_note,
                    position=idx + 1,
                    description=item_data.get("description", ""),
                    sku=item_data.get("sku", ""),
                    product_id=item_data.get("product_id"),
                    variant_id=item_data.get("variant_id"),
                    quantity=item_data.get("quantity", Decimal("1")),
                    unit_price=item_data.get("unit_price", Decimal("0")),
                    discount_type=item_data.get("discount_type", ""),
                    discount_value=item_data.get("discount_value", Decimal("0")),
                    tax_rate=item_data.get("tax_rate", Decimal("0")),
                    is_taxable=item_data.get("is_taxable", True),
                    tax_code=item_data.get("tax_code", ""),
                    hsn_code=item_data.get("hsn_code", ""),
                )
        elif amount is not None:
            # Simple single-item debit
            InvoiceLineItem.objects.create(
                invoice=debit_note,
                position=1,
                description=f"Additional charge: {reason_val}",
                quantity=Decimal("1"),
                unit_price=Decimal(str(amount)),
                is_taxable=False,
            )
        else:
            raise InvoiceError(
                "Debit note requires either 'items' or 'amount' to be provided."
            )

        InvoiceCalculationService.recalculate_invoice(debit_note.id)
        debit_note.refresh_from_db()

        from apps.invoices.services.invoice_service import InvoiceService
        InvoiceService._log_history(
            debit_note, "DEBIT_NOTE_CREATED", user=user,
            notes=f"Reason: {reason_val}. Original: {original.invoice_number or original.id}",
        )
        logger.info("Debit note %s created for invoice %s", debit_note.invoice_number, original.invoice_number)
        return debit_note

    @classmethod
    @transaction.atomic
    def issue_debit_note(cls, debit_note_id, user=None):
        """
        Issue and apply a debit note.

        Debit notes are created with ISSUED status, so this method
        primarily applies the debit to the original invoice.
        If the debit note is still DRAFT (edge case), it issues it first.
        """
        from apps.invoices.models import Invoice
        from apps.invoices.services.invoice_service import InvoiceService

        debit_note = Invoice.objects.select_for_update().get(id=debit_note_id)
        if debit_note.status == InvoiceStatus.DRAFT:
            debit_note = InvoiceService.issue_invoice(debit_note_id, user=user)
        if debit_note.related_invoice:
            cls.apply_debit_note(debit_note)
        return debit_note

    @classmethod
    @transaction.atomic
    def apply_debit_note(cls, debit_note):
        """Apply debit note — increases original invoice's balance."""
        original = debit_note.related_invoice
        if not original:
            return

        original.balance_due += debit_note.total
        if original.balance_due > Decimal("0.00") and original.status == InvoiceStatus.PAID:
            original.status = InvoiceStatus.PARTIAL
            original.paid_date = None
        original.save()
