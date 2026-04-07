"""
Customer Tag Service.

Business logic for managing customer tags, bulk assignment,
tag-based filtering, and tag statistics.
"""

import logging
from typing import Optional

from django.conf import settings
from django.db import models, transaction
from django.db.models import Count, QuerySet

from apps.customers.models.customer_tag import CustomerTag, CustomerTagAssignment

logger = logging.getLogger(__name__)


class CustomerTagService:
    """Service for customer tagging operations."""

    # ── Single Tag Operations ────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def assign_tag(
        customer_id,
        tag_id,
        assigned_by=None,
    ) -> CustomerTagAssignment:
        """
        Assign a tag to a customer. Returns existing assignment if
        already assigned (idempotent).
        """
        assignment, created = CustomerTagAssignment.objects.get_or_create(
            customer_id=customer_id,
            tag_id=tag_id,
            defaults={"assigned_by": assigned_by},
        )
        if created:
            logger.info(
                "Tag %s assigned to customer %s",
                tag_id,
                customer_id,
            )
        return assignment

    @staticmethod
    @transaction.atomic
    def remove_tag(customer_id, tag_id) -> bool:
        """Remove a tag from a customer. Returns True if removed."""
        deleted, _ = CustomerTagAssignment.objects.filter(
            customer_id=customer_id,
            tag_id=tag_id,
        ).delete()
        if deleted:
            logger.info(
                "Tag %s removed from customer %s",
                tag_id,
                customer_id,
            )
        return bool(deleted)

    # ── Bulk Operations ──────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def bulk_assign_tags(
        customer_ids: list,
        tag_id,
        assigned_by=None,
    ) -> int:
        """
        Assign a tag to multiple customers. Skips those already tagged.
        Returns count of new assignments.
        """
        existing = set(
            CustomerTagAssignment.objects.filter(
                tag_id=tag_id,
                customer_id__in=customer_ids,
            ).values_list("customer_id", flat=True)
        )
        new_ids = [cid for cid in customer_ids if cid not in existing]
        if not new_ids:
            return 0

        assignments = [
            CustomerTagAssignment(
                customer_id=cid,
                tag_id=tag_id,
                assigned_by=assigned_by,
            )
            for cid in new_ids
        ]
        CustomerTagAssignment.objects.bulk_create(assignments)
        logger.info(
            "Bulk-assigned tag %s to %d customers",
            tag_id,
            len(new_ids),
        )
        return len(new_ids)

    # ── Query Helpers ────────────────────────────────────────────────

    @staticmethod
    def get_customer_tags(customer_id) -> QuerySet:
        """Return all active tags for a customer."""
        return CustomerTag.objects.filter(
            assignments__customer_id=customer_id,
            is_active=True,
        ).order_by("name")

    @staticmethod
    def filter_by_tag(tag_id) -> QuerySet:
        """Return customers that have a specific tag."""
        from apps.customers.models import Customer

        return Customer.objects.filter(
            tag_assignments__tag_id=tag_id,
        ).distinct()

    @staticmethod
    def filter_by_tags(
        tag_ids: list,
        match_all: bool = False,
    ) -> QuerySet:
        """
        Return customers matching tags.

        Args:
            tag_ids: List of tag IDs.
            match_all: If True, customer must have ALL tags (AND).
                       If False, customer must have ANY tag (OR).
        """
        from apps.customers.models import Customer

        qs = Customer.objects.filter(
            tag_assignments__tag_id__in=tag_ids,
        )
        if match_all:
            qs = qs.annotate(
                matched_tags=Count(
                    "tag_assignments__tag_id",
                    filter=models.Q(tag_assignments__tag_id__in=tag_ids),
                    distinct=True,
                ),
            ).filter(matched_tags=len(tag_ids))
        return qs.distinct()

    # ── Statistics ───────────────────────────────────────────────────

    @staticmethod
    def get_tag_statistics() -> QuerySet:
        """Return all tags annotated with their customer count."""
        return (
            CustomerTag.objects.filter(is_active=True)
            .annotate(customer_count=Count("assignments", distinct=True))
            .order_by("-customer_count")
        )
