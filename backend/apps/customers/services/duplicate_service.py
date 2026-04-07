"""
Duplicate Detection & Merge Service.

Detects potential duplicate customers using email, phone, name, and
company matching with a weighted scoring algorithm. Provides a merge
operation that transfers all related records from duplicate to primary
customer and creates a full audit trail.

Score weights:
    Email match     → 100
    Phone match     → 90
    Name match      → 80
    Company match   → 70
    Address match   → 50
    District match  → 20
    Province match  → 10

Confidence levels:
    HIGH            ≥ 90
    MEDIUM          ≥ 60
    LOW             < 60
"""

import logging
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.db.models import QuerySet, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)

# ── Score weights ───────────────────────────────────────────────────
WEIGHT_EMAIL = 100
WEIGHT_PHONE = 90
WEIGHT_NAME = 80
WEIGHT_COMPANY = 70
WEIGHT_ADDRESS = 50
WEIGHT_DISTRICT = 20
WEIGHT_PROVINCE = 10

CONFIDENCE_HIGH = 150
CONFIDENCE_MEDIUM = 80


@dataclass
class DuplicateMatch:
    """Result of a duplicate-detection comparison."""

    customer_id: str
    display_name: str
    score: int = 0
    matched_fields: list = field(default_factory=list)

    @property
    def confidence(self) -> str:
        if self.score >= CONFIDENCE_HIGH:
            return "high"
        if self.score >= CONFIDENCE_MEDIUM:
            return "medium"
        return "low"


