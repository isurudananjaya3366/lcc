"""
Vendor Bill Service.

Business logic for creating, updating, and managing vendor bills
through their lifecycle.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from apps.vendor_bills.constants import (
    BILL_STATUS_APPROVED,
    BILL_STATUS_CANCELLED,
    BILL_STATUS_DISPUTED,
    BILL_STATUS_DRAFT,
    BILL_STATUS_PAID,
    BILL_STATUS_PARTIAL_PAID,
    BILL_STATUS_PENDING,
    BILL_STATUS_TRANSITIONS,
    CHANGE_TYPE_APPROVED,
    CHANGE_TYPE_CANCELLED,
    CHANGE_TYPE_CREATED,
    CHANGE_TYPE_DISPUTED,
    CHANGE_TYPE_LINE_ADDED,
    CHANGE_TYPE_LINE_REMOVED,
    CHANGE_TYPE_LINE_UPDATED,
    CHANGE_TYPE_STATUS_CHANGED,
    CHANGE_TYPE_SUBMITTED,
    CHANGE_TYPE_UPDATED,
    PAYMENT_TERMS_DAYS,
)
from apps.vendor_bills.models.bill_line_item import BillLineItem
from apps.vendor_bills.models.vendor_bill import VendorBill


# ── Custom Exceptions ──────────────────────────────────────────────────


class BillNotEditableError(Exception):
    """Raised when attempting to edit a bill not in DRAFT status."""
    pass


class InvalidBillTransitionError(Exception):
    """Raised when an invalid bill status transition is attempted."""
    pass


class BillValidationError(Exception):
    """Raised when bill validation fails."""
    pass


class BillService:
    """Service class for vendor bill lifecycle management."""

    # ── Bill Creation ─────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def create_from_po(cls, purchase_order, user, bill_data=None):
        """
        Create a vendor bill from a completed purchase order.

        Args:
            purchase_order: PurchaseOrder instance.
            user: User creating the bill.
            bill_data: Optional dict of additional bill fields.

        Returns:
            VendorBill instance.

        Raises:
            BillValidationError: If PO is not valid for billing.
        """
        bill_data = bill_data or {}

        # Validate PO
        if not hasattr(purchase_order, "status"):
            from apps.purchases.models.purchase_order import PurchaseOrder
            purchase_order = PurchaseOrder.objects.get(pk=purchase_order)

        if purchase_order.status not in ("received", "closed"):
            raise BillValidationError(
                "Purchase order must be in RECEIVED or CLOSED status to create a bill."
            )

        if purchase_order.bills.filter(
            status__in=[BILL_STATUS_DRAFT, BILL_STATUS_PENDING, BILL_STATUS_APPROVED]
        ).exists():
            raise BillValidationError("An active bill already exists for this PO.")

        if not purchase_order.vendor:
            raise BillValidationError("Purchase order must have a valid vendor.")

        # Calculate due date from payment terms
        bill_date = bill_data.get("bill_date", date.today())
        received_date = bill_data.get("received_date", date.today())
        payment_terms = bill_data.get("payment_terms", purchase_order.payment_terms or "net30")
        days = PAYMENT_TERMS_DAYS.get(payment_terms, 30)
        due_date = bill_data.get("due_date", bill_date + timedelta(days=days))

        bill = VendorBill(
            vendor=purchase_order.vendor,
            purchase_order=purchase_order,
            bill_date=bill_date,
            received_date=received_date,
            due_date=due_date,
            payment_terms=payment_terms,
            currency=getattr(purchase_order, "currency", "LKR"),
            status=BILL_STATUS_DRAFT,
            created_by=user,
            notes=bill_data.get("notes", ""),
            internal_notes=bill_data.get(
                "internal_notes",
                f"Created from {purchase_order.po_number}",
            ),
            vendor_invoice_number=bill_data.get("vendor_invoice_number", ""),
        )
        bill.save()

        # Create line items from PO lines
        line_data = cls._auto_fill_from_po(purchase_order)
        for idx, item in enumerate(line_data, start=1):
            BillLineItem.objects.create(
                vendor_bill=bill,
                line_number=idx,
                **item,
            )

        bill.recalculate_from_lines()

        cls._log_history(
            bill, user, CHANGE_TYPE_CREATED,
            new_status=BILL_STATUS_DRAFT,
            description=f"Bill created from {purchase_order.po_number}",
        )
        return bill

    @classmethod
    def _auto_fill_from_po(cls, purchase_order):
        """
        Build line item data from PO and associated GRN lines.

        Returns:
            List of dicts ready for BillLineItem creation.
        """
        line_items = []

        # Build GRN received-quantity map per PO line
        grn_qty_map = {}
        grn_line_map = {}
        try:
            for grn in purchase_order.goods_received_notes.filter(
                status__in=("completed", "received")
            ):
                for grn_line in grn.line_items.all():
                    po_line_id = getattr(grn_line, "po_line_id", None)
                    if po_line_id:
                        grn_qty_map[po_line_id] = grn_qty_map.get(
                            po_line_id, Decimal("0")
                        ) + (grn_line.quantity_received or grn_line.quantity or Decimal("0"))
                        grn_line_map.setdefault(po_line_id, grn_line)
        except Exception:
            pass

        for po_line in purchase_order.line_items.all():
            received_qty = grn_qty_map.get(
                po_line.pk, po_line.quantity_ordered or Decimal("0")
            )
            grn_line = grn_line_map.get(po_line.pk)

            item = {
                "product": po_line.product,
                "variant": getattr(po_line, "variant", None),
                "vendor_sku": getattr(po_line, "vendor_sku", "") or "",
                "item_description": getattr(
                    po_line, "item_description", ""
                ) or getattr(po_line, "product_name", "") or str(po_line.product or ""),
                "quantity": received_qty,
                "quantity_ordered": po_line.quantity_ordered or Decimal("0"),
                "quantity_received": received_qty,
                "unit_price": po_line.unit_price or Decimal("0"),
                "billed_price": po_line.unit_price or Decimal("0"),
                "tax_rate": getattr(po_line, "tax_rate", Decimal("0")) or Decimal("0"),
                "po_line": po_line,
            }
            if grn_line:
                item["grn_line"] = grn_line

            line_items.append(item)

        return line_items

    @classmethod
    @transaction.atomic
    def create_manual(cls, vendor, user, bill_data, line_items_data):
        """
        Create a vendor bill manually without a PO reference.

        Args:
            vendor: Vendor instance.
            user: User creating the bill.
            bill_data: Dict of bill header fields.
            line_items_data: List of dicts with line item fields.

        Returns:
            VendorBill instance.

        Raises:
            BillValidationError: If validation fails.
        """
        if hasattr(vendor, "is_active") and not vendor.is_active:
            raise BillValidationError("Cannot create bill for inactive vendor.")

        if not line_items_data:
            raise BillValidationError("At least one line item is required.")

        bill_date = bill_data.get("bill_date", date.today())
        received_date = bill_data.get("received_date", date.today())
        payment_terms = bill_data.get("payment_terms", "net30")
        days = PAYMENT_TERMS_DAYS.get(payment_terms, 30)
        due_date = bill_data.get("due_date", bill_date + timedelta(days=days))

        if due_date < bill_date:
            raise BillValidationError("Due date must be on or after bill date.")

        bill = VendorBill(
            vendor=vendor,
            bill_date=bill_date,
            received_date=received_date,
            due_date=due_date,
            payment_terms=payment_terms,
            currency=bill_data.get("currency", "LKR"),
            status=BILL_STATUS_DRAFT,
            created_by=user,
            notes=bill_data.get("notes", ""),
            internal_notes=bill_data.get("internal_notes", "Manual bill"),
            vendor_invoice_number=bill_data.get("vendor_invoice_number", ""),
        )
        if bill_data.get("bill_number"):
            bill.bill_number = bill_data["bill_number"]
        bill.save()

        for idx, item_data in enumerate(line_items_data, start=1):
            item_data.setdefault("line_number", idx)
            BillLineItem.objects.create(vendor_bill=bill, **item_data)

        bill.recalculate_from_lines()

        cls._log_history(
            bill, user, CHANGE_TYPE_CREATED,
            new_status=BILL_STATUS_DRAFT,
            description="Manual bill created",
        )
        return bill

    # ── Bill Editing ──────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def update_bill(cls, bill_id, data, user=None):
        """
        Update a bill. Only allowed when status is DRAFT.

        Args:
            bill_id: UUID of the bill.
            data: Dict of fields to update.
            user: User performing the update.

        Returns:
            Updated VendorBill instance.

        Raises:
            BillNotEditableError: If bill is not in DRAFT status.
        """
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        if bill.status != BILL_STATUS_DRAFT:
            raise BillNotEditableError(
                f"Cannot edit bill in '{bill.status}' status. Must be draft."
            )

        changes = {}
        for field, value in data.items():
            if hasattr(bill, field) and field not in (
                "id", "pk", "bill_number", "created_by", "status",
            ):
                old_value = getattr(bill, field)
                if old_value != value:
                    changes[field] = {"old": str(old_value), "new": str(value)}
                    setattr(bill, field, value)

        if changes:
            bill.save()
            cls._log_history(
                bill, user, CHANGE_TYPE_UPDATED,
                old_status=BILL_STATUS_DRAFT,
                new_status=BILL_STATUS_DRAFT,
                description="Bill updated",
                changes=changes,
            )
        return bill

    @classmethod
    @transaction.atomic
    def add_line_item(cls, bill_id, item_data, user=None):
        """Add a line item to a DRAFT bill."""
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        if bill.status != BILL_STATUS_DRAFT:
            raise BillNotEditableError(
                f"Cannot add line items when bill is in '{bill.status}' status."
            )

        max_line = bill.line_items.aggregate(
            max_num=models.Max("line_number")
        )["max_num"] or 0
        item_data.setdefault("line_number", max_line + 1)

        line_item = BillLineItem.objects.create(vendor_bill=bill, **item_data)
        bill.recalculate_from_lines()

        cls._log_history(
            bill, user, CHANGE_TYPE_LINE_ADDED,
            description=f"Line item added: {line_item.item_description}",
            changes={"line_item_id": str(line_item.pk)},
        )
        return line_item

    @classmethod
    @transaction.atomic
    def update_line_item(cls, bill_id, line_item_id, data, user=None):
        """Update a line item on a DRAFT bill."""
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        if bill.status != BILL_STATUS_DRAFT:
            raise BillNotEditableError(
                f"Cannot update line items when bill is in '{bill.status}' status."
            )

        line_item = BillLineItem.objects.get(pk=line_item_id, vendor_bill=bill)
        changes = {}
        for field, value in data.items():
            if hasattr(line_item, field):
                old_value = getattr(line_item, field)
                if old_value != value:
                    changes[field] = {"old": str(old_value), "new": str(value)}
                    setattr(line_item, field, value)

        if changes:
            line_item.save()
            bill.recalculate_from_lines()
            cls._log_history(
                bill, user, CHANGE_TYPE_LINE_UPDATED,
                description=f"Line item updated: {line_item.item_description}",
                changes=changes,
            )
        return line_item

    @classmethod
    @transaction.atomic
    def remove_line_item(cls, bill_id, line_item_id, user=None):
        """Remove a line item from a DRAFT bill."""
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        if bill.status != BILL_STATUS_DRAFT:
            raise BillNotEditableError(
                f"Cannot remove line items when bill is in '{bill.status}' status."
            )

        line_item = BillLineItem.objects.get(pk=line_item_id, vendor_bill=bill)
        description = line_item.item_description
        line_item.delete()
        bill.recalculate_from_lines()

        cls._log_history(
            bill, user, CHANGE_TYPE_LINE_REMOVED,
            description=f"Line item removed: {description}",
            changes={"line_item_id": str(line_item_id)},
        )

    # ── Status Transitions ────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def submit_bill(cls, bill_id, user):
        """
        Submit a bill for approval (DRAFT -> PENDING).

        Args:
            bill_id: UUID of the bill.
            user: User submitting the bill.

        Returns:
            Updated VendorBill instance.
        """
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        cls._validate_transition(bill, BILL_STATUS_PENDING)

        if not bill.line_items.exists():
            raise BillValidationError("Cannot submit a bill with no line items.")

        old_status = bill.status
        bill.status = BILL_STATUS_PENDING
        bill.save(update_fields=["status", "updated_on"])

        cls._log_history(
            bill, user, CHANGE_TYPE_SUBMITTED,
            old_status=old_status,
            new_status=BILL_STATUS_PENDING,
            description="Bill submitted for approval",
        )
        return bill

    @classmethod
    @transaction.atomic
    def approve_bill(cls, bill_id, user, notes=""):
        """
        Approve a bill (PENDING -> APPROVED).

        Args:
            bill_id: UUID of the bill.
            user: User approving the bill.
            notes: Optional approval notes.

        Returns:
            Updated VendorBill instance.
        """
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        cls._validate_transition(bill, BILL_STATUS_APPROVED)

        old_status = bill.status
        bill.status = BILL_STATUS_APPROVED
        bill.approved_by = user
        bill.approved_at = timezone.now()
        bill.save(update_fields=[
            "status", "approved_by", "approved_at", "updated_on",
        ])

        cls._log_history(
            bill, user, CHANGE_TYPE_APPROVED,
            old_status=old_status,
            new_status=BILL_STATUS_APPROVED,
            description=f"Bill approved: {notes}" if notes else "Bill approved",
        )
        return bill

    @classmethod
    @transaction.atomic
    def dispute_bill(cls, bill_id, user, reason):
        """
        Mark a bill as disputed.

        Args:
            bill_id: UUID of the bill.
            user: User raising the dispute.
            reason: Dispute reason (required).

        Returns:
            Updated VendorBill instance.
        """
        if not reason:
            raise BillValidationError("Dispute reason is required.")

        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        cls._validate_transition(bill, BILL_STATUS_DISPUTED)

        old_status = bill.status
        bill.status = BILL_STATUS_DISPUTED
        bill.dispute_reason = reason
        bill.save(update_fields=["status", "dispute_reason", "updated_on"])

        cls._log_history(
            bill, user, CHANGE_TYPE_DISPUTED,
            old_status=old_status,
            new_status=BILL_STATUS_DISPUTED,
            description=f"Bill disputed: {reason}",
        )
        return bill

    @classmethod
    @transaction.atomic
    def cancel_bill(cls, bill_id, user, reason=""):
        """
        Cancel a bill.

        Args:
            bill_id: UUID of the bill.
            user: User cancelling the bill.
            reason: Cancellation reason.

        Returns:
            Updated VendorBill instance.
        """
        bill = VendorBill.objects.select_for_update().get(pk=bill_id)
        cls._validate_transition(bill, BILL_STATUS_CANCELLED)

        old_status = bill.status
        bill.status = BILL_STATUS_CANCELLED
        bill.save(update_fields=["status", "updated_on"])

        cls._log_history(
            bill, user, CHANGE_TYPE_CANCELLED,
            old_status=old_status,
            new_status=BILL_STATUS_CANCELLED,
            description=f"Bill cancelled: {reason}" if reason else "Bill cancelled",
        )
        return bill

    # ── Duplication ───────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def duplicate_bill(cls, bill_id, user=None):
        """
        Duplicate an existing bill as a new DRAFT.

        Args:
            bill_id: UUID of the bill to duplicate.
            user: User performing the duplication.

        Returns:
            New VendorBill instance.
        """
        original = VendorBill.objects.get(pk=bill_id)
        duplicating_user = user or original.created_by

        new_bill = VendorBill(
            vendor=original.vendor,
            bill_date=date.today(),
            received_date=date.today(),
            due_date=date.today() + timedelta(
                days=PAYMENT_TERMS_DAYS.get(original.payment_terms, 30)
            ),
            payment_terms=original.payment_terms,
            currency=original.currency,
            status=BILL_STATUS_DRAFT,
            created_by=duplicating_user,
            notes=original.notes,
            internal_notes=f"Duplicated from {original.bill_number}",
        )
        new_bill.save()

        for line in original.line_items.all():
            BillLineItem.objects.create(
                vendor_bill=new_bill,
                line_number=line.line_number,
                product=line.product,
                variant=line.variant,
                vendor_sku=line.vendor_sku,
                item_description=line.item_description,
                quantity=line.quantity,
                quantity_ordered=line.quantity_ordered,
                quantity_received=line.quantity_received,
                unit_price=line.unit_price,
                billed_price=line.billed_price,
                tax_rate=line.tax_rate,
            )

        new_bill.recalculate_from_lines()

        cls._log_history(
            new_bill, duplicating_user, CHANGE_TYPE_CREATED,
            new_status=BILL_STATUS_DRAFT,
            description=f"Duplicated from {original.bill_number}",
        )
        return new_bill

    # ── Approval Helpers ──────────────────────────────────────────────

    @classmethod
    def check_requires_approval(cls, bill):
        """Check if a bill requires approval based on BillSettings."""
        try:
            from apps.vendor_bills.models.bill_settings import BillSettings
            settings = BillSettings.objects.first()
            if settings:
                return settings.is_approval_required(bill.total)
        except Exception:
            pass
        return True

    @classmethod
    def get_pending_approvals(cls):
        """Get all bills pending approval."""
        return VendorBill.objects.filter(
            status=BILL_STATUS_PENDING
        ).select_related("vendor", "created_by").order_by("created_on")

    # ── Private Helpers ───────────────────────────────────────────────

    @staticmethod
    def _validate_transition(bill, target_status):
        """Validate that a status transition is allowed."""
        allowed = BILL_STATUS_TRANSITIONS.get(bill.status, [])
        if target_status not in allowed:
            raise InvalidBillTransitionError(
                f"Cannot transition from '{bill.status}' to '{target_status}'. "
                f"Allowed transitions: {allowed}"
            )

    @staticmethod
    def _log_history(bill, user, change_type, old_status="", new_status="",
                     description="", changes=None):
        """Create a BillHistory entry."""
        from apps.vendor_bills.models.bill_history import BillHistory

        BillHistory.objects.create(
            vendor_bill=bill,
            changed_by=user,
            change_type=change_type,
            old_status=old_status,
            new_status=new_status,
            description=description,
            changes=changes or {},
        )
