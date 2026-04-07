"""
Currency and pricing constants for LankaCommerce Cloud POS.

LKR (Sri Lankan Rupee) formatting and validation rules.
"""

from decimal import Decimal

# ISO 4217 currency code
CURRENCY_CODE = "LKR"

# Currency display symbol
CURRENCY_SYMBOL = "₨"

# Full currency name
CURRENCY_NAME = "Sri Lankan Rupees"

# Decimal precision for LKR (cents)
CURRENCY_DECIMAL_PLACES = 2

# Total max digits (including decimal places) — supports up to 999,999,999.99
CURRENCY_MAX_DIGITS = 12

# Price boundaries
MIN_PRICE = Decimal("0.00")
MAX_PRICE = Decimal("999999999.99")
DEFAULT_PRICE = Decimal("0.00")

# Display format template
PRICE_FORMAT = "{symbol} {amount:,.2f}"

# Price type choices for history tracking
PRICE_TYPE_BASE = "BASE"
PRICE_TYPE_SALE = "SALE"
PRICE_TYPE_WHOLESALE = "WHOLESALE"
PRICE_TYPE_COST = "COST"

PRICE_TYPE_CHOICES = [
    (PRICE_TYPE_BASE, "Base Price"),
    (PRICE_TYPE_SALE, "Sale Price"),
    (PRICE_TYPE_WHOLESALE, "Wholesale Price"),
    (PRICE_TYPE_COST, "Cost Price"),
]

# Price adjustment type choices
ADJUSTMENT_TYPE_FIXED = "FIXED"
ADJUSTMENT_TYPE_PERCENTAGE = "PERCENTAGE"

ADJUSTMENT_TYPE_CHOICES = [
    (ADJUSTMENT_TYPE_FIXED, "Fixed Amount"),
    (ADJUSTMENT_TYPE_PERCENTAGE, "Percentage"),
]

# Change source choices for price history
CHANGE_SOURCE_MANUAL = "manual"
CHANGE_SOURCE_IMPORT = "import"
CHANGE_SOURCE_API = "api"
CHANGE_SOURCE_SCHEDULED = "scheduled"
CHANGE_SOURCE_PROMOTION = "promotion"

CHANGE_SOURCE_CHOICES = [
    (CHANGE_SOURCE_MANUAL, "Manual"),
    (CHANGE_SOURCE_IMPORT, "Import"),
    (CHANGE_SOURCE_API, "API"),
    (CHANGE_SOURCE_SCHEDULED, "Scheduled"),
    (CHANGE_SOURCE_PROMOTION, "Promotion"),
]
