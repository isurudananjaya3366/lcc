"""
Communication service.

Provides methods to log customer communications and retrieve
chronological communication timelines with filtering.
"""

from __future__ import annotations

import logging
from datetime import date

from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class CommunicationService:
    """
    Service for logging and querying customer communications.
    """

    @classmethod
    def log_communication(
        cls,
        customer,
        *,
        communication_type: str,
        subject: str = "",
        content: str = "",
        user=None,
        related_order=None,
        related_invoice=None,
        follow_up_date: date | None = None,
    ):
        """
        Create a new communication log entry.

        Returns the created CustomerCommunication instance.
        """
        from apps.customers.models import CustomerCommunication

        comm = CustomerCommunication.objects.create(
            customer=customer,
            contacted_by=user,
            communication_type=communication_type,
            subject=subject,
            content=content,
            related_order=related_order,
            related_invoice=related_invoice,
            follow_up_date=follow_up_date,
        )

        logger.info(
            "Logged %s communication for customer %s",
            communication_type,
            customer.pk,
        )
        return comm

    @classmethod
    def get_communication_timeline(
        cls,
        customer_id: str,
        *,
        communication_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        contacted_by_id: str | None = None,
    ) -> QuerySet:
        """
        Retrieve chronological communication history for a customer.

        Supports filtering by type, date range, and contacting user.
        Returns a queryset ordered newest-first.
        """
        from apps.customers.models import CustomerCommunication

        qs = CustomerCommunication.objects.filter(
            customer_id=customer_id,
        ).select_related("contacted_by", "related_order", "related_invoice")

        if communication_type:
            qs = qs.filter(communication_type=communication_type)

        if date_from:
            qs = qs.filter(communication_date__date__gte=date_from)

        if date_to:
            qs = qs.filter(communication_date__date__lte=date_to)

        if contacted_by_id:
            qs = qs.filter(contacted_by_id=contacted_by_id)

        return qs.order_by("-communication_date")

    @classmethod
    def get_pending_follow_ups(
        cls,
        customer_id: str | None = None,
    ) -> QuerySet:
        """
        Retrieve communications with pending follow-ups.
        """
        from apps.customers.models import CustomerCommunication

        qs = CustomerCommunication.objects.filter(
            follow_up_completed=False,
            follow_up_date__isnull=False,
        )
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs.order_by("follow_up_date")