class DuplicateDetectionService:
    """Detects duplicate customers and performs merge operations."""

    # ── Detection ────────────────────────────────────────────────────

    @classmethod
    def find_duplicates(
        cls,
        customer,
        *,
        min_score: int = 50,
    ) -> list[DuplicateMatch]:
        """
        Scan for potential duplicates of *customer*.
        Returns a list of DuplicateMatch sorted by descending score,
        filtered to those ≥ *min_score*.
        """
        from apps.customers.models import Customer

        candidates = (
            Customer.objects.filter(is_deleted=False)
            .exclude(pk=customer.pk)
        )
        matches: list[DuplicateMatch] = []

        for candidate in candidates.iterator(chunk_size=500):
            score, fields = cls._calculate_score(customer, candidate)
            if score >= min_score:
                matches.append(
                    DuplicateMatch(
                        customer_id=str(candidate.pk),
                        display_name=candidate.display_name or "",
                        score=score,
                        matched_fields=fields,
                    )
                )

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    @classmethod
    def find_duplicate_by_email(cls, email: str) -> QuerySet:
        """Quick lookup by exact email."""
        from apps.customers.models import Customer

        if not email:
            return Customer.objects.none()
        return Customer.objects.filter(
            email__iexact=email.strip(),
            is_deleted=False,
        )

    @classmethod
    def find_duplicate_by_phone(cls, phone: str) -> QuerySet:
        """Quick lookup by normalized phone number."""
        from apps.customers.models import Customer
        from django.db.models import Q

        normalized = cls._normalize_phone(phone)
        if not normalized:
            return Customer.objects.none()
        suffix = normalized[-9:]
        return Customer.objects.filter(
            is_deleted=False,
        ).filter(
            Q(phone__endswith=suffix)
            | Q(mobile__endswith=suffix)
            | Q(phone_numbers__phone_number__endswith=suffix)
        ).distinct()

    # ── Score Calculation ────────────────────────────────────────────

    @classmethod
    def _calculate_score(cls, source, candidate) -> tuple[int, list[str]]:
        """
        Compare two customers and return (score, matched_field_names).
        Score is cumulative across all matching fields.
        """
        score = 0
        fields: list[str] = []

        # Email
        if source.email and candidate.email:
            if source.email.strip().lower() == candidate.email.strip().lower():
                score += WEIGHT_EMAIL
                fields.append("email")

        # Phone (main fields)
        if cls._phones_match(source, candidate):
            score += WEIGHT_PHONE
            fields.append("phone")

        # Name (fuzzy)
        if cls._names_match(source, candidate):
            score += WEIGHT_NAME
            fields.append("name")

        # Company / business name
        if source.business_name and candidate.business_name:
            if (
                source.business_name.strip().lower()
                == candidate.business_name.strip().lower()
            ):
                score += WEIGHT_COMPANY
                fields.append("company")

        # Billing address line 1
        if source.billing_address_line_1 and candidate.billing_address_line_1:
            if (
                source.billing_address_line_1.strip().lower()
                == candidate.billing_address_line_1.strip().lower()
            ):
                score += WEIGHT_ADDRESS
                fields.append("address")

        # District
        if source.billing_city and candidate.billing_city:
            if (
                source.billing_city.strip().lower()
                == candidate.billing_city.strip().lower()
            ):
                score += WEIGHT_DISTRICT
                fields.append("district")

        # Province
        if source.billing_state_province and candidate.billing_state_province:
            if (
                source.billing_state_province.strip().lower()
                == candidate.billing_state_province.strip().lower()
            ):
                score += WEIGHT_PROVINCE
                fields.append("province")

        return score, fields

    # ── Matching Helpers ─────────────────────────────────────────────

    @classmethod
    def _phones_match(cls, a, b) -> bool:
        """Compare phone/mobile fields using last-9-digit normalization."""
        phones_a = {
            cls._normalize_phone(a.phone),
            cls._normalize_phone(a.mobile),
        } - {""}
        phones_b = {
            cls._normalize_phone(b.phone),
            cls._normalize_phone(b.mobile),
        } - {""}
        if not phones_a or not phones_b:
            return False
        # Compare final 9 digits (skips country code)
        tails_a = {p[-9:] for p in phones_a if len(p) >= 9}
        tails_b = {p[-9:] for p in phones_b if len(p) >= 9}
        return bool(tails_a & tails_b)

    @classmethod
    def _names_match(cls, a, b) -> bool:
        """
        Fuzzy name matching: checks first_name + last_name.
        Uses simple normalized equality – sufficient for most duplicates.
        """
        name_a = f"{a.first_name or ''} {a.last_name or ''}".strip().lower()
        name_b = f"{b.first_name or ''} {b.last_name or ''}".strip().lower()
        if not name_a or not name_b:
            return False
        return name_a == name_b

    @staticmethod
    def _normalize_phone(phone: Optional[str]) -> str:
        """Strip non-digit characters."""
        if not phone:
            return ""
        return re.sub(r"\D", "", phone)

    # ── Merge Preview ────────────────────────────────────────────────

    @classmethod
    def get_merge_preview(cls, primary, duplicate) -> dict:
        """
        Return a preview of what a merge would do, without
        actually modifying any data.
        """
        return {
            "primary": {
                "id": str(primary.pk),
                "display_name": primary.display_name,
            },
            "duplicate": {
                "id": str(duplicate.pk),
                "display_name": duplicate.display_name,
            },
            "orders_to_transfer": duplicate.orders.count(),
            "invoices_to_transfer": duplicate.invoices.count(),
            "payments_to_transfer": duplicate.payments.count(),
            "addresses_to_transfer": duplicate.addresses.count(),
            "phones_to_transfer": duplicate.phone_numbers.count(),
            "communications_to_transfer": duplicate.communications.count(),
            "duplicate_score": cls._calculate_score(primary, duplicate)[0],
        }

    # ── Merge Operation ──────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def merge_customers(
        cls,
        primary,
        duplicate,
        *,
        merged_by=None,
        merge_reason: str = "",
    ):
        """
        Merge *duplicate* into *primary*:
        1. Transfer orders, invoices, payments, addresses, phones, communications.
        2. Aggregate financial totals onto primary.
        3. Soft-delete the duplicate.
        4. Create a CustomerMerge audit record.

        Returns the CustomerMerge instance.
        """
        from apps.customers.models.customer_merge import CustomerMerge

        # Snapshot the duplicate before changes
        snapshot = {
            "customer_code": duplicate.customer_code,
            "display_name": duplicate.display_name,
            "email": duplicate.email,
            "phone": duplicate.phone,
            "mobile": duplicate.mobile,
            "business_name": duplicate.business_name or "",
            "total_purchases": str(duplicate.total_purchases or 0),
            "total_payments": str(duplicate.total_payments or 0),
            "order_count": duplicate.order_count or 0,
        }

        score, _ = cls._calculate_score(primary, duplicate)

        # ── Transfer related records ─────────────────────────────────
        orders_count = duplicate.orders.update(customer=primary)
        invoices_count = duplicate.invoices.update(customer=primary)
        payments_count = duplicate.payments.update(customer=primary)
        addresses_count = duplicate.addresses.update(customer=primary)
        phones_count = duplicate.phone_numbers.update(customer=primary)

        # Communications
        comms_transferred = 0
        if hasattr(duplicate, "communications"):
            comms_transferred = duplicate.communications.update(customer=primary)

        # Tag assignments (skip tags already on primary)
        tags_transferred = 0
        existing_tag_ids = set(
            primary.tag_assignments.values_list("tag_id", flat=True)
        )
        dup_tags = duplicate.tag_assignments.exclude(tag_id__in=existing_tag_ids)
        tags_transferred = dup_tags.update(customer=primary)
        # Remove leftover duplicate-tag rows (already on primary)
        duplicate.tag_assignments.all().delete()

        # ── Aggregate financials ─────────────────────────────────────
        purchases_added = Decimal(str(duplicate.total_purchases or 0))
        primary.total_purchases = (
            Decimal(str(primary.total_purchases or 0)) + purchases_added
        )
        primary.total_payments = Decimal(str(primary.total_payments or 0)) + Decimal(
            str(duplicate.total_payments or 0)
        )
        primary.outstanding_balance = (
            Decimal(str(primary.outstanding_balance or 0))
            + Decimal(str(duplicate.outstanding_balance or 0))
        )
        primary.order_count = (primary.order_count or 0) + (
            duplicate.order_count or 0
        )
        primary.save(
            update_fields=[
                "total_purchases",
                "total_payments",
                "outstanding_balance",
                "order_count",
                "updated_on",
            ]
        )

        # ── Soft-delete duplicate ────────────────────────────────────
        duplicate.is_deleted = True
        duplicate.deleted_on = timezone.now()
        duplicate.status = "archived"
        duplicate.is_active = False
        duplicate.save(
            update_fields=[
                "is_deleted",
                "deleted_on",
                "status",
                "is_active",
                "updated_on",
            ]
        )

        # ── Audit record ────────────────────────────────────────────
        merge_record = CustomerMerge.objects.create(
            primary_customer=primary,
            duplicate_customer=duplicate,
            merged_by=merged_by,
            merge_reason=merge_reason,
            duplicate_score=score,
            orders_transferred=orders_count,
            invoices_transferred=invoices_count,
            payments_transferred=payments_count,
            addresses_transferred=addresses_count,
            phones_transferred=phones_count,
            total_purchases_added=purchases_added,
            duplicate_customer_snapshot=snapshot,
        )

        logger.info(
            "Merged customer %s into %s (score=%d, orders=%d, invoices=%d, "
            "payments=%d, addresses=%d, phones=%d)",
            duplicate.pk,
            primary.pk,
            score,
            orders_count,
            invoices_count,
            payments_count,
            addresses_count,
            phones_count,
        )

        return merge_record
