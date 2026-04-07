"""
Customer history service.

Records audit-trail entries whenever customer fields are created
or changed. Used by CustomerService to log changes automatically.
"""

from __future__ import annotations

import logging
from typing import Any

from apps.customers.models.customer_history import (
    CHANGE_TYPE_CREATE,
    CHANGE_TYPE_STATUS_CHANGE,
    CHANGE_TYPE_UPDATE,
)

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Creates CustomerHistory records for customer changes.
    """

    # Fields that should not be tracked in history
    EXCLUDED_FIELDS = {
        "id",
        "created_on",
        "updated_on",
        "is_deleted",
        "deleted_on",
        "search_vector",
    }

    @classmethod
    def log_creation(cls, customer, *, user=None) -> None:
        """
        Log the creation of a new customer.

        Creates a single history entry with change_type=CREATE and
        the initial values for key fields.
        """
        from apps.customers.models.customer_history import CustomerHistory

        CustomerHistory.objects.create(
            customer=customer,
            changed_by=user,
            field_name="__all__",
            old_value="",
            new_value=f"Customer created: {customer.display_name or customer.customer_code}",
            change_type=CHANGE_TYPE_CREATE,
        )

    @classmethod
    def log_change(
        cls,
        customer,
        field_name: str,
        old_value: Any,
        new_value: Any,
        *,
        user=None,
        change_type: str = CHANGE_TYPE_UPDATE,
    ) -> None:
        """
        Log a single field change on a customer.
        """
        from apps.customers.models.customer_history import CustomerHistory

        CustomerHistory.objects.create(
            customer=customer,
            changed_by=user,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else "",
            new_value=str(new_value) if new_value is not None else "",
            change_type=change_type,
        )

    @classmethod
    def log_changes(
        cls,
        customer,
        old_values: dict[str, Any],
        new_values: dict[str, Any],
        *,
        user=None,
    ) -> int:
        """
        Compare old and new field values and log any differences.

        Returns the number of changes logged.
        """
        count = 0
        for field_name, new_val in new_values.items():
            if field_name in cls.EXCLUDED_FIELDS:
                continue
            old_val = old_values.get(field_name)
            if str(old_val) != str(new_val):
                change_type = (
                    CHANGE_TYPE_STATUS_CHANGE
                    if field_name == "status"
                    else CHANGE_TYPE_UPDATE
                )
                cls.log_change(
                    customer,
                    field_name,
                    old_val,
                    new_val,
                    user=user,
                    change_type=change_type,
                )
                count += 1
        return count
