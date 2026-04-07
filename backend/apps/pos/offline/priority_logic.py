"""
Sync Priority Logic.

Functions for determining sync priority of offline transactions and
data entities, ordering the sync queue, applying priority boosts, and
creating batched sync groups.
"""

from decimal import Decimal

from django.utils import timezone

# ── Priority Level Constants ──────────────────────────────────────────────
PRIORITY_CRITICAL = 10
PRIORITY_HIGH = 8
PRIORITY_NORMAL = 5
PRIORITY_LOW = 3
PRIORITY_DEFERRED = 1

# LKR threshold for high-value transactions
HIGH_VALUE_THRESHOLD = Decimal("100000.00")

# ── Entity Priority Mapping ──────────────────────────────────────────────
ENTITY_PRIORITY_MAP = {
    "tax_rate": PRIORITY_CRITICAL,
    "pos_setting": PRIORITY_CRITICAL,
    "payment_method": PRIORITY_HIGH,
    "product_price": PRIORITY_HIGH,
    "product": PRIORITY_HIGH,
    "product_variant": PRIORITY_HIGH,
    "discount_rule": PRIORITY_HIGH,
    "customer": PRIORITY_NORMAL,
    "employee": PRIORITY_NORMAL,
    "terminal": PRIORITY_NORMAL,
    "category": PRIORITY_NORMAL,
    "quick_button": PRIORITY_NORMAL,
    "warehouse": PRIORITY_LOW,
    "unit_of_measure": PRIORITY_LOW,
    "historical_data": PRIORITY_LOW,
    "product_image": PRIORITY_DEFERRED,
}


def get_transaction_priority(transaction):
    """
    Calculate the sync priority (1-10) for an offline transaction.

    Rules (highest applicable wins):
    - grand_total > 100 000 LKR → CRITICAL
    - Standard sale / refund     → HIGH
    - void                       → NORMAL
    - adjustment / draft         → LOW
    """
    from apps.pos.offline.constants import (
        TRANSACTION_TYPE_ADJUSTMENT,
        TRANSACTION_TYPE_EXCHANGE,
        TRANSACTION_TYPE_REFUND,
        TRANSACTION_TYPE_SALE,
        TRANSACTION_TYPE_VOID,
    )

    if transaction.grand_total > HIGH_VALUE_THRESHOLD:
        return PRIORITY_CRITICAL

    type_map = {
        TRANSACTION_TYPE_SALE: PRIORITY_HIGH,
        TRANSACTION_TYPE_REFUND: PRIORITY_HIGH,
        TRANSACTION_TYPE_EXCHANGE: PRIORITY_HIGH,
        TRANSACTION_TYPE_VOID: PRIORITY_NORMAL,
        TRANSACTION_TYPE_ADJUSTMENT: PRIORITY_LOW,
    }
    return type_map.get(transaction.transaction_type, PRIORITY_NORMAL)


def get_entity_sync_priority(entity_type):
    """Return the sync priority for the given entity type string."""
    return ENTITY_PRIORITY_MAP.get(entity_type, PRIORITY_NORMAL)


def boost_priority_if_needed(transaction):
    """
    Apply priority boosts based on age and retry count.

    Returns the adjusted priority (capped at 10).
    """
    priority = transaction.sync_priority
    now = timezone.now()

    # Age-based boost
    if transaction.offline_timestamp:
        age_hours = (now - transaction.offline_timestamp).total_seconds() / 3600
        if age_hours > 72:
            priority += 3
        elif age_hours > 24:
            priority += 2

    # Retry-based boost
    if transaction.retry_count >= 5:
        priority += 2
    elif transaction.retry_count >= 3:
        priority += 1

    # Refund boost (customer satisfaction)
    from apps.pos.offline.constants import TRANSACTION_TYPE_REFUND

    if transaction.transaction_type == TRANSACTION_TYPE_REFUND:
        priority += 1

    return min(priority, PRIORITY_CRITICAL)


def order_sync_queue(transactions):
    """
    Sort transactions for optimal sync order.

    Primary sort: descending priority (highest first).
    Secondary sort: ascending offline_timestamp (FIFO within same priority).

    Returns a new sorted list.
    """
    return sorted(
        transactions,
        key=lambda t: (-t.sync_priority, t.offline_timestamp),
    )


def create_priority_batches(transactions, batch_size=50):
    """
    Group transactions into priority-labelled batches.

    Returns a list of dicts::

        [
            {"priority": 10, "label": "CRITICAL", "transactions": [...]},
            {"priority": 8,  "label": "HIGH",     "transactions": [...]},
            ...
        ]

    Within each priority level the transactions are chunked into
    sub-lists of at most *batch_size* items.
    """
    LABEL_MAP = {
        PRIORITY_CRITICAL: "CRITICAL",
        PRIORITY_HIGH: "HIGH",
        PRIORITY_NORMAL: "NORMAL",
        PRIORITY_LOW: "LOW",
        PRIORITY_DEFERRED: "DEFERRED",
    }

    # Group by priority
    groups = {}
    for txn in transactions:
        prio = txn.sync_priority
        groups.setdefault(prio, []).append(txn)

    batches = []
    for prio in sorted(groups.keys(), reverse=True):
        txns = sorted(groups[prio], key=lambda t: t.offline_timestamp)
        label = LABEL_MAP.get(prio, f"PRIORITY_{prio}")
        for i in range(0, len(txns), batch_size):
            batches.append({
                "priority": prio,
                "label": label,
                "transactions": txns[i : i + batch_size],
            })

    return batches
