"""
Factories / helpers for pricing tests.

Uses the DB-free ``Model.__new__`` pattern established in the codebase
so that unit tests can run without a database connection.
"""

import uuid
from datetime import timedelta
from decimal import Decimal

from django.db.models.base import ModelState
from django.utils import timezone


# ---------------------------------------------------------------------------
# Generic helper
# ---------------------------------------------------------------------------

def _make(model_cls, **kwargs):
    """Instantiate a model without hitting the DB."""
    obj = model_cls.__new__(model_cls)
    obj._state = ModelState()
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


# ---------------------------------------------------------------------------
# Stub / related-model factories
# ---------------------------------------------------------------------------

def make_product(**kw):
    from apps.products.models import Product

    defaults = {
        "id": kw.pop("id", uuid.uuid4()),
        "name": kw.pop("name", "Test Product"),
        "sku": kw.pop("sku", "TP-001"),
        "is_active": True,
        "is_deleted": False,
    }
    defaults.update(kw)
    return _make(Product, **defaults)


def make_variant(**kw):
    from apps.products.models import ProductVariant

    defaults = {
        "id": kw.pop("id", uuid.uuid4()),
        "sku": kw.pop("sku", "TPV-001"),
        "is_active": True,
        "is_deleted": False,
    }
    defaults.update(kw)
    return _make(ProductVariant, **defaults)


def make_tax_class(**kw):
    from apps.products.models import TaxClass

    defaults = {
        "id": kw.pop("id", uuid.uuid4()),
        "name": kw.pop("name", "Standard VAT"),
        "rate": kw.pop("rate", Decimal("15.00")),
        "description": kw.pop("description", ""),
        "is_default": kw.pop("is_default", False),
    }
    defaults.update(kw)
    return _make(TaxClass, **defaults)


# ---------------------------------------------------------------------------
# Pricing model factories
# ---------------------------------------------------------------------------

def make_product_price(**kw):
    from apps.products.pricing.models import ProductPrice

    now = timezone.now()
    defaults = {
        "id": kw.pop("id", uuid.uuid4()),
        "base_price": kw.pop("base_price", Decimal("1000.00")),
        "cost_price": kw.pop("cost_price", Decimal("600.00")),
        "sale_price": kw.pop("sale_price", None),
        "wholesale_price": kw.pop("wholesale_price", None),
        "is_taxable": kw.pop("is_taxable", True),
        "is_tax_inclusive": kw.pop("is_tax_inclusive", False),
        "is_active": True,
        "is_deleted": False,
        "created_on": now,
        "updated_on": now,
    }
    defaults.update(kw)
    return _make(ProductPrice, **defaults)


def make_variant_price(**kw):
    from apps.products.pricing.models import VariantPrice

    now = timezone.now()
    defaults = {
        "id": kw.pop("id", uuid.uuid4()),
        "use_product_price": kw.pop("use_product_price", True),
        "base_price": kw.pop("base_price", None),
        "cost_price": kw.pop("cost_price", None),
        "sale_price": kw.pop("sale_price", None),
        "price_adjustment": kw.pop("price_adjustment", Decimal("0.00")),
        "adjustment_type": kw.pop("adjustment_type", "none"),
        "is_active": True,
        "is_deleted": False,
        "created_on": now,
        "updated_on": now,
    }
    defaults.update(kw)
    return _make(VariantPrice, **defaults)


def make_tiered_pricing(**kw):
    from apps.products.pricing.models import TieredPricing

    now = timezone.now()
    defaults = {
        "id": kw.pop("id", uuid.uuid4()),
        "min_quantity": kw.pop("min_quantity", 10),
        "max_quantity": kw.pop("max_quantity", 50),
        "tier_price": kw.pop("tier_price", Decimal("900.00")),
        "tier_type": kw.pop("tier_type", "all_units"),
        "is_active": True,
        "is_deleted": False,
        "created_on": now,
        "updated_on": now,
    }
    defaults.update(kw)
    return _make(TieredPricing, **defaults)


def make_scheduled_price(**kw):
    from apps.products.pricing.models import ScheduledPrice

    now = timezone.now()
    defaults = {
        "id": kw.pop("id", uuid.uuid4()),
        "name": kw.pop("name", "Test Schedule"),
        "sale_price": kw.pop("sale_price", Decimal("800.00")),
        "start_datetime": kw.pop("start_datetime", now - timedelta(hours=1)),
        "end_datetime": kw.pop("end_datetime", now + timedelta(days=7)),
        "status": kw.pop("status", "ACTIVE"),
        "priority": kw.pop("priority", 0),
        "is_active": True,
        "is_deleted": False,
        "created_on": now,
        "updated_on": now,
    }
    defaults.update(kw)
    return _make(ScheduledPrice, **defaults)


def make_flash_sale(**kw):
    from apps.products.pricing.models import FlashSale

    defaults = {
        "scheduled_price_id": kw.pop("scheduled_price_id", uuid.uuid4()),
        "max_quantity": kw.pop("max_quantity", 100),
        "quantity_sold": kw.pop("quantity_sold", 0),
        "is_sold_out": kw.pop("is_sold_out", False),
    }
    defaults.update(kw)
    return _make(FlashSale, **defaults)


def make_promotional_price(**kw):
    from apps.products.pricing.models import PromotionalPrice

    now = timezone.now()
    defaults = {
        "id": kw.pop("id", uuid.uuid4()),
        "name": kw.pop("name", "Test Promo"),
        "discount_type": kw.pop("discount_type", "PERCENTAGE_OFF"),
        "discount_value": kw.pop("discount_value", Decimal("10.00")),
        "start_datetime": kw.pop("start_datetime", now - timedelta(hours=1)),
        "end_datetime": kw.pop("end_datetime", now + timedelta(days=7)),
        "min_quantity": kw.pop("min_quantity", 1),
        "min_order_value": kw.pop("min_order_value", None),
        "max_discount_amount": kw.pop("max_discount_amount", None),
        "priority": kw.pop("priority", 0),
        "is_stackable": kw.pop("is_stackable", False),
        "is_active": True,
        "is_deleted": False,
        "created_on": now,
        "updated_on": now,
    }
    defaults.update(kw)
    return _make(PromotionalPrice, **defaults)
