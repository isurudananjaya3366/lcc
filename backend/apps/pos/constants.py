"""
POS Constants.

All constants for the Point of Sale module including terminal statuses,
session statuses, cart statuses, payment methods, and hardware types.
"""

# ── Terminal Status Constants ─────────────────────────────────────────────
TERMINAL_STATUS_ACTIVE = "active"
TERMINAL_STATUS_INACTIVE = "inactive"
TERMINAL_STATUS_MAINTENANCE = "maintenance"
TERMINAL_STATUS_OFFLINE = "offline"

TERMINAL_STATUS_CHOICES = (
    (TERMINAL_STATUS_ACTIVE, "Active"),
    (TERMINAL_STATUS_INACTIVE, "Inactive"),
    (TERMINAL_STATUS_MAINTENANCE, "Maintenance"),
    (TERMINAL_STATUS_OFFLINE, "Offline"),
)

# ── Session Status Constants ──────────────────────────────────────────────
SESSION_STATUS_OPEN = "open"
SESSION_STATUS_CLOSED = "closed"
SESSION_STATUS_SUSPENDED = "suspended"
SESSION_STATUS_FORCE_CLOSED = "force_closed"

SESSION_STATUS_CHOICES = (
    (SESSION_STATUS_OPEN, "Open"),
    (SESSION_STATUS_CLOSED, "Closed"),
    (SESSION_STATUS_SUSPENDED, "Suspended"),
    (SESSION_STATUS_FORCE_CLOSED, "Force Closed"),
)

# ── Printer Type Constants ────────────────────────────────────────────────
PRINTER_TYPE_THERMAL = "thermal"
PRINTER_TYPE_IMPACT = "impact"
PRINTER_TYPE_NONE = "none"

PRINTER_TYPE_CHOICES = (
    (PRINTER_TYPE_THERMAL, "Thermal Printer"),
    (PRINTER_TYPE_IMPACT, "Impact Printer"),
    (PRINTER_TYPE_NONE, "No Printer"),
)

# ── Scanner Interface Constants ───────────────────────────────────────────
SCANNER_INTERFACE_USB = "usb"
SCANNER_INTERFACE_BLUETOOTH = "bluetooth"
SCANNER_INTERFACE_WIRELESS = "wireless"

SCANNER_INTERFACE_CHOICES = (
    (SCANNER_INTERFACE_USB, "USB"),
    (SCANNER_INTERFACE_BLUETOOTH, "Bluetooth"),
    (SCANNER_INTERFACE_WIRELESS, "Wireless"),
)

# ── Receipt Language Constants ────────────────────────────────────────────
RECEIPT_LANGUAGE_ENGLISH = "en"
RECEIPT_LANGUAGE_SINHALA = "si"
RECEIPT_LANGUAGE_TAMIL = "ta"

RECEIPT_LANGUAGE_CHOICES = (
    (RECEIPT_LANGUAGE_ENGLISH, "English"),
    (RECEIPT_LANGUAGE_SINHALA, "Sinhala"),
    (RECEIPT_LANGUAGE_TAMIL, "Tamil"),
)

# ── Cart Status Constants ─────────────────────────────────────────────────
CART_STATUS_ACTIVE = "active"
CART_STATUS_HELD = "held"
CART_STATUS_COMPLETED = "completed"
CART_STATUS_VOIDED = "voided"
CART_STATUS_ABANDONED = "abandoned"
DEFAULT_CART_STATUS = CART_STATUS_ACTIVE
CART_STATUS_CHOICES = (
    (CART_STATUS_ACTIVE, "Active"),
    (CART_STATUS_HELD, "Held"),
    (CART_STATUS_COMPLETED, "Completed"),
    (CART_STATUS_VOIDED, "Voided"),
    (CART_STATUS_ABANDONED, "Abandoned"),
)

# ── Discount Type Constants ───────────────────────────────────────────────
DISCOUNT_TYPE_PERCENT = "percent"
DISCOUNT_TYPE_FIXED = "fixed"
DISCOUNT_TYPE_NONE = "none"

DISCOUNT_TYPE_CHOICES = (
    (DISCOUNT_TYPE_PERCENT, "Percentage"),
    (DISCOUNT_TYPE_FIXED, "Fixed Amount"),
    (DISCOUNT_TYPE_NONE, "No Discount"),
)

