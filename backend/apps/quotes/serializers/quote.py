"""
Quote serializers.
"""

from rest_framework import serializers

from apps.quotes.constants import QuoteStatus
from apps.quotes.models import Quote
from apps.quotes.serializers.line_item import QuoteLineItemListSerializer


class QuoteListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views."""

    customer_display_name = serializers.CharField(read_only=True)
    is_editable = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    status_display = serializers.SerializerMethodField()
    line_items_count = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = [
            "id",
            "quote_number",
            "status",
            "status_display",
            "title",
            "customer",
            "customer_display_name",
            "total",
            "currency",
            "issue_date",
            "valid_until",
            "is_editable",
            "days_until_expiry",
            "line_items_count",
            "revision_number",
            "is_latest_revision",
            "created_on",
        ]
        read_only_fields = fields

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_line_items_count(self, obj):
        return obj.line_items.count()


class QuoteSerializer(serializers.ModelSerializer):
    """Full serializer for create / update / detail."""

    line_items = QuoteLineItemListSerializer(many=True, read_only=True)
    customer_display_name = serializers.CharField(read_only=True)
    customer_email_address = serializers.EmailField(read_only=True)
    currency_symbol = serializers.CharField(read_only=True)
    is_editable = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_locked = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    needs_regeneration = serializers.BooleanField(read_only=True)
    public_url = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = [
            "id",
            "quote_number",
            "status",
            "title",
            # Customer
            "customer",
            "customer_display_name",
            "customer_email_address",
            "guest_name",
            "guest_email",
            "guest_phone",
            "guest_company",
            # Dates
            "issue_date",
            "valid_until",
            "sent_at",
            "accepted_at",
            "rejected_at",
            "expired_at",
            "converted_at",
            # Financials
            "subtotal",
            "discount_amount",
            "tax_amount",
            "total",
            "currency",
            "currency_symbol",
            "discount_type",
            "discount_value",
            # Content
            "notes",
            "terms",
            "internal_notes",
            "tags",
            # PDF
            "pdf_file",
            "pdf_generated_at",
            "needs_regeneration",
            "public_url",
            # Email
            "email_sent_to",
            "email_sent_at",
            "email_sent_count",
            # Revisions
            "revision_of",
            "revision_number",
            "is_latest_revision",
            # Template
            "template",
            # Conversion
            "converted_to_order",
            "rejection_reason",
            # Computed
            "is_editable",
            "is_expired",
            "is_locked",
            "days_until_expiry",
            # Relations
            "line_items",
            "created_by",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "quote_number",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "total",
            "sent_at",
            "accepted_at",
            "rejected_at",
            "expired_at",
            "converted_at",
            "pdf_file",
            "pdf_generated_at",
            "email_sent_to",
            "email_sent_at",
            "email_sent_count",
            "converted_to_order",
            "revision_number",
            "is_latest_revision",
            "created_by",
            "created_on",
            "updated_on",
        ]

    def get_public_url(self, obj):
        request = self.context.get("request")
        return obj.get_public_url(request)

    def validate(self, attrs):
        # Cannot edit locked quotes
        if self.instance and self.instance.is_locked:
            raise serializers.ValidationError("This quote is locked and cannot be edited.")
        return attrs


class QuoteCreateSerializer(serializers.ModelSerializer):
    """Serializer specifically for quote creation."""

    class Meta:
        model = Quote
        fields = [
            "title",
            "customer",
            "guest_name",
            "guest_email",
            "guest_phone",
            "guest_company",
            "issue_date",
            "valid_until",
            "currency",
            "discount_type",
            "discount_value",
            "notes",
            "terms",
            "internal_notes",
            "tags",
            "template",
        ]


class PublicQuoteSerializer(serializers.ModelSerializer):
    """Serializer for unauthenticated public quote access (via public_token)."""

    line_items = QuoteLineItemListSerializer(many=True, read_only=True)
    customer_display_name = serializers.CharField(read_only=True)
    currency_symbol = serializers.CharField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quote
        fields = [
            "quote_number",
            "status",
            "title",
            "customer_display_name",
            "issue_date",
            "valid_until",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "total",
            "currency",
            "currency_symbol",
            "notes",
            "terms",
            "days_until_expiry",
            "line_items",
        ]
        read_only_fields = fields


class QuoteStatusActionSerializer(serializers.Serializer):
    """Serializer for status-transition actions (send, accept, reject)."""

    notes = serializers.CharField(required=False, allow_blank=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
