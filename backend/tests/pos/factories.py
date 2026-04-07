"""
Model factories for POS module tests.

Uses factory_boy and Faker for generating realistic test data.
These factories complement the conftest.py fixtures and can be used
directly in tests for more flexible data generation.

Usage:
    terminal = POSTerminalFactory()
    session = POSSessionFactory(terminal=terminal)
    product = ProductFactory(barcode="8901234567890")
"""

import factory
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for PlatformUser (cashier/manager) creation."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n:04d}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@testpos.com")
    password = factory.PostGenerationMethodCall(
        "set_password", "testpass123"
    )
    is_active = True
    is_staff = False


class CashierFactory(UserFactory):
    """Factory for cashier users."""

    username = factory.Sequence(lambda n: f"cashier{n:04d}")
    is_staff = False


class ManagerFactory(UserFactory):
    """Factory for manager users with staff privileges."""

    username = factory.Sequence(lambda n: f"manager{n:04d}")
    is_staff = True


class WarehouseFactory(factory.django.DjangoModelFactory):
    """Factory for Warehouse (store) creation."""

    class Meta:
        model = "warehouses.Warehouse"
        skip_postgeneration_save = True

    name = factory.Faker("company")
    code = factory.Sequence(lambda n: f"WH-{n:04d}")
    warehouse_type = "main"
    address_line_1 = factory.Faker("street_address")
    city = factory.Faker("city")
    district = "colombo"
    phone = factory.Sequence(lambda n: f"+9411{n:07d}")
    status = "active"


class POSTerminalFactory(factory.django.DjangoModelFactory):
    """Factory for POSTerminal creation."""

    class Meta:
        model = "pos.POSTerminal"
        skip_postgeneration_save = True

    name = factory.Faker("bs")
    code = factory.Sequence(lambda n: f"T{n:03d}")
    warehouse = factory.SubFactory(WarehouseFactory)
    location = factory.Faker("word")
    status = "active"


class POSSessionFactory(factory.django.DjangoModelFactory):
    """Factory for POSSession creation.

    Note: This creates the session record but does NOT call open_session().
    For a fully opened session, use the conftest `session` fixture or call
    open_session() manually after creation.
    """

    class Meta:
        model = "pos.POSSession"
        skip_postgeneration_save = True
        exclude = ["_terminal_for_number"]

    terminal = factory.SubFactory(POSTerminalFactory)
    user = factory.SubFactory(CashierFactory)
    session_number = factory.LazyAttribute(
        lambda o: f"SES-{o.terminal.code}-0001"
    )
    opening_cash_amount = Decimal("10000.00")
    status = "open"


class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for Product creation."""

    class Meta:
        model = "products.Product"
        skip_postgeneration_save = True

    name = factory.Faker("catch_phrase")
    sku = factory.Sequence(lambda n: f"PROD-{n:05d}")
    barcode = factory.Sequence(lambda n: f"890123{n:07d}")
    selling_price = factory.Faker(
        "pydecimal", left_digits=4, right_digits=2, positive=True
    )
    cost_price = factory.LazyAttribute(
        lambda o: o.selling_price * Decimal("0.6")
    )
    is_pos_visible = True
    status = "active"


class ProductVariantFactory(factory.django.DjangoModelFactory):
    """Factory for ProductVariant creation."""

    class Meta:
        model = "products.ProductVariant"
        skip_postgeneration_save = True

    product = factory.SubFactory(ProductFactory)
    sku = factory.Sequence(lambda n: f"VAR-{n:05d}")
    barcode = factory.Sequence(lambda n: f"890199{n:07d}")


class CustomerFactory(factory.django.DjangoModelFactory):
    """Factory for Customer creation."""

    class Meta:
        model = "customers.Customer"
        skip_postgeneration_save = True

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = factory.Sequence(lambda n: f"+9477{n:07d}")
