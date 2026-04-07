"""Customers serializers package."""

from apps.customers.serializers.address_serializer import (
    CustomerAddressSerializer,
)
from apps.customers.serializers.customer_serializer import (
    CustomerCreateUpdateSerializer,
    CustomerListSerializer,
    CustomerSerializer,
)
from apps.customers.serializers.phone_serializer import (
    CustomerPhoneSerializer,
)
from apps.customers.serializers.tag_serializer import (
    CustomerTagSerializer,
)

__all__ = [
    "CustomerAddressSerializer",
    "CustomerCreateUpdateSerializer",
    "CustomerListSerializer",
    "CustomerPhoneSerializer",
    "CustomerSerializer",
    "CustomerTagSerializer",
]
