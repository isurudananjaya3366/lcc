"""
StockTakeService — manage stock take lifecycle.

Handles creation, starting (populating items), recording counts,
completion (creating adjustments), and variance approval.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Q, F
from django.utils import timezone

from apps.inventory.stock.constants import (
    APPROVAL_APPROVED,
    APPROVAL_NOT_REQUIRED,
    APPROVAL_PENDING,
    APPROVAL_REJECTED,
    MOVEMENT_TYPE_ADJUSTMENT,
    REASON_STOCK_TAKE,
    REFERENCE_TYPE_STOCK_TAKE,
    STOCK_TAKE_CANCELLED,
    STOCK_TAKE_COMPLETED,
    STOCK_TAKE_COUNTING,
    STOCK_TAKE_DRAFT,
    STOCK_TAKE_IN_PROGRESS,
    STOCK_TAKE_ITEM_COUNTED,
    STOCK_TAKE_ITEM_PENDING,
    STOCK_TAKE_REVIEW,
    STOCK_TAKE_SCOPE_FULL,
    VARIANCE_SIGNIFICANT_THRESHOLD,
)
from apps.inventory.stock.exceptions import StockOperationError
from apps.inventory.stock.results import OperationResult

logger = logging.getLogger("inventory.stock.operations")


class StockTakeService:
    """Service for managing stock take lifecycle."""

    def __init__(self, user=None):
        self.user = user

    # ── Helpers ─────────────────────────────────────────────────────

    def _get_stock_take(self, stock_take_id, lock=False):
        from apps.inventory.stock.models.stock_take import StockTake

        qs = StockTake.objects.filter(pk=stock_take_id)
        if lock:
            qs = qs.select_for_update()
        try:
            return qs.get()
        except StockTake.DoesNotExist:
            raise StockOperationError(f"StockTake {stock_take_id} not found.")

    def _generate_reference(self):
        """Generate a unique reference number like ST-2026-XXXX."""
        from apps.inventory.stock.models.stock_take import StockTake

        now = timezone.now()
        year = now.year
        prefix = f"ST-{year}-"
        last = (
            StockTake.objects.filter(reference__startswith=prefix)
            .order_by("-reference")
            .values_list("reference", flat=True)
            .first()
        )
        if last:
            try:
                seq = int(last.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"

    # ── Task 65: Create Stock Take ──────────────────────────────────

    @transaction.atomic
    def create_stock_take(
        self,
        warehouse,
        name,
        scope=STOCK_TAKE_SCOPE_FULL,
        is_blind_count=False,
        scheduled_date=None,
        description="",
    ):
        """Create a new stock take in DRAFT status."""
        from apps.inventory.stock.models.stock_take import StockTake

        reference = self._generate_reference()

        stock_take = StockTake.objects.create(
            name=name,
            description=description,
            reference=reference,
            warehouse=warehouse,
            status=STOCK_TAKE_DRAFT,
            scope=scope,
            is_blind_count=is_blind_count,
            scheduled_date=scheduled_date,
            created_by=self.user,
        )

        logger.info(
            "STOCK_TAKE_CREATED ref=%s warehouse=%s scope=%s user=%s",
            reference,
            warehouse.pk,
            scope,
            self.user.pk if self.user else None,
        )

        return OperationResult.ok(
            "create_stock_take",
            data={"stock_take_id": str(stock_take.pk), "reference": reference},
            message=f"Stock take '{reference}' created.",
        )

    # ── Task 66: Start Stock Take (populate items) ──────────────────

    @transaction.atomic
    def start_stock_take(self, stock_take_id):
        """Populate items from StockLevel and transition to COUNTING."""
        from apps.inventory.stock.models.stock_level import StockLevel
        from apps.inventory.stock.models.stock_take_item import StockTakeItem

        stock_take = self._get_stock_take(stock_take_id, lock=True)

        if stock_take.status not in (STOCK_TAKE_DRAFT, STOCK_TAKE_IN_PROGRESS):
            raise StockOperationError(
                f"Cannot start counting from status '{stock_take.status}'."
            )

        # Query stock levels for this warehouse
        qs = StockLevel.objects.filter(
            warehouse=stock_take.warehouse,
        ).select_related("product", "variant", "location")

        if stock_take.scope != STOCK_TAKE_SCOPE_FULL:
            # For partial/cycle, only include items with existing stock levels
            # (products would be pre-filtered in future via M2M relation)
            qs = qs.filter(quantity__gt=0)

        items_to_create = []
        sequence = 0
        for sl in qs.order_by("product__name", "variant__name"):
            sequence += 1
            items_to_create.append(
                StockTakeItem(
                    stock_take=stock_take,
                    product=sl.product,
                    variant=sl.variant,
                    location=sl.location,
                    expected_quantity=sl.quantity,
                    system_quantity=sl.quantity,
                    cost_per_unit=sl.cost_per_unit,
                    expected_value=sl.quantity * sl.cost_per_unit,
                    status=STOCK_TAKE_ITEM_PENDING,
                    count_sequence=sequence,
                )
            )

        if items_to_create:
            StockTakeItem.objects.bulk_create(items_to_create)

        stock_take.status = STOCK_TAKE_COUNTING
        stock_take.started_at = timezone.now()
        stock_take.total_items = len(items_to_create)
        stock_take.counted_items = 0
        stock_take.save(
            update_fields=[
                "status",
                "started_at",
                "total_items",
                "counted_items",
                "updated_on",
            ]
        )

        logger.info(
            "STOCK_TAKE_STARTED ref=%s items=%d",
            stock_take.reference,
            len(items_to_create),
        )

        return OperationResult.ok(
            "start_stock_take",
            data={
                "stock_take_id": str(stock_take.pk),
                "items_created": len(items_to_create),
            },
            message=f"Stock take started with {len(items_to_create)} items.",
        )

    # ── Task 67: Record Count ───────────────────────────────────────

    @transaction.atomic
    def record_count(
        self,
        stock_take_item_id,
        counted_quantity,
        user=None,
        notes="",
    ):
        """Record a physical count for a single item."""
        from apps.inventory.stock.models.stock_take_item import StockTakeItem

        counter = user or self.user

        try:
            item = StockTakeItem.objects.select_for_update().get(pk=stock_take_item_id)
        except StockTakeItem.DoesNotExist:
            raise StockOperationError(
                f"StockTakeItem {stock_take_item_id} not found."
            )

        if item.stock_take.status != STOCK_TAKE_COUNTING:
            raise StockOperationError("Stock take is not in COUNTING status.")

        if item.is_locked:
            raise StockOperationError("This item is locked and cannot be updated.")

        counted_quantity = Decimal(str(counted_quantity))
        if counted_quantity < 0:
            raise StockOperationError("Counted quantity cannot be negative.")

        was_pending = item.status == STOCK_TAKE_ITEM_PENDING

        item.counted_quantity = counted_quantity
        item.counted_by = counter
        item.counted_at = timezone.now()
        item.status = STOCK_TAKE_ITEM_COUNTED
        if notes:
            item.notes = notes

        # Flag for recount if variance is significant
        item.calculate_variance()
        if (
            item.variance_percentage is not None
            and abs(item.variance_percentage) > VARIANCE_SIGNIFICANT_THRESHOLD
        ):
            item.requires_recount = True

        item.save()

        # Update parent statistics
        if was_pending:
            st = item.stock_take
            st.counted_items = F("counted_items") + 1
            if item.variance_quantity != 0:
                st.items_with_variance = F("items_with_variance") + 1
                st.total_variance_value = F("total_variance_value") + item.variance_value
            st.save(
                update_fields=[
                    "counted_items",
                    "items_with_variance",
                    "total_variance_value",
                    "updated_on",
                ]
            )

        return OperationResult.ok(
            "record_count",
            data={
                "item_id": str(item.pk),
                "variance_quantity": str(item.variance_quantity),
                "variance_percentage": str(item.variance_percentage)
                if item.variance_percentage is not None
                else None,
                "requires_recount": item.requires_recount,
            },
            message="Count recorded.",
        )

    # ── Task 67 (bulk): Record Counts Bulk ──────────────────────────

    @transaction.atomic
    def record_counts_bulk(self, counts_list, user=None):
        """
        Record counts for multiple items.

        counts_list: list of dicts with keys 'item_id', 'counted_quantity',
                     and optionally 'notes'.
        """
        counter = user or self.user
        results = []
        errors = []

        for entry in counts_list:
            try:
                result = self.record_count(
                    stock_take_item_id=entry["item_id"],
                    counted_quantity=entry["counted_quantity"],
                    user=counter,
                    notes=entry.get("notes", ""),
                )
                results.append(result)
            except StockOperationError as exc:
                errors.append({"item_id": str(entry.get("item_id")), "error": str(exc)})

        return OperationResult.ok(
            "record_counts_bulk",
            data={
                "recorded": len(results),
                "errors": errors,
            },
            message=f"Recorded {len(results)} counts, {len(errors)} errors.",
        )

    # ── Task 68: Complete Stock Take ────────────────────────────────

    @transaction.atomic
    def complete_stock_take(self, stock_take_id, user=None, force=False):
        """
        Finalize stock take: create adjustments for variances and
        update stock levels.
        """
        from apps.inventory.stock.models.stock_level import StockLevel
        from apps.inventory.stock.models.stock_movement import StockMovement
        from apps.inventory.stock.models.stock_take_item import StockTakeItem

        finalizer = user or self.user
        stock_take = self._get_stock_take(stock_take_id, lock=True)

        if stock_take.status != STOCK_TAKE_REVIEW:
            raise StockOperationError(
                "Stock take must be in REVIEW status to complete."
            )

        # Check all items counted
        pending = stock_take.items.filter(status=STOCK_TAKE_ITEM_PENDING).count()
        if pending > 0 and not force:
            raise StockOperationError(
                f"{pending} items still pending. Count all items or use force=True."
            )

        # Check recount flags
        recount = stock_take.items.filter(requires_recount=True).count()
        if recount > 0 and not force:
            raise StockOperationError(
                f"{recount} items flagged for recount. Resolve or use force=True."
            )

        # Create adjustments for items with variance
        items_with_var = stock_take.items.exclude(variance_quantity=Decimal("0")).filter(
            counted_quantity__isnull=False,
        )

        adjustments_created = 0
        for item in items_with_var.select_related("product", "variant"):
            # Determine warehouse and location from stock take
            warehouse = stock_take.warehouse

            # Lock and update stock level
            sl_qs = StockLevel.objects.select_for_update().filter(
                product=item.product,
                variant=item.variant,
                warehouse=warehouse,
                location=item.location,
            )
            sl = sl_qs.first()
            if sl:
                sl.quantity += item.variance_quantity
                sl.last_stock_update = timezone.now()
                sl.save(update_fields=["quantity", "last_stock_update", "updated_on"])

            # Create movement record
            movement_kwargs = {
                "product": item.product,
                "variant": item.variant,
                "movement_type": MOVEMENT_TYPE_ADJUSTMENT,
                "quantity": abs(item.variance_quantity),
                "reason": REASON_STOCK_TAKE,
                "cost_per_unit": item.cost_per_unit,
                "reference_type": REFERENCE_TYPE_STOCK_TAKE,
                "reference_id": str(stock_take.pk),
                "reference_number": stock_take.reference,
                "notes": f"Stock take adjustment: {item.variance_quantity}",
                "created_by": finalizer,
            }
            if item.variance_quantity > 0:
                movement_kwargs["to_warehouse"] = warehouse
                movement_kwargs["to_location"] = item.location
            else:
                movement_kwargs["from_warehouse"] = warehouse
                movement_kwargs["from_location"] = item.location

            StockMovement.objects.create(**movement_kwargs)
            adjustments_created += 1

        # Finalize stock take
        stock_take.status = STOCK_TAKE_COMPLETED
        stock_take.completed_at = timezone.now()
        stock_take.completed_by = finalizer
        stock_take.save(
            update_fields=[
                "status",
                "completed_at",
                "completed_by",
                "updated_on",
            ]
        )

        logger.info(
            "STOCK_TAKE_COMPLETED ref=%s adjustments=%d user=%s",
            stock_take.reference,
            adjustments_created,
            finalizer.pk if finalizer else None,
        )

        return OperationResult.ok(
            "complete_stock_take",
            data={
                "stock_take_id": str(stock_take.pk),
                "adjustments_created": adjustments_created,
            },
            message=f"Stock take completed with {adjustments_created} adjustments.",
        )

    # ── Task 69: Variance Approval ──────────────────────────────────

    @transaction.atomic
    def submit_for_review(self, stock_take_id):
        """Move stock take from COUNTING to REVIEW and determine approval needs."""
        stock_take = self._get_stock_take(stock_take_id, lock=True)

        if stock_take.status != STOCK_TAKE_COUNTING:
            raise StockOperationError(
                "Can only submit for review from COUNTING status."
            )

        # Refresh aggregate stats
        items = stock_take.items.all()

        stock_take.counted_items = items.exclude(
            status=STOCK_TAKE_ITEM_PENDING
        ).count()
        stock_take.items_with_variance = items.exclude(
            variance_quantity=Decimal("0")
        ).filter(counted_quantity__isnull=False).count()

        total_var = items.filter(counted_quantity__isnull=False).aggregate(
            total_var=Sum("variance_value")
        )["total_var"] or Decimal("0")
        stock_take.total_variance_value = total_var

        # Determine if approval is needed
        significant = items.filter(
            counted_quantity__isnull=False,
        ).filter(
            Q(variance_percentage__gt=VARIANCE_SIGNIFICANT_THRESHOLD)
            | Q(variance_percentage__lt=-VARIANCE_SIGNIFICANT_THRESHOLD)
        ).exists()

        if significant:
            stock_take.approval_status = APPROVAL_PENDING
        else:
            stock_take.approval_status = APPROVAL_NOT_REQUIRED

        stock_take.status = STOCK_TAKE_REVIEW
        stock_take.save(
            update_fields=[
                "status",
                "counted_items",
                "items_with_variance",
                "total_variance_value",
                "approval_status",
                "updated_on",
            ]
        )

        logger.info(
            "STOCK_TAKE_REVIEW ref=%s approval=%s",
            stock_take.reference,
            stock_take.approval_status,
        )

        return OperationResult.ok(
            "submit_for_review",
            data={
                "stock_take_id": str(stock_take.pk),
                "approval_status": stock_take.approval_status,
                "items_with_variance": stock_take.items_with_variance,
                "total_variance_value": str(stock_take.total_variance_value),
            },
            message="Stock take submitted for review.",
        )

    @transaction.atomic
    def approve_stock_take(self, stock_take_id, approver=None, notes=""):
        """Approve a stock take that requires approval."""
        approver = approver or self.user
        stock_take = self._get_stock_take(stock_take_id, lock=True)

        if stock_take.status != STOCK_TAKE_REVIEW:
            raise StockOperationError("Stock take must be in REVIEW status.")

        if stock_take.approval_status not in (APPROVAL_PENDING, APPROVAL_NOT_REQUIRED):
            raise StockOperationError(
                f"Cannot approve — current approval status is '{stock_take.approval_status}'."
            )

        stock_take.approval_status = APPROVAL_APPROVED
        stock_take.approved_by = approver
        stock_take.save(
            update_fields=["approval_status", "approved_by", "updated_on"]
        )

        logger.info(
            "STOCK_TAKE_APPROVED ref=%s approver=%s",
            stock_take.reference,
            approver.pk if approver else None,
        )

        return OperationResult.ok(
            "approve_stock_take",
            data={"stock_take_id": str(stock_take.pk)},
            message="Stock take approved.",
        )

    @transaction.atomic
    def reject_stock_take(self, stock_take_id, approver=None, reason=""):
        """Reject a stock take — sends it back for re-counting."""
        approver = approver or self.user
        stock_take = self._get_stock_take(stock_take_id, lock=True)

        if stock_take.status != STOCK_TAKE_REVIEW:
            raise StockOperationError("Stock take must be in REVIEW status.")

        stock_take.approval_status = APPROVAL_REJECTED
        stock_take.approved_by = approver
        # Revert to counting so items can be recounted
        stock_take.status = STOCK_TAKE_COUNTING
        stock_take.save(
            update_fields=["approval_status", "approved_by", "status", "updated_on"]
        )

        logger.info(
            "STOCK_TAKE_REJECTED ref=%s approver=%s reason=%s",
            stock_take.reference,
            approver.pk if approver else None,
            reason,
        )

        return OperationResult.ok(
            "reject_stock_take",
            data={"stock_take_id": str(stock_take.pk)},
            message=f"Stock take rejected: {reason}" if reason else "Stock take rejected.",
        )

    # ── Task 72: Cancel Stock Take ──────────────────────────────────

    @transaction.atomic
    def cancel_stock_take(self, stock_take_id):
        """Cancel a stock take that hasn't been completed."""
        stock_take = self._get_stock_take(stock_take_id, lock=True)

        if stock_take.status == STOCK_TAKE_COMPLETED:
            raise StockOperationError("Cannot cancel a completed stock take.")

        stock_take.status = STOCK_TAKE_CANCELLED
        stock_take.cancelled_at = timezone.now()
        stock_take.save(
            update_fields=["status", "cancelled_at", "updated_on"]
        )

        logger.info(
            "STOCK_TAKE_CANCELLED ref=%s user=%s",
            stock_take.reference,
            self.user.pk if self.user else None,
        )

        return OperationResult.ok(
            "cancel_stock_take",
            data={"stock_take_id": str(stock_take.pk)},
            message="Stock take cancelled.",
        )

    # ── Task 70: Report Data Helper ─────────────────────────────────

    def get_report_data(self, stock_take_id):
        """Gather summary data for stock take reports."""
        stock_take = self._get_stock_take(stock_take_id)
        items = stock_take.items.select_related(
            "product", "variant", "location", "counted_by"
        ).order_by("count_sequence")

        summary = items.filter(counted_quantity__isnull=False).aggregate(
            total_expected_value=Sum("expected_value"),
            total_counted_value=Sum("counted_value"),
            total_variance_value=Sum("variance_value"),
        )

        return {
            "stock_take": {
                "id": str(stock_take.pk),
                "reference": stock_take.reference,
                "name": stock_take.name,
                "warehouse": str(stock_take.warehouse),
                "status": stock_take.status,
                "scope": stock_take.scope,
                "total_items": stock_take.total_items,
                "counted_items": stock_take.counted_items,
                "items_with_variance": stock_take.items_with_variance,
                "started_at": str(stock_take.started_at) if stock_take.started_at else None,
                "completed_at": str(stock_take.completed_at) if stock_take.completed_at else None,
            },
            "summary": {
                "total_expected_value": str(summary["total_expected_value"] or 0),
                "total_counted_value": str(summary["total_counted_value"] or 0),
                "total_variance_value": str(summary["total_variance_value"] or 0),
            },
            "items": [
                {
                    "id": str(i.pk),
                    "product": str(i.product),
                    "variant": str(i.variant) if i.variant else None,
                    "location": str(i.location) if i.location else None,
                    "expected_quantity": str(i.expected_quantity),
                    "counted_quantity": str(i.counted_quantity) if i.counted_quantity is not None else None,
                    "variance_quantity": str(i.variance_quantity),
                    "variance_percentage": str(i.variance_percentage) if i.variance_percentage is not None else None,
                    "variance_value": str(i.variance_value),
                    "classification": i.get_variance_classification(),
                    "counted_by": str(i.counted_by) if i.counted_by else None,
                    "counted_at": str(i.counted_at) if i.counted_at else None,
                }
                for i in items
            ],
        }

    # ── Task 69: Per-Item Approval ──────────────────────────────────

    @transaction.atomic
    def determine_item_approvals(self, stock_take_id):
        """Determine approval requirements for each item based on variance thresholds."""
        from apps.inventory.stock.constants import (
            APPROVAL_APPROVED as ITEM_APPROVED,
            APPROVAL_PENDING as ITEM_PENDING,
            APPROVAL_NOT_REQUIRED as ITEM_NOT_REQUIRED,
        )

        stock_take = self._get_stock_take(stock_take_id)
        items = stock_take.items.filter(counted_quantity__isnull=False)

        auto_approved = 0
        requires_approval = 0

        for item in items:
            level = item.determine_approval_level()
            item.item_approval_level = level
            if level == "auto":
                item.item_approval_status = ITEM_NOT_REQUIRED
                auto_approved += 1
            else:
                item.item_approval_status = ITEM_PENDING
                requires_approval += 1
            item.save(update_fields=[
                "item_approval_status", "item_approval_level", "updated_on",
            ])

        return OperationResult.ok(
            "determine_item_approvals",
            data={
                "auto_approved": auto_approved,
                "requires_approval": requires_approval,
            },
        )

    @transaction.atomic
    def approve_variance(self, item_id, approver=None, notes=""):
        """Approve a specific stock take item's variance."""
        from apps.inventory.stock.models.stock_take_item import StockTakeItem
        from apps.inventory.stock.constants import APPROVAL_APPROVED, APPROVAL_PENDING

        approver = approver or self.user
        try:
            item = StockTakeItem.objects.select_for_update().get(pk=item_id)
        except StockTakeItem.DoesNotExist:
            raise StockOperationError(f"StockTakeItem {item_id} not found.")

        if item.item_approval_status != APPROVAL_PENDING:
            raise StockOperationError("Item is not pending approval.")

        item.item_approval_status = APPROVAL_APPROVED
        item.item_approved_by = approver
        item.item_approved_at = timezone.now()
        if notes:
            item.notes = notes
        item.save(update_fields=[
            "item_approval_status", "item_approved_by", "item_approved_at",
            "notes", "updated_on",
        ])

        return OperationResult.ok(
            "approve_variance",
            data={"item_id": str(item.pk)},
            message="Item variance approved.",
        )

    @transaction.atomic
    def reject_variance(self, item_id, approver=None, reason=""):
        """Reject a specific stock take item's variance."""
        from apps.inventory.stock.models.stock_take_item import StockTakeItem
        from apps.inventory.stock.constants import APPROVAL_PENDING, APPROVAL_REJECTED

        approver = approver or self.user
        try:
            item = StockTakeItem.objects.select_for_update().get(pk=item_id)
        except StockTakeItem.DoesNotExist:
            raise StockOperationError(f"StockTakeItem {item_id} not found.")

        if item.item_approval_status != APPROVAL_PENDING:
            raise StockOperationError("Item is not pending approval.")

        item.item_approval_status = APPROVAL_REJECTED
        item.item_approved_by = approver
        item.item_approved_at = timezone.now()
        item.item_rejection_reason = reason
        item.requires_recount = True
        item.save(update_fields=[
            "item_approval_status", "item_approved_by", "item_approved_at",
            "item_rejection_reason", "requires_recount", "updated_on",
        ])

        return OperationResult.ok(
            "reject_variance",
            data={"item_id": str(item.pk)},
            message=f"Item variance rejected: {reason}" if reason else "Item variance rejected.",
        )

    # ── Task 70: Export Reports ─────────────────────────────────────

    def export_report_csv(self, stock_take_id):
        """Generate CSV report content for a stock take."""
        import csv
        import io

        data = self.get_report_data(stock_take_id)
        output = io.StringIO()
        writer = csv.writer(output)

        # Header info
        st = data["stock_take"]
        writer.writerow(["Stock Take Report"])
        writer.writerow(["Reference", st["reference"]])
        writer.writerow(["Name", st["name"]])
        writer.writerow(["Warehouse", st["warehouse"]])
        writer.writerow(["Status", st["status"]])
        writer.writerow(["Scope", st["scope"]])
        writer.writerow([])

        # Summary
        summ = data["summary"]
        writer.writerow(["Summary"])
        writer.writerow(["Total Expected Value", summ["total_expected_value"]])
        writer.writerow(["Total Counted Value", summ["total_counted_value"]])
        writer.writerow(["Total Variance Value", summ["total_variance_value"]])
        writer.writerow([])

        # Items
        writer.writerow([
            "Product", "Variant", "Location",
            "Expected Qty", "Counted Qty",
            "Variance Qty", "Variance %", "Variance Value",
            "Classification", "Counted By", "Counted At",
        ])
        for item in data["items"]:
            writer.writerow([
                item["product"],
                item.get("variant", ""),
                item.get("location", ""),
                item["expected_quantity"],
                item.get("counted_quantity", ""),
                item["variance_quantity"],
                item.get("variance_percentage", ""),
                item["variance_value"],
                item["classification"],
                item.get("counted_by", ""),
                item.get("counted_at", ""),
            ])

        return output.getvalue()

    def export_report_excel(self, stock_take_id):
        """Generate Excel report bytes for a stock take (requires openpyxl)."""
        try:
            import openpyxl
        except ImportError:
            raise StockOperationError(
                "openpyxl is required for Excel exports. "
                "Install with: pip install openpyxl"
            )
        import io

        data = self.get_report_data(stock_take_id)
        wb = openpyxl.Workbook()

        # Summary sheet
        ws = wb.active
        ws.title = "Summary"
        st = data["stock_take"]
        ws.append(["Stock Take Report"])
        ws.append(["Reference", st["reference"]])
        ws.append(["Name", st["name"]])
        ws.append(["Warehouse", st["warehouse"]])
        ws.append(["Status", st["status"]])
        ws.append(["Scope", st["scope"]])
        ws.append(["Total Items", st["total_items"]])
        ws.append(["Counted Items", st["counted_items"]])
        ws.append(["Items with Variance", st["items_with_variance"]])
        ws.append([])
        summ = data["summary"]
        ws.append(["Total Expected Value", summ["total_expected_value"]])
        ws.append(["Total Counted Value", summ["total_counted_value"]])
        ws.append(["Total Variance Value", summ["total_variance_value"]])

        # Items sheet
        ws_items = wb.create_sheet("Items")
        ws_items.append([
            "Product", "Variant", "Location",
            "Expected Qty", "Counted Qty",
            "Variance Qty", "Variance %", "Variance Value",
            "Classification", "Counted By", "Counted At",
        ])
        for item in data["items"]:
            ws_items.append([
                item["product"],
                item.get("variant", ""),
                item.get("location", ""),
                item["expected_quantity"],
                item.get("counted_quantity", ""),
                item["variance_quantity"],
                item.get("variance_percentage", ""),
                item["variance_value"],
                item["classification"],
                item.get("counted_by", ""),
                item.get("counted_at", ""),
            ])

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    def export_report_pdf(self, stock_take_id):
        """Generate PDF report for a stock take using HTML template."""
        data = self.get_report_data(stock_take_id)
        st = data["stock_take"]
        summ = data["summary"]

        # Build HTML content
        html_parts = [
            "<html><head><style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "table { border-collapse: collapse; width: 100%; margin-top: 10px; }",
            "th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; font-size: 11px; }",
            "th { background-color: #f0f0f0; }",
            "h1 { font-size: 18px; } h2 { font-size: 14px; }",
            ".neg { color: red; } .pos { color: green; }",
            "</style></head><body>",
            f"<h1>Stock Take Report: {st['reference']}</h1>",
            f"<p><strong>Name:</strong> {st['name']}<br>",
            f"<strong>Warehouse:</strong> {st['warehouse']}<br>",
            f"<strong>Status:</strong> {st['status']}<br>",
            f"<strong>Scope:</strong> {st['scope']}</p>",
            "<h2>Summary</h2>",
            f"<p>Total Items: {st['total_items']} | Counted: {st['counted_items']} | ",
            f"With Variance: {st['items_with_variance']}</p>",
            "<table><tr><th>Metric</th><th>Value</th></tr>",
            f"<tr><td>Total Expected Value</td><td>{summ['total_expected_value']}</td></tr>",
            f"<tr><td>Total Counted Value</td><td>{summ['total_counted_value']}</td></tr>",
            f"<tr><td>Total Variance Value</td><td>{summ['total_variance_value']}</td></tr>",
            "</table>",
            "<h2>Items</h2>",
            "<table><tr>",
            "<th>Product</th><th>Variant</th><th>Location</th>",
            "<th>Expected</th><th>Counted</th>",
            "<th>Variance</th><th>Var %</th><th>Var Value</th>",
            "<th>Classification</th></tr>",
        ]
        for item in data["items"]:
            var_class = "neg" if item["variance_quantity"].startswith("-") else "pos"
            html_parts.append(
                f"<tr><td>{item['product']}</td>"
                f"<td>{item.get('variant', '')}</td>"
                f"<td>{item.get('location', '')}</td>"
                f"<td>{item['expected_quantity']}</td>"
                f"<td>{item.get('counted_quantity', '')}</td>"
                f"<td class='{var_class}'>{item['variance_quantity']}</td>"
                f"<td>{item.get('variance_percentage', '')}</td>"
                f"<td>{item['variance_value']}</td>"
                f"<td>{item['classification']}</td></tr>"
            )
        html_parts.append("</table></body></html>")
        html_content = "".join(html_parts)

        # Try to use WeasyPrint for PDF generation
        try:
            from weasyprint import HTML
            return HTML(string=html_content).write_pdf()
        except ImportError:
            # Return HTML content as fallback if weasyprint not installed
            return html_content.encode("utf-8")

    # ── Task 72: Cycle Count Schedule Integration ───────────────────

    def get_products_due_for_count(self, warehouse=None):
        """Get products that are due for cycle counting."""
        from apps.inventory.stock.models.cycle_count_schedule import CycleCountSchedule

        qs = CycleCountSchedule.objects.due_for_count()
        if warehouse:
            qs = qs.filter(warehouse=warehouse)
        return qs.select_related("product", "variant", "warehouse")

    @transaction.atomic
    def create_cycle_count_stock_take(self, warehouse, schedules=None):
        """Create a stock take from due cycle count schedules."""
        from apps.inventory.stock.constants import STOCK_TAKE_SCOPE_CYCLE

        if schedules is None:
            schedules = self.get_products_due_for_count(warehouse=warehouse)

        if not schedules.exists() if hasattr(schedules, 'exists') else not schedules:
            return OperationResult.ok(
                "create_cycle_count_stock_take",
                data={"stock_take_id": None, "items": 0},
                message="No products due for cycle counting.",
            )

        result = self.create_stock_take(
            warehouse=warehouse,
            name=f"Cycle Count - {timezone.now().strftime('%Y-%m-%d')}",
            scope=STOCK_TAKE_SCOPE_CYCLE,
            description="Auto-generated from cycle count schedule.",
        )

        return OperationResult.ok(
            "create_cycle_count_stock_take",
            data={
                "stock_take_id": result.data.get("stock_take_id"),
                "reference": result.data.get("reference"),
                "schedules_count": schedules.count() if hasattr(schedules, 'count') else len(schedules),
            },
            message="Cycle count stock take created.",
        )
