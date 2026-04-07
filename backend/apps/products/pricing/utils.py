"""
Pricing utility functions.

Formatting, parsing, rounding, comparison, and analysis helpers for
LKR pricing throughout the application.
"""

import math as _math
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from .constants import (
    CURRENCY_DECIMAL_PLACES,
    CURRENCY_SYMBOL,
    MAX_PRICE,
    MIN_PRICE,
    PRICE_FORMAT,
)


# ── Formatting ─────────────────────────────────────────────────


def format_lkr(amount: Decimal | None) -> str:
    """Format a Decimal amount as an LKR string, e.g. '₨ 1,500.00'."""
    if amount is None:
        return f"{CURRENCY_SYMBOL} 0.00"
    return PRICE_FORMAT.format(symbol=CURRENCY_SYMBOL, amount=amount)


def format_lkr_html(amount: Decimal | None) -> str:
    """Format as LKR with an HTML <span> wrapper for styling."""
    formatted = format_lkr(amount)
    return f'<span class="price">{formatted}</span>'


def parse_lkr(value: str) -> Decimal:
    """
    Parse an LKR-formatted string back to Decimal.

    Strips the currency symbol, commas, and whitespace.
    """
    cleaned = value.replace(CURRENCY_SYMBOL, "").replace(",", "").strip()
    return Decimal(cleaned)


