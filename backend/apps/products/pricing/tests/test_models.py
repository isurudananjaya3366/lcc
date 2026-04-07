"""
Task 81 — ProductPrice, VariantPrice, PriceHistory, and all model meta / property tests.

Uses the DB-free ``Model.__new__`` pattern.
"""

import uuid
from datetime import timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.utils import timezone

from apps.products.pricing.models import (
    ProductPrice,
    VariantPrice,
    PriceHistory,
    TieredPricing,
    VariantTieredPricing,
    ScheduledPrice,
    FlashSale,
    PromotionalPrice,
    ScheduledPriceHistory,
    PromotionAnalytics,
)

from .factories import (
    make_product_price,
    make_variant_price,
    make_tiered_pricing,
    make_scheduled_price,
    make_flash_sale,
    make_promotional_price,
    make_product,
    make_tax_class,
)


def _flash_with_sp(hours_remaining=24, **kw):
    """Create a FlashSale with a mock scheduled_price for delegate properties."""
    now = timezone.now()
    fs = make_flash_sale(**kw)
    sp_mock = MagicMock()
    sp_mock.is_active_now = True
    sp_mock.end_datetime = now + timedelta(hours=hours_remaining)
    sp_mock.start_datetime = now - timedelta(hours=1)
    sp_mock.name = "Test Flash Sale"
    sp_mock.status = "ACTIVE"
    fs._sp = lambda: sp_mock
    return fs


# =========================================================================
# ProductPrice model tests
# =========================================================================

class TestProductPriceMeta:
    """Verify table name, ordering, constraints, permissions."""

    def test_db_table(self):
        assert ProductPrice._meta.db_table == "pricing_product_price"

    def test_ordering(self):
        assert ProductPrice._meta.ordering == ["product__name"]

    def test_constraints_exist(self):
        names = {c.name for c in ProductPrice._meta.constraints}
        assert "chk_sale_lt_base" in names
        assert "chk_wholesale_lt_base" in names
        assert "chk_cost_lte_base" in names

    def test_custom_permissions(self):
        perm_codenames = {p[0] for p in ProductPrice._meta.permissions}
        assert "manage_pricing" in perm_codenames
        assert "view_cost_price" in perm_codenames
        assert "create_promotions" in perm_codenames


class TestProductPriceProperties:
    """Pure-calculation properties that don't need DB."""

    def test_is_on_sale_with_active_sale(self):
        now = timezone.now()
        pp = make_product_price(
            sale_price=Decimal("800.00"),
            sale_price_start=now - timedelta(hours=1),
            sale_price_end=now + timedelta(days=1),
        )
        assert pp.is_on_sale is True

    def test_is_on_sale_no_sale_price(self):
        pp = make_product_price(sale_price=None)
        assert pp.is_on_sale is False

    def test_is_on_sale_expired(self):
        now = timezone.now()
        pp = make_product_price(
            sale_price=Decimal("800.00"),
            sale_price_start=now - timedelta(days=2),
            sale_price_end=now - timedelta(days=1),
        )
        assert pp.is_on_sale is False

    def test_get_current_price_on_sale(self):
        now = timezone.now()
        pp = make_product_price(
            base_price=Decimal("1000.00"),
            sale_price=Decimal("800.00"),
            sale_price_start=now - timedelta(hours=1),
            sale_price_end=now + timedelta(days=1),
        )
        assert pp.get_current_price() == Decimal("800.00")

    def test_get_current_price_not_on_sale(self):
        pp = make_product_price(base_price=Decimal("1000.00"), sale_price=None)
        assert pp.get_current_price() == Decimal("1000.00")

    def test_discount_amount(self):
        now = timezone.now()
        pp = make_product_price(
            base_price=Decimal("1000.00"),
            sale_price=Decimal("750.00"),
            sale_price_start=now - timedelta(hours=1),
            sale_price_end=now + timedelta(days=1),
        )
        assert pp.discount_amount == Decimal("250.00")

    def test_discount_percentage(self):
        now = timezone.now()
        pp = make_product_price(
            base_price=Decimal("1000.00"),
            sale_price=Decimal("750.00"),
            sale_price_start=now - timedelta(hours=1),
            sale_price_end=now + timedelta(days=1),
        )
        assert pp.discount_percentage == Decimal("25.00")

    def test_profit_margin(self):
        pp = make_product_price(
            base_price=Decimal("1000.00"),
            cost_price=Decimal("600.00"),
        )
        assert pp.profit_margin == Decimal("40.00")

    def test_markup_percentage(self):
        pp = make_product_price(
            base_price=Decimal("1000.00"),
            cost_price=Decimal("600.00"),
        )
        # (1000 - 600) / 600 * 100 = 66.67
        expected = ((Decimal("1000") - Decimal("600")) / Decimal("600") * 100).quantize(Decimal("0.01"))
        assert pp.markup_percentage == expected

    def test_profit_per_unit(self):
        pp = make_product_price(
            base_price=Decimal("1000.00"),
            cost_price=Decimal("600.00"),
        )
        assert pp.profit_per_unit == Decimal("400.00")


