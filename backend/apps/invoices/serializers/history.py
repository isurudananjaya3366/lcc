"""Invoice history serializer."""

from rest_framework import serializers

from apps.invoices.models import InvoiceHistory


class InvoiceHistorySerializer(serializers.ModelSerializer):
    """Read-only serializer for invoice audit history."""

    user_display = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceHistory
        fields = [
            "id",
            "action",
            "old_status",
            "new_status",
            "user",
            "user_display",
            "notes",
            "metadata",
            "created_on",
        ]
        read_only_fields = fields

    def get_user_display(self, obj):
        if obj.user:
            return str(obj.user)
        return "System"
