"""Tag serializer for the customers API."""

from rest_framework import serializers

from apps.customers.models import CustomerTag


class CustomerTagSerializer(serializers.ModelSerializer):
    """Lightweight serializer for customer tags."""

    class Meta:
        model = CustomerTag
        fields = ["id", "name", "color", "description"]
        read_only_fields = ["id"]
