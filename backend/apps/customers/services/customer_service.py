"""
Customer service.

Contains the main business logic for creating, updating, and
managing customer lifecycle (active / inactive / blocked).
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.customers.constants import (
    CUSTOMER_STATUS_ACTIVE,
    CUSTOMER_STATUS_BLOCKED,
    CUSTOMER_STATUS_INACTIVE,
)

logger = logging.getLogger(__name__)


class CustomerService:
    """
    Service class for customer CRUD and lifecycle operations.
    """

    # ── Settings helper ─────────────────────────────────────────────

    @staticmethod
    def get_settings():
        """
        Return the CustomerSettings singleton (create with defaults
        if it does not exist yet).
        """
        from apps.customers.models.customer_settings import CustomerSettings

        settings, _created = CustomerSettings.objects.get_or_create(
            defaults={},
        )
        return settings

    # ── Read ────────────────────────────────────────────────────────

    @staticmethod
    def get_customer(customer_id):
        """Return a non-deleted customer by primary key."""
        from apps.customers.models import Customer

        return Customer.objects.get(pk=customer_id, is_deleted=False)

    @staticmethod
    def list_customers(**filters):
        """Return a queryset of non-deleted customers, with optional filters."""
        from apps.customers.models import Customer

        return Customer.objects.filter(is_deleted=False, **filters)

    # ── Create ──────────────────────────────────────────────────────

    @classmethod
    def create_customer(
        cls,
        data: dict[str, Any],
        *,
        addresses: list[dict] | None = None,
        phones: list[dict] | None = None,
        user=None,
    ):
        """
        Create a new customer with optional addresses and phones.

        All operations run inside a single atomic transaction.

        Args:
            data: Field values for the Customer model.
            addresses: Optional list of address dicts.
            phones: Optional list of phone dicts.
            user: The user performing the action (for audit trail).

        Returns:
            The created Customer instance.

        Raises:
            ValidationError: If required fields are missing or
                duplicates are detected (per settings).
        """
        from apps.customers.models import Customer, CustomerAddress, CustomerPhone
        from apps.customers.services.history_service import HistoryService

        settings = cls.get_settings()

        # ── Apply default status from settings ──────────────────
        if "status" not in data:
            data["status"] = settings.default_status

        # ── Validate required fields per settings ───────────────
        errors = {}
        if settings.require_email and not data.get("email"):
            errors["email"] = "Email is required."
        if settings.require_phone and not data.get("phone"):
            errors["phone"] = "Phone number is required."
        if errors:
            raise ValidationError(errors)

        # ── Check duplicates per settings ───────────────────────
        email = data.get("email")
        if email and not settings.allow_duplicate_email:
            if Customer.objects.filter(email__iexact=email).exists():
                raise ValidationError(
                    {"email": "A customer with this email already exists."}
                )

        phone = data.get("phone")
        if phone and not settings.allow_duplicate_phone:
            if Customer.objects.filter(phone=phone).exists():
                raise ValidationError(
                    {"phone": "A customer with this phone already exists."}
                )

        # ── Set created_by ──────────────────────────────────────
        if user:
            data["created_by"] = user

        with transaction.atomic():
            customer = Customer(**data)
            customer.full_clean()
            customer.save()

            # ── Create related addresses ────────────────────────
            if addresses:
                for addr_data in addresses:
                    addr = CustomerAddress(customer=customer, **addr_data)
                    addr.full_clean()
                    addr.save()

            # ── Create related phones ───────────────────────────
            if phones:
                for phone_data in phones:
                    ph = CustomerPhone(customer=customer, **phone_data)
                    ph.full_clean()
                    ph.save()

            HistoryService.log_creation(customer, user=user)

        logger.info("Created customer %s (code=%s)", customer.pk, customer.customer_code)
        return customer

    # ── Update ──────────────────────────────────────────────────────

    @classmethod
    def update_customer(
        cls,
        customer,
        data: dict[str, Any],
        *,
        user=None,
    ):
        """
        Update a customer and log field-level changes.

        Args:
            customer: The Customer instance to update.
            data: Dict of field_name → new_value.
            user: The user performing the action.

        Returns:
            The updated Customer instance.
        """
        from apps.customers.services.history_service import HistoryService

        old_values = {}
        for field_name in data:
            if hasattr(customer, field_name):
                old_values[field_name] = getattr(customer, field_name)

        for field_name, value in data.items():
            if hasattr(customer, field_name):
                setattr(customer, field_name, value)

        customer.full_clean()
        customer.save()

        HistoryService.log_changes(
            customer,
            old_values,
            data,
            user=user,
        )

        logger.info("Updated customer %s", customer.pk)
        return customer

    # ── Lifecycle ───────────────────────────────────────────────────

    @classmethod
    def deactivate_customer(cls, customer, *, user=None):
        """Set customer status to inactive."""
        return cls._change_status(customer, CUSTOMER_STATUS_INACTIVE, user=user)

    @classmethod
    def reactivate_customer(cls, customer, *, user=None):
        """Set customer status back to active."""
        return cls._change_status(customer, CUSTOMER_STATUS_ACTIVE, user=user)

    @classmethod
    def block_customer(cls, customer, *, user=None):
        """Block a customer from transactions."""
        return cls._change_status(customer, CUSTOMER_STATUS_BLOCKED, user=user)

    @classmethod
    def _change_status(cls, customer, new_status: str, *, user=None):
        """Internal helper for status transitions."""
        from apps.customers.services.history_service import HistoryService

        old_status = customer.status
        if old_status == new_status:
            return customer

        customer.status = new_status
        customer.is_active = new_status == CUSTOMER_STATUS_ACTIVE
        customer.save(update_fields=["status", "is_active", "updated_on"])

        HistoryService.log_change(
            customer,
            "status",
            old_status,
            new_status,
            user=user,
            change_type="status_change",
        )

        logger.info(
            "Customer %s status changed: %s → %s",
            customer.pk, old_status, new_status,
        )
        return customer
