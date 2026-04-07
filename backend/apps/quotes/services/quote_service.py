"""
QuoteService — Core business logic for quote operations.

Tasks 37-47, 49: Quote CRUD, status transitions, validation,
expiry, conversion, revision, locking, and history logging.
"""

import logging
from datetime import timedelta
from decimal import Decimal
from functools import wraps

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


# ── Custom Exceptions ────────────────────────────────────────────

class QuoteValidationError(Exception):
    pass


class InvalidStatusTransition(QuoteValidationError):
    pass


class QuoteExpiredError(QuoteValidationError):
    pass


class QuoteLockedError(QuoteValidationError):
    pass


# ── Decorator ────────────────────────────────────────────────────

def validate_not_locked(func):
    """Decorator to prevent operations on locked quotes."""
    @wraps(func)
    def wrapper(quote_or_cls, *args, **kwargs):
        from apps.quotes.models import Quote

        # Support both classmethod and instance method patterns
        quote_arg = args[0] if args else kwargs.get("quote")
        if hasattr(quote_arg, "is_locked") and quote_arg.is_locked:
            raise QuoteLockedError(
                f"Cannot perform operation on locked quote "
                f"{quote_arg.quote_number} (status: {quote_arg.status})"
            )
        return func(quote_or_cls, *args, **kwargs)
    return wrapper


# ── Allowed Transitions ─────────────────────────────────────────

ALLOWED_TRANSITIONS = {
    "DRAFT": ["SENT"],
    "SENT": ["ACCEPTED", "REJECTED", "EXPIRED"],
    "ACCEPTED": ["CONVERTED"],
    "REJECTED": [],
    "EXPIRED": [],
    "CONVERTED": [],
}


