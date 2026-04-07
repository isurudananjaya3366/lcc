"""
Invoice service — core business logic for invoice operations.

Handles creation, status transitions, overdue checks, and aging.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from apps.invoices.constants import (
    ALLOWED_TRANSITIONS,
    EDITABLE_STATES,
    InvoiceStatus,
    InvoiceType,
    TERMINAL_STATES,
)
from apps.invoices.exceptions import (
    InvoiceError,
    InvoiceLockedError,
    InvalidTransitionError,
)

logger = logging.getLogger(__name__)


class InvoiceService:
    """Stateless service for invoice business operations."""

    # ── Status Transitions ──────────────────────────────────────────

    @classmethod
    def _validate_transition(cls, invoice, new_status):
        """Validate that the status transition is allowed."""
        allowed = ALLOWED_TRANSITIONS.get(invoice.status, [])
        if new_status not in allowed:
            raise InvalidTransitionError(
                f"Cannot transition from {invoice.status} to {new_status}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

    @classmethod
    @transaction.atomic
    def issue_invoice(cls, invoice_id, user=None):
        """Issue a draft invoice — assigns number and locks it."""
        from apps.invoices.models import Invoice
        from apps.invoices.services.number_generator import InvoiceNumberGenerator

        invoice = Invoice.objects.select_for_update().get(id=invoice_id)
        cls._validate_transition(invoice, InvoiceStatus.ISSUED)

        if not invoice.line_items.exists():
            raise InvoiceError("Cannot issue an invoice with no line items.")

        if not invoice.invoice_number:
            invoice.invoice_number = InvoiceNumberGenerator.get_next_number(invoice.type)

        invoice.status = InvoiceStatus.ISSUED
        if not invoice.issue_date:
            invoice.issue_date = timezone.now().date()
        if not invoice.due_date:
            invoice.due_date = cls._calculate_due_date(
                invoice.issue_date, days=invoice.payment_terms
            )
        invoice.save()

        cls._log_history(invoice, "ISSUED", user=user)
        logger.info("Invoice %s issued", invoice.invoice_number)
        return invoice

    @classmethod
    @transaction.atomic
    def send_invoice(cls, invoice_id, user=None):
        """Mark invoice as sent."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.select_for_update().get(id=invoice_id)
        cls._validate_transition(invoice, InvoiceStatus.SENT)
        invoice.status = InvoiceStatus.SENT
        invoice.save(update_fields=["status", "updated_on"])
        cls._log_history(invoice, "SENT", user=user)
        return invoice

    @classmethod
    @transaction.atomic
    def mark_paid(cls, invoice_id, amount=None, paid_date=None, user=None):
        """Record payment — full or partial."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.select_for_update().get(id=invoice_id)
        if amount is None:
            amount = invoice.balance_due

        invoice.amount_paid += amount
        invoice.balance_due = invoice.total - invoice.amount_paid

        if invoice.balance_due <= Decimal("0.00"):
            cls._validate_transition(invoice, InvoiceStatus.PAID)
            invoice.status = InvoiceStatus.PAID
            invoice.paid_date = paid_date or timezone.now().date()
            invoice.balance_due = Decimal("0.00")
        else:
            if invoice.status not in (InvoiceStatus.PARTIAL,):
                cls._validate_transition(invoice, InvoiceStatus.PARTIAL)
            invoice.status = InvoiceStatus.PARTIAL

        invoice.save()
        cls._log_history(invoice, "PAYMENT_RECORDED", user=user, notes=f"Amount: {amount}")
        return invoice

    @classmethod
    @transaction.atomic
    def cancel_invoice(cls, invoice_id, reason="", user=None):
        """Cancel a draft invoice."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.select_for_update().get(id=invoice_id)
        cls._validate_transition(invoice, InvoiceStatus.CANCELLED)
        invoice.status = InvoiceStatus.CANCELLED
        invoice.cancelled_date = timezone.now()
        invoice.internal_notes = (
            f"{invoice.internal_notes}\nCancelled: {reason}".strip()
            if reason else invoice.internal_notes
        )
        invoice.save()
        cls._log_history(invoice, "CANCELLED", user=user, notes=reason)
        return invoice

    @classmethod
    @transaction.atomic
    def void_invoice(cls, invoice_id, reason="", user=None):
        """Void an issued invoice."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.select_for_update().get(id=invoice_id)
        cls._validate_transition(invoice, InvoiceStatus.VOID)
        invoice.status = InvoiceStatus.VOID
        invoice.voided_date = timezone.now()
        invoice.internal_notes = (
            f"{invoice.internal_notes}\nVoided: {reason}".strip()
            if reason else invoice.internal_notes
        )
        invoice.save()
        cls._log_history(invoice, "VOIDED", user=user, notes=reason)
        return invoice

    # ── Creation Methods ────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def create_invoice(cls, data, line_items_data=None, user=None):
        """Create an invoice manually (without an order)."""
        from apps.invoices.models import Invoice, InvoiceLineItem
        from apps.invoices.services.calculation_service import InvoiceCalculationService

        invoice = Invoice(
            type=data.get("type", InvoiceType.STANDARD),
            status=InvoiceStatus.DRAFT,
            customer_id=data.get("customer_id"),
            customer_name=data.get("customer_name", ""),
            customer_email=data.get("customer_email", ""),
            customer_phone=data.get("customer_phone", ""),
            customer_address=data.get("customer_address", ""),
            business_name=data.get("business_name", ""),
            business_address=data.get("business_address", ""),
            business_phone=data.get("business_phone", ""),
            business_email=data.get("business_email", ""),
            notes=data.get("notes", ""),
            terms_and_conditions=data.get("terms_and_conditions", ""),
            payment_instructions=data.get("payment_instructions", ""),
            currency=data.get("currency", "LKR"),
            tax_scheme=data.get("tax_scheme", "VAT"),
            created_by=user,
        )
        invoice.save()

        if line_items_data:
            for idx, item_data in enumerate(line_items_data):
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    position=idx + 1,
                    description=item_data.get("description", ""),
                    sku=item_data.get("sku", ""),
                    product_id=item_data.get("product_id"),
                    variant_id=item_data.get("variant_id"),
                    quantity=item_data.get("quantity", Decimal("1")),
                    unit_price=item_data.get("unit_price", Decimal("0")),
                    original_price=item_data.get("original_price", Decimal("0")),
                    discount_type=item_data.get("discount_type", ""),
                    discount_value=item_data.get("discount_value", Decimal("0")),
                    tax_rate=item_data.get("tax_rate", Decimal("0")),
                    is_taxable=item_data.get("is_taxable", True),
                    tax_code=item_data.get("tax_code", ""),
                    hsn_code=item_data.get("hsn_code", ""),
                )

        InvoiceCalculationService.recalculate_invoice(invoice.id)
        invoice.refresh_from_db()
        cls._log_history(invoice, "CREATED", user=user)
        return invoice

    @classmethod
    @transaction.atomic
    def create_from_order(cls, order_id, user=None):
        """Auto-generate an invoice from a completed order."""
        from apps.invoices.models import Invoice
        from apps.invoices.services.calculation_service import InvoiceCalculationService
        from apps.orders.models import Order

        order = Order.objects.select_related("customer").get(id=order_id)

        invoice = Invoice(
            type=InvoiceType.STANDARD,
            status=InvoiceStatus.DRAFT,
            order=order,
            customer=order.customer,
            customer_name=getattr(order, "customer_name", "") or "",
            customer_email=getattr(order, "customer_email", "") or "",
            customer_phone=getattr(order, "customer_phone", "") or "",
            issue_date=timezone.now().date(),
            due_date=cls._calculate_due_date(timezone.now().date()),
            notes=getattr(order, "notes", "") or "",
            external_reference=order.order_number,
            created_by=user,
        )
        invoice.save()

        cls._copy_order_line_items(order, invoice)
        InvoiceCalculationService.recalculate_invoice(invoice.id)
        invoice.refresh_from_db()
        cls._log_history(invoice, "CREATED_FROM_ORDER", user=user, notes=f"Order: {order.order_number}")
        return invoice

    @classmethod
    def _copy_order_line_items(cls, order, invoice):
        """Copy line items from an order to an invoice."""
        from apps.invoices.models import InvoiceLineItem

        for idx, order_item in enumerate(order.line_items.all().order_by("id")):
            InvoiceLineItem.objects.create(
                invoice=invoice,
                position=idx + 1,
                product=getattr(order_item, "product", None),
                variant=getattr(order_item, "variant", None),
                description=getattr(order_item, "description", "") or "",
                sku=getattr(order_item, "sku", "") or "",
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                original_price=getattr(order_item, "original_price", order_item.unit_price),
                discount_amount=getattr(order_item, "discount_amount", Decimal("0")),
                tax_amount=getattr(order_item, "tax_amount", Decimal("0")),
                tax_rate=getattr(order_item, "tax_rate", Decimal("0")) or Decimal("0"),
                is_taxable=True,
                line_total=getattr(order_item, "line_total", Decimal("0")),
            )

    @classmethod
    @transaction.atomic
    def duplicate_invoice(cls, invoice_id, user=None):
        """Duplicate an existing invoice as a new draft."""
        from apps.invoices.models import Invoice, InvoiceLineItem
        from apps.invoices.services.calculation_service import InvoiceCalculationService

        source = Invoice.objects.get(id=invoice_id)

        new_invoice = Invoice(
            type=source.type,
            status=InvoiceStatus.DRAFT,
            customer=source.customer,
            customer_name=source.customer_name,
            customer_email=source.customer_email,
            customer_phone=source.customer_phone,
            customer_address=source.customer_address,
            business_name=source.business_name,
            business_address=source.business_address,
            business_phone=source.business_phone,
            business_email=source.business_email,
            business_website=source.business_website,
            business_registration_number=source.business_registration_number,
            vat_registration_number=source.vat_registration_number,
            svat_number=source.svat_number,
            tax_scheme=source.tax_scheme,
            discount_type=source.discount_type,
            discount_value=source.discount_value,
            terms_and_conditions=source.terms_and_conditions,
            payment_instructions=source.payment_instructions,
            footer_text=source.footer_text,
            notes=source.notes,
            currency=source.currency,
            exchange_rate=source.exchange_rate,
            currency_symbol=source.currency_symbol,
            created_by=user,
        )
        new_invoice.save()

        for item in source.line_items.all().order_by("position"):
            InvoiceLineItem.objects.create(
                invoice=new_invoice,
                position=item.position,
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

        InvoiceCalculationService.recalculate_invoice(new_invoice.id)
        new_invoice.refresh_from_db()
        cls._log_history(new_invoice, "DUPLICATED", user=user, notes=f"From: {source.invoice_number or source.id}")
        return new_invoice

    # ── Overdue & Aging ─────────────────────────────────────────────

    @classmethod
    def check_and_mark_overdue(cls):
        """Find and mark overdue invoices. Returns count of affected."""
        from apps.invoices.models import Invoice

        today = timezone.now().date()
        overdue_qs = Invoice.objects.filter(
            status__in=[InvoiceStatus.ISSUED, InvoiceStatus.SENT, InvoiceStatus.PARTIAL],
            due_date__lt=today,
            balance_due__gt=Decimal("0.00"),
            is_deleted=False,
        )
        count = overdue_qs.update(status=InvoiceStatus.OVERDUE)
        if count:
            logger.info("Marked %d invoices as overdue", count)
        return count

    @classmethod
    def get_aging_report(cls):
        """
        Return invoice aging summary grouped by bucket.
        Buckets: current, 1-30, 31-60, 61-90, 90+
        """
        from apps.invoices.models import Invoice

        today = timezone.now().date()
        unpaid = Invoice.objects.filter(
            status__in=[
                InvoiceStatus.ISSUED, InvoiceStatus.SENT,
                InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE,
            ],
            is_deleted=False,
        )

        buckets = {
            "current": Decimal("0.00"),
            "30_days": Decimal("0.00"),
            "60_days": Decimal("0.00"),
            "90_days": Decimal("0.00"),
            "90_plus": Decimal("0.00"),
        }

        for inv in unpaid.only("due_date", "balance_due"):
            if not inv.due_date or inv.due_date >= today:
                buckets["current"] += inv.balance_due
            else:
                days = (today - inv.due_date).days
                if days <= 30:
                    buckets["30_days"] += inv.balance_due
                elif days <= 60:
                    buckets["60_days"] += inv.balance_due
                elif days <= 90:
                    buckets["90_days"] += inv.balance_due
                else:
                    buckets["90_plus"] += inv.balance_due

        buckets["total"] = sum(buckets.values())
        return buckets

    # ── History ─────────────────────────────────────────────────────

    @classmethod
    def _log_history(cls, invoice, action, user=None, notes="", **metadata):
        """Log an invoice history event."""
        from apps.invoices.models.history import InvoiceHistory

        InvoiceHistory.objects.create(
            invoice=invoice,
            action=action,
            old_status=getattr(invoice, "_original_status", ""),
            new_status=invoice.status,
            user=user,
            notes=notes,
            metadata=metadata if metadata else {},
        )

    # ── Helpers ─────────────────────────────────────────────────────

    @classmethod
    def _calculate_due_date(cls, issue_date, days=None):
        """Calculate due date from issue date."""
        if days is None:
            days = 30
        return issue_date + timedelta(days=days)

    # ── Convenience Aliases ──────────────────────────────────────────

    issue = issue_invoice
    send = send_invoice
    cancel = cancel_invoice
    void = void_invoice
