"""
Quote Management Constants

Defines choices, constants, and configuration values for the quotes app.
"""

from django.db import models


class QuoteStatus(models.TextChoices):
    """
    Quote lifecycle status choices.

    Status Flow:
        DRAFT → SENT → ACCEPTED → CONVERTED
                   ↓
              REJECTED / EXPIRED

    Terminal States: REJECTED, EXPIRED, CONVERTED
    """

    DRAFT = "DRAFT", "Draft"
    SENT = "SENT", "Sent"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    EXPIRED = "EXPIRED", "Expired"
    CONVERTED = "CONVERTED", "Converted"


# Allowed status transitions
QUOTE_STATUS_TRANSITIONS = {
    QuoteStatus.DRAFT: [QuoteStatus.SENT, QuoteStatus.EXPIRED],
    QuoteStatus.SENT: [QuoteStatus.ACCEPTED, QuoteStatus.REJECTED, QuoteStatus.EXPIRED],
    QuoteStatus.ACCEPTED: [QuoteStatus.CONVERTED],
    QuoteStatus.REJECTED: [],
    QuoteStatus.EXPIRED: [],
    QuoteStatus.CONVERTED: [],
}

# Terminal states (cannot transition further)
TERMINAL_STATES = {QuoteStatus.REJECTED, QuoteStatus.EXPIRED, QuoteStatus.CONVERTED}

# Editable states
EDITABLE_STATES = {QuoteStatus.DRAFT}


class CurrencyChoice(models.TextChoices):
    """
    Supported currencies for quotes.

    Default: LKR (Sri Lankan Rupee)
    """

    LKR = "LKR", "Sri Lankan Rupee (₨)"
    USD = "USD", "US Dollar ($)"


# Currency symbol mapping
CURRENCY_SYMBOLS = {
    "LKR": "₨",
    "USD": "$",
}


class DiscountType(models.TextChoices):
    """
    Discount type choices for header-level quote discounts.
    """

    PERCENTAGE = "PERCENTAGE", "Percentage"
    FIXED = "FIXED", "Fixed Amount"
