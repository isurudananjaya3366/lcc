"""
Purchases constants module.

Defines choices, status values, and other constants used across
the purchases application models.
"""

# ════════════════════════════════════════════════════════════════════════
# Purchase Order Status
# ════════════════════════════════════════════════════════════════════════

PO_STATUS_DRAFT = "draft"
PO_STATUS_PENDING_APPROVAL = "pending_approval"
PO_STATUS_SENT = "sent"
PO_STATUS_ACKNOWLEDGED = "acknowledged"
PO_STATUS_PARTIAL_RECEIVED = "partial_received"
PO_STATUS_RECEIVED = "received"
PO_STATUS_CANCELLED = "cancelled"
PO_STATUS_CLOSED = "closed"

PO_STATUS_CHOICES = [
    (PO_STATUS_DRAFT, "Draft"),
    (PO_STATUS_PENDING_APPROVAL, "Pending Approval"),
    (PO_STATUS_SENT, "Sent to Vendor"),
    (PO_STATUS_ACKNOWLEDGED, "Acknowledged"),
    (PO_STATUS_PARTIAL_RECEIVED, "Partially Received"),
    (PO_STATUS_RECEIVED, "Received"),
    (PO_STATUS_CANCELLED, "Cancelled"),
    (PO_STATUS_CLOSED, "Closed"),
]

DEFAULT_PO_STATUS = PO_STATUS_DRAFT

# Valid status transitions
PO_STATUS_TRANSITIONS = {
    PO_STATUS_DRAFT: [PO_STATUS_SENT, PO_STATUS_PENDING_APPROVAL, PO_STATUS_CANCELLED],
    PO_STATUS_PENDING_APPROVAL: [PO_STATUS_SENT, PO_STATUS_DRAFT, PO_STATUS_CANCELLED],
    PO_STATUS_SENT: [PO_STATUS_ACKNOWLEDGED, PO_STATUS_CANCELLED],
    PO_STATUS_ACKNOWLEDGED: [
        PO_STATUS_PARTIAL_RECEIVED,
        PO_STATUS_RECEIVED,
        PO_STATUS_CANCELLED,
    ],
    PO_STATUS_PARTIAL_RECEIVED: [PO_STATUS_RECEIVED, PO_STATUS_CLOSED],
    PO_STATUS_RECEIVED: [PO_STATUS_CLOSED],
    PO_STATUS_CANCELLED: [],
    PO_STATUS_CLOSED: [],
}

# ════════════════════════════════════════════════════════════════════════
# Payment Status
# ════════════════════════════════════════════════════════════════════════

PAYMENT_STATUS_UNPAID = "unpaid"
PAYMENT_STATUS_PARTIAL = "partial"
PAYMENT_STATUS_PAID = "paid"

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_STATUS_UNPAID, "Unpaid"),
    (PAYMENT_STATUS_PARTIAL, "Partially Paid"),
    (PAYMENT_STATUS_PAID, "Paid"),
]

DEFAULT_PAYMENT_STATUS = PAYMENT_STATUS_UNPAID

# ════════════════════════════════════════════════════════════════════════
# PO Line Item Status
# ════════════════════════════════════════════════════════════════════════

LINE_STATUS_PENDING = "pending"
LINE_STATUS_PARTIAL = "partial"
LINE_STATUS_RECEIVED = "received"
LINE_STATUS_CANCELLED = "cancelled"

LINE_STATUS_CHOICES = [
    (LINE_STATUS_PENDING, "Pending"),
    (LINE_STATUS_PARTIAL, "Partially Received"),
    (LINE_STATUS_RECEIVED, "Received"),
    (LINE_STATUS_CANCELLED, "Cancelled"),
]

DEFAULT_LINE_STATUS = LINE_STATUS_PENDING

# ════════════════════════════════════════════════════════════════════════
# GRN Inspection Status
# ════════════════════════════════════════════════════════════════════════

