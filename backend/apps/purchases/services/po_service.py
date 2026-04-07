"""
Purchase Order Service.

Business logic for creating, updating, and managing purchase orders
through their lifecycle.
"""

from datetime import date
from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from apps.purchases.constants import (
    CHANGE_TYPE_APPROVED,
    CHANGE_TYPE_CANCELLED,
    CHANGE_TYPE_CLOSED,
    CHANGE_TYPE_CREATED,
    CHANGE_TYPE_LINE_ADDED,
    CHANGE_TYPE_LINE_REMOVED,
    CHANGE_TYPE_LINE_UPDATED,
    CHANGE_TYPE_REJECTED,
    CHANGE_TYPE_SENT,
    CHANGE_TYPE_STATUS_CHANGED,
    CHANGE_TYPE_UPDATED,
    PO_STATUS_ACKNOWLEDGED,
    PO_STATUS_CANCELLED,
    PO_STATUS_CLOSED,
    PO_STATUS_DRAFT,
    PO_STATUS_PENDING_APPROVAL,
    PO_STATUS_RECEIVED,
    PO_STATUS_SENT,
    PO_STATUS_TRANSITIONS,
    URGENCY_CRITICAL,
    URGENCY_HIGH,
)
from apps.purchases.models.po_line_item import POLineItem
from apps.purchases.models.purchase_order import PurchaseOrder


# ── Custom Exceptions ──────────────────────────────────────────────────

class PONotEditableError(Exception):
    """Raised when attempting to edit a PO that is not in DRAFT status."""
    pass


class InvalidStatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""
    pass


class POValidationError(Exception):
    """Raised when PO validation fails."""
    pass


