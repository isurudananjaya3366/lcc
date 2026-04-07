"""
Customer Segment Service.

Dynamic segmentation engine that evaluates rule-based segments
against customers. Supports a rich operator set and AND/OR logic
for composing segment rules.

Rule format (stored as JSON on CustomerSegment.rules):
{
    "operator": "and",    # "and" | "or"
    "conditions": [
        {
            "field": "total_purchases",
            "operator": "gte",
            "value": 50000
        },
        {
            "field": "status",
            "operator": "eq",
            "value": "active"
        }
    ]
}
"""

import logging
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from django.db import models, transaction
from django.db.models import QuerySet

from apps.customers.models.customer_segment import CustomerSegment

logger = logging.getLogger(__name__)

# Operators that can be applied in Python on resolved values
OPERATORS = {
    "eq": lambda a, b: a == b,
    "neq": lambda a, b: a != b,
    "gt": lambda a, b: _to_num(a) > _to_num(b),
    "gte": lambda a, b: _to_num(a) >= _to_num(b),
    "lt": lambda a, b: _to_num(a) < _to_num(b),
    "lte": lambda a, b: _to_num(a) <= _to_num(b),
    "contains": lambda a, b: str(b).lower() in str(a).lower() if a else False,
    "in": lambda a, b: a in (b if isinstance(b, (list, tuple, set)) else [b]),
    "not_in": lambda a, b: a not in (b if isinstance(b, (list, tuple, set)) else [b]),
    "is_null": lambda a, b: a is None,
    "is_not_null": lambda a, b: a is not None,
}


def _to_num(val) -> Decimal:
    """Safely cast to Decimal for comparison operators."""
    if isinstance(val, Decimal):
        return val
    try:
        return Decimal(str(val))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(0)


class CustomerSegmentService:
    """Service for segment evaluation and management."""

    # ── Single-Customer Evaluation ───────────────────────────────────

    @classmethod
    def evaluate_customer(cls, customer, segment: CustomerSegment) -> bool:
        """
        Check whether *customer* satisfies *segment*.rules.

        Returns True if all/any conditions match (depending on
        the top-level operator).
        """
        rules = segment.rules
        if not rules or "conditions" not in rules:
            return False

        logic = rules.get("operator", "and").lower()
        conditions = rules["conditions"]
        if not conditions:
            return False

        results = [
            cls._evaluate_condition(customer, cond) for cond in conditions
        ]

        if logic == "or":
            return any(results)
        return all(results)  # default AND

    @classmethod
    def _evaluate_condition(cls, customer, condition: dict) -> bool:
        """Evaluate a single condition dict against a customer."""
        field = condition.get("field", "")
        op_name = condition.get("operator", "eq")
        expected = condition.get("value")

        op_fn = OPERATORS.get(op_name)
        if op_fn is None:
            logger.warning("Unknown segment operator: %s", op_name)
            return False

        actual = cls._resolve_field(customer, field)
        try:
            return op_fn(actual, expected)
        except Exception:
            logger.debug(
                "Condition evaluation failed for field=%s op=%s",
                field,
                op_name,
                exc_info=True,
            )
            return False

    @staticmethod
    def _resolve_field(customer, field_name: str) -> Any:
        """
        Resolve a dotted or simple field name on the customer instance.
        E.g. 'status', 'total_purchases', 'customer_type'.
        """
        obj = customer
        for part in field_name.split("."):
            try:
                obj = getattr(obj, part)
            except AttributeError:
                return None
        # If the final result is callable (e.g. a property getter),
        # leave it as-is — properties are already resolved by getattr.
        return obj

    # ── QuerySet-Based Evaluation ────────────────────────────────────

    @classmethod
    def get_segment_customers(cls, segment: CustomerSegment) -> QuerySet:
        """
        Return a queryset of customers matching **segment**
        by building ORM filters where possible.
        Falls back to in-memory evaluation for complex operators.
        """
        from apps.customers.models import Customer

        qs = Customer.objects.filter(is_deleted=False)
        rules = segment.rules
        if not rules or "conditions" not in rules:
            return qs.none()

        conditions = rules.get("conditions", [])
        logic = rules.get("operator", "and").lower()

        q_objects = []
        for cond in conditions:
            q = cls._condition_to_q(cond)
            if q is not None:
                q_objects.append(q)

        if not q_objects:
            return qs.none()

        combined = q_objects[0]
        for q in q_objects[1:]:
            if logic == "or":
                combined |= q
            else:
                combined &= q

        return qs.filter(combined)

    @classmethod
    def _condition_to_q(cls, condition: dict) -> Optional[models.Q]:
        """Convert a condition dict to a Django Q object."""
        field = condition.get("field", "")
        op = condition.get("operator", "eq")
        value = condition.get("value")

        lookup_map = {
            "eq": "",
            "neq": "",
            "gt": "__gt",
            "gte": "__gte",
            "lt": "__lt",
            "lte": "__lte",
            "contains": "__icontains",
            "in": "__in",
            "not_in": "__in",
            "is_null": "__isnull",
            "is_not_null": "__isnull",
        }
        suffix = lookup_map.get(op)
        if suffix is None:
            return None

        lookup = f"{field}{suffix}"

        if op == "neq":
            return ~models.Q(**{field: value})
        if op == "not_in":
            return ~models.Q(**{lookup: value})
        if op == "is_null":
            return models.Q(**{lookup: True})
        if op == "is_not_null":
            return models.Q(**{lookup: False})

        return models.Q(**{lookup: value})

    # ── Batch Operations ─────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def evaluate_all_segments(cls) -> dict:
        """
        Re-evaluate all active segments and update customer_count.
        Returns a dict mapping segment_id → count.
        """
        results = {}
        for segment in CustomerSegment.objects.filter(is_active=True):
            count = cls.get_segment_customers(segment).count()
            if segment.customer_count != count:
                segment.customer_count = count
                segment.save(update_fields=["customer_count"])
            results[str(segment.pk)] = count
        return results

    @classmethod
    def refresh_segment_counts(cls) -> None:
        """Alias for evaluate_all_segments (void return)."""
        cls.evaluate_all_segments()

    @classmethod
    def auto_assign_segments(cls) -> dict:
        """
        For segments with auto_assign=True, evaluate every active
        customer and return a mapping of segment_id → matched IDs.
        (Hook for future M2M or tagging integration.)
        """
        results = {}
        for segment in CustomerSegment.objects.filter(
            is_active=True,
            auto_assign=True,
        ):
            customer_ids = list(
                cls.get_segment_customers(segment).values_list("id", flat=True)
            )
            results[str(segment.pk)] = customer_ids
            if segment.customer_count != len(customer_ids):
                segment.customer_count = len(customer_ids)
                segment.save(update_fields=["customer_count"])
        return results
