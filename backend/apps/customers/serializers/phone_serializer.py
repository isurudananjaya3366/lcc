"""Phone serializer for the customers API."""

from rest_framework import serializers

from apps.customers.models import CustomerPhone
from apps.customers.validators import validate_phone_number


class CustomerPhoneSerializer(serializers.ModelSerializer):
    """Serializer for CustomerPhone with SL phone validation."""

    class Meta:
        model = CustomerPhone
        fields = [
            "id",
            "phone_type",
            "phone_number",
            "is_primary",
            "is_verified",
            "is_whatsapp",
        ]
        read_only_fields = ["id", "is_verified"]

    def validate_phone_number(self, value):
        validate_phone_number(value)
        return value