class QuoteService:
    """Core service for quote business logic."""

    def __init__(self, quote=None):
        self.quote = quote

    # ── Private Helpers (Task 37) ────────────────────────────────

    @staticmethod
    def _validate_status_transition(from_status, to_status):
        allowed = ALLOWED_TRANSITIONS.get(from_status, [])
        if to_status not in allowed:
            raise InvalidStatusTransition(
                f"Cannot transition from '{from_status}' to '{to_status}'. "
                f"Allowed: {allowed}"
            )
        return True

    @staticmethod
    def _can_edit_quote(quote):
        return quote.status in ("DRAFT", "SENT")

    @staticmethod
    def _can_delete_quote(quote):
        return quote.status == "DRAFT"

    @staticmethod
    def _can_send_quote(quote):
        if quote.status != "DRAFT":
            return False
        if not quote.line_items.exists():
            return False
        if not quote.customer_id and not quote.guest_email:
            return False
        return True

    # ── Quote Creation (Task 38) ─────────────────────────────────

    @classmethod
    @transaction.atomic
    def create_quote(cls, quote_data, line_items_data, user):
        """Create a new quote with line items."""
        from apps.quotes.models import Quote, QuoteLineItem
        from apps.quotes.services.calculation import QuoteCalculationService

        validity_days = int(quote_data.get("validity_days", 30))
        issue_date = timezone.now().date()
        valid_until = issue_date + timedelta(days=validity_days)

        quote = Quote.objects.create(
            customer_id=quote_data.get("customer_id"),
            guest_name=quote_data.get("guest_name", ""),
            guest_email=quote_data.get("guest_email", ""),
            guest_phone=quote_data.get("guest_phone", ""),
            guest_company=quote_data.get("guest_company", ""),
            title=quote_data.get("title", "New Quote"),
            status="DRAFT",
            issue_date=issue_date,
            valid_until=valid_until,
            notes=quote_data.get("notes", ""),
            terms=quote_data.get("terms", ""),
            discount_type=quote_data.get("discount_type"),
            discount_value=Decimal(str(quote_data.get("discount_value", 0))),
            currency=quote_data.get("currency", "LKR"),
            created_by=user,
        )

        # Create line items
        for idx, item_data in enumerate(line_items_data):
            line_item = QuoteLineItem(
                quote=quote,
                position=idx,
                product_id=item_data.get("product_id"),
                variant_id=item_data.get("variant_id"),
                product_name=item_data.get("product_name", ""),
                custom_description=item_data.get("custom_description", ""),
                custom_sku=item_data.get("custom_sku", ""),
                quantity=Decimal(str(item_data.get("quantity", 1))),
                unit_of_measure=item_data.get("unit_of_measure", "unit"),
                unit_price=Decimal(str(item_data.get("unit_price", 0))),
                discount_type=item_data.get("discount_type"),
                discount_value=Decimal(str(item_data.get("discount_value", 0))),
                is_taxable=item_data.get("is_taxable", True),
                tax_rate=Decimal(str(item_data.get("tax_rate", 0))),
                notes=item_data.get("notes", ""),
            )

            # Snapshot from product if available
            if line_item.product_id:
                product = line_item.product
                variant = line_item.variant if line_item.variant_id else None
                line_item.snapshot_from_product(product, variant)

            line_item.save()

        # Calculate totals
        QuoteCalculationService(quote).calculate_all(save=True)

        # Log history
        cls.log_history(quote, "CREATED", user=user)

        return quote

    # ── Quote Duplication (Task 39) ──────────────────────────────

    @classmethod
    @transaction.atomic
    def duplicate_quote(cls, quote, user=None):
        """Create a copy of an existing quote."""
        from apps.quotes.models import Quote, QuoteLineItem
        from apps.quotes.services.calculation import QuoteCalculationService

        original = Quote.objects.prefetch_related("line_items").get(id=quote.id if hasattr(quote, 'id') else quote)
        issue_date = timezone.now().date()

        new_quote = Quote.objects.create(
            customer=original.customer,
            guest_name=original.guest_name,
            guest_email=original.guest_email,
            guest_phone=original.guest_phone,
            guest_company=original.guest_company,
            title=f"{original.title or 'Quote'} (Copy)",
            status="DRAFT",
            issue_date=issue_date,
            valid_until=issue_date + timedelta(days=30),
            notes=original.notes,
            terms=original.terms,
            discount_type=original.discount_type,
            discount_value=original.discount_value,
            currency=original.currency,
            created_by=user,
        )

        for item in original.line_items.order_by("position"):
            QuoteLineItem.objects.create(
                quote=new_quote,
                position=item.position,
                product=item.product,
                variant=item.variant,
                product_name=item.product_name,
                custom_description=item.custom_description,
                custom_sku=item.custom_sku,
                quantity=item.quantity,
                unit_of_measure=item.unit_of_measure,
                unit_price=item.unit_price,
                original_price=item.original_price,
                cost_price=item.cost_price,
                discount_type=item.discount_type,
                discount_value=item.discount_value,
                is_taxable=item.is_taxable,
                tax_rate=item.tax_rate,
                notes=item.notes,
            )

        QuoteCalculationService(new_quote).calculate_all(save=True)
        cls.log_history(new_quote, "CREATED", user=user, notes="Duplicated from " + original.quote_number)

        return new_quote

    # ── Status Transitions (Task 40) ─────────────────────────────

    @classmethod
    @transaction.atomic
    def send_quote(cls, quote, user=None):
        """Transition quote from DRAFT to SENT."""
        from apps.quotes.models import Quote

        quote = Quote.objects.select_for_update().get(id=quote.id if hasattr(quote, 'id') else quote)
        cls._validate_status_transition(quote.status, "SENT")

        if not cls._can_send_quote(quote):
            raise QuoteValidationError(
                "Quote must have line items and a customer or guest email to send."
            )

        old_status = quote.status
        quote.status = "SENT"
        quote.sent_at = timezone.now()
        quote.sent_by = user
        quote.save(update_fields=["status", "sent_at", "sent_by", "updated_on"])

        cls.log_history(
            quote, "SENT", user=user,
            old_values={"status": old_status},
            new_values={"status": "SENT"},
        )
        return quote

    @classmethod
    @transaction.atomic
    def accept_quote(cls, quote, user=None):
        """Transition quote from SENT to ACCEPTED."""
        from apps.quotes.models import Quote

        quote = Quote.objects.select_for_update().get(id=quote.id if hasattr(quote, 'id') else quote)
        cls._validate_status_transition(quote.status, "ACCEPTED")

        if quote.valid_until and quote.valid_until < timezone.now().date():
            raise QuoteExpiredError("Cannot accept an expired quote.")

        old_status = quote.status
        quote.status = "ACCEPTED"
        quote.accepted_at = timezone.now()
        quote.accepted_by = user
        quote.save(update_fields=["status", "accepted_at", "accepted_by", "updated_on"])

        cls.log_history(
            quote, "ACCEPTED", user=user,
            old_values={"status": old_status},
            new_values={"status": "ACCEPTED"},
        )
        return quote

    @classmethod
    @transaction.atomic
    def reject_quote(cls, quote, user=None, reason=""):
        """Transition quote from SENT to REJECTED."""
        from apps.quotes.models import Quote

        quote = Quote.objects.select_for_update().get(id=quote.id if hasattr(quote, 'id') else quote)
        cls._validate_status_transition(quote.status, "REJECTED")

        old_status = quote.status
        quote.status = "REJECTED"
        quote.rejected_at = timezone.now()
        quote.rejected_by = user
        quote.rejection_reason = reason
        quote.save(update_fields=[
            "status", "rejected_at", "rejected_by", "rejection_reason", "updated_on",
        ])

        cls.log_history(
            quote, "REJECTED", user=user,
            old_values={"status": old_status},
            new_values={"status": "REJECTED", "rejection_reason": reason},
        )
        return quote

    # ── Validation (Task 41) ─────────────────────────────────────

    @staticmethod
    def validate_before_send(quote):
        """Validate quote is ready to send. Returns list of error messages."""
        errors = []
        if not quote.line_items.exists():
            errors.append("Quote has no line items.")
        if not quote.customer_id and not quote.guest_email:
            errors.append("Quote requires a customer or guest email.")
        if quote.valid_until and quote.valid_until < timezone.now().date():
            errors.append("Quote validity date is in the past.")
        if quote.total <= 0:
            errors.append("Quote total must be greater than zero.")
        return errors

    @staticmethod
    def validate_before_accept(quote):
        """Validate quote can be accepted."""
        errors = []
        if quote.status != "SENT":
            errors.append("Only SENT quotes can be accepted.")
        if quote.valid_until and quote.valid_until < timezone.now().date():
            errors.append("Quote has expired.")
        return errors

    @staticmethod
    def validate_before_convert(quote):
        """Validate quote can be converted to an order."""
        errors = []
        if quote.status != "ACCEPTED":
            errors.append("Only ACCEPTED quotes can be converted.")
        if not quote.customer_id:
            errors.append("Quote must have a registered customer for conversion.")
        return errors

    @staticmethod
    def get_available_actions(quote):
        """Return action name strings available for the current status."""
        details = QuoteService.get_available_actions_detailed(quote)
        return [a["name"] for a in details]

    @staticmethod
    def get_available_actions_detailed(quote):
        """Return detailed actions with name/label/enabled for the current status."""
        actions = []
        status = quote.status
        if status == "DRAFT":
            can_send = QuoteService._can_send_quote(quote)
            actions.extend([
                {"name": "send", "label": "Send Quote", "enabled": can_send},
                {"name": "edit", "label": "Edit Quote", "enabled": True},
                {"name": "delete", "label": "Delete Quote", "enabled": True},
                {"name": "duplicate", "label": "Duplicate Quote", "enabled": True},
            ])
        elif status == "SENT":
            is_expired = quote.valid_until and quote.valid_until < timezone.now().date()
            actions.extend([
                {"name": "accept", "label": "Accept Quote", "enabled": not is_expired},
                {"name": "reject", "label": "Reject Quote", "enabled": True},
                {"name": "duplicate", "label": "Duplicate Quote", "enabled": True},
                {"name": "revise", "label": "Create Revision", "enabled": True},
            ])
        elif status == "ACCEPTED":
            actions.extend([
                {"name": "convert", "label": "Convert to Order", "enabled": True},
                {"name": "duplicate", "label": "Duplicate Quote", "enabled": True},
            ])
        return actions

    @staticmethod
    def can_perform_action(quote, action):
        """Check if a specific action is available."""
        for act in QuoteService.get_available_actions(quote):
            if act["name"] == action:
                return act["enabled"]
        return False

    # ── Quote Expiry (Task 42) ───────────────────────────────────

    @classmethod
    @transaction.atomic
    def expire_quote(cls, quote):
        """Transition quote from SENT to EXPIRED."""
        from apps.quotes.models import Quote

        quote = Quote.objects.select_for_update().get(id=quote.id if hasattr(quote, 'id') else quote)
        cls._validate_status_transition(quote.status, "EXPIRED")

        old_status = quote.status
        quote.status = "EXPIRED"
        quote.expired_at = timezone.now()
        quote.save(update_fields=["status", "expired_at", "updated_on"])

        cls.log_history(
            quote, "EXPIRED",
            old_values={"status": old_status},
            new_values={"status": "EXPIRED"},
        )
        return quote

    @classmethod
    def check_and_expire_quote(cls, quote):
        """Expire a quote if it's past its validity date. Returns True if expired."""
        from apps.quotes.models import Quote

        try:
            quote_obj = Quote.objects.get(id=quote.id if hasattr(quote, 'id') else quote)
            if quote_obj.status == "SENT" and quote_obj.valid_until and quote_obj.valid_until < timezone.now().date():
                cls.expire_quote(quote_obj)
                return True
        except Exception:
            logger.exception("Error checking quote expiry for %s", quote)
        return False

    @classmethod
    def get_expired_quotes(cls):
        """Get SENT quotes that have passed their validity date."""
        from apps.quotes.models import Quote

        today = timezone.now().date()
        return Quote.objects.filter(
            status="SENT",
            valid_until__lt=today,
        ).select_related("customer")

    @classmethod
    def get_expiring_soon(cls, days=7):
        """Get quotes expiring within the next N days."""
        from apps.quotes.models import Quote

        today = timezone.now().date()
        return Quote.objects.filter(
            status="SENT",
            valid_until__gte=today,
            valid_until__lte=today + timedelta(days=days),
        ).select_related("customer")

    @classmethod
    def bulk_expire_quotes(cls, quotes=None):
        """Expire multiple quotes. Returns count of expired."""
        if quotes is None:
            quotes = cls.get_expired_quotes()

        now = timezone.now()
        count = 0
        for quote in quotes:
            try:
                quote.status = "EXPIRED"
                quote.expired_at = now
                quote.save(update_fields=["status", "expired_at", "updated_on"])
                cls.log_history(
                    quote, "EXPIRED",
                    old_values={"status": "SENT"},
                    new_values={"status": "EXPIRED"},
                )
                count += 1
            except Exception:
                logger.exception("Failed to expire quote %s", quote.quote_number)
        return count

    # ── Quote to Order Conversion (Task 44) ──────────────────────

    @classmethod
    @transaction.atomic
    def convert_to_order(cls, quote, user=None, allow_backorder=False):
        """
        Convert an accepted quote into a sales order.

        Returns the created Order, or raises if conversion fails.
        Note: Requires the orders app to have Order and OrderLineItem models.
        """
        from apps.quotes.models import Quote

        quote = (
            Quote.objects
            .prefetch_related("line_items__product", "line_items__variant")
            .select_for_update()
            .get(id=quote.id if hasattr(quote, 'id') else quote)
        )
        cls._validate_status_transition(quote.status, "CONVERTED")

        if quote.converted_to_order_id:
            raise QuoteValidationError("Quote has already been converted.")

        # Inventory check (Task 45)
        if not allow_backorder:
            availability = cls.validate_inventory_availability(quote)
            if not availability["valid"]:
                raise QuoteValidationError(availability["message"])

        # Lazy import — the orders app may not exist yet
        try:
            from apps.orders.models import Order, OrderLineItem
        except ImportError:
            raise QuoteValidationError(
                "The orders module is not yet available. "
                "Cannot convert quote to order."
            )

        order = Order.objects.create(
            customer=quote.customer,
            order_type="FROM_QUOTE",
            status="CONFIRMED",
            notes=quote.notes,
            terms_and_conditions=quote.terms,
            discount_type=quote.discount_type,
            discount_value=quote.discount_value,
            created_by=user,
        )

        for item in quote.line_items.order_by("position"):
            OrderLineItem.objects.create(
                order=order,
                position=item.position,
                product=item.product,
                variant=item.variant,
                product_name=item.product_name,
                custom_description=item.custom_description,
                quantity=item.quantity,
                unit_of_measure=item.unit_of_measure,
                unit_price=item.unit_price,
                discount_type=item.discount_type,
                discount_value=item.discount_value,
                is_taxable=item.is_taxable,
                tax_rate=item.tax_rate,
            )

        old_status = quote.status
        quote.status = "CONVERTED"
        quote.converted_at = timezone.now()
        quote.converted_to_order = order
        quote.save(update_fields=[
            "status", "converted_at", "converted_to_order", "updated_on",
        ])

        cls.log_history(
            quote, "CONVERTED", user=user,
            old_values={"status": old_status},
            new_values={"status": "CONVERTED"},
            notes=f"Converted to order {order}",
        )
        return order

    # ── Inventory Validation (Task 45) ───────────────────────────

    @staticmethod
    def validate_inventory_availability(quote):
        """Check inventory for all product-based line items."""
        result = {"valid": True, "insufficient_items": [], "message": ""}

        try:
            from apps.inventory.models import Stock
        except ImportError:
            # Inventory module may not be available
            return result

        for item in quote.line_items.filter(product__isnull=False):
            try:
                if item.variant_id:
                    stock = Stock.objects.filter(variant=item.variant).first()
                else:
                    stock = Stock.objects.filter(
                        product=item.product, variant__isnull=True
                    ).first()

                available = Decimal("0")
                if stock and hasattr(stock, "available_quantity"):
                    available = stock.available_quantity or Decimal("0")
                elif stock and hasattr(stock, "quantity"):
                    available = stock.quantity or Decimal("0")

                if available < item.quantity:
                    shortage = item.quantity - available
                    result["valid"] = False
                    result["insufficient_items"].append({
                        "product_name": item.product_name,
                        "required": item.quantity,
                        "available": available,
                        "shortage": shortage,
                    })
            except Exception:
                logger.exception(
                    "Error checking inventory for line item %s", item.id
                )

        if not result["valid"]:
            names = [i["product_name"] for i in result["insufficient_items"]]
            result["message"] = f"Insufficient stock for: {', '.join(names)}"

        return result

    # ── Quote Revision (Task 46) ─────────────────────────────────

    @classmethod
    @transaction.atomic
    def create_revision(cls, quote, user=None, reason=""):
        """Create a new revision of a quote."""
        from apps.quotes.models import Quote, QuoteLineItem
        from apps.quotes.services.calculation import QuoteCalculationService

        original = (
            Quote.objects
            .prefetch_related("line_items")
            .select_for_update()
            .get(id=quote.id if hasattr(quote, 'id') else quote)
        )

        root = original.revision_of or original
        next_number = root.revisions.count() + 2  # root is revision 1

        # Mark original as no longer latest
        original.is_latest_revision = False
        original.save(update_fields=["is_latest_revision", "updated_on"])

        issue_date = timezone.now().date()
        revision = Quote.objects.create(
            customer=original.customer,
            guest_name=original.guest_name,
            guest_email=original.guest_email,
            guest_phone=original.guest_phone,
            guest_company=original.guest_company,
            title=original.title,
            status="DRAFT",
            issue_date=issue_date,
            valid_until=issue_date + timedelta(days=30),
            notes=original.notes,
            terms=original.terms,
            discount_type=original.discount_type,
            discount_value=original.discount_value,
            currency=original.currency,
            revision_of=root,
            revision_number=next_number,
            is_latest_revision=True,
            created_by=user,
        )

        for item in original.line_items.order_by("position"):
            QuoteLineItem.objects.create(
                quote=revision,
                position=item.position,
                product=item.product,
                variant=item.variant,
                product_name=item.product_name,
                custom_description=item.custom_description,
                custom_sku=item.custom_sku,
                quantity=item.quantity,
                unit_of_measure=item.unit_of_measure,
                unit_price=item.unit_price,
                original_price=item.original_price,
                cost_price=item.cost_price,
                discount_type=item.discount_type,
                discount_value=item.discount_value,
                is_taxable=item.is_taxable,
                tax_rate=item.tax_rate,
                notes=item.notes,
            )

        QuoteCalculationService(revision).calculate_all(save=True)

        cls.log_history(
            revision, "REVISION_CREATED", user=user,
            notes=f"Revision {next_number} of {root.quote_number}. {reason}".strip(),
        )
        return revision

    # ── History Logging (Task 49) ────────────────────────────────

    @staticmethod
    def log_history(quote, event_type, user=None, notes="",
                    old_values=None, new_values=None):
        """Create a QuoteHistory entry."""
        from apps.quotes.models.history import QuoteHistory

        QuoteHistory.objects.create(
            quote=quote,
            event_type=event_type,
            user=user,
            notes=notes,
            old_values=old_values,
            new_values=new_values,
        )

    @staticmethod
    def get_quote_history(quote_id, event_type=None):
        """Retrieve history for a quote."""
        from apps.quotes.models.history import QuoteHistory

        qs = QuoteHistory.objects.filter(quote_id=quote_id).select_related("user")
        if event_type:
            qs = qs.filter(event_type=event_type)
        return qs

    @staticmethod
    def get_recent_history(quote_id, limit=10):
        """Return the most recent history entries."""
        return QuoteService.get_quote_history(quote_id)[:limit]

    # ── Default Settings (Task 51) ───────────────────────────────

    @staticmethod
    def apply_default_settings(quote):
        """Apply tenant defaults to a quote if fields are empty."""
        from apps.quotes.models.settings import QuoteSettings

        tenant = getattr(quote, "tenant", None)
        if not tenant:
            return

        try:
            settings = QuoteSettings.get_or_create_for_tenant(tenant)
        except Exception:
            return

        if not quote.terms:
            quote.terms = settings.default_terms_and_conditions
        if not quote.notes:
            quote.notes = settings.default_notes
        if not quote.discount_type and settings.default_discount_type:
            quote.discount_type = settings.default_discount_type
            quote.discount_value = settings.default_discount_value or Decimal("0")
        if not quote.valid_until:
            quote.valid_until = Quote.calculate_valid_until(
                quote.issue_date, settings.default_validity_days
            )
