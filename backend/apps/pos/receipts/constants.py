"""
Receipt generation constants.

Defines receipt types, paper sizes, and display configuration constants
used throughout the receipt generation module.
"""

# =============================================================================
# Receipt Type Constants (Task 02)
# =============================================================================

RECEIPT_TYPE_SALE = "sale"
RECEIPT_TYPE_REFUND = "refund"
RECEIPT_TYPE_VOID = "void"
RECEIPT_TYPE_REPRINT = "reprint"

RECEIPT_TYPES = (
    (RECEIPT_TYPE_SALE, "Sale"),
    (RECEIPT_TYPE_REFUND, "Refund"),
    (RECEIPT_TYPE_VOID, "Void"),
    (RECEIPT_TYPE_REPRINT, "Reprint"),
)

# =============================================================================
# Paper Size Constants (Task 03)
# =============================================================================

PAPER_SIZE_THERMAL_80MM = "80mm"
PAPER_SIZE_THERMAL_58MM = "58mm"
PAPER_SIZE_A4 = "a4"

PAPER_SIZES = (
    (PAPER_SIZE_THERMAL_80MM, "Thermal 80mm"),
    (PAPER_SIZE_THERMAL_58MM, "Thermal 58mm"),
    (PAPER_SIZE_A4, "A4"),
)

# Character width per paper size (for text formatting/wrapping)
PAPER_SIZE_CHAR_WIDTHS = {
    PAPER_SIZE_THERMAL_80MM: 48,
    PAPER_SIZE_THERMAL_58MM: 32,
    PAPER_SIZE_A4: 72,
}

# =============================================================================
# Logo Size Constants (Task 05)
# =============================================================================

LOGO_SIZE_SMALL = "small"
LOGO_SIZE_MEDIUM = "medium"
LOGO_SIZE_LARGE = "large"

LOGO_SIZE_CHOICES = (
    (LOGO_SIZE_SMALL, "Small"),
    (LOGO_SIZE_MEDIUM, "Medium"),
    (LOGO_SIZE_LARGE, "Large"),
)

# =============================================================================
# QR Code Constants (Task 13)
# =============================================================================

QR_CONTENT_TRANSACTION_ID = "transaction_id"
QR_CONTENT_DIGITAL_RECEIPT = "digital_receipt"
QR_CONTENT_LOYALTY = "loyalty"
QR_CONTENT_FEEDBACK = "feedback"
QR_CONTENT_PAYMENT_VERIFY = "payment_verify"
QR_CONTENT_WEBSITE = "website"

QR_CONTENT_TYPE_CHOICES = (
    (QR_CONTENT_TRANSACTION_ID, "Transaction ID"),
    (QR_CONTENT_DIGITAL_RECEIPT, "Digital Receipt URL"),
    (QR_CONTENT_LOYALTY, "Loyalty Program"),
    (QR_CONTENT_FEEDBACK, "Feedback Form"),
    (QR_CONTENT_PAYMENT_VERIFY, "Payment Verification"),
    (QR_CONTENT_WEBSITE, "Website"),
)

QR_SIZE_SMALL = "small"
QR_SIZE_MEDIUM = "medium"
QR_SIZE_LARGE = "large"

QR_SIZE_CHOICES = (
    (QR_SIZE_SMALL, "Small"),
    (QR_SIZE_MEDIUM, "Medium"),
    (QR_SIZE_LARGE, "Large"),
)

QR_POSITION_BEFORE_FOOTER = "before_footer"
QR_POSITION_AFTER_FOOTER = "after_footer"

QR_POSITION_CHOICES = (
    (QR_POSITION_BEFORE_FOOTER, "Before Footer"),
    (QR_POSITION_AFTER_FOOTER, "After Footer"),
)

# =============================================================================
# Font Size Constants (Task 14)
# =============================================================================

FONT_SIZE_SMALL = "small"
FONT_SIZE_NORMAL = "normal"
FONT_SIZE_LARGE = "large"

FONT_SIZE_CHOICES = (
    (FONT_SIZE_SMALL, "Small"),
    (FONT_SIZE_NORMAL, "Normal"),
    (FONT_SIZE_LARGE, "Large"),
)

SEPARATOR_STYLE_EQUALS = "equals"
SEPARATOR_STYLE_DASHES = "dashes"
SEPARATOR_STYLE_STARS = "stars"
SEPARATOR_STYLE_NONE = "none"

SEPARATOR_STYLE_CHOICES = (
    (SEPARATOR_STYLE_EQUALS, "Equals (═)"),
    (SEPARATOR_STYLE_DASHES, "Dashes (─)"),
    (SEPARATOR_STYLE_STARS, "Stars (*)"),
    (SEPARATOR_STYLE_NONE, "None"),
)

SEPARATOR_LENGTH_FULL = "full"
SEPARATOR_LENGTH_HALF = "half"
SEPARATOR_LENGTH_CUSTOM = "custom"

SEPARATOR_LENGTH_CHOICES = (
    (SEPARATOR_LENGTH_FULL, "Full Width"),
    (SEPARATOR_LENGTH_HALF, "Half Width"),
    (SEPARATOR_LENGTH_CUSTOM, "Custom"),
)
