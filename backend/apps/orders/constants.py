"""
Orders constants module.

Defines choices, status values, transition rules, and other constants
used across the orders application models.
"""

from django.db import models


# ════════════════════════════════════════════════════════════════════════
# Order Status Choices
# ════════════════════════════════════════════════════════════════════════


class OrderStatus(models.TextChoices):
    """
    Order lifecycle statuses.

    Lifecycle:
        PENDING → CONFIRMED → PROCESSING → PARTIALLY_FULFILLED → SHIPPED → DELIVERED → COMPLETED
        PENDING/CONFIRMED/PROCESSING → CANCELLED
        DELIVERED/COMPLETED → RETURNED
    """

    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PROCESSING = "processing", "Processing"
    PARTIALLY_FULFILLED = "partially_fulfilled", "Partially Fulfilled"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    RETURNED = "returned", "Returned"


class OrderSource(models.TextChoices):
    """Order origin/source channel."""

    POS = "pos", "Point of Sale"
    WEBSTORE = "webstore", "Webstore"
    QUOTE = "quote", "Quote Conversion"
    MANUAL = "manual", "Manual Entry"
    IMPORT = "import", "Import"


class PaymentStatus(models.TextChoices):
    """Order payment status."""

    UNPAID = "unpaid", "Unpaid"
    PARTIAL = "partial", "Partially Paid"
    PAID = "paid", "Paid"
    REFUNDED = "refunded", "Refunded"


class CurrencyChoice(models.TextChoices):
    """Supported currencies."""

    LKR = "LKR", "Sri Lankan Rupee (LKR)"
    USD = "USD", "US Dollar (USD)"


class DiscountType(models.TextChoices):
    """Discount type."""

    PERCENTAGE = "percentage", "Percentage"
    FIXED = "fixed", "Fixed Amount"


class OrderLineItemStatus(models.TextChoices):
    """Line item fulfillment status."""

    PENDING = "pending", "Pending"
    ALLOCATED = "allocated", "Allocated"
    PICKED = "picked", "Picked"
    PACKED = "packed", "Packed"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"
    RETURNED = "returned", "Returned"


class TaxStrategy(models.TextChoices):
    """Tax calculation strategy."""

    LINE_ITEM_TAX = "line_item", "Per Line Item"
    ORDER_LEVEL_TAX = "order_level", "Order Level"


# Sri Lanka tax rates
SRI_LANKA_VAT_RATE = 18
SRI_LANKA_REDUCED_RATE = 8
SRI_LANKA_ZERO_RATE = 0


# ════════════════════════════════════════════════════════════════════════
# Status Transitions
# ════════════════════════════════════════════════════════════════════════

ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
    OrderStatus.PROCESSING: [
        OrderStatus.PARTIALLY_FULFILLED,
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,
    ],
    OrderStatus.PARTIALLY_FULFILLED: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
    OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [OrderStatus.COMPLETED, OrderStatus.RETURNED],
    OrderStatus.COMPLETED: [OrderStatus.RETURNED],
    OrderStatus.CANCELLED: [],
    OrderStatus.RETURNED: [],
}

TERMINAL_STATES = {OrderStatus.CANCELLED, OrderStatus.RETURNED, OrderStatus.COMPLETED}
EDITABLE_STATES = {OrderStatus.PENDING, OrderStatus.CONFIRMED}
CANCELLABLE_STATES = {OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING}

CURRENCY_SYMBOLS = {
    CurrencyChoice.LKR: "₨",
    CurrencyChoice.USD: "$",
}

# Legacy aliases for backward compatibility
ORDER_STATUS_PENDING = OrderStatus.PENDING
ORDER_STATUS_CONFIRMED = OrderStatus.CONFIRMED
ORDER_STATUS_PROCESSING = OrderStatus.PROCESSING
ORDER_STATUS_SHIPPED = OrderStatus.SHIPPED
ORDER_STATUS_DELIVERED = OrderStatus.DELIVERED
ORDER_STATUS_CANCELLED = OrderStatus.CANCELLED
ORDER_STATUS_RETURNED = OrderStatus.RETURNED
ORDER_STATUS_CHOICES = OrderStatus.choices
DEFAULT_ORDER_STATUS = OrderStatus.PENDING


# ════════════════════════════════════════════════════════════════════════
# Lock Reasons (Task 46)
# ════════════════════════════════════════════════════════════════════════


class LockReason(models.TextChoices):
    """Reasons for locking an order."""

    FRAUD_REVIEW = "fraud_review", "Fraud Review"
    PAYMENT_PENDING = "payment_pending", "Payment Pending"
    CUSTOMER_REQUEST = "customer_request", "Customer Request"
    INVENTORY_ISSUE = "inventory_issue", "Inventory Issue"
    CUSTOM_WORK = "custom_work", "Custom Work"
    MANAGEMENT_REVIEW = "management_review", "Management Review"