class POService:
    """Service class for purchase order lifecycle management."""

    @classmethod
    @transaction.atomic
    def create_po(cls, vendor, created_by, line_items_data=None, **kwargs):
        """
        Create a new purchase order with optional line items.

        Args:
            vendor: Vendor instance.
            created_by: User creating the PO.
            line_items_data: List of dicts with line item fields.
            **kwargs: Additional PO field values.

        Returns:
            PurchaseOrder instance.

        Raises:
            POValidationError: If vendor is not active.
        """
        # Validate vendor is active
        if hasattr(vendor, "is_active") and not vendor.is_active:
            raise POValidationError("Cannot create PO for inactive vendor.")

        # Apply defaults from POSettings if available
        try:
            from apps.purchases.models.po_settings import POSettings
            settings = POSettings.objects.first()
            if settings:
                kwargs.setdefault("payment_terms", settings.default_payment_terms)
                kwargs.setdefault("payment_terms_days", settings.default_payment_terms_days)
                kwargs.setdefault("currency", settings.default_currency)
        except Exception:
            pass

        po = PurchaseOrder(
            vendor=vendor,
            created_by=created_by,
            status=PO_STATUS_DRAFT,
            **kwargs,
        )
        po.save()

        if line_items_data:
            for idx, item_data in enumerate(line_items_data, start=1):
                item_data.setdefault("line_number", idx)
                POLineItem.objects.create(purchase_order=po, **item_data)

        # Recalculate totals
        cls._recalculate_po(po)

        cls._log_history(po, created_by, CHANGE_TYPE_CREATED, description="PO created")
        return po

    @classmethod
    @transaction.atomic
    def create_from_reorder_suggestions(cls, suggestions, created_by):
        """
        Create POs from reorder suggestions, grouped by vendor.

        Args:
            suggestions: List of dicts with vendor, product, quantity, unit_price.
            created_by: User creating the POs.

        Returns:
            List of PurchaseOrder instances.
        """
        vendor_groups = {}
        for suggestion in suggestions:
            vendor = suggestion["vendor"]
            vendor_id = vendor.pk if hasattr(vendor, "pk") else vendor
            if vendor_id not in vendor_groups:
                vendor_groups[vendor_id] = {"vendor": vendor, "items": []}
            vendor_groups[vendor_id]["items"].append(suggestion)

        purchase_orders = []
        for group in vendor_groups.values():
            line_items_data = [
                {
                    "product": item.get("product"),
                    "product_name": str(item.get("product", "")),
                    "quantity_ordered": item["quantity"],
                    "unit_price": item.get("unit_price", Decimal("0.00")),
                }
                for item in group["items"]
            ]
            po = cls.create_po(
                vendor=group["vendor"],
                created_by=created_by,
                line_items_data=line_items_data,
            )
            purchase_orders.append(po)
        return purchase_orders

    @classmethod
    @transaction.atomic
    def create_from_low_stock(cls, low_stock_items, created_by):
        """
        Create POs from low-stock product alerts, grouped by default vendor.
        Supports urgency levels: critical, high, medium.

        Args:
            low_stock_items: List of dicts with product, vendor, quantity,
                unit_price, and optional urgency ('critical'/'high'/'medium').
            created_by: User creating the POs.

        Returns:
            List of PurchaseOrder instances.
        """
        # Enrich items with urgency-based settings
        enriched = []
        for item in low_stock_items:
            urgency = item.get("urgency", "medium")
            enriched_item = dict(item)

            if urgency == URGENCY_CRITICAL:
                enriched_item.setdefault("shipping_method", "Express/Expedited")
                enriched_item.setdefault("priority_note", "CRITICAL: Stock depleted - expedited shipping required")
            elif urgency == URGENCY_HIGH:
                enriched_item.setdefault("priority_note", "HIGH PRIORITY: Low stock alert")

            enriched.append(enriched_item)

        # Group by vendor and create POs
        vendor_groups = {}
        for item in enriched:
            vendor = item["vendor"]
            vendor_id = vendor.pk if hasattr(vendor, "pk") else vendor
            if vendor_id not in vendor_groups:
                vendor_groups[vendor_id] = {"vendor": vendor, "items": [], "shipping_method": None}
            vendor_groups[vendor_id]["items"].append(item)
            # Use the most urgent shipping method
            if item.get("shipping_method"):
                vendor_groups[vendor_id]["shipping_method"] = item["shipping_method"]

        purchase_orders = []
        for group in vendor_groups.values():
            priority_notes = [
                item["priority_note"] for item in group["items"]
                if item.get("priority_note")
            ]
            line_items_data = [
                {
                    "product": item.get("product"),
                    "product_name": str(item.get("product", "")),
                    "quantity_ordered": item["quantity"],
                    "unit_price": item.get("unit_price", Decimal("0.00")),
                }
                for item in group["items"]
            ]
            kwargs = {}
            if group["shipping_method"]:
                kwargs["shipping_method"] = group["shipping_method"]
            if priority_notes:
                kwargs["internal_notes"] = "\n".join(priority_notes)

            po = cls.create_po(
                vendor=group["vendor"],
                created_by=created_by,
                line_items_data=line_items_data,
                **kwargs,
            )
            purchase_orders.append(po)
        return purchase_orders

    @classmethod
    @transaction.atomic
    def duplicate_po(cls, po_id, user=None):
        """
        Duplicate an existing PO as a new DRAFT.

        Args:
            po_id: UUID of the PO to duplicate.
            user: User performing the duplication (optional).

        Returns:
            New PurchaseOrder instance.
        """
        original = PurchaseOrder.objects.get(pk=po_id)
        duplicating_user = user or original.created_by
        new_po = PurchaseOrder(
            vendor=original.vendor,
            created_by=duplicating_user,
            status=PO_STATUS_DRAFT,
            order_date=date.today(),
            expected_delivery_date=original.expected_delivery_date,
            ship_to_address=original.ship_to_address,
            shipping_method=original.shipping_method,
            currency=original.currency,
            payment_terms=original.payment_terms,
            payment_terms_days=original.payment_terms_days,
            receiving_warehouse=original.receiving_warehouse,
            notes=original.notes,
            vendor_notes=original.vendor_notes,
            delivery_instructions=original.delivery_instructions,
            internal_notes=f"Duplicated from {original.po_number}",
        )
        new_po.save()

        for line in original.line_items.all():
            POLineItem.objects.create(
                purchase_order=new_po,
                line_number=line.line_number,
                product=line.product,
                variant=line.variant,
                vendor_sku=line.vendor_sku,
                product_name=line.product_name,
                item_description=line.item_description,
                is_service=line.is_service,
                quantity_ordered=line.quantity_ordered,
                unit_price=line.unit_price,
                discount_percentage=line.discount_percentage,
                discount_amount=line.discount_amount,
                tax_rate=line.tax_rate,
            )

        cls._recalculate_po(new_po)

        cls._log_history(
            new_po,
            duplicating_user,
            CHANGE_TYPE_CREATED,
            description=f"Duplicated from {original.po_number}",
        )
        return new_po

    @classmethod
    @transaction.atomic
    def update_po(cls, po_id, data, user=None):
        """
        Update a PO. Only allowed when status is DRAFT.

        Args:
            po_id: UUID of the PO.
            data: Dict of fields to update.
            user: User performing the update (for audit).

        Returns:
            Updated PurchaseOrder instance.

        Raises:
            PONotEditableError: If PO is not in DRAFT status.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        if po.status != PO_STATUS_DRAFT:
            raise PONotEditableError(
                f"Cannot edit PO in '{po.status}' status. Must be draft."
            )

        changes = {}
        for field, value in data.items():
            if hasattr(po, field):
                old_value = getattr(po, field)
                if old_value != value:
                    changes[field] = {"old": str(old_value), "new": str(value)}
                    setattr(po, field, value)

        if changes:
            po.save()
            cls._recalculate_po(po)
            cls._log_history(
                po,
                user,
                CHANGE_TYPE_UPDATED,
                description="PO updated",
                changes=changes,
            )
        return po

    # ── Line Item Management ──────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def add_line_item(cls, po_id, item_data, user=None):
        """
        Add a line item to an existing PO. Only allowed in DRAFT status.

        Args:
            po_id: UUID of the PO.
            item_data: Dict of line item fields.
            user: User performing the action.

        Returns:
            Created POLineItem instance.

        Raises:
            PONotEditableError: If PO is not DRAFT.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        if po.status != PO_STATUS_DRAFT:
            raise PONotEditableError(
                f"Cannot add line items when PO is in '{po.status}' status."
            )

        # Auto-assign line number
        max_line = po.line_items.aggregate(
            max_num=models.Max("line_number")
        )["max_num"] or 0
        item_data.setdefault("line_number", max_line + 1)

        line_item = POLineItem.objects.create(purchase_order=po, **item_data)
        cls._recalculate_po(po)

        cls._log_history(
            po, user, CHANGE_TYPE_LINE_ADDED,
            description=f"Line item added: {line_item.product_name}",
            changes={"line_item_id": str(line_item.pk)},
        )
        return line_item

    @classmethod
    @transaction.atomic
    def update_line_item(cls, po_id, line_item_id, data, user=None):
        """
        Update a line item on an existing PO. Only allowed in DRAFT status.

        Args:
            po_id: UUID of the PO.
            line_item_id: UUID of the line item to update.
            data: Dict of fields to update.
            user: User performing the action.

        Returns:
            Updated POLineItem instance.

        Raises:
            PONotEditableError: If PO is not DRAFT.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        if po.status != PO_STATUS_DRAFT:
            raise PONotEditableError(
                f"Cannot update line items when PO is in '{po.status}' status."
            )

        line_item = POLineItem.objects.get(pk=line_item_id, purchase_order=po)
        changes = {}
        for field, value in data.items():
            if hasattr(line_item, field):
                old_value = getattr(line_item, field)
                if old_value != value:
                    changes[field] = {"old": str(old_value), "new": str(value)}
                    setattr(line_item, field, value)

        if changes:
            line_item.save()
            cls._recalculate_po(po)
            cls._log_history(
                po, user, CHANGE_TYPE_LINE_UPDATED,
                description=f"Line item updated: {line_item.product_name}",
                changes=changes,
            )
        return line_item

    @classmethod
    @transaction.atomic
    def remove_line_item(cls, po_id, line_item_id, user=None):
        """
        Remove a line item from an existing PO. Only allowed in DRAFT status.

        Args:
            po_id: UUID of the PO.
            line_item_id: UUID of the line item to remove.
            user: User performing the action.

        Raises:
            PONotEditableError: If PO is not DRAFT.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        if po.status != PO_STATUS_DRAFT:
            raise PONotEditableError(
                f"Cannot remove line items when PO is in '{po.status}' status."
            )

        line_item = POLineItem.objects.get(pk=line_item_id, purchase_order=po)
        product_name = line_item.product_name
        line_item.delete()
        cls._recalculate_po(po)

        cls._log_history(
            po, user, CHANGE_TYPE_LINE_REMOVED,
            description=f"Line item removed: {product_name}",
            changes={"line_item_id": str(line_item_id)},
        )

    # ── Status Transitions ────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def send_po(cls, po_id, user):
        """
        Transition a PO from DRAFT to SENT.

        Validates required fields before sending.

        Args:
            po_id: UUID of the PO.
            user: User sending the PO.

        Returns:
            Updated PurchaseOrder instance.

        Raises:
            InvalidStatusTransitionError: If PO cannot transition.
            POValidationError: If PO has no line items.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        cls._validate_transition(po, PO_STATUS_SENT)

        if not po.line_items.exists():
            raise POValidationError("Cannot send a PO with no line items.")

        old_status = po.status
        po.status = PO_STATUS_SENT
        po.save(update_fields=["status", "updated_on"])

        cls._log_history(
            po,
            user,
            CHANGE_TYPE_SENT,
            old_status=old_status,
            new_status=PO_STATUS_SENT,
            description="PO sent to vendor",
        )
        return po

    @classmethod
    @transaction.atomic
    def acknowledge_po(cls, po_id, user, vendor_reference=None):
        """
        Vendor acknowledges receipt of the PO (SENT -> ACKNOWLEDGED).

        Args:
            po_id: UUID of the PO.
            user: User recording the acknowledgement.
            vendor_reference: Optional vendor reference number.

        Returns:
            Updated PurchaseOrder instance.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        cls._validate_transition(po, PO_STATUS_ACKNOWLEDGED)

        old_status = po.status
        po.status = PO_STATUS_ACKNOWLEDGED
        po.acknowledged_at = timezone.now()
        if vendor_reference:
            po.vendor_reference = vendor_reference
        po.save(update_fields=["status", "acknowledged_at", "vendor_reference", "updated_on"])

        cls._log_history(
            po,
            user,
            CHANGE_TYPE_STATUS_CHANGED,
            old_status=old_status,
            new_status=PO_STATUS_ACKNOWLEDGED,
            description="Vendor acknowledged PO",
        )
        return po

    @classmethod
    @transaction.atomic
    def cancel_po(cls, po_id, user, reason=""):
        """
        Cancel a PO. Allowed from DRAFT, SENT, or ACKNOWLEDGED states.

        Args:
            po_id: UUID of the PO.
            user: User cancelling the PO.
            reason: Cancellation reason.

        Returns:
            Updated PurchaseOrder instance.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        cls._validate_transition(po, PO_STATUS_CANCELLED)

        old_status = po.status
        po.status = PO_STATUS_CANCELLED
        po.save(update_fields=["status", "updated_on"])

        cls._log_history(
            po,
            user,
            CHANGE_TYPE_CANCELLED,
            old_status=old_status,
            new_status=PO_STATUS_CANCELLED,
            description=f"PO cancelled: {reason}" if reason else "PO cancelled",
        )
        return po

    @classmethod
    @transaction.atomic
    def close_po(cls, po_id, user):
        """
        Close a fully received PO (RECEIVED -> CLOSED).

        Args:
            po_id: UUID of the PO.
            user: User closing the PO.

        Returns:
            Updated PurchaseOrder instance.

        Raises:
            InvalidStatusTransitionError: If not in RECEIVED status.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        cls._validate_transition(po, PO_STATUS_CLOSED)

        old_status = po.status
        po.status = PO_STATUS_CLOSED
        po.save(update_fields=["status", "updated_on"])

        cls._log_history(
            po,
            user,
            CHANGE_TYPE_CLOSED,
            old_status=old_status,
            new_status=PO_STATUS_CLOSED,
            description="PO closed",
        )
        return po

    # ── Approval Workflow ─────────────────────────────────────────────

    @classmethod
    def check_requires_approval(cls, po):
        """
        Check if a PO requires approval based on POSettings threshold.

        Args:
            po: PurchaseOrder instance.

        Returns:
            bool: True if approval is required.
        """
        try:
            from apps.purchases.models.po_settings import POSettings
            settings = POSettings.objects.first()
            if settings and settings.requires_approval_above > 0:
                return po.total >= settings.requires_approval_above
        except Exception:
            pass
        return False

    @classmethod
    @transaction.atomic
    def request_approval(cls, po_id, user):
        """
        Submit a PO for approval (DRAFT -> PENDING_APPROVAL).

        Args:
            po_id: UUID of the PO.
            user: User requesting approval.

        Returns:
            Updated PurchaseOrder instance.

        Raises:
            InvalidStatusTransitionError: If not in DRAFT status.
            POValidationError: If PO has no line items.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        cls._validate_transition(po, PO_STATUS_PENDING_APPROVAL)

        if not po.line_items.exists():
            raise POValidationError("Cannot submit a PO with no line items for approval.")

        old_status = po.status
        po.status = PO_STATUS_PENDING_APPROVAL
        po.requires_approval = True
        po.save(update_fields=["status", "requires_approval", "updated_on"])

        cls._log_history(
            po,
            user,
            CHANGE_TYPE_STATUS_CHANGED,
            old_status=old_status,
            new_status=PO_STATUS_PENDING_APPROVAL,
            description="PO submitted for approval",
        )
        return po

    @classmethod
    @transaction.atomic
    def approve_po(cls, po_id, user, notes=""):
        """
        Approve a PO and transition to SENT (PENDING_APPROVAL -> SENT).

        Args:
            po_id: UUID of the PO.
            user: User approving the PO.
            notes: Optional approval notes.

        Returns:
            Updated PurchaseOrder instance.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        cls._validate_transition(po, PO_STATUS_SENT)

        old_status = po.status
        po.status = PO_STATUS_SENT
        po.approved_by = user
        po.approved_at = timezone.now()
        po.approval_notes = notes
        po.save(update_fields=[
            "status", "approved_by", "approved_at", "approval_notes", "updated_on",
        ])

        cls._log_history(
            po,
            user,
            CHANGE_TYPE_APPROVED,
            old_status=old_status,
            new_status=PO_STATUS_SENT,
            description=f"PO approved: {notes}" if notes else "PO approved",
        )
        return po

    @classmethod
    @transaction.atomic
    def reject_po(cls, po_id, user, reason=""):
        """
        Reject a PO and return to DRAFT (PENDING_APPROVAL -> DRAFT).

        Args:
            po_id: UUID of the PO.
            user: User rejecting the PO.
            reason: Rejection reason.

        Returns:
            Updated PurchaseOrder instance.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        cls._validate_transition(po, PO_STATUS_DRAFT)

        old_status = po.status
        po.status = PO_STATUS_DRAFT
        po.rejected_at = timezone.now()
        po.rejection_reason = reason
        po.save(update_fields=[
            "status", "rejected_at", "rejection_reason", "updated_on",
        ])

        cls._log_history(
            po,
            user,
            CHANGE_TYPE_REJECTED,
            old_status=old_status,
            new_status=PO_STATUS_DRAFT,
            description=f"PO rejected: {reason}" if reason else "PO rejected",
        )
        return po

    @classmethod
    def get_pending_approvals(cls):
        """
        Get all POs that are pending approval.

        Returns:
            QuerySet of PurchaseOrder instances with PENDING_APPROVAL status.
        """
        return PurchaseOrder.objects.filter(
            status=PO_STATUS_PENDING_APPROVAL
        ).select_related("vendor", "created_by").order_by("created_on")

    # ── Splitting / Consolidation ─────────────────────────────────────

    @classmethod
    @transaction.atomic
    def split_by_vendor(cls, items, created_by):
        """
        Split a list of items into separate POs by vendor.

        Args:
            items: List of dicts with vendor, product, quantity, unit_price.
            created_by: User creating the POs.

        Returns:
            List of PurchaseOrder instances.
        """
        return cls.create_from_reorder_suggestions(items, created_by)

    @classmethod
    @transaction.atomic
    def consolidate_pos(cls, po_ids, created_by):
        """
        Merge multiple DRAFT POs (same vendor) into one.
        Original POs are cancelled after consolidation.

        Args:
            po_ids: List of PO UUIDs to consolidate.
            created_by: User performing consolidation.

        Returns:
            New PurchaseOrder instance containing all merged lines.

        Raises:
            POValidationError: If POs have different vendors or are not all DRAFT.
        """
        pos = list(PurchaseOrder.objects.filter(pk__in=po_ids).select_related("vendor"))
        if not pos:
            raise POValidationError("No purchase orders found.")

        vendors = {po.vendor_id for po in pos}
        if len(vendors) > 1:
            raise POValidationError("Cannot consolidate POs from different vendors.")

        for po in pos:
            if po.status != PO_STATUS_DRAFT:
                raise POValidationError(
                    f"PO {po.po_number} is '{po.status}'. All POs must be DRAFT."
                )

        base_po = pos[0]
        new_po = PurchaseOrder(
            vendor=base_po.vendor,
            created_by=created_by,
            status=PO_STATUS_DRAFT,
            order_date=date.today(),
            currency=base_po.currency,
            payment_terms=base_po.payment_terms,
            payment_terms_days=base_po.payment_terms_days,
            receiving_warehouse=base_po.receiving_warehouse,
        )
        new_po.save()

        line_number = 1
        source_po_numbers = []
        for po in pos:
            source_po_numbers.append(po.po_number)
            for line in po.line_items.all():
                POLineItem.objects.create(
                    purchase_order=new_po,
                    line_number=line_number,
                    product=line.product,
                    variant=line.variant,
                    vendor_sku=line.vendor_sku,
                    product_name=line.product_name,
                    item_description=line.item_description,
                    is_service=line.is_service,
                    quantity_ordered=line.quantity_ordered,
                    unit_price=line.unit_price,
                    discount_percentage=line.discount_percentage,
                    discount_amount=line.discount_amount,
                    tax_rate=line.tax_rate,
                )
                line_number += 1

        cls._recalculate_po(new_po)

        # Cancel original POs
        for po in pos:
            po.status = PO_STATUS_CANCELLED
            po.save(update_fields=["status", "updated_on"])
            cls._log_history(
                po,
                created_by,
                CHANGE_TYPE_CANCELLED,
                old_status=PO_STATUS_DRAFT,
                new_status=PO_STATUS_CANCELLED,
                description=f"Cancelled: consolidated into {new_po.po_number}",
            )

        cls._log_history(
            new_po,
            created_by,
            CHANGE_TYPE_CREATED,
            description=f"Consolidated from: {', '.join(source_po_numbers)}",
        )
        return new_po

    # ── Private helpers ───────────────────────────────────────────────

    @staticmethod
    def _validate_transition(po, target_status):
        """Validate that a status transition is allowed."""
        allowed = PO_STATUS_TRANSITIONS.get(po.status, [])
        if target_status not in allowed:
            raise InvalidStatusTransitionError(
                f"Cannot transition from '{po.status}' to '{target_status}'. "
                f"Allowed transitions: {allowed}"
            )

    @staticmethod
    def _recalculate_po(po):
        """Recalculate PO totals from line items."""
        try:
            from apps.purchases.services.calculation_service import POCalculationService
            POCalculationService.recalculate_po(po)
        except Exception:
            pass

    @staticmethod
    def _log_history(po, user, change_type, old_status="", new_status="",
                     description="", changes=None):
        """Create a POHistory entry."""
        from apps.purchases.models.po_history import POHistory

        POHistory.objects.create(
            purchase_order=po,
            changed_by=user,
            change_type=change_type,
            old_status=old_status,
            new_status=new_status,
            description=description,
            changes=changes or {},
        )