INSPECTION_PENDING = "pending"
INSPECTION_PASSED = "passed"
INSPECTION_FAILED = "failed"
INSPECTION_PARTIAL = "partial"

INSPECTION_STATUS_CHOICES = [
    (INSPECTION_PENDING, "Pending Inspection"),
    (INSPECTION_PASSED, "Passed"),
    (INSPECTION_FAILED, "Failed"),
    (INSPECTION_PARTIAL, "Partial Pass"),
]

DEFAULT_INSPECTION_STATUS = INSPECTION_PENDING

# ════════════════════════════════════════════════════════════════════════
# GRN Item Condition
# ════════════════════════════════════════════════════════════════════════

CONDITION_GOOD = "good"
CONDITION_DAMAGED = "damaged"
CONDITION_DEFECTIVE = "defective"

CONDITION_CHOICES = [
    (CONDITION_GOOD, "Good"),
    (CONDITION_DAMAGED, "Damaged"),
    (CONDITION_DEFECTIVE, "Defective"),
]

DEFAULT_CONDITION = CONDITION_GOOD

# ════════════════════════════════════════════════════════════════════════
# PO History Change Types
# ════════════════════════════════════════════════════════════════════════

CHANGE_TYPE_CREATED = "created"
CHANGE_TYPE_UPDATED = "updated"
CHANGE_TYPE_STATUS_CHANGED = "status_changed"
CHANGE_TYPE_APPROVED = "approved"
CHANGE_TYPE_REJECTED = "rejected"
CHANGE_TYPE_SENT = "sent"
CHANGE_TYPE_RECEIVED = "received"
CHANGE_TYPE_CANCELLED = "cancelled"
CHANGE_TYPE_LINE_ADDED = "line_added"
CHANGE_TYPE_LINE_UPDATED = "line_updated"
CHANGE_TYPE_LINE_REMOVED = "line_removed"
CHANGE_TYPE_CLOSED = "closed"

CHANGE_TYPE_CHOICES = [
    (CHANGE_TYPE_CREATED, "Created"),
    (CHANGE_TYPE_UPDATED, "Updated"),
    (CHANGE_TYPE_STATUS_CHANGED, "Status Changed"),
    (CHANGE_TYPE_APPROVED, "Approved"),
    (CHANGE_TYPE_REJECTED, "Rejected"),
    (CHANGE_TYPE_SENT, "Sent"),
    (CHANGE_TYPE_RECEIVED, "Received"),
    (CHANGE_TYPE_CANCELLED, "Cancelled"),
    (CHANGE_TYPE_LINE_ADDED, "Line Added"),
    (CHANGE_TYPE_LINE_UPDATED, "Line Updated"),
    (CHANGE_TYPE_LINE_REMOVED, "Line Removed"),
    (CHANGE_TYPE_CLOSED, "Closed"),
]

# ════════════════════════════════════════════════════════════════════════
# GRN Status
# ════════════════════════════════════════════════════════════════════════

GRN_STATUS_PENDING = "pending"
GRN_STATUS_COMPLETED = "completed"
GRN_STATUS_CANCELLED = "cancelled"

GRN_STATUS_CHOICES = [
    (GRN_STATUS_PENDING, "Pending"),
    (GRN_STATUS_COMPLETED, "Completed"),
    (GRN_STATUS_CANCELLED, "Cancelled"),
]

DEFAULT_GRN_STATUS = GRN_STATUS_PENDING

# ════════════════════════════════════════════════════════════════════════
# PO Urgency Levels (for low-stock auto-PO creation)
# ════════════════════════════════════════════════════════════════════════

URGENCY_CRITICAL = "critical"
URGENCY_HIGH = "high"
URGENCY_MEDIUM = "medium"

URGENCY_CHOICES = [
    (URGENCY_CRITICAL, "Critical"),
    (URGENCY_HIGH, "High"),
    (URGENCY_MEDIUM, "Medium"),
]