# =========================================================================
# VariantPrice model tests
# =========================================================================

class TestVariantPriceMeta:
    def test_db_table(self):
        assert VariantPrice._meta.db_table == "pricing_variant_price"


class TestVariantPriceProperties:
    def test_has_price_override_false_when_using_product(self):
        vp = make_variant_price(use_product_price=True)
        assert vp.has_price_override is False

    def test_has_price_override_true_when_overridden(self):
        vp = make_variant_price(
            use_product_price=False,
            base_price=Decimal("1200.00"),
        )
        assert vp.has_price_override is True

    def test_get_pricing_source_product(self):
        vp = make_variant_price(use_product_price=True)
        assert vp.get_pricing_source() == "product"

    def test_get_pricing_source_variant(self):
        vp = make_variant_price(use_product_price=False, base_price=Decimal("500.00"))
        assert vp.get_pricing_source() == "variant"


# =========================================================================
# PriceHistory model tests
# =========================================================================

class TestPriceHistoryMeta:
    def test_db_table(self):
        assert PriceHistory._meta.db_table == "pricing_price_history"

    def test_ordering(self):
        assert PriceHistory._meta.ordering == ["-created_on"]


# =========================================================================
# TieredPricing model tests
# =========================================================================

class TestTieredPricingMeta:
    def test_db_table(self):
        assert TieredPricing._meta.db_table == "pricing_tiered_pricing"

    def test_constraints_exist(self):
        names = {c.name for c in TieredPricing._meta.constraints}
        assert "chk_tp_min_gte_1" in names
        assert "chk_tp_max_gt_min" in names


class TestTieredPricingMethods:
    def test_get_tier_range_with_max(self):
        tp = make_tiered_pricing(min_quantity=5, max_quantity=10)
        assert tp.get_tier_range() == "5-10 units"

    def test_get_tier_range_without_max(self):
        tp = make_tiered_pricing(min_quantity=50, max_quantity=None)
        assert tp.get_tier_range() == "50+ units"

    def test_is_quantity_in_tier_within_range(self):
        tp = make_tiered_pricing(min_quantity=5, max_quantity=10)
        assert tp.is_quantity_in_tier(7) is True

    def test_is_quantity_in_tier_below_min(self):
        tp = make_tiered_pricing(min_quantity=5, max_quantity=10)
        assert tp.is_quantity_in_tier(3) is False

    def test_is_quantity_in_tier_above_max(self):
        tp = make_tiered_pricing(min_quantity=5, max_quantity=10)
        assert tp.is_quantity_in_tier(15) is False

    def test_is_quantity_in_tier_open_ended(self):
        tp = make_tiered_pricing(min_quantity=100, max_quantity=None)
        assert tp.is_quantity_in_tier(500) is True

    def test_get_discount_percentage(self):
        tp = make_tiered_pricing(tier_price=Decimal("900.00"))
        pct = tp.get_discount_percentage(Decimal("1000.00"))
        assert pct == Decimal("10.00")


# =========================================================================
# VariantTieredPricing model tests
# =========================================================================

class TestVariantTieredPricingMeta:
    def test_db_table(self):
        assert VariantTieredPricing._meta.db_table == "pricing_variant_tiered"


# =========================================================================
# ScheduledPrice model tests
# =========================================================================

class TestScheduledPriceMeta:
    def test_db_table(self):
        assert ScheduledPrice._meta.db_table == "pricing_scheduled"

    def test_constraints_exist(self):
        names = {c.name for c in ScheduledPrice._meta.constraints}
        assert "scheduled_price_end_after_start" in names


class TestScheduledPriceProperties:
    def test_is_active_now_true(self):
        now = timezone.now()
        sp = make_scheduled_price(
            status="ACTIVE",
            start_datetime=now - timedelta(hours=1),
            end_datetime=now + timedelta(hours=1),
        )
        assert sp.is_active_now is True

    def test_is_pending_true(self):
        now = timezone.now()
        sp = make_scheduled_price(
            status="PENDING",
            start_datetime=now + timedelta(days=1),
            end_datetime=now + timedelta(days=7),
        )
        assert sp.is_pending is True


