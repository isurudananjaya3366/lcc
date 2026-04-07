"""Vendor contact serializer."""

from rest_framework import serializers
from apps.vendors.models import VendorContact


class VendorContactSerializer(serializers.ModelSerializer):
    """Serializer for VendorContact."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = VendorContact
        fields = [
            "id", "first_name", "last_name", "full_name",
            "email", "phone", "mobile", "whatsapp",
            "role", "department", "job_title",
            "is_primary", "is_active", "notes",
        ]
        read_only_fields = ["id", "full_name"]

    def validate(self, attrs):
        email = attrs.get("email") or (self.instance.email if self.instance else None)
        phone = attrs.get("phone") or (self.instance.phone if self.instance else None)
        if not email and not phone:
            raise serializers.ValidationError("At least one of email or phone is required.")
        return attrs
