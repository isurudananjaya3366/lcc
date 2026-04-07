"""
Sales constants module.

Defines choices, status values, and other constants used across
the sales application models (invoices, payments, POS).
"""

# ════════════════════════════════════════════════════════════════════════
# Invoice Status Choices
# ════════════════════════════════════════════════════════════════════════

INVOICE_STATUS_DRAFT = "draft"
INVOICE_STATUS_SENT = "sent"
INVOICE_STATUS_PAID = "paid"
INVOICE_STATUS_OVERDUE = "overdue"
INVOICE_STATUS_CANCELLED = "cancelled"
INVOICE_STATUS_PARTIALLY_PAID = "partially_paid"

INVOICE_STATUS_CHOICES = [
    (INVOICE_STATUS_DRAFT, "Draft"),
    (INVOICE_STATUS_SENT, "Sent"),
    (INVOICE_STATUS_PARTIALLY_PAID, "Partially Paid"),
    (INVOICE_STATUS_PAID, "Paid"),
    (INVOICE_STATUS_OVERDUE, "Overdue"),
    (INVOICE_STATUS_CANCELLED, "Cancelled"),
]

# Default invoice status for new invoices
DEFAULT_INVOICE_STATUS = INVOICE_STATUS_DRAFT


# ════════════════════════════════════════════════════════════════════════
# Payment Method Choices
# ════════════════════════════════════════════════════════════════════════

PAYMENT_METHOD_CASH = "cash"
PAYMENT_METHOD_CARD = "card"
PAYMENT_METHOD_BANK_TRANSFER = "bank_transfer"
PAYMENT_METHOD_CHEQUE = "cheque"
PAYMENT_METHOD_MOBILE = "mobile"

PAYMENT_METHOD_CHOICES = [
    (PAYMENT_METHOD_CASH, "Cash"),
    (PAYMENT_METHOD_CARD, "Credit/Debit Card"),
    (PAYMENT_METHOD_BANK_TRANSFER, "Bank Transfer"),
    (PAYMENT_METHOD_CHEQUE, "Cheque"),
    (PAYMENT_METHOD_MOBILE, "Mobile Payment"),
]

# Default payment method
DEFAULT_PAYMENT_METHOD = PAYMENT_METHOD_CASH
