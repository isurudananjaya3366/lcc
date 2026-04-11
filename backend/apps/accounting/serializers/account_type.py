"""AccountTypeConfig serializer."""

from rest_framework import serializers

from apps.accounting.models import AccountTypeConfig


class AccountTypeConfigSerializer(serializers.ModelSerializer):
    """Serializer for account type configuration records."""

    code_range_display = serializers.SerializerMethodField()

    class Meta:
        model = AccountTypeConfig
        fields = [
            "id",
            "type_name",
            "normal_balance",
            "code_start",
            "code_end",
            "display_order",
            "description",
            "code_range_display",
        ]
        read_only_fields = ["id"]

    def get_code_range_display(self, obj) -> str:
        return f"{obj.code_start}-{obj.code_end}"