# ── Payment Method Constants ──────────────────────────────────────────────
PAYMENT_METHOD_CASH = "cash"
PAYMENT_METHOD_CARD = "card"
PAYMENT_METHOD_BANK_TRANSFER = "bank_transfer"
PAYMENT_METHOD_MOBILE_FRIMI = "mobile_frimi"
PAYMENT_METHOD_MOBILE_GENIE = "mobile_genie"
PAYMENT_METHOD_STORE_CREDIT = "store_credit"
PAYMENT_METHOD_PAYHERE = "payhere"

PAYMENT_METHOD_CHOICES = (
    (PAYMENT_METHOD_CASH, "Cash"),
    (PAYMENT_METHOD_CARD, "Card (Visa/Mastercard)"),
    (PAYMENT_METHOD_BANK_TRANSFER, "Bank Transfer"),
    (PAYMENT_METHOD_MOBILE_FRIMI, "FriMi"),
    (PAYMENT_METHOD_MOBILE_GENIE, "Dialog Genie"),
    (PAYMENT_METHOD_STORE_CREDIT, "Store Credit"),
    (PAYMENT_METHOD_PAYHERE, "PayHere"),
)

# ── Payment Status Constants ──────────────────────────────────────────────
PAYMENT_STATUS_PENDING = "pending"
PAYMENT_STATUS_COMPLETED = "completed"
PAYMENT_STATUS_FAILED = "failed"
PAYMENT_STATUS_REFUNDED = "refunded"
PAYMENT_STATUS_VOIDED = "voided"

PAYMENT_STATUS_CHOICES = (
    (PAYMENT_STATUS_PENDING, "Pending"),
    (PAYMENT_STATUS_COMPLETED, "Completed"),
    (PAYMENT_STATUS_FAILED, "Failed"),
    (PAYMENT_STATUS_REFUNDED, "Refunded"),
    (PAYMENT_STATUS_VOIDED, "Voided"),
)

# ── Search Method Constants ───────────────────────────────────────────────
SEARCH_METHOD_BARCODE = "barcode"
SEARCH_METHOD_SKU = "sku"
SEARCH_METHOD_NAME = "name"
SEARCH_METHOD_COMBINED = "combined"

SEARCH_METHOD_CHOICES = (
    (SEARCH_METHOD_BARCODE, "Barcode Scan"),
    (SEARCH_METHOD_SKU, "SKU Lookup"),
    (SEARCH_METHOD_NAME, "Name Search"),
    (SEARCH_METHOD_COMBINED, "Combined Search"),
)

# ── Barcode Format Constants ─────────────────────────────────────────────
BARCODE_FORMAT_EAN13 = "ean13"
BARCODE_FORMAT_EAN8 = "ean8"
BARCODE_FORMAT_UPC_A = "upc_a"
BARCODE_FORMAT_CODE128 = "code128"
BARCODE_FORMAT_WEIGHT = "weight"

WEIGHT_BARCODE_PREFIX = "2"
WEIGHT_BARCODE_PRODUCT_DIGITS = 5
WEIGHT_BARCODE_WEIGHT_DIGITS = 5

# ── Payment Audit Event Constants ─────────────────────────────────────────
PAYMENT_EVENT_INITIATED = "payment_initiated"
PAYMENT_EVENT_COMPLETED = "payment_completed"
PAYMENT_EVENT_FAILED = "payment_failed"
PAYMENT_EVENT_VOIDED = "payment_voided"
PAYMENT_EVENT_REFUNDED = "payment_refunded"
PAYMENT_EVENT_CART_COMPLETED = "cart_completed"
PAYMENT_EVENT_CART_VOIDED = "cart_voided"

PAYMENT_EVENT_CHOICES = (
    (PAYMENT_EVENT_INITIATED, "Payment Initiated"),
    (PAYMENT_EVENT_COMPLETED, "Payment Completed"),
    (PAYMENT_EVENT_FAILED, "Payment Failed"),
    (PAYMENT_EVENT_VOIDED, "Payment Voided"),
    (PAYMENT_EVENT_REFUNDED, "Payment Refunded"),
    (PAYMENT_EVENT_CART_COMPLETED, "Cart Completed"),
    (PAYMENT_EVENT_CART_VOIDED, "Cart Voided"),
)
