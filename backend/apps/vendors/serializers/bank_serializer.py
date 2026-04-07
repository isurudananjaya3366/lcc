"""Vendor bank account serializer."""

from rest_framework import serializers
from apps.vendors.models import VendorBankAccount


class VendorBankAccountSerializer(serializers.ModelSerializer):
    """Serializer for VendorBankAccount."""
    class Meta:
        model = VendorBankAccount
        fields = [
            "id", "bank_name", "branch_name", "account_name", "account_number",
            "swift_code", "branch_code", "iban", "currency",
            "is_default", "is_active", "verification_status", "notes",
        ]
        read_only_fields = ["id", "verification_status"]
