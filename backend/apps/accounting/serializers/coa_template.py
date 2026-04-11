"""COATemplate serializer."""

from rest_framework import serializers

from apps.accounting.models import COATemplate


class COATemplateSerializer(serializers.ModelSerializer):
    """Serializer for COA template records."""

    account_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = COATemplate
        fields = [
            "id",
            "template_name",
            "industry",
            "template_accounts",
            "description",
            "is_active",
            "account_count",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "account_count", "created_on", "updated_on"]
