"""
Bulk / volume pricing calculation service.

Supports two modes:
- **all_units**: The matched tier's price applies to *every* unit.
- **incremental**: Each tier's price applies only to the units within
  that tier's range (graduated / progressive pricing).
"""

from decimal import Decimal

from ..utils import format_lkr


class BulkPricingService:
    """
    Stateless service for quantity-based tier calculation.

    Usage::

        from apps.products.pricing.services.bulk_pricing import BulkPricingService

        svc = BulkPricingService()
        result = svc.calculate_tiered_price(tiers, quantity, base_price)
    """

    # ── Main entry ─────────────────────────────────────────────

    def calculate_tiered_price(
        self,
        tiers,
        quantity: int,
        base_price: Decimal,
        *,
        tier_type: str | None = None,
    ) -> dict:
        """
        Calculate price for *quantity* units given a queryset/list of tiers.

        Parameters
        ----------
        tiers :
            Iterable of tier objects (TieredPricing or VariantTieredPricing)
            sorted by ``min_quantity`` ascending.
        quantity :
            Number of units being purchased.
        base_price :
            The product/variant base price (used for « no-tier » fallback).
        tier_type :
            Force a specific mode (``"all_units"`` or ``"incremental"``).
            When *None* the first matching tier's ``tier_type`` is used.

        Returns
        -------
        dict
            ``total``, ``unit_price``, ``tier_applied``, ``breakdown``,
            ``savings``, ``discount_pct``.
        """
        tiers_list = list(tiers)
        if not tiers_list or quantity <= 0:
            return self._base_result(base_price, quantity)

        effective_type = tier_type or getattr(tiers_list[0], "tier_type", "all_units")

        if effective_type == "incremental":
            return self._incremental(tiers_list, quantity, base_price)
        return self._all_units(tiers_list, quantity, base_price)

    # ── All-units mode ─────────────────────────────────────────

    def _all_units(self, tiers: list, quantity: int, base_price: Decimal) -> dict:
        """Entire order at the matched tier's unit price."""
        matched = self._find_tier(tiers, quantity)
        if not matched:
            return self._base_result(base_price, quantity)

        unit_price = matched.tier_price
        total = unit_price * quantity
        base_total = base_price * quantity
        savings = base_total - total
        discount = (savings / base_total * 100).quantize(Decimal("0.01")) if base_total else Decimal("0")

        return {
            "total": total,
            "unit_price": unit_price,
            "tier_applied": getattr(matched, "name", None) or matched.get_tier_range(),
            "tier_type": "all_units",
            "breakdown": [
                {
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "subtotal": total,
                    "tier_range": matched.get_tier_range(),
                }
            ],
            "savings": savings,
            "discount_pct": discount,
        }

    # ── Incremental / graduated mode ──────────────────────────

    def _incremental(self, tiers: list, quantity: int, base_price: Decimal) -> dict:
        """Each segment priced at its own tier rate."""
        sorted_tiers = sorted(tiers, key=lambda t: t.min_quantity)
        remaining = quantity
        total = Decimal("0")
        breakdown = []

        for tier in sorted_tiers:
            if remaining <= 0:
                break
            t_max = tier.max_quantity if tier.max_quantity else remaining + tier.min_quantity
            # how many units fall into this tier?
            tier_units = min(remaining, max(0, t_max - tier.min_quantity + 1))
            if tier_units <= 0:
                continue
            subtotal = tier.tier_price * tier_units
            total += subtotal
            breakdown.append(
                {
                    "quantity": tier_units,
                    "unit_price": tier.tier_price,
                    "subtotal": subtotal,
                    "tier_range": tier.get_tier_range(),
                }
            )
            remaining -= tier_units

        # Leftover units priced at base_price (no tier covers them)
        if remaining > 0:
            subtotal = base_price * remaining
            total += subtotal
            breakdown.append(
                {
                    "quantity": remaining,
                    "unit_price": base_price,
                    "subtotal": subtotal,
                    "tier_range": "Base price",
                }
            )

        unit_price = (total / quantity).quantize(Decimal("0.01")) if quantity else Decimal("0")
        base_total = base_price * quantity
        savings = base_total - total
        discount = (savings / base_total * 100).quantize(Decimal("0.01")) if base_total else Decimal("0")

        return {
            "total": total,
            "unit_price": unit_price,
            "tier_applied": "Incremental (graduated)",
            "tier_type": "incremental",
            "breakdown": breakdown,
            "savings": savings,
            "discount_pct": discount,
        }

    # ── Cart-aware helpers ─────────────────────────────────────

    def calculate_cart_line(
        self,
        product,
        quantity: int,
        base_price: Decimal,
        *,
        variant=None,
    ) -> dict:
        """
        Calculate the tier-adjusted line total for a cart line.

        Automatically resolves variant vs. product tiers.
        """
        from ..models.tiered_pricing import TieredPricing, VariantTieredPricing

        if variant:
            tiers = VariantTieredPricing.get_tiers_or_inherit(variant)
        else:
            tiers = TieredPricing.get_all_tiers(product)

        return self.calculate_tiered_price(tiers, quantity, base_price)

    def get_next_tier_savings(
        self, product, current_quantity: int, base_price: Decimal, *, variant=None
    ) -> dict | None:
        """
        Return info about the savings available at the next tier break.

        Useful for "Buy X more to save Y" prompts.
        """
        from ..models.tiered_pricing import TieredPricing, VariantTieredPricing

        if variant:
            tiers = list(VariantTieredPricing.get_tiers_or_inherit(variant))
        else:
            tiers = list(TieredPricing.get_all_tiers(product))

        if not tiers:
            return None

        # Find the first tier whose min_quantity > current_quantity
        for t in sorted(tiers, key=lambda x: x.min_quantity):
            if t.min_quantity > current_quantity:
                extra = t.min_quantity - current_quantity
                current_total = self.calculate_tiered_price(tiers, current_quantity, base_price)["total"]
                next_total = self.calculate_tiered_price(tiers, t.min_quantity, base_price)["total"]
                return {
                    "next_tier_name": getattr(t, "name", "") or t.get_tier_range(),
                    "quantity_needed": extra,
                    "next_quantity": t.min_quantity,
                    "current_total": current_total,
                    "next_total": next_total,
                    "per_unit_at_next": t.tier_price,
                    "formatted_savings": format_lkr(current_total + base_price * extra - next_total),
                }
        return None

    # ── Generate tier summary ──────────────────────────────────

    def get_tier_summary(self, tiers, base_price: Decimal) -> list[dict]:
        """Human-readable summary for UI rendering."""
        result = []
        for t in sorted(tiers, key=lambda x: x.min_quantity):
            saving = base_price - t.tier_price if base_price > t.tier_price else Decimal("0")
            result.append(
                {
                    "range": t.get_tier_range(),
                    "price": format_lkr(t.tier_price),
                    "saving": format_lkr(saving),
                    "discount": (
                        f"{((saving / base_price) * 100).quantize(Decimal('0.1'))}%"
                        if base_price
                        else "0%"
                    ),
                }
            )
        return result

    # ── Internals ──────────────────────────────────────────────

    @staticmethod
    def _find_tier(tiers: list, quantity: int):
        """Find the best matching tier for *quantity* (highest min_quantity match)."""
        matched = None
        for t in sorted(tiers, key=lambda x: x.min_quantity):
            if t.is_quantity_in_tier(quantity):
                matched = t
        return matched

    @staticmethod
    def _base_result(base_price: Decimal, quantity: int) -> dict:
        total = base_price * quantity if quantity > 0 else Decimal("0")
        return {
            "total": total,
            "unit_price": base_price,
            "tier_applied": None,
            "tier_type": None,
            "breakdown": [
                {
                    "quantity": quantity,
                    "unit_price": base_price,
                    "subtotal": total,
                    "tier_range": "Base price",
                }
            ]
            if quantity
            else [],
            "savings": Decimal("0"),
            "discount_pct": Decimal("0"),
        }