def round_lkr(amount: Decimal) -> Decimal:
    """Round to 2 decimal places (LKR precision)."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def round_price(amount: Decimal, decimal_places: int = 2) -> Decimal:
    """Round with ROUND_HALF_UP to *decimal_places*."""
    quant = Decimal(10) ** -decimal_places
    return amount.quantize(quant, rounding=ROUND_HALF_UP)


def round_to_nearest(amount: Decimal, nearest: Decimal) -> Decimal:
    """Round *amount* to the nearest multiple of *nearest*."""
    if nearest <= 0:
        return amount
    return (amount / nearest).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * nearest


def round_up_to_nearest(amount: Decimal, nearest: Decimal) -> Decimal:
    """Round *amount* UP to the nearest multiple of *nearest*."""
    if nearest <= 0:
        return amount
    return Decimal(_math.ceil(amount / nearest)) * nearest


def round_down_to_nearest(amount: Decimal, nearest: Decimal) -> Decimal:
    """Round *amount* DOWN to the nearest multiple of *nearest*."""
    if nearest <= 0:
        return amount
    return Decimal(_math.floor(amount / nearest)) * nearest


def psychological_price(amount: Decimal) -> Decimal:
    """Adjust price to a psychological price point (e.g. 1000 → 999)."""
    if amount <= 0:
        return amount
    return amount - Decimal("1")


def validate_rounded_price(price: Decimal) -> bool:
    """Check that *price* is properly rounded to 2 dp."""
    return price == price.quantize(Decimal("0.01"))


def format_price_range(min_price: Decimal, max_price: Decimal) -> str:
    """Format a price range, e.g. '₨ 100.00 – ₨ 500.00'."""
    return f"{format_lkr(min_price)} – {format_lkr(max_price)}"


def format_discount(original: Decimal, discounted: Decimal) -> str:
    """Return a human-readable discount string with percentage."""
    if not original:
        return format_lkr(discounted)
    pct = ((original - discounted) / original * 100).quantize(Decimal("0.01"))
    return f"{format_lkr(discounted)} ({pct}% off)"


def get_price_display(
    base_price: Decimal,
    sale_price: Decimal | None = None,
    is_on_sale: bool = False,
) -> str:
    """
    Return a user-facing price string.

    Shows strike-through original + sale price when on sale.
    """
    if is_on_sale and sale_price is not None:
        return f"{format_lkr(sale_price)} (was {format_lkr(base_price)})"
    return format_lkr(base_price)


# ── Comparison / analysis ──────────────────────────────────────


def compare_prices(price_a: Decimal, price_b: Decimal) -> dict:
    """
    Compare two prices and return difference metrics.

    Returns dict with keys: difference, percentage, direction.
    """
    diff = price_b - price_a
    pct = Decimal("0.00")
    if price_a:
        pct = (diff / price_a * 100).quantize(Decimal("0.01"))
    if diff > 0:
        direction = "increase"
    elif diff < 0:
        direction = "decrease"
    else:
        direction = "unchanged"
    return {
        "difference": diff,
        "percentage": pct,
        "direction": direction,
    }


def calculate_price_difference(old: Decimal, new: Decimal) -> Decimal:
    """Simple difference: new − old."""
    return new - old


def is_price_higher(price_a: Decimal, price_b: Decimal) -> bool:
    """Return True if price_a is strictly greater than price_b."""
    return price_a > price_b


def is_significant_change(
    old: Decimal,
    new: Decimal,
    threshold: Decimal = Decimal("5"),
) -> bool:
    """Return True if % change exceeds *threshold*."""
    if not old:
        return True
    pct = abs((new - old) / old * 100)
    return pct > threshold


def get_price_trend(prices: list[Decimal]) -> str:
    """
    Determine trend direction from an ordered list of prices.

    Returns 'increasing', 'decreasing', 'stable', or 'fluctuating'.
    """
    if len(prices) < 2:
        return "stable"
    diffs = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    if all(d > 0 for d in diffs):
        return "increasing"
    if all(d < 0 for d in diffs):
        return "decreasing"
    if all(d == 0 for d in diffs):
        return "stable"
    return "fluctuating"


def compare_product_prices(prices_a: dict, prices_b: dict) -> dict:
    """
    Compare two product-price dicts (field → Decimal).

    Returns a dict of field → comparison result for each differing field.
    """
    result = {}
    all_fields = set(prices_a) | set(prices_b)
    for field in all_fields:
        a = prices_a.get(field)
        b = prices_b.get(field)
        if a is not None and b is not None:
            result[field] = compare_prices(a, b)
    return result


def get_price_statistics(prices: list[Decimal]) -> dict:
    """
    Compute basic statistics for a list of prices.

    Returns min, max, avg, median, count.
    """
    if not prices:
        return {
            "min": Decimal("0"),
            "max": Decimal("0"),
            "avg": Decimal("0"),
            "median": Decimal("0"),
            "count": 0,
        }
    sorted_prices = sorted(prices)
    count = len(sorted_prices)
    total = sum(sorted_prices)
    mid = count // 2
    if count % 2 == 0:
        median = ((sorted_prices[mid - 1] + sorted_prices[mid]) / 2).quantize(
            Decimal("0.01")
        )
    else:
        median = sorted_prices[mid]
    return {
        "min": sorted_prices[0],
        "max": sorted_prices[-1],
        "avg": (total / count).quantize(Decimal("0.01")),
        "median": median,
        "count": count,
    }


def find_pricing_anomalies(
    prices: list[Decimal],
    std_dev_threshold: float = 2.0,
) -> list[Decimal]:
    """
    Identify anomalous prices that deviate significantly from the mean.
    """
    if len(prices) < 3:
        return []
    import math

    mean = sum(prices) / len(prices)
    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
    std_dev = Decimal(str(math.sqrt(float(variance))))
    threshold = std_dev * Decimal(str(std_dev_threshold))
    return [p for p in prices if abs(p - mean) > threshold]


def calculate_optimal_price(
    cost: Decimal,
    target_margin: Decimal,
) -> Decimal:
    """
    Calculate selling price for a desired profit margin %.

    margin = (price - cost) / price * 100
    ⇒ price = cost / (1 - margin/100)
    """
    if target_margin >= 100:
        return MAX_PRICE
    divisor = 1 - target_margin / Decimal("100")
    if divisor <= 0:
        return MAX_PRICE
    return (cost / divisor).quantize(Decimal("0.01"))


def suggest_price_tiers(
    base_price: Decimal,
    tiers: int = 3,
    step_pct: Decimal = Decimal("10"),
) -> list[dict]:
    """
    Generate price tier suggestions based on percentage steps.

    Returns a list of dicts with quantity_min and price.
    """
    result = []
    for i in range(tiers):
        discount = step_pct * (i + 1)
        tier_price = (base_price * (1 - discount / Decimal("100"))).quantize(
            Decimal("0.01")
        )
        result.append(
            {
                "tier": i + 1,
                "discount_percentage": discount,
                "price": max(tier_price, MIN_PRICE),
            }
        )
    return result
