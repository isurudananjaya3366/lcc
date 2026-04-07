"""Constants for the Vendor Bills application."""

from decimal import Decimal

# =============================================================================
# Bill Status Constants
# =============================================================================

BILL_STATUS_DRAFT = "draft"
BILL_STATUS_PENDING = "pending"
BILL_STATUS_APPROVED = "approved"
BILL_STATUS_PARTIAL_PAID = "partial_paid"
BILL_STATUS_PAID = "paid"
BILL_STATUS_CANCELLED = "cancelled"
BILL_STATUS_DISPUTED = "disputed"

BILL_STATUS_CHOICES = [
    (BILL_STATUS_DRAFT, "Draft"),
    (BILL_STATUS_PENDING, "Pending"),
    (BILL_STATUS_APPROVED, "Approved"),
    (BILL_STATUS_PARTIAL_PAID, "Partially Paid"),
    (BILL_STATUS_PAID, "Paid"),
    (BILL_STATUS_CANCELLED, "Cancelled"),
    (BILL_STATUS_DISPUTED, "Disputed"),
]

BILL_STATUS_TRANSITIONS = {
    BILL_STATUS_DRAFT: [BILL_STATUS_PENDING, BILL_STATUS_CANCELLED],
    BILL_STATUS_PENDING: [BILL_STATUS_APPROVED, BILL_STATUS_DISPUTED, BILL_STATUS_CANCELLED],
    BILL_STATUS_APPROVED: [BILL_STATUS_PARTIAL_PAID, BILL_STATUS_PAID, BILL_STATUS_DISPUTED, BILL_STATUS_CANCELLED],
    BILL_STATUS_PARTIAL_PAID: [BILL_STATUS_PAID, BILL_STATUS_DISPUTED],
    BILL_STATUS_PAID: [],
    BILL_STATUS_CANCELLED: [],
    BILL_STATUS_DISPUTED: [BILL_STATUS_PENDING, BILL_STATUS_CANCELLED],
}

DEFAULT_BILL_STATUS = BILL_STATUS_DRAFT

# =============================================================================
# Payment Terms Constants
# =============================================================================

PAYMENT_TERMS_CIA = "cia"
PAYMENT_TERMS_COD = "cod"
PAYMENT_TERMS_NET15 = "net15"
PAYMENT_TERMS_NET30 = "net30"
PAYMENT_TERMS_NET45 = "net45"
PAYMENT_TERMS_NET60 = "net60"
PAYMENT_TERMS_NET90 = "net90"
PAYMENT_TERMS_CUSTOM = "custom"

PAYMENT_TERMS_CHOICES = [
    (PAYMENT_TERMS_CIA, "Cash in Advance"),
    (PAYMENT_TERMS_COD, "Cash on Delivery"),
    (PAYMENT_TERMS_NET15, "Net 15 Days"),
    (PAYMENT_TERMS_NET30, "Net 30 Days"),
    (PAYMENT_TERMS_NET45, "Net 45 Days"),
    (PAYMENT_TERMS_NET60, "Net 60 Days"),
    (PAYMENT_TERMS_NET90, "Net 90 Days"),
    (PAYMENT_TERMS_CUSTOM, "Custom"),
]

PAYMENT_TERMS_DAYS = {
    PAYMENT_TERMS_CIA: 0,
    PAYMENT_TERMS_COD: 0,
    PAYMENT_TERMS_NET15: 15,
    PAYMENT_TERMS_NET30: 30,
    PAYMENT_TERMS_NET45: 45,
    PAYMENT_TERMS_NET60: 60,
    PAYMENT_TERMS_NET90: 90,
}

# =============================================================================
# Matching Status Constants
# =============================================================================

MATCHING_STATUS_NOT_MATCHED = "not_matched"
MATCHING_STATUS_MATCHED = "matched"
MATCHING_STATUS_VARIANCE_WITHIN = "variance_within_tolerance"
MATCHING_STATUS_VARIANCE_EXCEEDS = "variance_exceeds_tolerance"

MATCHING_STATUS_CHOICES = [
    (MATCHING_STATUS_NOT_MATCHED, "Not Matched"),
    (MATCHING_STATUS_MATCHED, "Matched"),
    (MATCHING_STATUS_VARIANCE_WITHIN, "Variance Within Tolerance"),
    (MATCHING_STATUS_VARIANCE_EXCEEDS, "Variance Exceeds Tolerance"),
]

