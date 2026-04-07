"""Vendor address serializer."""

from rest_framework import serializers
from apps.vendors.models import VendorAddress


class VendorAddressSerializer(serializers.ModelSerializer):
    """Serializer for VendorAddress."""
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = VendorAddress
        fields = [
            "id", "address_type", "address_line_1", "address_line_2",
            "city", "district", "province", "postal_code", "country",
            "is_default", "is_active", "full_address", "notes",
        ]
        read_only_fields = ["id", "full_address"]
