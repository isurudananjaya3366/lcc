"""Address serializer for the customers API."""

from rest_framework import serializers

from apps.customers.models import CustomerAddress
from apps.customers.validators import validate_district_province


class CustomerAddressSerializer(serializers.ModelSerializer):
    """Serializer for CustomerAddress with district-province validation."""

    class Meta:
        model = CustomerAddress
        fields = [
            "id",
            "address_type",
            "address_line_1",
            "address_line_2",
            "city",
            "district",
            "province",
            "postal_code",
            "country",
            "is_default_billing",
            "is_default_shipping",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        district = attrs.get("district")
        province = attrs.get("province")
        if district and province:
            validate_district_province(district, province)
        return attrs
