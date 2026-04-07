"""PDF generation utilities for payment receipts."""

from decimal import Decimal


# Page dimensions (A4)
PAGE_WIDTH = 595.27
PAGE_HEIGHT = 841.89
MARGIN_LEFT = 50
MARGIN_RIGHT = 50
MARGIN_TOP = 50
MARGIN_BOTTOM = 50
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Colors (RGB normalized 0-1)
PRIMARY_COLOR = (37 / 255, 99 / 255, 235 / 255)  # #2563eb
SUCCESS_COLOR = (22 / 255, 163 / 255, 74 / 255)  # #16a34a
WARNING_COLOR = (202 / 255, 138 / 255, 4 / 255)  # #ca8a04
DARK_COLOR = (31 / 255, 41 / 255, 55 / 255)  # #1f2937
LIGHT_COLOR = (243 / 255, 244 / 255, 246 / 255)  # #f3f4f6
WHITE_COLOR = (1, 1, 1)

# Company defaults (can be overridden via settings)
DEFAULT_COMPANY_NAME = "ABC Corporation"
DEFAULT_COMPANY_ADDRESS = "123 Business Street, Colombo 03, Sri Lanka"
DEFAULT_COMPANY_CONTACT = "+94 11 234 5678 | info@abccorp.lk"
DEFAULT_COMPANY_REGISTRATION = "PV 12345"
DEFAULT_COMPANY_VAT_NUMBER = ""
DEFAULT_RECEIPT_THANK_YOU = "Thank you for your payment!"
DEFAULT_RECEIPT_FOOTER = "This is a computer-generated receipt."
DEFAULT_RECEIPT_TERMS = ""


def format_currency(amount, currency="LKR"):
    """Format amount with currency symbol."""
    if currency == "LKR":
        prefix = "Rs."
    elif currency == "USD":
        prefix = "$"
    elif currency == "EUR":
        prefix = "€"
    elif currency == "GBP":
        prefix = "£"
    else:
        prefix = currency

    if isinstance(amount, Decimal):
        formatted = f"{amount:,.2f}"
    else:
        formatted = f"{float(amount):,.2f}"

    return f"{prefix} {formatted}"


def get_company_setting(key, default=None):
    """Get company setting from Django settings or use defaults."""
    from django.conf import settings

    defaults_map = {
        "COMPANY_NAME": DEFAULT_COMPANY_NAME,
        "COMPANY_ADDRESS": DEFAULT_COMPANY_ADDRESS,
        "COMPANY_CONTACT": DEFAULT_COMPANY_CONTACT,
        "COMPANY_REGISTRATION": DEFAULT_COMPANY_REGISTRATION,
        "COMPANY_VAT_NUMBER": DEFAULT_COMPANY_VAT_NUMBER,
        "RECEIPT_THANK_YOU_MESSAGE": DEFAULT_RECEIPT_THANK_YOU,
        "RECEIPT_FOOTER_MESSAGE": DEFAULT_RECEIPT_FOOTER,
        "RECEIPT_TERMS_TEXT": DEFAULT_RECEIPT_TERMS,
    }

    return getattr(settings, key, defaults_map.get(key, default))
