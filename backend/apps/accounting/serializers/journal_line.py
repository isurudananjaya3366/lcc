"""
Serializer for journal entry line items.
"""

from rest_framework import serializers

from apps.accounting.models import JournalEntryLine


class JournalEntryLineSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source="account.code", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)

    class Meta:
        model = JournalEntryLine
        fields = [
            "id",
            "account",
            "account_code",
            "account_name",
            "debit_amount",
            "credit_amount",
            "description",
            "sort_order",
        ]
        read_only_fields = ["id"]
