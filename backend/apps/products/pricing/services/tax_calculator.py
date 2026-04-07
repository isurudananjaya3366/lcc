"""
TaxCalculator service – all VAT / SVAT / compound tax logic.

Handles tax-inclusive ↔ tax-exclusive conversions, compound tax
calculations, SVAT exemption checks, and formatted breakdowns
for the Sri Lankan multi-tenant pricing system.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from ..constants import CURRENCY_DECIMAL_PLACES
from ..utils import format_lkr

_TWO_PLACES = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    """Round to 2 dp using banker's rounding."""
    return value.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)


class TaxCalculator:
    """
    Stateless tax calculator for LKR pricing.

    Can be instantiated with a ``tax_class`` and optional ``customer``
    for SVAT handling, or used via individual methods.
    """

    def __init__(self, tax_class=None, customer=None):
        self.tax_class = tax_class
        self.customer = customer

    # ── Core helpers ───────────────────────────────────────────

    @staticmethod
    def get_decimal_rate(tax_class) -> Decimal:
        """Convert a TaxClass percentage to a decimal multiplier."""
        if tax_class is None:
            return Decimal("0")
        return tax_class.rate / Decimal("100")

    def get_effective_tax_rate(self, tax_class=None, customer=None) -> Decimal:
        """
        Return the applicable tax *percentage* taking SVAT into account.

        If the customer has ``is_svat_registered=True`` the rate is 0.
        """
        tc = tax_class or self.tax_class
        cust = customer or self.customer
        if cust and getattr(cust, "is_svat_registered", False):
            return Decimal("0")
        if tc is None:
            return Decimal("0")
        return tc.rate

    # ── Simple tax math ────────────────────────────────────────

    @staticmethod
    def calculate_tax_amount(base_amount: Decimal, tax_rate: Decimal) -> Decimal:
        """Tax = base × rate / 100."""
        return _round(base_amount * tax_rate / Decimal("100"))

    @staticmethod
    def calculate_price_with_tax(base_amount: Decimal, tax_rate: Decimal) -> Decimal:
        """Total = base + tax."""
        return _round(base_amount + base_amount * tax_rate / Decimal("100"))

    @staticmethod
    def calculate_price_without_tax(total_amount: Decimal, tax_rate: Decimal) -> Decimal:
        """Base = total / (1 + rate/100)."""
        return _round(total_amount / (1 + tax_rate / Decimal("100")))

    @staticmethod
    def extract_tax_from_inclusive_price(inclusive_price: Decimal, tax_rate: Decimal) -> Decimal:
        """Tax component from an inclusive price."""
        base = _round(inclusive_price / (1 + tax_rate / Decimal("100")))
        return _round(inclusive_price - base)

    # ── Inclusive ↔ Exclusive conversions ───────────────────────

    def convert_inclusive_to_exclusive(
        self, inclusive_price: Decimal, tax_rate: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Return (base_price, tax_amount) from a tax-inclusive price."""
        base = self.calculate_price_without_tax(inclusive_price, tax_rate)
        tax = _round(inclusive_price - base)
        return base, tax

    def get_base_from_inclusive(self, inclusive_price: Decimal, tax_rate: Decimal) -> Decimal:
        return self.convert_inclusive_to_exclusive(inclusive_price, tax_rate)[0]

    def get_tax_from_inclusive(self, inclusive_price: Decimal, tax_rate: Decimal) -> Decimal:
        return self.convert_inclusive_to_exclusive(inclusive_price, tax_rate)[1]

    def batch_convert_inclusive_to_exclusive(
        self, prices: list[Decimal], tax_rate: Decimal
    ) -> list[tuple[Decimal, Decimal]]:
        return [self.convert_inclusive_to_exclusive(p, tax_rate) for p in prices]

    def convert_inclusive_with_tax_class(
        self, inclusive_price: Decimal, tax_class=None
    ) -> dict:
        tc = tax_class or self.tax_class
        rate = tc.rate if tc else Decimal("0")
        base, tax = self.convert_inclusive_to_exclusive(inclusive_price, rate)
        return {
            "base_price": base,
            "tax_amount": tax,
            "total_price": inclusive_price,
            "tax_rate": rate,
            "tax_class": str(tc) if tc else None,
        }

    def validate_inclusive_conversion(
        self, inclusive_price: Decimal, base_price: Decimal, tax_amount: Decimal
    ) -> bool:
        diff = abs((base_price + tax_amount) - inclusive_price)
        if diff > _TWO_PLACES:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                f"Tax calculation mismatch: {base_price} + {tax_amount} != {inclusive_price}"
            )
        return True

    def get_inclusive_breakdown_display(
        self, inclusive_price: Decimal, tax_rate: Decimal
    ) -> dict:
        base, tax = self.convert_inclusive_to_exclusive(inclusive_price, tax_rate)
        return {
            "formatted_total": format_lkr(inclusive_price),
            "formatted_base": format_lkr(base),
            "formatted_tax": format_lkr(tax),
            "tax_rate": tax_rate,
            "tax_percentage_display": f"{tax_rate}%",
        }

    # ── Exclusive → Inclusive ──────────────────────────────────

    def convert_exclusive_to_inclusive(
        self, base_price: Decimal, tax_rate: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Return (total_price, tax_amount) from a tax-exclusive price."""
        tax = self.calculate_tax_amount(base_price, tax_rate)
        total = _round(base_price + tax)
        return total, tax

    def get_total_from_exclusive(self, base_price: Decimal, tax_rate: Decimal) -> Decimal:
        return self.convert_exclusive_to_inclusive(base_price, tax_rate)[0]

    def apply_tax_to_price(self, base_price: Decimal, tax_rate: Decimal) -> tuple[Decimal, Decimal]:
        return self.convert_exclusive_to_inclusive(base_price, tax_rate)

    def batch_convert_exclusive_to_inclusive(
        self, prices: list[Decimal], tax_rate: Decimal
    ) -> list[tuple[Decimal, Decimal]]:
        return [self.convert_exclusive_to_inclusive(p, tax_rate) for p in prices]

    def convert_exclusive_with_tax_class(
        self, base_price: Decimal, tax_class=None, customer=None
    ) -> dict:
        tc = tax_class or self.tax_class
        cust = customer or self.customer
        rate = self.get_effective_tax_rate(tc, cust)
        total, tax = self.convert_exclusive_to_inclusive(base_price, rate)
        return {
            "base_price": base_price,
            "tax_amount": tax,
            "total_price": total,
            "tax_rate": rate,
            "tax_class": str(tc) if tc else None,
        }

    def get_exclusive_breakdown_display(
        self, base_price: Decimal, tax_rate: Decimal
    ) -> dict:
        total, tax = self.convert_exclusive_to_inclusive(base_price, tax_rate)
        return {
            "formatted_base": format_lkr(base_price),
            "formatted_tax": format_lkr(tax),
            "formatted_total": format_lkr(total),
            "tax_rate": tax_rate,
        }

    def compare_inclusive_exclusive(
        self, base_price: Decimal, tax_rate: Decimal
    ) -> dict:
        total, tax = self.convert_exclusive_to_inclusive(base_price, tax_rate)
        return {
            "base_price": format_lkr(base_price),
            "tax_amount": format_lkr(tax),
            "with_tax": format_lkr(total),
            "tax_rate": f"{tax_rate}%",
            "difference": format_lkr(tax),
        }

    # ── Compound tax ───────────────────────────────────────────

    def calculate_compound_tax(
        self, base_price: Decimal, tax_layers: list[dict]
    ) -> tuple[Decimal, list[dict]]:
        """
        Apply taxes sequentially (compound).

        Parameters
        ----------
        tax_layers : list of dicts, each with 'name' and 'rate'.

        Returns
        -------
        (final_total, list_of_tax_dicts)
        """
        cumulative = base_price
        taxes: list[dict] = []
        for layer in tax_layers:
            rate = layer["rate"]
            amount = _round(cumulative * rate / Decimal("100"))
            taxes.append({"name": layer["name"], "rate": rate, "amount": amount})
            cumulative = _round(cumulative + amount)
        return cumulative, taxes

    def get_compound_tax_breakdown(
        self, base_price: Decimal, tax_layers: list[dict]
    ) -> dict:
        final, taxes = self.calculate_compound_tax(base_price, tax_layers)
        total_tax = sum(t["amount"] for t in taxes)
        eff_rate = Decimal("0")
        if base_price:
            eff_rate = _round(total_tax / base_price * 100)
        layers_display = []
        cumulative = base_price
        for t in taxes:
            cumulative = _round(cumulative + t["amount"])
            layers_display.append(
                {
                    "name": t["name"],
                    "rate": t["rate"],
                    "amount": t["amount"],
                    "cumulative": cumulative,
                }
            )
        return {
            "original_base": base_price,
            "tax_layers": layers_display,
            "final_total": final,
            "total_tax_amount": total_tax,
            "effective_tax_rate": eff_rate,
        }

    @staticmethod
    def calculate_effective_compound_rate(rates: list[Decimal]) -> Decimal:
        """(1+r1)(1+r2)…−1 expressed as a percentage."""
        product = Decimal("1")
        for r in rates:
            product *= 1 + r / Decimal("100")
        return _round((product - 1) * 100)

    def apply_compound_taxes_in_order(
        self, base_price: Decimal, layers: list[tuple[str, Decimal]]
    ) -> list[dict]:
        """layers = [(name, rate), …]"""
        result: list[dict] = []
        cumulative = base_price
        for name, rate in layers:
            tax = _round(cumulative * rate / Decimal("100"))
            cumulative = _round(cumulative + tax)
            result.append({"name": name, "rate": rate, "tax": tax, "subtotal": cumulative})
        return result

    def validate_compound_calculation(
        self, base: Decimal, tax_layers: list[dict], final_total: Decimal
    ) -> bool:
        calculated, _ = self.calculate_compound_tax(base, tax_layers)
        diff = abs(calculated - final_total)
        if diff > _TWO_PLACES:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                f"Compound tax mismatch: calculated {calculated} != expected {final_total}"
            )
        return True

    def decompose_compound_price(
        self, final_price: Decimal, rates: list[Decimal]
    ) -> dict:
        """Reverse a compound-tax price to extract base and each layer."""
        # Reverse the rates
        base = final_price
        for rate in reversed(rates):
            base = _round(base / (1 + rate / Decimal("100")))

        # Forward pass to get each tax
        _, taxes = self.calculate_compound_tax(
            base, [{"name": f"tax_{i+1}", "rate": r} for i, r in enumerate(rates)]
        )
        result: dict[str, Any] = {"base_price": base}
        for i, t in enumerate(taxes):
            result[f"tax_{i+1}"] = t["amount"]
        result["total_tax"] = sum(t["amount"] for t in taxes)
        return result

    # ── Tax breakdown for invoices ─────────────────────────────

    def get_tax_breakdown(
        self,
        price: Decimal,
        tax_rate: Decimal,
        is_inclusive: bool = True,
        customer=None,
    ) -> dict:
        """Complete breakdown suitable for invoice display."""
        effective = self.get_effective_tax_rate(customer=customer)
        # When a rate is passed explicitly, use it unless SVAT zeroed it
        rate = effective if customer and effective == Decimal("0") else tax_rate

        if is_inclusive:
            base, tax = self.convert_inclusive_to_exclusive(price, rate)
            total = price
        else:
            base = price
            total, tax = self.convert_exclusive_to_inclusive(price, rate)

        return {
            "base_price": base,
            "tax_amount": tax,
            "total_price": total,
            "tax_rate": rate,
            "is_inclusive": is_inclusive,
        }

    # ── SVAT helpers ───────────────────────────────────────────

    @staticmethod
    def is_svat_eligible(customer) -> bool:
        """Check if a customer qualifies for SVAT zero-rating."""
        return bool(getattr(customer, "is_svat_registered", False))

    def get_svat_breakdown(
        self, price: Decimal, tax_rate: Decimal, customer=None
    ) -> dict:
        """Return breakdown with SVAT flag for display."""
        cust = customer or self.customer
        svat = self.is_svat_eligible(cust) if cust else False
        effective = Decimal("0") if svat else tax_rate
        base, tax = self.convert_inclusive_to_exclusive(price, effective)
        return {
            "base_price": base,
            "tax_amount": tax,
            "total_price": _round(base + tax),
            "svat_applied": svat,
            "effective_rate": effective,
        }

    # ── Price rounding utility ─────────────────────────────────

    @staticmethod
    def round_price(amount: Decimal) -> Decimal:
        """Round to LKR precision (2 dp)."""
        return _round(amount)

    # ── Validation ─────────────────────────────────────────────

    @staticmethod
    def validate_tax_calculation(
        base: Decimal, tax: Decimal, total: Decimal
    ) -> bool:
        diff = abs((base + tax) - total)
        if diff > _TWO_PLACES:
            from django.core.exceptions import ValidationError

            raise ValidationError("Tax calculation mismatch")
        return True
