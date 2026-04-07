"""Serializers for the Vendor Bills application."""

from rest_framework import serializers

from apps.vendor_bills.models.bill_line_item import BillLineItem
from apps.vendor_bills.models.payment_schedule import PaymentSchedule
from apps.vendor_bills.models.vendor_bill import VendorBill
from apps.vendor_bills.models.vendor_payment import VendorPayment


# =====================================================================
# Bill Line Item Serializers
# =====================================================================


class BillLineItemSerializer(serializers.ModelSerializer):
    """Full serializer for bill line items."""

    quantity_variance = serializers.ReadOnlyField()
    price_variance = serializers.ReadOnlyField()

    class Meta:
        model = BillLineItem
        fields = [
            "id",
            "vendor_bill",
            "line_number",
            "product",
            "variant",
            "vendor_sku",
            "item_description",
            "quantity",
            "quantity_ordered",
            "quantity_received",
            "billed_price",
            "unit_price",
            "tax_rate",
            "tax_amount",
            "line_total",
            "po_line",
            "grn_line",
            "quantity_variance",
            "price_variance",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "tax_amount",
            "line_total",
            "quantity_variance",
            "price_variance",
            "created_on",
            "updated_on",
        ]


class BillLineItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bill line items."""

    class Meta:
        model = BillLineItem
        fields = [
            "product",
            "variant",
            "vendor_sku",
            "item_description",
            "quantity",
            "billed_price",
            "unit_price",
            "tax_rate",
            "po_line",
            "grn_line",
        ]


# =====================================================================
# Vendor Bill Serializers
# =====================================================================


class VendorBillListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for vendor bill listings."""

    vendor_name = serializers.CharField(
        source="vendor.company_name", read_only=True
    )
    is_overdue = serializers.ReadOnlyField()
    amount_due = serializers.ReadOnlyField()

    class Meta:
        model = VendorBill
        fields = [
            "id",
            "bill_number",
            "vendor",
            "vendor_name",
            "vendor_invoice_number",
            "status",
            "bill_date",
            "due_date",
            "total",
            "amount_paid",
            "amount_due",
            "currency",
            "is_overdue",
            "is_matched",
            "created_on",
        ]
        read_only_fields = fields


class VendorBillDetailSerializer(serializers.ModelSerializer):
    """Full serializer for vendor bill detail view."""

    vendor_name = serializers.CharField(
        source="vendor.company_name", read_only=True
    )
    line_items = BillLineItemSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    amount_due = serializers.ReadOnlyField()
    aging_bucket = serializers.ReadOnlyField()

    class Meta:
        model = VendorBill
        fields = [
            "id",
            "bill_number",
            "status",
            "vendor",
            "vendor_name",
            "vendor_invoice_number",
            "purchase_order",
            "bill_date",
            "received_date",
            "due_date",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "total",
            "currency",
            "amount_paid",
            "amount_due",
            "payment_terms",
            "is_matched",
            "matched_at",
            "matching_status",
            "matching_variance",
            "matching_variance_percentage",
            "is_overdue",
            "aging_bucket",
            "created_by",
            "approved_by",
            "approved_at",
            "notes",
            "internal_notes",
            "dispute_reason",
            "attachment",
            "line_items",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "bill_number",
            "subtotal",
            "tax_amount",
            "total",
            "amount_due",
            "is_overdue",
            "aging_bucket",
            "created_on",
            "updated_on",
        ]


class VendorBillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new vendor bill."""

    line_items_data = BillLineItemCreateSerializer(
        many=True, required=False, write_only=True
    )

    class Meta:
        model = VendorBill
        fields = [
            "vendor",
            "vendor_invoice_number",
            "purchase_order",
            "bill_date",
            "received_date",
            "due_date",
            "currency",
            "payment_terms",
            "discount_amount",
            "notes",
            "internal_notes",
            "attachment",
            "line_items_data",
        ]

    def create(self, validated_data):
        from apps.vendor_bills.services.bill_service import BillService

        line_items_data = validated_data.pop("line_items_data", [])
        user = self.context["request"].user
        vendor = validated_data.pop("vendor")

        if validated_data.get("purchase_order"):
            po = validated_data.pop("purchase_order")
            return BillService.create_from_po(po, user, validated_data)

        return BillService.create_manual(
            vendor=vendor,
            user=user,
            bill_data=validated_data,
            line_items_data=line_items_data,
        )


class VendorBillUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an existing vendor bill."""

    class Meta:
        model = VendorBill
        fields = [
            "vendor_invoice_number",
            "bill_date",
            "received_date",
            "due_date",
            "currency",
            "payment_terms",
            "discount_amount",
            "notes",
            "internal_notes",
            "attachment",
        ]

    def update(self, instance, validated_data):
        from apps.vendor_bills.services.bill_service import BillService

        user = self.context["request"].user
        return BillService.update_bill(instance.pk, validated_data, user)


# =====================================================================
# Vendor Payment Serializers
# =====================================================================


class VendorPaymentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment listings."""

    vendor_name = serializers.CharField(
        source="vendor.company_name", read_only=True
    )

    class Meta:
        model = VendorPayment
        fields = [
            "id",
            "payment_number",
            "vendor",
            "vendor_name",
            "vendor_bill",
            "amount",
            "payment_date",
            "payment_method",
            "status",
            "is_advance",
            "currency",
            "created_on",
        ]
        read_only_fields = fields


class VendorPaymentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for payment detail view."""

    vendor_name = serializers.CharField(
        source="vendor.company_name", read_only=True
    )
    bill_number = serializers.CharField(
        source="vendor_bill.bill_number", read_only=True, default=None
    )

    class Meta:
        model = VendorPayment
        fields = [
            "id",
            "payment_number",
            "vendor",
            "vendor_name",
            "vendor_bill",
            "bill_number",
            "amount",
            "payment_date",
            "payment_method",
            "status",
            "reference",
            "check_number",
            "bank_name",
            "bank_account_number",
            "transaction_id",
            "notes",
            "created_by",
            "approved_by",
            "approved_at",
            "is_advance",
            "currency",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "payment_number",
            "created_on",
            "updated_on",
        ]


class VendorPaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a payment."""

    class Meta:
        model = VendorPayment
        fields = [
            "vendor",
            "vendor_bill",
            "amount",
            "payment_date",
            "payment_method",
            "reference",
            "check_number",
            "bank_name",
            "bank_account_number",
            "transaction_id",
            "notes",
            "is_advance",
            "currency",
        ]

    def create(self, validated_data):
        from apps.vendor_bills.services.payment_service import PaymentService

        user = self.context["request"].user
        vendor_bill = validated_data.pop("vendor_bill", None)
        vendor = validated_data.pop("vendor")
        amount = validated_data.pop("amount")
        is_advance = validated_data.pop("is_advance", False)

        if is_advance or vendor_bill is None:
            return PaymentService.record_advance_payment(
                vendor, amount, user, validated_data
            )

        return PaymentService.record_partial_payment(
            vendor_bill.pk, amount, user, validated_data
        )


# =====================================================================
# Payment Schedule Serializer
# =====================================================================


class PaymentScheduleSerializer(serializers.ModelSerializer):
    """Serializer for payment schedules."""

    class Meta:
        model = PaymentSchedule
        fields = [
            "id",
            "vendor_bill",
            "scheduled_date",
            "amount",
            "status",
            "payment",
            "notes",
            "reminder_sent",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]