# =============================================================================
# Payment Method Constants
# =============================================================================

PAYMENT_METHOD_BANK_TRANSFER = "bank_transfer"
PAYMENT_METHOD_CHECK = "check"
PAYMENT_METHOD_CASH = "cash"
PAYMENT_METHOD_ONLINE = "online"

PAYMENT_METHOD_CHOICES = [
    (PAYMENT_METHOD_BANK_TRANSFER, "Bank Transfer"),
    (PAYMENT_METHOD_CHECK, "Check"),
    (PAYMENT_METHOD_CASH, "Cash"),
    (PAYMENT_METHOD_ONLINE, "Online Payment"),
]

# =============================================================================
# Payment Status Constants
# =============================================================================

VENDOR_PAYMENT_STATUS_PENDING = "pending"
VENDOR_PAYMENT_STATUS_COMPLETED = "completed"
VENDOR_PAYMENT_STATUS_FAILED = "failed"
VENDOR_PAYMENT_STATUS_REVERSED = "reversed"

VENDOR_PAYMENT_STATUS_CHOICES = [
    (VENDOR_PAYMENT_STATUS_PENDING, "Pending"),
    (VENDOR_PAYMENT_STATUS_COMPLETED, "Completed"),
    (VENDOR_PAYMENT_STATUS_FAILED, "Failed"),
    (VENDOR_PAYMENT_STATUS_REVERSED, "Reversed"),
]

# =============================================================================
# Bill Change Type Constants
# =============================================================================

CHANGE_TYPE_CREATED = "created"
CHANGE_TYPE_UPDATED = "updated"
CHANGE_TYPE_STATUS_CHANGED = "status_changed"
CHANGE_TYPE_SUBMITTED = "submitted"
CHANGE_TYPE_APPROVED = "approved"
CHANGE_TYPE_DISPUTED = "disputed"
CHANGE_TYPE_CANCELLED = "cancelled"
CHANGE_TYPE_PAYMENT_RECORDED = "payment_recorded"
CHANGE_TYPE_MATCHED = "matched"
CHANGE_TYPE_LINE_ADDED = "line_added"
CHANGE_TYPE_LINE_UPDATED = "line_updated"
CHANGE_TYPE_LINE_REMOVED = "line_removed"

CHANGE_TYPE_CHOICES = [
    (CHANGE_TYPE_CREATED, "Created"),
    (CHANGE_TYPE_UPDATED, "Updated"),
    (CHANGE_TYPE_STATUS_CHANGED, "Status Changed"),
    (CHANGE_TYPE_SUBMITTED, "Submitted"),
    (CHANGE_TYPE_APPROVED, "Approved"),
    (CHANGE_TYPE_DISPUTED, "Disputed"),
    (CHANGE_TYPE_CANCELLED, "Cancelled"),
    (CHANGE_TYPE_PAYMENT_RECORDED, "Payment Recorded"),
    (CHANGE_TYPE_MATCHED, "Matched"),
    (CHANGE_TYPE_LINE_ADDED, "Line Added"),
    (CHANGE_TYPE_LINE_UPDATED, "Line Updated"),
    (CHANGE_TYPE_LINE_REMOVED, "Line Removed"),
]

# =============================================================================
# Schedule Status Constants
# =============================================================================

SCHEDULE_STATUS_SCHEDULED = "scheduled"
SCHEDULE_STATUS_PAID = "paid"
SCHEDULE_STATUS_OVERDUE = "overdue"
SCHEDULE_STATUS_CANCELLED = "cancelled"

SCHEDULE_STATUS_CHOICES = [
    (SCHEDULE_STATUS_SCHEDULED, "Scheduled"),
    (SCHEDULE_STATUS_PAID, "Paid"),
    (SCHEDULE_STATUS_OVERDUE, "Overdue"),
    (SCHEDULE_STATUS_CANCELLED, "Cancelled"),
]

# =============================================================================
# Aging Bucket Constants
# =============================================================================

AGING_CURRENT = "current"
AGING_1_30 = "1-30"
AGING_31_60 = "31-60"
AGING_61_90 = "61-90"
AGING_OVER_90 = "over_90"

# =============================================================================
# Default Values
# =============================================================================

DEFAULT_CURRENCY = "LKR"
DEFAULT_MATCHING_TOLERANCE = Decimal("0.01")
DEFAULT_MATCHING_TOLERANCE_PERCENT = Decimal("1.00")
