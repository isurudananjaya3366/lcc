"""Customer serializers for the customers API."""

from rest_framework import serializers

from apps.customers.models import Customer
from apps.customers.serializers.address_serializer import CustomerAddressSerializer
from apps.customers.serializers.phone_serializer import CustomerPhoneSerializer
from apps.customers.serializers.tag_serializer import CustomerTagSerializer


class CustomerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for customer list views."""

    class Meta:
        model = Customer
        fields = [
            "id",
            "customer_code",
            "display_name",
            "customer_type",
            "status",
            "email",
            "phone",
            "is_active",
            "total_purchases",
            "outstanding_balance",
            "created_on",
        ]
        read_only_fields = fields


class CustomerSerializer(serializers.ModelSerializer):
    """
    Full serializer for Customer detail views with nested relations.
    """

    full_name = serializers.SerializerMethodField()
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    phone_numbers = CustomerPhoneSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()
    purchase_summary = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "customer_code",
            "customer_type",
            "status",
            "is_active",
            "first_name",
            "last_name",
            "full_name",
            "display_name",
            "business_name",
            "email",
            "phone",
            "mobile",
            "billing_address_line_1",
            "billing_address_line_2",
            "billing_city",
            "billing_state_province",
            "billing_postal_code",
            "billing_country",
            "shipping_address_line_1",
            "shipping_address_line_2",
            "shipping_city",
            "shipping_state_province",
            "shipping_postal_code",
            "shipping_country",
            "company_registration",
            "tax_id",
            "vat_number",
            "tax_exempt_status",
            "credit_limit",
            "current_balance",
            "total_purchases",
            "total_payments",
            "outstanding_balance",
            "order_count",
            "first_purchase_date",
            "last_purchase_date",
            "last_contact_date",
            "next_follow_up_date",
            "date_of_birth",
            "source",
            "notes",
            "internal_notes",
            "addresses",
            "phone_numbers",
            "tags",
            "purchase_summary",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "customer_code",
            "total_purchases",
            "total_payments",
            "outstanding_balance",
            "order_count",
            "current_balance",
            "first_purchase_date",
            "created_on",
            "updated_on",
        ]

    def get_full_name(self, obj) -> str:
        return obj.full_name or ""

    def get_tags(self, obj) -> list[dict]:
        tags = obj.tag_assignments.select_related("tag").filter(tag__is_active=True)
        return CustomerTagSerializer(
            [ta.tag for ta in tags], many=True
        ).data

    def get_purchase_summary(self, obj) -> dict:
        return {
            "total_orders": obj.order_count or 0,
            "average_order_value": float(obj.average_order_value or 0),
            "last_purchase_date": (
                obj.last_purchase_date.isoformat() if obj.last_purchase_date else None
            ),
        }


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating / updating customers."""

    class Meta:
        model = Customer
        fields = [
            "customer_type",
            "status",
            "is_active",
            "first_name",
            "last_name",
            "display_name",
            "business_name",
            "email",
            "phone",
            "mobile",
            "billing_address_line_1",
            "billing_address_line_2",
            "billing_city",
            "billing_state_province",
            "billing_postal_code",
            "billing_country",
            "shipping_address_line_1",
            "shipping_address_line_2",
            "shipping_city",
            "shipping_state_province",
            "shipping_postal_code",
            "shipping_country",
            "company_registration",
            "tax_id",
            "vat_number",
            "tax_exempt_status",
            "credit_limit",
            "source",
            "notes",
            "internal_notes",
            "date_of_birth",
            "accepts_marketing",
        ]

    def validate_email(self, value):
        if not value:
            return value
        qs = Customer.objects.filter(email__iexact=value, is_deleted=False)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A customer with this email already exists.")
        return value
