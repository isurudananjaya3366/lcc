"""
SVAT (Simplified Value Added Tax) handler for Sri Lanka B2B scenarios.

Encapsulates all SVAT-specific logic: eligibility checks,
registration validation, and exemption application.
"""

from __future__ import annotations

import logging
import re
from decimal import Decimal

from .tax_calculator import TaxCalculator

logger = logging.getLogger(__name__)


class SVATHandler:
    """
    Manage Simplified VAT exemptions for registered B2B customers.

    SVAT allows registered businesses to purchase goods without paying
    VAT at the point of sale, subject to valid registration.
    """

    # Sri Lanka SVAT registration format: alphanumeric, typically 9-12 chars
    _SVAT_PATTERN = re.compile(r"^[A-Z0-9]{9,12}$")

    @staticmethod
    def is_svat_eligible(customer) -> bool:
        """Check if *customer* qualifies for SVAT exemption."""
        if customer is None:
            return False
        return bool(getattr(customer, "is_svat_registered", False))

    @classmethod
    def validate_svat_registration(cls, registration_number: str) -> bool:
        """Validate the format of an SVAT registration number."""
        if not registration_number:
            return False
        return bool(cls._SVAT_PATTERN.match(registration_number.upper().strip()))

    @staticmethod
    def apply_svat_exemption(
        price: Decimal, tax_rate: Decimal, customer
    ) -> dict:
        """
        Apply SVAT exemption if eligible.

        Returns dict with ``price``, ``tax_amount``, ``svat_applied``.
        """
        if SVATHandler.is_svat_eligible(customer):
            return {
                "price": price,
                "tax_amount": Decimal("0"),
                "svat_applied": True,
            }
        tax = TaxCalculator.calculate_tax_amount(price, tax_rate)
        return {
            "price": price + tax,
            "tax_amount": tax,
            "svat_applied": False,
        }

    @staticmethod
    def get_svat_tax_rate(customer, tax_class) -> Decimal:
        """Return effective rate — 0 for SVAT-eligible customers."""
        if SVATHandler.is_svat_eligible(customer):
            return Decimal("0")
        return getattr(tax_class, "rate", Decimal("0"))

    @staticmethod
    def svat_exemption_details(customer) -> dict:
        """Return a summary dict of the customer's SVAT status."""
        eligible = SVATHandler.is_svat_eligible(customer)
        return {
            "is_eligible": eligible,
            "registration_number": getattr(customer, "svat_registration_number", None),
            "customer": str(customer) if customer else None,
        }

    @staticmethod
    def svat_audit_log(customer, product, amount: Decimal, exempted_tax: Decimal) -> None:
        """Emit a structured log entry for SVAT exemption events."""
        logger.info(
            "SVAT exemption applied",
            extra={
                "customer": str(customer),
                "product": str(product),
                "amount": str(amount),
                "exempted_tax": str(exempted_tax),
                "svat_registration": getattr(customer, "svat_registration_number", None),
            },
        )
