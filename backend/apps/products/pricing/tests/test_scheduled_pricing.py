"""
Task 84 — Scheduled pricing, flash sale, and promotional price tests.

Uses DB-free stubs where possible and mocks for service-layer DB calls.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.products.pricing.models.scheduled_price import ScheduledPrice
from apps.products.pricing.models.flash_sale import FlashSale
from apps.products.pricing.models.promotional_price import (
    PromotionalPrice,
    PromotionalConditionResult,
)
from apps.products.pricing.services.price_resolution import PriceResolutionService

from .factories import (
    make_scheduled_price,
    make_flash_sale,
    make_promotional_price,
    make_product,
    make_product_price,
)


# =========================================================================
# ScheduledPrice tests
# =========================================================================

class TestScheduledPriceStatus:
    def test_status_choices_exist(self):
        assert hasattr(ScheduledPrice, "Status")
        assert "PENDING" == ScheduledPrice.Status.PENDING
        assert "ACTIVE" == ScheduledPrice.Status.ACTIVE
        assert "EXPIRED" == ScheduledPrice.Status.EXPIRED


# =========================================================================
# FlashSale calculation tests
# =========================================================================


def _flash_with_sp(hours_remaining=24, **kw):
    """Create a FlashSale with a mock ScheduledPrice for delegate properties."""
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


class TestFlashSaleCalculations:
    def test_quantity_remaining(self):
        fs = make_flash_sale(max_quantity=100, quantity_sold=30)
        assert fs.quantity_remaining == 70

    def test_percent_sold(self):
        fs = make_flash_sale(max_quantity=200, quantity_sold=50)
        assert fs.percent_sold == 25.0

    def test_percent_sold_zero_max(self):
        fs = make_flash_sale(max_quantity=0, quantity_sold=0)
        assert fs.percent_sold == 0.0

    def test_urgency_levels(self):
        # critical — percent_sold >= 90 (no _sp needed)
        assert make_flash_sale(max_quantity=100, quantity_sold=96).urgency_level == "critical"
        # high — percent_sold >= 75 (needs _sp for hours_left)
        assert _flash_with_sp(hours_remaining=24, max_quantity=100, quantity_sold=82).urgency_level == "high"
        # medium — hours_left <= 6 (needs _sp)
        assert _flash_with_sp(hours_remaining=5, max_quantity=100, quantity_sold=55).urgency_level == "medium"
        # low — hours_left > 6 and percent_sold < 75
        assert _flash_with_sp(hours_remaining=24, max_quantity=100, quantity_sold=10).urgency_level == "low"

    def test_get_urgency_message_returns_string(self):
        fs = make_flash_sale(max_quantity=100, quantity_sold=96, is_sold_out=True)
        msg = fs.get_urgency_message()
        assert isinstance(msg, str)
        assert msg == "SOLD OUT"


# =========================================================================
# PromotionalConditionResult tests
# =========================================================================

class TestPromotionalConditionResult:
    def test_truthy_when_met(self):
        r = PromotionalConditionResult(is_met=True, reason="OK")
        assert bool(r) is True

    def test_falsy_when_not_met(self):
        r = PromotionalConditionResult(is_met=False, reason="Not enough")
        assert bool(r) is False


# =========================================================================
# PromotionalPrice discount calculation
# =========================================================================

class TestPromotionalDiscount:
    def test_percentage_off(self):
        promo = make_promotional_price(
            discount_type="PERCENTAGE_OFF",
            discount_value=Decimal("25.00"),
        )
        assert promo.calculate_discounted_price(Decimal("1000.00"), 1) == Decimal("750.00")

    def test_fixed_off(self):
        promo = make_promotional_price(
            discount_type="FIXED_OFF",
            discount_value=Decimal("150.00"),
        )
        assert promo.calculate_discounted_price(Decimal("1000.00"), 1) == Decimal("850.00")

    def test_fixed_price(self):
        promo = make_promotional_price(
            discount_type="FIXED_PRICE",
            discount_value=Decimal("499.00"),
        )
        assert promo.calculate_discounted_price(Decimal("1000.00"), 1) == Decimal("499.00")

    def test_max_discount_cap(self):
        promo = make_promotional_price(
            discount_type="PERCENTAGE_OFF",
            discount_value=Decimal("50.00"),
            max_discount_amount=Decimal("200.00"),
        )
        # 50% of 1000 = 500, capped at 200 → price = 800
        assert promo.calculate_discounted_price(Decimal("1000.00"), 1) == Decimal("800.00")

    def test_percentage_off_100(self):
        promo = make_promotional_price(
            discount_type="PERCENTAGE_OFF",
            discount_value=Decimal("100.00"),
        )
        assert promo.calculate_discounted_price(Decimal("1000.00"), 1) == Decimal("0.00")


# =========================================================================
# PriceResolutionService — unit tests with mocks
# =========================================================================

class TestPriceResolutionService:
    """Mocked tests for the price resolution priority chain."""

    def test_returns_dict_with_required_keys(self):
        """Ensure the return contract is correct."""
        product = make_product()
        pp = make_product_price(base_price=Decimal("1000.00"), sale_price=None)
        product._state.fields_cache = {"product_price": pp}

        with (
            patch.object(PriceResolutionService, "_check_flash_sales", return_value=None),
            patch.object(PriceResolutionService, "_check_scheduled_prices", return_value=None),
            patch.object(PriceResolutionService, "_check_promotional_prices", return_value=None),
            patch.object(PriceResolutionService, "_check_sale_price", return_value=None),
            patch.object(
                PriceResolutionService,
                "_get_base_price",
                return_value=Decimal("1000.00"),
            ),
            patch.object(
                PriceResolutionService,
                "_resolve_product_variant",
                return_value=(product, None),
            ),
        ):
            result = PriceResolutionService.get_effective_price(product)
            assert "price" in result
            assert "price_type" in result
            assert "reason" in result
            assert "original_price" in result
            assert "discount_amount" in result
            assert "discount_percentage" in result

    def test_flash_sale_takes_priority(self):
        product = make_product()

        with (
            patch.object(
                PriceResolutionService,
                "_resolve_product_variant",
                return_value=(product, None),
            ),
            patch.object(
                PriceResolutionService,
                "_get_base_price",
                return_value=Decimal("1000.00"),
            ),
            patch.object(
                PriceResolutionService,
                "_check_flash_sales",
                return_value=Decimal("600.00"),
            ),
        ):
            result = PriceResolutionService.get_effective_price(product)
            assert result["price"] == Decimal("600.00")
            assert result["price_type"] == "flash_sale"

    def test_scheduled_takes_priority_over_promo(self):
        product = make_product()

        with (
            patch.object(
                PriceResolutionService,
                "_resolve_product_variant",
                return_value=(product, None),
            ),
            patch.object(
                PriceResolutionService,
                "_get_base_price",
                return_value=Decimal("1000.00"),
            ),
            patch.object(PriceResolutionService, "_check_flash_sales", return_value=None),
            patch.object(
                PriceResolutionService,
                "_check_scheduled_prices",
                return_value=Decimal("750.00"),
            ),
        ):
            result = PriceResolutionService.get_effective_price(product)
            assert result["price_type"] == "scheduled"

    def test_discount_amount_calculated(self):
        product = make_product()

        with (
            patch.object(
                PriceResolutionService,
                "_resolve_product_variant",
                return_value=(product, None),
            ),
            patch.object(
                PriceResolutionService,
                "_get_base_price",
                return_value=Decimal("1000.00"),
            ),
            patch.object(PriceResolutionService, "_check_flash_sales", return_value=None),
            patch.object(PriceResolutionService, "_check_scheduled_prices", return_value=None),
            patch.object(PriceResolutionService, "_check_promotional_prices", return_value=None),
            patch.object(
                PriceResolutionService,
                "_check_sale_price",
                return_value=Decimal("800.00"),
            ),
        ):
            result = PriceResolutionService.get_effective_price(product)
            assert result["discount_amount"] == Decimal("200.00")
            assert result["discount_percentage"] == Decimal("20.00")
