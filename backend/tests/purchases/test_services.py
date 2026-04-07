"""Tests for purchases services."""

import pytest
from decimal import Decimal

from apps.purchases.constants import (
    PO_STATUS_ACKNOWLEDGED,
    PO_STATUS_CANCELLED,
    PO_STATUS_DRAFT,
    PO_STATUS_SENT,
)
from apps.purchases.models import POHistory, POLineItem, PurchaseOrder
from apps.purchases.services.po_service import (
    POService,
    PONotEditableError,
    POValidationError,
    InvalidStatusTransitionError,
)
from apps.purchases.services.calculation_service import POCalculationService
from apps.purchases.services.receiving_service import ReceivingService

pytestmark = pytest.mark.django_db


class TestPOService:
    """Tests for POService."""

    def test_create_po(self, vendor, user):
        po = POService.create_po(vendor=vendor, created_by=user)
        assert po.pk is not None
        assert po.status == PO_STATUS_DRAFT
        assert POHistory.objects.filter(purchase_order=po).exists()

    def test_create_po_with_lines(self, vendor, user):
        line_items = [
            {
                "product_name": "Item A",
                "quantity_ordered": 5,
                "unit_price": Decimal("10.00"),
            },
            {
                "product_name": "Item B",
                "quantity_ordered": 3,
                "unit_price": Decimal("20.00"),
            },
        ]
        po = POService.create_po(
            vendor=vendor, created_by=user, line_items_data=line_items
        )
        assert po.line_items.count() == 2

    def test_send_po(self, po_with_lines, user):
        po = POService.send_po(po_with_lines.pk, user)
        assert po.status == PO_STATUS_SENT

    def test_send_po_no_lines_fails(self, purchase_order, user):
        with pytest.raises(POValidationError, match="no line items"):
            POService.send_po(purchase_order.pk, user)

    def test_acknowledge_po(self, po_with_lines, user):
        po = POService.send_po(po_with_lines.pk, user)
        po = POService.acknowledge_po(po.pk, user, vendor_reference="V-REF-001")
        assert po.status == PO_STATUS_ACKNOWLEDGED
        assert po.vendor_reference == "V-REF-001"

    def test_cancel_po(self, po_with_lines, user):
        po = POService.cancel_po(po_with_lines.pk, user, reason="No longer needed")
        assert po.status == PO_STATUS_CANCELLED

    def test_invalid_transition(self, po_with_lines, user):
        po = POService.cancel_po(po_with_lines.pk, user)
        with pytest.raises(InvalidStatusTransitionError, match="Cannot transition"):
            POService.send_po(po.pk, user)

    def test_duplicate_po(self, po_with_lines, user):
        new_po = POService.duplicate_po(po_with_lines.pk)
        assert new_po.pk != po_with_lines.pk
        assert new_po.status == PO_STATUS_DRAFT
        assert new_po.line_items.count() == po_with_lines.line_items.count()
        assert new_po.po_number != po_with_lines.po_number

    def test_update_po_draft(self, purchase_order, user):
        po = POService.update_po(
            purchase_order.pk,
            {"vendor_reference": "NEW-REF"},
            user=user,
        )
        assert po.vendor_reference == "NEW-REF"

    def test_update_po_non_draft_fails(self, po_with_lines, user):
        POService.send_po(po_with_lines.pk, user)
        with pytest.raises(PONotEditableError, match="Must be draft"):
            POService.update_po(po_with_lines.pk, {"notes": "test"}, user=user)

    def test_consolidate_pos(self, vendor, user):
        po1 = POService.create_po(
            vendor=vendor,
            created_by=user,
            line_items_data=[
                {"product_name": "A", "quantity_ordered": 5, "unit_price": Decimal("10")},
            ],
        )
        po2 = POService.create_po(
            vendor=vendor,
            created_by=user,
            line_items_data=[
                {"product_name": "B", "quantity_ordered": 3, "unit_price": Decimal("20")},
            ],
        )
        merged = POService.consolidate_pos([po1.pk, po2.pk], user)
        assert merged.line_items.count() == 2
        assert merged.status == PO_STATUS_DRAFT

    def test_consolidate_different_vendors_fails(self, vendor, second_vendor, user):
        po1 = POService.create_po(vendor=vendor, created_by=user)
        po2 = POService.create_po(vendor=second_vendor, created_by=user)
        with pytest.raises(POValidationError, match="different vendors"):
            POService.consolidate_pos([po1.pk, po2.pk], user)


class TestPOCalculationService:
    """Tests for POCalculationService."""

    def test_recalculate_po(self, po_with_lines):
        POCalculationService.recalculate_po(po_with_lines)
        po_with_lines.refresh_from_db()
        assert po_with_lines.subtotal > Decimal("0")
        assert po_with_lines.total > Decimal("0")


class TestReceivingService:
    """Tests for ReceivingService."""

    def test_receive_full(self, po_with_lines, user):
        # Must be in receivable state
        POService.send_po(po_with_lines.pk, user)
        POService.acknowledge_po(po_with_lines.pk, user)

        grn = ReceivingService.receive_full(po_with_lines.pk, user)
        assert grn.pk is not None
        assert grn.grn_number.startswith("GRN-")
        assert grn.line_items.count() > 0

    def test_receive_partial(self, po_with_lines, user):
        POService.send_po(po_with_lines.pk, user)
        POService.acknowledge_po(po_with_lines.pk, user)

        first_line = po_with_lines.line_items.first()
        line_data = [
            {
                "po_line_id": str(first_line.pk),
                "quantity_received": 3,
            }
        ]
        grn = ReceivingService.receive_partial(po_with_lines.pk, user, line_data)
        assert grn.pk is not None

        first_line.refresh_from_db()
        assert first_line.quantity_received == 3
