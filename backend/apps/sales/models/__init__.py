"""
Sales models package.

Exports all models from the sales application for convenient
importing. Models can be imported directly from apps.sales.models:

    from apps.sales.models import Invoice, Payment
"""

from apps.sales.models.invoice import Invoice
from apps.sales.models.payment import Payment

__all__ = [
    "Invoice",
    "Payment",
]
