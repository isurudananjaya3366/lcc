"""
Currency utilities for Sri Lankan Rupees (LKR).

Format: Rs. 1,500.00
Symbol: Rs. or රු
ISO Code: LKR
Decimal places: 2
"""

from decimal import Decimal, InvalidOperation


def format_lkr(amount, show_symbol=True):
    """
    Format amount as Sri Lankan Rupees.

    Args:
        amount: Numeric amount (int, float, Decimal, or str)
        show_symbol: Include Rs. symbol (default True)

    Returns:
        str: Formatted currency string

    Examples:
        >>> format_lkr(1500)
        'Rs. 1,500.00'
        >>> format_lkr(1500000)
        'Rs. 1,500,000.00'
        >>> format_lkr(1500.50, show_symbol=False)
        '1,500.50'
        >>> format_lkr(-500)
        'Rs. -500.00'
    """
    amount_decimal = Decimal(str(amount))
    formatted = "{:,.2f}".format(amount_decimal)

    if show_symbol:
        return f"Rs. {formatted}"
    return formatted


def parse_lkr(value):
    """
    Parse LKR formatted string to Decimal.

    Args:
        value: Formatted currency string or number

    Returns:
        Decimal: Parsed amount

    Raises:
        ValueError: If value cannot be parsed

    Examples:
        >>> parse_lkr("Rs. 1,500.00")
        Decimal('1500.00')
        >>> parse_lkr("1,500")
        Decimal('1500')
        >>> parse_lkr(1500)
        Decimal('1500')
    """
    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float)):
        return Decimal(str(value))

    if not isinstance(value, str):
        raise ValueError(f"Cannot parse value of type {type(value).__name__}")

    # Remove currency symbols and whitespace
    cleaned = value.replace('Rs.', '').replace('රු', '')
    cleaned = cleaned.replace(',', '').strip()

    if not cleaned:
        raise ValueError("Empty value after cleaning")

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"Cannot parse '{value}' as currency")


def convert_currency(amount, from_currency, to_currency, exchange_rate=None):
    """
    Convert between currencies.

    NOTE: This is a placeholder. Exchange rate API integration
    will be added in Phase 09 (Integrations).

    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., 'LKR')
        to_currency: Target currency code (e.g., 'USD')
        exchange_rate: Exchange rate (required for now)

    Returns:
        Decimal: Converted amount

    Raises:
        ValueError: If exchange_rate is not provided

    Example:
        >>> convert_currency(300, 'LKR', 'USD', exchange_rate=0.0033)
        Decimal('0.99')
    """
    if exchange_rate is None:
        raise ValueError(
            "Exchange rate required. API integration pending (Phase 09)."
        )

    amount_decimal = Decimal(str(amount))
    rate_decimal = Decimal(str(exchange_rate))

    return amount_decimal * rate_decimal
