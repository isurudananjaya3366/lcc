"""Tests for purchases models."""

import pytest
from decimal import Decimal
from datetime import date

from apps.purchases.models import (
    PurchaseOrder,
    POLineItem,
    POHistory,
    POSettings,
    GoodsReceipt,
    GRNLineItem,
    POTemplate,
)
from apps.purchases.constants import (
    PO_STATUS_DRAFT,
    PO_STATUS_SENT,
    LINE_STATUS_PENDING,
    PAYMENT_STATUS_UNPAID,
    INSPECTION_PENDING,
    CONDITION_GOOD,
)

pytestmark = pytest.mark.django_db


class TestPurchaseOrderModel:
    """Tests for the PurchaseOrder model."""

    def test_create_purchase_order(self, purchase_order):
        assert purchase_order.pk is not None
        assert purchase_order.po_number.startswith("PO-")
        assert purchase_order.status == PO_STATUS_DRAFT
        assert purchase_order.payment_status == PAYMENT_STATUS_UNPAID
        assert purchase_order.currency == "LKR"

    def test_po_number_auto_generated(self, purchase_order):
        year = date.today().year
        assert purchase_order.po_number.startswith(f"PO-{year}-")
        assert len(purchase_order.po_number.split("-")) == 3

    def test_po_str(self, purchase_order):
        assert str(purchase_order) == purchase_order.po_number

    def test_po_default_values(self, purchase_order):
        assert purchase_order.subtotal == Decimal("0.00")
        assert purchase_order.total == Decimal("0.00")
        assert purchase_order.order_date == date.today()
        assert purchase_order.requires_approval is False
        assert purchase_order.pdf_version == 1

    def test_po_unique_numbers(self, tenant_context, vendor, user):
        po1 = PurchaseOrder.objects.create(vendor=vendor, created_by=user)
        po2 = PurchaseOrder.objects.create(vendor=vendor, created_by=user)
        assert po1.po_number != po2.po_number


class TestPOLineItemModel:
    """Tests for the POLineItem model."""

    def test_create_line_item(self, purchase_order):
        line = POLineItem.objects.create(
            purchase_order=purchase_order,
            line_number=1,
            product_name="Test Product",
            quantity_ordered=10,
            unit_price=Decimal("100.00"),
        )
        assert line.pk is not None
        assert line.status == LINE_STATUS_PENDING

    def test_line_total_calculated(self, purchase_order):
        line = POLineItem.objects.create(
            purchase_order=purchase_order,
            line_number=1,
            product_name="Test Product",
            quantity_ordered=10,
            unit_price=Decimal("100.00"),
            tax_rate=Decimal("10.00"),
        )
        assert line.line_total > Decimal("0")

    def test_quantity_pending(self, purchase_order):
        line = POLineItem.objects.create(
            purchase_order=purchase_order,
            line_number=1,
            product_name="Test Product",
            quantity_ordered=10,
            unit_price=Decimal("50.00"),
        )
        assert line.quantity_pending == 10

        line.quantity_received = 3
        line.quantity_cancelled = 2
        line.save()
        assert line.quantity_pending == 5


class TestPOHistoryModel:
    """Tests for the POHistory model."""

    def test_create_history_entry(self, purchase_order, user):
        entry = POHistory.objects.create(
            purchase_order=purchase_order,
            changed_by=user,
            change_type="created",
            description="PO created",
        )
        assert entry.pk is not None
        assert str(entry) == f"{purchase_order} - Created"


class TestPOSettingsModel:
    """Tests for the POSettings model."""

    def test_create_settings(self, tenant_context):
        settings = POSettings.objects.create(
            po_number_prefix="PO",
            default_currency="LKR",
        )
        assert settings.pk is not None
        assert settings.default_payment_terms_days == 30

    def test_singleton_per_tenant(self, tenant_context):
        s1 = POSettings.objects.create(po_number_prefix="PO")
        s2 = POSettings(po_number_prefix="INV")
        s2.save()
        # Should update the existing one, not create a new one
        assert POSettings.objects.count() == 1


class TestGoodsReceiptModel:
    """Tests for the GoodsReceipt model."""

    def test_create_grn(self, purchase_order, user):
        grn = GoodsReceipt.objects.create(
            purchase_order=purchase_order,
            received_by=user,
        )
        assert grn.pk is not None
        year = date.today().year
        assert grn.grn_number.startswith(f"GRN-{year}-")
        assert grn.inspection_status == INSPECTION_PENDING

    def test_grn_unique_numbers(self, purchase_order, user):
        g1 = GoodsReceipt.objects.create(
            purchase_order=purchase_order, received_by=user
        )
        g2 = GoodsReceipt.objects.create(
            purchase_order=purchase_order, received_by=user
        )
        assert g1.grn_number != g2.grn_number


class TestGRNLineItemModel:
    """Tests for the GRNLineItem model."""

    def test_create_grn_line_item(self, po_with_lines, user):
        grn = GoodsReceipt.objects.create(
            purchase_order=po_with_lines, received_by=user
        )
        po_line = po_with_lines.line_items.first()
        grn_line = GRNLineItem.objects.create(
            goods_receipt=grn,
            po_line=po_line,
            quantity_received=5,
        )
        assert grn_line.pk is not None
        assert grn_line.condition == CONDITION_GOOD
        assert grn_line.quantity_rejected == 0


class TestPOTemplateModel:
    """Tests for the POTemplate model."""

    def test_create_template(self, tenant_context):
        tmpl = POTemplate.objects.create(
            template_name="Test Template",
            company_name="Test Corp",
        )
        assert tmpl.pk is not None
        assert tmpl.primary_color == "#000000"
        assert tmpl.show_logo is True

    def test_default_template_singleton(self, tenant_context):
        t1 = POTemplate.objects.create(template_name="Template 1", is_default=True)
        t2 = POTemplate.objects.create(template_name="Template 2", is_default=True)
        t1.refresh_from_db()
        assert t1.is_default is False
        assert t2.is_default is True
