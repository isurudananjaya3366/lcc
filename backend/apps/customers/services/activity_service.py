"""
Customer activity feed service.

Provides a unified, paginated timeline of all customer interactions
including orders, payments, communications, and profile changes.
"""

from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

# Activity type constants
ACTIVITY_ORDER_PLACED = "ORDER_PLACED"
ACTIVITY_PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
ACTIVITY_COMMUNICATION_LOGGED = "COMMUNICATION_LOGGED"
ACTIVITY_PROFILE_UPDATED = "PROFILE_UPDATED"


class CustomerActivityService:
    """
    Unified activity feed for a customer.
    """

    @classmethod
    def get_activity_feed(
        cls,
        customer_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
        activity_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Return a paginated, chronologically-sorted activity feed.

        Aggregates from multiple sources: orders, payments,
        communications, and profile history.
        """
        activities: list[dict[str, Any]] = []

        types = set(activity_types) if activity_types else None

        if not types or ACTIVITY_ORDER_PLACED in types:
            activities.extend(cls._get_order_activities(customer_id))

        if not types or ACTIVITY_PAYMENT_RECEIVED in types:
            activities.extend(cls._get_payment_activities(customer_id))

        if not types or ACTIVITY_COMMUNICATION_LOGGED in types:
            activities.extend(cls._get_communication_activities(customer_id))

        if not types or ACTIVITY_PROFILE_UPDATED in types:
            activities.extend(cls._get_profile_activities(customer_id))

        # Sort newest-first
        activities.sort(key=lambda a: a["date"], reverse=True)

        total_count = len(activities)
        total_pages = max(1, math.ceil(total_count / page_size))
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "activities": activities[start:end],
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count,
        }

    # ── Private source collectors ───────────────────────────────────

    @classmethod
    def _get_order_activities(cls, customer_id: str) -> list[dict]:
        try:
            from apps.orders.models import Order

            orders = Order.objects.filter(customer_id=customer_id).values(
                "id", "order_number", "total_amount", "created_on",
            )
            return [
                {
                    "type": ACTIVITY_ORDER_PLACED,
                    "date": o["created_on"],
                    "description": (
                        f"Placed order #{o['order_number']} "
                        f"for LKR {o['total_amount']:,.2f}"
                    ),
                    "related_id": str(o["id"]),
                }
                for o in orders
            ]
        except Exception:
            logger.debug("Could not load order activities", exc_info=True)
            return []

    @classmethod
    def _get_payment_activities(cls, customer_id: str) -> list[dict]:
        try:
            from apps.payments.models import Payment

            payments = Payment.objects.filter(customer_id=customer_id).values(
                "id", "payment_number", "amount", "created_on",
            )
            return [
                {
                    "type": ACTIVITY_PAYMENT_RECEIVED,
                    "date": p["created_on"],
                    "description": (
                        f"Payment #{p['payment_number']} "
                        f"of LKR {p['amount']:,.2f}"
                    ),
                    "related_id": str(p["id"]),
                }
                for p in payments
            ]
        except Exception:
            logger.debug("Could not load payment activities", exc_info=True)
            return []

    @classmethod
    def _get_communication_activities(cls, customer_id: str) -> list[dict]:
        try:
            from apps.customers.models import CustomerCommunication

            comms = CustomerCommunication.objects.filter(
                customer_id=customer_id,
            ).values("id", "communication_type", "subject", "communication_date")
            return [
                {
                    "type": ACTIVITY_COMMUNICATION_LOGGED,
                    "date": c["communication_date"],
                    "description": (
                        f"{c['communication_type'].replace('_', ' ').title()}: "
                        f"{c['subject'] or '(no subject)'}"
                    ),
                    "related_id": str(c["id"]),
                }
                for c in comms
            ]
        except Exception:
            logger.debug("Could not load communication activities", exc_info=True)
            return []

    @classmethod
    def _get_profile_activities(cls, customer_id: str) -> list[dict]:
        try:
            from apps.customers.models import CustomerHistory

            changes = CustomerHistory.objects.filter(
                customer_id=customer_id,
            ).values("id", "change_type", "field_name", "changed_at")
            return [
                {
                    "type": ACTIVITY_PROFILE_UPDATED,
                    "date": h["changed_at"],
                    "description": (
                        f"{h['change_type'].replace('_', ' ').title()}: "
                        f"{h['field_name']}"
                    ),
                    "related_id": str(h["id"]),
                }
                for h in changes
            ]
        except Exception:
            logger.debug("Could not load profile activities", exc_info=True)
            return []
