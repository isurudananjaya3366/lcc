"""
Task 83 — Tiered / bulk pricing service tests.

BulkPricingService methods accept tier objects or querysets.
We use lightweight mock objects to avoid DB access.
"""

from decimal import Decimal

import pytest

from apps.products.pricing.services.bulk_pricing import BulkPricingService


# ---------------------------------------------------------------------------
# Lightweight tier stub
# ---------------------------------------------------------------------------

class _TierStub:
    """Mimics a TieredPricing row for the service."""

    def __init__(self, min_quantity, max_quantity, tier_price, tier_type="all_units", name=None):
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.tier_price = Decimal(str(tier_price))
        self.tier_type = tier_type
        self.name = name or f"Tier {min_quantity}-{max_quantity or '+'}"

    def is_quantity_in_tier(self, qty):
        if self.max_quantity is None:
            return qty >= self.min_quantity
        return self.min_quantity <= qty <= self.max_quantity

    def get_tier_range(self):
        if self.max_quantity is None:
            return f"{self.min_quantity}+ units"
        return f"{self.min_quantity}-{self.max_quantity} units"


def _make_tiers():
    """Standard 3-tier set for all_units pricing."""
    return [
        _TierStub(1, 9, "100.00"),
        _TierStub(10, 49, "90.00"),
        _TierStub(50, None, "80.00"),
    ]


def _make_incremental_tiers():
    """Same quantities but for incremental pricing."""
    return [
        _TierStub(1, 9, "100.00", "incremental"),
        _TierStub(10, 49, "90.00", "incremental"),
        _TierStub(50, None, "80.00", "incremental"),
    ]


# =========================================================================
# All-units pricing
# =========================================================================

class TestAllUnitsPricing:
    def setup_method(self):
        self.svc = BulkPricingService()
        self.tiers = _make_tiers()

    def test_quantity_in_first_tier(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 5, Decimal("100.00"), tier_type="all_units"
        )
        assert result["unit_price"] == Decimal("100.00")
        assert result["total"] == Decimal("500.00")

    def test_quantity_in_second_tier(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 20, Decimal("100.00"), tier_type="all_units"
        )
        assert result["unit_price"] == Decimal("90.00")
        assert result["total"] == Decimal("1800.00")

    def test_quantity_in_highest_tier(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 100, Decimal("100.00"), tier_type="all_units"
        )
        assert result["unit_price"] == Decimal("80.00")
        assert result["total"] == Decimal("8000.00")

    def test_savings_calculated(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 20, Decimal("100.00"), tier_type="all_units"
        )
        # Regular price would be 100 * 20 = 2000, tiered = 1800
        assert result["savings"] == Decimal("200.00")

    def test_discount_percentage(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 20, Decimal("100.00"), tier_type="all_units"
        )
        assert result["discount_pct"] == Decimal("10.00")

    def test_tier_applied_info(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 50, Decimal("100.00"), tier_type="all_units"
        )
        assert result["tier_applied"] is not None


# =========================================================================
# Incremental (graduated) pricing
# =========================================================================

class TestIncrementalPricing:
    def setup_method(self):
        self.svc = BulkPricingService()
        self.tiers = _make_incremental_tiers()

    def test_single_tier(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 5, Decimal("100.00"), tier_type="incremental"
        )
        assert result["total"] == Decimal("500.00")

    def test_spans_two_tiers(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 15, Decimal("100.00"), tier_type="incremental"
        )
        # First 9 units @ 100 = 900, next 6 units @ 90 = 540  → 1440
        assert result["total"] == Decimal("1440.00")

    def test_spans_all_tiers(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 60, Decimal("100.00"), tier_type="incremental"
        )
        # 9 @ 100 = 900, 40 @ 90 = 3600, 11 @ 80 = 880  → 5380
        assert result["total"] == Decimal("5380.00")

    def test_breakdown_present(self):
        result = self.svc.calculate_tiered_price(
            self.tiers, 60, Decimal("100.00"), tier_type="incremental"
        )
        assert "breakdown" in result
        assert len(result["breakdown"]) >= 2


# =========================================================================
# Edge cases
# =========================================================================

class TestBulkPricingEdgeCases:
    def setup_method(self):
        self.svc = BulkPricingService()

    def test_empty_tiers_use_base(self):
        result = self.svc.calculate_tiered_price(
            [], 10, Decimal("100.00")
        )
        assert result["unit_price"] == Decimal("100.00")
        assert result["total"] == Decimal("1000.00")

    def test_quantity_one(self):
        tiers = _make_tiers()
        result = self.svc.calculate_tiered_price(
            tiers, 1, Decimal("100.00"), tier_type="all_units"
        )
        assert result["total"] == Decimal("100.00")

    def test_zero_quantity_returns_base(self):
        tiers = _make_tiers()
        result = self.svc.calculate_tiered_price(
            tiers, 0, Decimal("100.00"), tier_type="all_units"
        )
        assert result["total"] == Decimal("0.00")


# =========================================================================
# Tier summary helper
# =========================================================================

class TestTierSummary:
    def test_returns_list(self):
        svc = BulkPricingService()
        tiers = _make_tiers()
        summary = svc.get_tier_summary(tiers, Decimal("100.00"))
        assert isinstance(summary, list)
        assert len(summary) == 3

    def test_summary_fields(self):
        svc = BulkPricingService()
        tiers = _make_tiers()
        summary = svc.get_tier_summary(tiers, Decimal("100.00"))
        first = summary[0]
        assert "range" in first
        assert "price" in first
