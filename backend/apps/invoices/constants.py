"""
Invoices constants module.

Defines choices, status values, transition rules, and other constants
used across the invoices application models.
"""

from django.db import models


class InvoiceType(models.TextChoices):
    """Invoice document types."""
    STANDARD = "STANDARD", "Standard Invoice"
    SVAT = "SVAT", "Simplified VAT Invoice"
    CREDIT_NOTE = "CREDIT_NOTE", "Credit Note"
    DEBIT_NOTE = "DEBIT_NOTE", "Debit Note"


class InvoiceStatus(models.TextChoices):
    """
    Invoice lifecycle statuses.

    Lifecycle:
        DRAFT → ISSUED → SENT → PAID (terminal)
        DRAFT → CANCELLED (terminal)
        ISSUED/SENT → VOID (terminal)
        ISSUED/SENT → PARTIAL → PAID/OVERDUE
    """
    DRAFT = "DRAFT", "Draft"
    ISSUED = "ISSUED", "Issued"
    SENT = "SENT", "Sent"
    PAID = "PAID", "Paid"
    PARTIAL = "PARTIAL", "Partially Paid"
    OVERDUE = "OVERDUE", "Overdue"
    CANCELLED = "CANCELLED", "Cancelled"
    VOID = "VOID", "Void"


class TaxScheme(models.TextChoices):
    """Tax scheme for the invoice."""
    VAT = "VAT", "Value Added Tax"
    SVAT = "SVAT", "Simplified VAT"
    EXEMPT = "EXEMPT", "Tax Exempt"
    NONE = "NONE", "No Tax"


class DiscountType(models.TextChoices):
    """Discount type."""
    PERCENTAGE = "percentage", "Percentage"
    FIXED = "fixed", "Fixed Amount"


class CurrencyChoice(models.TextChoices):
    """Supported currencies."""
    LKR = "LKR", "Sri Lankan Rupee (LKR)"
    USD = "USD", "US Dollar (USD)"


class CreditNoteReason(models.TextChoices):
    """Reasons for credit notes."""
    RETURN = "RETURN", "Goods Return"
    OVERCHARGE = "OVERCHARGE", "Overcharge Correction"
    DISCOUNT = "DISCOUNT", "Post-Sale Discount"
    DAMAGED = "DAMAGED", "Damaged Goods"
    GOODWILL = "GOODWILL", "Goodwill Gesture"
    ERROR = "ERROR", "Invoicing Error"
    PARTIAL_REFUND = "PARTIAL_REFUND", "Partial Refund"
    CANCELLED_ORDER = "CANCELLED_ORDER", "Order Cancelled"
    OTHER = "OTHER", "Other"


class DebitNoteReason(models.TextChoices):
    """Reasons for debit notes."""
    UNDERCHARGE = "UNDERCHARGE", "Undercharge Correction"
    ADDITIONAL_CHARGE = "ADDITIONAL_CHARGE", "Additional Charge"
    INTEREST = "INTEREST", "Interest on Late Payment"
    SHIPPING = "SHIPPING", "Additional Shipping Charges"
    ADJUSTMENT = "ADJUSTMENT", "Price Adjustment"
    PENALTY = "PENALTY", "Penalty Charge"
    HANDLING = "HANDLING", "Additional Handling Fees"
    SERVICES = "SERVICES", "Additional Services"
    OTHER = "OTHER", "Other"


# Status transition rules
ALLOWED_TRANSITIONS = {
    InvoiceStatus.DRAFT: [InvoiceStatus.ISSUED, InvoiceStatus.CANCELLED],
    InvoiceStatus.ISSUED: [InvoiceStatus.SENT, InvoiceStatus.PAID, InvoiceStatus.PARTIAL, InvoiceStatus.VOID],
    InvoiceStatus.SENT: [InvoiceStatus.PAID, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE, InvoiceStatus.VOID],
    InvoiceStatus.PAID: [],
    InvoiceStatus.PARTIAL: [InvoiceStatus.PAID, InvoiceStatus.OVERDUE, InvoiceStatus.VOID],
    InvoiceStatus.OVERDUE: [InvoiceStatus.PAID, InvoiceStatus.PARTIAL, InvoiceStatus.VOID],
    InvoiceStatus.CANCELLED: [],
    InvoiceStatus.VOID: [],
}

TERMINAL_STATES = {InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.VOID}
EDITABLE_STATES = {InvoiceStatus.DRAFT}

# Sri Lanka tax rates
SRI_LANKA_VAT_RATE = 12
SRI_LANKA_SVAT_RATE = 0
SRI_LANKA_ZERO_RATE = 0

CURRENCY_SYMBOLS = {
    CurrencyChoice.LKR: "₨",
    CurrencyChoice.USD: "$",
}

# Invoice number prefixes per type
INVOICE_NUMBER_PREFIX = {
    InvoiceType.STANDARD: "INV",
    InvoiceType.SVAT: "SVAT",
    InvoiceType.CREDIT_NOTE: "CN",
    InvoiceType.DEBIT_NOTE: "DN",
}
