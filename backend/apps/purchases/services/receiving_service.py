"""
Receiving Service for the purchases application.

Business logic for goods receipt, partial receiving, quality inspection,
stock updates, and PO status management.
"""

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.purchases.constants import (
    CHANGE_TYPE_RECEIVED,
    CHANGE_TYPE_STATUS_CHANGED,
    CONDITION_GOOD,
    GRN_STATUS_COMPLETED,
    INSPECTION_FAILED,
    INSPECTION_PARTIAL,
    INSPECTION_PASSED,
    LINE_STATUS_PARTIAL,
    LINE_STATUS_PENDING,
    LINE_STATUS_RECEIVED,
    PO_STATUS_PARTIAL_RECEIVED,
    PO_STATUS_RECEIVED,
)
from apps.purchases.models.goods_receipt import GoodsReceipt
from apps.purchases.models.grn_line_item import GRNLineItem
from apps.purchases.models.po_line_item import POLineItem
from apps.purchases.models.purchase_order import PurchaseOrder


class ReceivingService:
    """Service for managing goods receiving against purchase orders."""

    @classmethod
    @transaction.atomic
    def receive_full(cls, po_id, received_by, line_data=None):
        """
        Receive all remaining quantities on a PO.

        Args:
            po_id: UUID of the purchase order.
            received_by: User performing receiving.
            line_data: Optional list of dicts overriding per-line data.

        Returns:
            GoodsReceipt instance.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        grn = GoodsReceipt.objects.create(
            purchase_order=po,
            received_by=received_by,
        )

        line_data_map = {}
        if line_data:
            for ld in line_data:
                line_data_map[str(ld["po_line_id"])] = ld

        line_number = 1
        for po_line in po.line_items.all():
            ld = line_data_map.get(str(po_line.pk), {})
            qty = ld.get("quantity_received", po_line.quantity_pending)
            if qty <= 0:
                continue

            GRNLineItem.objects.create(
                goods_receipt=grn,
                po_line=po_line,
                line_number=line_number,
                quantity_received=qty,
                quantity_rejected=ld.get("quantity_rejected", 0),
                condition=ld.get("condition", CONDITION_GOOD),
                rejection_reason=ld.get("rejection_reason", ""),
                notes=ld.get("notes", ""),
                receiving_warehouse=ld.get("receiving_warehouse") or po_line.receiving_warehouse,
                receiving_location=ld.get("receiving_location") or po_line.receiving_location,
            )
            cls.update_po_line_quantities(po_line)
            line_number += 1

        grn.status = GRN_STATUS_COMPLETED
        grn.save(update_fields=["status", "updated_on"])

        cls.update_po_status(po, received_by)
        return grn

    @classmethod
    @transaction.atomic
    def receive_partial(cls, po_id, received_by, line_data):
        """
        Partially receive items on a PO.

        Args:
            po_id: UUID of the purchase order.
            received_by: User performing receiving.
            line_data: List of dicts with po_line_id, quantity_received, etc.

        Returns:
            GoodsReceipt instance with back_order_info attribute.
        """
        po = PurchaseOrder.objects.select_for_update().get(pk=po_id)
        grn = GoodsReceipt.objects.create(
            purchase_order=po,
            received_by=received_by,
        )

        line_number = 1
        back_order_info = []
        for ld in line_data:
            po_line = POLineItem.objects.get(pk=ld["po_line_id"])
            qty = ld.get("quantity_received", 0)
            if qty <= 0:
                continue

            GRNLineItem.objects.create(
                goods_receipt=grn,
                po_line=po_line,
                line_number=line_number,
                quantity_received=qty,
                quantity_rejected=ld.get("quantity_rejected", 0),
                condition=ld.get("condition", CONDITION_GOOD),
                rejection_reason=ld.get("rejection_reason", ""),
                notes=ld.get("notes", ""),
                receiving_warehouse=ld.get("receiving_warehouse") or po_line.receiving_warehouse,
                receiving_location=ld.get("receiving_location") or po_line.receiving_location,
            )
            cls.update_po_line_quantities(po_line)
            line_number += 1

            # Track back-order info
            po_line.refresh_from_db()
            pending = po_line.quantity_pending
            if pending > 0:
                back_order_info.append({
                    "po_line_id": str(po_line.pk),
                    "product_name": po_line.product_name,
                    "quantity_pending": pending,
                })

        grn.status = GRN_STATUS_COMPLETED
        grn.save(update_fields=["status", "updated_on"])

        cls.update_po_status(po, received_by)

        # Attach back-order info to GRN for caller access
        grn.back_order_info = back_order_info
        return grn

    @classmethod
    def update_po_line_status(cls, po_line):
        """
        Update a PO line item's status based on received/ordered quantities.

        Args:
            po_line: POLineItem instance.
        """
        if po_line.quantity_received >= po_line.quantity_ordered:
            po_line.status = LINE_STATUS_RECEIVED
        elif po_line.quantity_received > 0:
            po_line.status = LINE_STATUS_PARTIAL
        po_line.save(update_fields=["status", "updated_on"])

    @classmethod
    def update_po_line_quantities(cls, po_line):
        """
        Aggregate received/rejected quantities from all GRN line items
        and update the PO line.

        Args:
            po_line: POLineItem instance.
        """
        totals = po_line.grn_line_items.aggregate(
            total_received=Sum("quantity_received"),
            total_rejected=Sum("quantity_rejected"),
        )
        po_line.quantity_received = totals["total_received"] or 0
        po_line.quantity_rejected = totals["total_rejected"] or 0
        po_line.save(update_fields=[
            "quantity_received", "quantity_rejected", "updated_on",
        ])
        cls.update_po_line_status(po_line)

    @classmethod
    def update_po_status(cls, po, received_by):
        """
        Update PO status based on aggregate line item statuses.

        Args:
            po: PurchaseOrder instance.
            received_by: User performing receipt.
        """
        from apps.purchases.services.po_service import POService

        lines = po.line_items.all()
        all_received = all(
            line.quantity_received >= line.quantity_ordered for line in lines
        )
        any_received = any(line.quantity_received > 0 for line in lines)

        old_status = po.status
        if all_received:
            po.status = PO_STATUS_RECEIVED
            po.received_at = timezone.now()
            po.received_by = received_by
            po.save(update_fields=[
                "status", "received_at", "received_by", "updated_on",
            ])

            # Auto-close if settings say so
            try:
                from apps.purchases.models.po_settings import POSettings
                settings = POSettings.objects.first()
                if settings and settings.auto_close_on_full_receive:
                    POService.close_po(po.pk, received_by)
            except Exception:
                pass
        elif any_received:
            po.status = PO_STATUS_PARTIAL_RECEIVED
            po.save(update_fields=["status", "updated_on"])

        if po.status != old_status:
            POService._log_history(
                po,
                received_by,
                CHANGE_TYPE_RECEIVED if po.status == PO_STATUS_RECEIVED
                else CHANGE_TYPE_STATUS_CHANGED,
                old_status=old_status,
                new_status=po.status,
                description=f"PO status updated to {po.status}",
            )

    @classmethod
    def add_to_stock(cls, grn_id):
        """
        Add received items from a GRN to inventory stock.

        Args:
            grn_id: UUID of the GoodsReceipt.

        Returns:
            List of dicts with stock update results.
        """
        grn = GoodsReceipt.objects.select_related("purchase_order").get(pk=grn_id)
        results = []
        for grn_line in grn.line_items.select_related("po_line__product").all():
            accepted = grn_line.quantity_accepted
            if accepted <= 0:
                continue

            product = grn_line.po_line.product
            if not product:
                results.append({
                    "po_line_id": str(grn_line.po_line.pk),
                    "product_name": grn_line.po_line.product_name,
                    "quantity": accepted,
                    "status": "skipped",
                    "reason": "No linked product",
                })
                continue

            # Try to update product stock if stock_quantity field exists
            if hasattr(product, "stock_quantity"):
                product.stock_quantity += accepted
                product.save(update_fields=["stock_quantity"])
                results.append({
                    "po_line_id": str(grn_line.po_line.pk),
                    "product_name": grn_line.po_line.product_name,
                    "quantity": accepted,
                    "status": "updated",
                })
            else:
                results.append({
                    "po_line_id": str(grn_line.po_line.pk),
                    "product_name": grn_line.po_line.product_name,
                    "quantity": accepted,
                    "status": "pending",
                    "reason": "Stock management delegated to inventory module",
                })
        return results

    @classmethod
    def get_back_orders(cls, po_id):
        """
        Get items still pending receipt on a PO.

        Args:
            po_id: UUID of the purchase order.

        Returns:
            List of dicts with back-order details.
        """
        po = PurchaseOrder.objects.get(pk=po_id)
        back_orders = []
        for line in po.line_items.all():
            pending = line.quantity_pending
            if pending > 0:
                back_orders.append({
                    "po_line_id": str(line.pk),
                    "line_number": line.line_number,
                    "product": str(line.product) if line.product else None,
                    "product_name": line.product_name,
                    "quantity_ordered": line.quantity_ordered,
                    "quantity_received": line.quantity_received,
                    "quantity_pending": pending,
                    "status": line.status,
                })
        return back_orders

    @classmethod
    def reject_items(cls, grn_line, quantity, reason=""):
        """
        Handle quality rejection of received items.

        Args:
            grn_line: GRNLineItem instance.
            quantity: Number of items to reject.
            reason: Rejection reason text.
        """
        grn_line.quantity_rejected += quantity
        grn_line.rejection_reason = reason
        grn_line.requires_followup = True
        grn_line.save(update_fields=[
            "quantity_rejected", "rejection_reason", "requires_followup", "updated_on",
        ])

        # Update the PO line quantities
        cls.update_po_line_quantities(grn_line.po_line)
        cls._update_po_line_quantities(grn_line.po_line)

        # Update GRN inspection status
        grn = grn_line.goods_receipt
        grn_lines = grn.line_items.all()
        total_rejected = sum(l.quantity_rejected for l in grn_lines)
        total_received = sum(l.quantity_received for l in grn_lines)

        if total_rejected == 0:
            grn.inspection_status = INSPECTION_PASSED
        elif total_rejected >= total_received:
            grn.inspection_status = INSPECTION_FAILED
        else:
            grn.inspection_status = INSPECTION_PARTIAL
        grn.save(update_fields=["inspection_status", "updated_on"])
