"""
Credit note service — creation and application of credit notes.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.invoices.constants import (
    CreditNoteReason,
    InvoiceStatus,
    InvoiceType,
    TERMINAL_STATES,
)
from apps.invoices.exceptions import CreditLimitExceededError, InvoiceError

logger = logging.getLogger(__name__)


class CreditNoteService:
    """Service for credit note operations."""

    @classmethod
    @transaction.atomic
    def create_credit_note(
        cls, original_invoice_id, reason, amount=None, items=None,
        reason_notes="", user=None,
        # Legacy aliases
        line_items_data=None, notes=None,
    ):
        """
        Create a credit note linked to an original invoice.

        Args:
            original_invoice_id: UUID of the original invoice.
            reason: CreditNoteReason value.
            amount: Optional total credit amount (for simple single-item credit).
            items: List of line item dicts (for itemized credit).
            reason_notes: Detailed explanation.
            user: User creating the credit note.
            line_items_data: Legacy alias for items.
            notes: Legacy alias for reason_notes.

        If neither items nor amount is provided, copies all line items
        from the original invoice (full credit).
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
        valid_reasons = {r.value for r in CreditNoteReason}
        reason_val = reason.value if hasattr(reason, "value") else reason
        if reason_val not in valid_reasons:
            raise InvoiceError(f"Invalid credit note reason: {reason_val}")

        original = Invoice.objects.select_for_update().get(id=original_invoice_id)

        if original.status in {InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED, InvoiceStatus.VOID}:
            raise InvoiceError(
                f"Cannot create credit note for invoice in {original.status} status."
            )

        credit_note = Invoice(
            type=InvoiceType.CREDIT_NOTE,
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
        # Generate credit note number
        credit_note.invoice_number = InvoiceNumberGenerator.get_next_number(
            InvoiceType.CREDIT_NOTE
        )
        credit_note.save()

        if items:
            # Itemized credit
            for idx, item_data in enumerate(items):
                InvoiceLineItem.objects.create(
                    invoice=credit_note,
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
            # Simple single-item credit
            InvoiceLineItem.objects.create(
                invoice=credit_note,
                position=1,
                description=f"Credit: {reason_val}",
                quantity=Decimal("1"),
                unit_price=Decimal(str(amount)),
                is_taxable=False,
            )
        else:
            # Full credit — copy all line items from original invoice
            cls.copy_line_items_from_invoice(original_invoice_id, credit_note)

        InvoiceCalculationService.recalculate_invoice(credit_note.id)
        credit_note.refresh_from_db()

        # Validate credit limit
        cls._validate_credit_limit(original, credit_note)

        from apps.invoices.services.invoice_service import InvoiceService
        InvoiceService._log_history(
            credit_note, "CREDIT_NOTE_CREATED", user=user,
            notes=f"Reason: {reason_val}. Original: {original.invoice_number or original.id}",
        )
        logger.info("Credit note %s created for invoice %s", credit_note.invoice_number, original.invoice_number)
        return credit_note

    @classmethod
    def _validate_credit_limit(cls, original, credit_note):
        """Ensure total credits don't exceed original invoice total."""
        from apps.invoices.models import Invoice

        existing_credits = (
            Invoice.objects.filter(
                related_invoice=original,
                type=InvoiceType.CREDIT_NOTE,
                is_deleted=False,
            )
            .exclude(status__in=[InvoiceStatus.CANCELLED, InvoiceStatus.VOID])
            .exclude(id=credit_note.id)
        )
        applied = sum(
            cn.total for cn in existing_credits.filter(status=InvoiceStatus.PAID)
        )
        pending = sum(
            cn.total for cn in existing_credits.exclude(status=InvoiceStatus.PAID)
        )
        max_creditable = original.total - original.amount_paid - applied - pending
        if credit_note.total > max_creditable:
            raise CreditLimitExceededError(
                f"Credit note total ({credit_note.total}) exceeds maximum "
                f"creditable amount ({max_creditable}). "
                f"Original total: {original.total}, paid: {original.amount_paid}, "
                f"applied credits: {applied}, pending credits: {pending}."
            )

    @classmethod
    @transaction.atomic
    def issue_credit_note(cls, credit_note_id, user=None):
        """
        Issue and apply a credit note.

        Credit notes are created with ISSUED status, so this method
        primarily applies the credit to the original invoice.
        If the credit note is still DRAFT (edge case), it issues it first.
        """
        from apps.invoices.models import Invoice
        from apps.invoices.services.invoice_service import InvoiceService

        credit_note = Invoice.objects.select_for_update().get(id=credit_note_id)
        if credit_note.status == InvoiceStatus.DRAFT:
            credit_note = InvoiceService.issue_invoice(credit_note_id, user=user)
        if credit_note.related_invoice:
            cls.apply_credit_note(credit_note)
        return credit_note

    @classmethod
    @transaction.atomic
    def apply_credit_note(cls, credit_note):
        """Apply credit note amount to the original invoice's balance."""
        original = credit_note.related_invoice
        if not original:
            return

        original.amount_paid += credit_note.total
        original.balance_due = original.total - original.amount_paid
        if original.balance_due <= Decimal("0.00"):
            original.balance_due = Decimal("0.00")
            if original.status not in TERMINAL_STATES:
                original.status = InvoiceStatus.PAID
                original.paid_date = timezone.now().date()
        original.save()

    @classmethod
    def copy_line_items_from_invoice(cls, original_invoice_id, credit_note, item_ids=None):
        """Copy selected (or all) line items from the original invoice."""
        from apps.invoices.models import Invoice, InvoiceLineItem

        original = Invoice.objects.get(id=original_invoice_id)
        qs = original.line_items.all().order_by("position")
        if item_ids:
            qs = qs.filter(id__in=item_ids)

        for idx, item in enumerate(qs):
            InvoiceLineItem.objects.create(
                invoice=credit_note,
                position=idx + 1,
                product=item.product,
                variant=item.variant,
                description=item.description,
                sku=item.sku,
                quantity=item.quantity,
                unit_price=item.unit_price,
                original_price=item.original_price,
                unit_of_measure=item.unit_of_measure,
                discount_type=item.discount_type,
                discount_value=item.discount_value,
                tax_rate=item.tax_rate,
                is_taxable=item.is_taxable,
                tax_code=item.tax_code,
                tax_description=item.tax_description,
                hsn_code=item.hsn_code,
            )