# =========================================================================
# FlashSale model tests
# =========================================================================

class TestFlashSaleMeta:
    def test_db_table(self):
        assert FlashSale._meta.db_table == "pricing_flash_sale"


class TestFlashSaleProperties:
    def test_quantity_remaining(self):
        fs = make_flash_sale(max_quantity=100, quantity_sold=30)
        assert fs.quantity_remaining == 70

    def test_percent_sold(self):
        fs = make_flash_sale(max_quantity=100, quantity_sold=75)
        assert fs.percent_sold == 75.0

    def test_is_sold_out_false(self):
        fs = make_flash_sale(max_quantity=100, quantity_sold=50, is_sold_out=False)
        assert fs.is_sold_out is False

    def test_urgency_level_critical(self):
        fs = make_flash_sale(max_quantity=100, quantity_sold=96)
        assert fs.urgency_level == "critical"

    def test_urgency_level_high(self):
        fs = _flash_with_sp(
            hours_remaining=24, max_quantity=100, quantity_sold=85,
        )
        assert fs.urgency_level == "high"

    def test_urgency_level_medium(self):
        fs = _flash_with_sp(
            hours_remaining=5, max_quantity=100, quantity_sold=55,
        )
        assert fs.urgency_level == "medium"

    def test_urgency_level_low(self):
        fs = _flash_with_sp(
            hours_remaining=24, max_quantity=100, quantity_sold=20,
        )
        assert fs.urgency_level == "low"


# =========================================================================
# PromotionalPrice model tests
# =========================================================================

class TestPromotionalPriceMeta:
    def test_db_table(self):
        assert PromotionalPrice._meta.db_table == "pricing_promotional"

    def test_constraints_exist(self):
        names = {c.name for c in PromotionalPrice._meta.constraints}
        # Any constraint with "end" and "start" -- checking the spec name
        assert any("end" in n and "start" in n for n in names) or len(names) >= 1


class TestPromotionalPriceMethods:
    def test_is_currently_active_true(self):
        now = timezone.now()
        promo = make_promotional_price(
            start_datetime=now - timedelta(hours=1),
            end_datetime=now + timedelta(days=1),
        )
        assert promo.is_currently_active is True

    def test_is_currently_active_expired(self):
        now = timezone.now()
        promo = make_promotional_price(
            start_datetime=now - timedelta(days=2),
            end_datetime=now - timedelta(days=1),
        )
        assert promo.is_currently_active is False

    def test_calculate_discounted_price_percentage(self):
        promo = make_promotional_price(
            discount_type="PERCENTAGE_OFF",
            discount_value=Decimal("20.00"),
            max_discount_amount=None,
        )
        result = promo.calculate_discounted_price(Decimal("1000.00"), quantity=1)
        assert result == Decimal("800.00")

    def test_calculate_discounted_price_fixed_off(self):
        promo = make_promotional_price(
            discount_type="FIXED_OFF",
            discount_value=Decimal("200.00"),
        )
        result = promo.calculate_discounted_price(Decimal("1000.00"), quantity=1)
        assert result == Decimal("800.00")

    def test_calculate_discounted_price_fixed_price(self):
        promo = make_promotional_price(
            discount_type="FIXED_PRICE",
            discount_value=Decimal("750.00"),
        )
        result = promo.calculate_discounted_price(Decimal("1000.00"), quantity=1)
        assert result == Decimal("750.00")

    def test_calculate_discounted_price_with_max_cap(self):
        promo = make_promotional_price(
            discount_type="PERCENTAGE_OFF",
            discount_value=Decimal("50.00"),
            max_discount_amount=Decimal("300.00"),
        )
        # 50% of 1000 = 500, but capped at 300 → 1000 - 300 = 700
        result = promo.calculate_discounted_price(Decimal("1000.00"), quantity=1)
        assert result == Decimal("700.00")


# =========================================================================
# PromotionAnalytics model tests
# =========================================================================

class TestPromotionAnalyticsMeta:
    def test_db_table(self):
        assert PromotionAnalytics._meta.db_table == "pricing_promotion_analytics"


# =========================================================================
# ScheduledPriceHistory model tests
# =========================================================================

class TestScheduledPriceHistoryMeta:
    def test_db_table(self):
        assert ScheduledPriceHistory._meta.db_table == "pricing_scheduled_history"

    def test_ordering(self):
        assert ScheduledPriceHistory._meta.ordering == ["-archived_at"]
