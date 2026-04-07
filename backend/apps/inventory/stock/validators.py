"""
Reusable validators for the stock module.

Provides validation functions for stock-related fields that can be
used across models and serializers.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError


def validate_positive_quantity(value):
    """Validate that a quantity value is non-negative."""
    if value is not None and Decimal(str(value)) < 0:
        raise ValidationError(
            "%(value)s is not a valid quantity. Must be >= 0.",
            params={"value": value},
        )
