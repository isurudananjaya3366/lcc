"""
SKU pattern configuration for variant generation.

Provides constants and helper functions for formatting variant SKUs
following configurable patterns.
"""

import re

DEFAULT_SKU_PATTERN = "{product_sku}-{options}"
SKU_SEPARATOR = "-"
SKU_MAX_RETRY = 999


def validate_sku_pattern(pattern: str) -> bool:
    """
    Validate that a SKU pattern contains required placeholders.

    A valid pattern must include ``{product_sku}`` and at least one of
    ``{options}``, ``{option_1}``, or ``{counter}``.

    Args:
        pattern: SKU pattern string with placeholders.

    Returns:
        True if the pattern is valid.
    """
    if "{product_sku}" not in pattern:
        return False
    has_options = any(
        ph in pattern
        for ph in ("{options}", "{option_1}", "{counter}")
    )
    return has_options


def format_option_value_for_sku(value: str) -> str:
    """
    Format an option value string for use in a SKU.

    Converts to uppercase, removes spaces and special characters,
    and truncates to 20 characters.

    Args:
        value: Raw option value (e.g., ``"16 GB"``, ``"Red"``).

    Returns:
        Cleaned string suitable for SKU (e.g., ``"16GB"``, ``"RED"``).
    """
    cleaned = value.upper()
    cleaned = re.sub(r"[^A-Z0-9]", "", cleaned)
    return cleaned[:20]
