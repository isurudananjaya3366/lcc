"""Vendor serializers."""

from rest_framework import serializers
from apps.vendors.models import Vendor
from apps.vendors.serializers.contact_serializer import VendorContactSerializer
from apps.vendors.serializers.address_serializer import VendorAddressSerializer
from apps.vendors.serializers.bank_serializer import VendorBankAccountSerializer


class VendorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for vendor list views."""
    class Meta:
        model = Vendor
        fields = [
            "id", "vendor_code", "company_name", "display_name",
            "status", "vendor_type", "primary_email", "primary_phone",
            "is_preferred_vendor", "rating", "total_orders", "total_spend",
            "created_on",
        ]
        read_only_fields = fields


class VendorSerializer(serializers.ModelSerializer):
    """Full detail serializer with nested relationships."""
    contacts = VendorContactSerializer(many=True, read_only=True)
    addresses = VendorAddressSerializer(many=True, read_only=True)
    bank_accounts = VendorBankAccountSerializer(many=True, read_only=True)
    products_count = serializers.SerializerMethodField()
    latest_performance = serializers.SerializerMethodField()
    contact_email = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = [
            "id", "vendor_code", "company_name", "display_name",
            "status", "vendor_type", "business_registration", "tax_id",
            "is_local_vendor", "country",
            "address_line_1", "address_line_2", "city", "district", "province", "postal_code",
            "primary_email", "secondary_email", "primary_phone", "secondary_phone",
            "mobile", "fax", "website",
            "payment_terms_days", "payment_terms_description", "credit_limit", "currency",
            "requires_purchase_order", "accepts_returns",
            "default_lead_time_days", "minimum_order_value", "minimum_order_quantity", "order_multiple",
            "notes", "internal_notes", "tags",
            "rating", "total_orders", "total_spend", "is_preferred_vendor",
            "last_rating_update", "first_order_date", "last_order_date",
            "approved_at", "logo",
            "contacts", "addresses", "bank_accounts",
            "products_count", "latest_performance", "contact_email",
            "created_on", "updated_on",
        ]
        read_only_fields = [
            "id", "vendor_code", "total_orders", "total_spend",
            "last_rating_update", "first_order_date", "last_order_date",
            "approved_at", "created_on", "updated_on",
        ]

    def get_products_count(self, obj) -> int:
        return obj.vendor_products.count()

    def get_latest_performance(self, obj) -> dict | None:
        perf = obj.performance_records.first()
        if not perf:
            return None
        return {
            "period_start": perf.period_start.isoformat() if perf.period_start else None,
            "period_end": perf.period_end.isoformat() if perf.period_end else None,
            "on_time_delivery_rate": float(perf.on_time_delivery_rate),
            "quality_score": float(perf.quality_score),
            "overall_rating": float(perf.overall_rating),
        }

    def get_contact_email(self, obj) -> str | None:
        primary = obj.contacts.filter(is_primary=True).first()
        if primary and primary.email:
            return primary.email
        return obj.primary_email or None

    def validate_vendor_type(self, value):
        from apps.vendors.constants import VENDOR_TYPE_CHOICES
        valid = [c[0] for c in VENDOR_TYPE_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f"Invalid vendor type. Must be one of: {valid}")
        return value

    def validate_primary_email(self, value):
        if value:
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError as DjangoValidationError
            try:
                validate_email(value)
            except DjangoValidationError:
                raise serializers.ValidationError("Invalid email format.")
        return value

    def validate_rating(self, value):
        if value is not None and (value < 0 or value > 5):
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        return value


class VendorCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating vendors."""
    class Meta:
        model = Vendor
        fields = [
            "company_name", "display_name", "status", "vendor_type",
            "business_registration", "tax_id", "is_local_vendor", "country",
            "address_line_1", "address_line_2", "city", "district", "province", "postal_code",
            "primary_email", "secondary_email", "primary_phone", "secondary_phone",
            "mobile", "fax", "website",
            "payment_terms_days", "payment_terms_description", "credit_limit", "currency",
            "requires_purchase_order", "accepts_returns",
            "default_lead_time_days", "minimum_order_value", "minimum_order_quantity", "order_multiple",
            "notes", "internal_notes", "tags",
            "is_preferred_vendor", "logo",
        ]

    def validate_credit_limit(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Credit limit cannot be negative.")
        return value
