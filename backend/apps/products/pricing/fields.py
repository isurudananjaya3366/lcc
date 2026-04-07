"""
Custom PriceField for LKR currency with built-in validation.
"""

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import models

from .constants import CURRENCY_DECIMAL_PLACES, CURRENCY_MAX_DIGITS, MAX_PRICE, MIN_PRICE


class PriceField(models.DecimalField):
    """
    A price field for LKR currency with validation.

    Defaults to max_digits=12, decimal_places=2, enforcing the
    range 0.00 – 999,999,999.99.

    Usage::

        base_price = PriceField()
        special_price = PriceField(max_digits=10, decimal_places=2)
    """

    description = "A price field for LKR currency with validation"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_digits", CURRENCY_MAX_DIGITS)
        kwargs.setdefault("decimal_places", CURRENCY_DECIMAL_PLACES)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get("max_digits") == CURRENCY_MAX_DIGITS:
            del kwargs["max_digits"]
        if kwargs.get("decimal_places") == CURRENCY_DECIMAL_PLACES:
            del kwargs["decimal_places"]
        return name, path, args, kwargs

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value is not None:
            if value < MIN_PRICE:
                raise ValidationError(
                    f"Price cannot be negative. Got {value}.",
                    code="min_price",
                )
            if value > MAX_PRICE:
                raise ValidationError(
                    f"Price cannot exceed {MAX_PRICE}. Got {value}.",
                    code="max_price",
                )

    def get_prep_value(self, value):
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return super().get_prep_value(value)
