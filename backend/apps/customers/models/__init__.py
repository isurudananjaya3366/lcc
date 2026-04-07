"""
Customers models package.

Exports all models from the customers application for convenient
importing. Models can be imported directly from apps.customers.models:

    from apps.customers.models import (
        Customer, CustomerAddress, CustomerPhone,
        CustomerCommunication, CustomerHistory, CustomerImport,
        CustomerMerge, CustomerSegment, CustomerSettings,
        CustomerTag, CustomerTagAssignment,
    )
"""

from apps.customers.models.customer import Customer
from apps.customers.models.customer_address import CustomerAddress
from apps.customers.models.customer_communication import CustomerCommunication
from apps.customers.models.customer_history import CustomerHistory
from apps.customers.models.customer_import import CustomerImport
from apps.customers.models.customer_merge import CustomerMerge
from apps.customers.models.customer_phone import CustomerPhone
from apps.customers.models.customer_segment import CustomerSegment
from apps.customers.models.customer_settings import CustomerSettings
from apps.customers.models.customer_tag import CustomerTag, CustomerTagAssignment

__all__ = [
    "Customer",
    "CustomerAddress",
    "CustomerCommunication",
    "CustomerHistory",
    "CustomerImport",
    "CustomerMerge",
    "CustomerPhone",
    "CustomerSegment",
    "CustomerSettings",
    "CustomerTag",
    "CustomerTagAssignment",
]
