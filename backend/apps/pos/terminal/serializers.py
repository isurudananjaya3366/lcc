"""
POS Terminal and Session serializers.

Provides serialization for POSTerminal and POSSession models
with computed fields, nested representations, and validation.
"""

from decimal import Decimal

from django.conf import settings
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import serializers

from apps.pos.constants import (
    PAYMENT_METHOD_CASH,
    PAYMENT_METHOD_CARD,
    PAYMENT_STATUS_COMPLETED,
    SESSION_STATUS_OPEN,
    TERMINAL_STATUS_ACTIVE,
    TERMINAL_STATUS_INACTIVE,
    TERMINAL_STATUS_MAINTENANCE,
)
from apps.pos.payment.models import POSPayment
from apps.pos.terminal.models import POSSession, POSTerminal


# ── Nested / Lightweight Serializers ────────────────────────────────────


class SimpleOperatorSerializer(serializers.Serializer):
    """Lightweight user serializer for nested use."""

    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        first = getattr(obj, "first_name", "")
        last = getattr(obj, "last_name", "")
        return f"{first} {last}".strip() or str(obj)


class SimpleSessionSerializer(serializers.ModelSerializer):
    """Lightweight session serializer for nested use inside terminal."""

    operator = SimpleOperatorSerializer(source="user", read_only=True)

    class Meta:
        model = POSSession
        fields = [
            "id",
            "session_number",
            "status",
            "opened_at",
            "operator",
            "opening_cash_amount",
        ]
        read_only_fields = fields


class SimpleTerminalSerializer(serializers.ModelSerializer):
    """Lightweight terminal serializer for nested use inside session."""

    class Meta:
        model = POSTerminal
        fields = ["id", "code", "name", "location"]
        read_only_fields = fields


# ── POSTerminalSerializer ───────────────────────────────────────────────


class POSTerminalSerializer(serializers.ModelSerializer):
    """Serializer for POSTerminal list/detail views."""

    current_session = serializers.SerializerMethodField()
    has_open_session = serializers.SerializerMethodField()
    can_open_session = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()

    class Meta:
        model = POSTerminal
        fields = [
            "id",
            "code",
            "name",
            "warehouse",
            "status",
            "description",
            "location",
            "floor",
            "section",
            "is_mobile",
            "ip_address",
            # hardware
            "printer_type",
            "receipt_printer_ip",
            "cash_drawer_enabled",
            "barcode_scanner_enabled",
            "scanner_interface",
            # settings
            "default_tax",
            "allow_price_override",
            "allow_discount",
            "max_discount_percent",
            "require_customer",
            "allow_negative_inventory",
            "auto_print_receipt",
            "receipt_copies",
            "offline_mode_enabled",
            # receipt
            "receipt_header",
            "receipt_footer",
            "receipt_language",
            # computed
            "current_session",
            "has_open_session",
            "can_open_session",
            "last_activity",
            # audit
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "created_on",
            "updated_on",
            "current_session",
            "has_open_session",
            "can_open_session",
            "last_activity",
        ]
        extra_kwargs = {
            "name": {"required": True},
            "location": {"allow_blank": True},
        }

    # ── computed fields ─────────────────────────────────────────────

    def get_current_session(self, obj):
        session = (
            POSSession.objects.filter(
                terminal=obj, status=SESSION_STATUS_OPEN
            )
            .select_related("user")
            .first()
        )
        if session:
            return SimpleSessionSerializer(session).data
        return None

    def get_has_open_session(self, obj):
        return POSSession.objects.filter(
            terminal=obj, status=SESSION_STATUS_OPEN
        ).exists()

    def get_can_open_session(self, obj):
        if obj.status != TERMINAL_STATUS_ACTIVE or not obj.is_active:
            return False
        return not POSSession.objects.filter(
            terminal=obj, status=SESSION_STATUS_OPEN
        ).exists()

    def get_last_activity(self, obj):
        from apps.pos.cart.models import POSCart

        last_cart = (
            POSCart.objects.filter(session__terminal=obj)
            .order_by("-updated_on")
            .values_list("updated_on", flat=True)
            .first()
        )
        return last_cart.isoformat() if last_cart else None

    # ── validation ──────────────────────────────────────────────────

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Terminal name cannot be blank.")
        return value.strip()

    def validate_status(self, value):
        if not self.instance:
            return value
        old_status = self.instance.status
        allowed = {
            TERMINAL_STATUS_ACTIVE: {
                TERMINAL_STATUS_INACTIVE,
                TERMINAL_STATUS_MAINTENANCE,
            },
            TERMINAL_STATUS_INACTIVE: {TERMINAL_STATUS_ACTIVE},
            TERMINAL_STATUS_MAINTENANCE: {
                TERMINAL_STATUS_ACTIVE,
                TERMINAL_STATUS_INACTIVE,
            },
        }
        if value != old_status and value not in allowed.get(old_status, set()):
            raise serializers.ValidationError(
                f"Cannot transition from {old_status} to {value}."
            )
        return value

    def validate(self, attrs):
        if self.instance:
            new_status = attrs.get("status", self.instance.status)
            if (
                self.instance.status == TERMINAL_STATUS_ACTIVE
                and new_status != TERMINAL_STATUS_ACTIVE
            ):
                has_open = POSSession.objects.filter(
                    terminal=self.instance, status=SESSION_STATUS_OPEN
                ).exists()
                if has_open:
                    raise serializers.ValidationError(
                        {
                            "status": "Cannot change status while an open session exists."
                        }
                    )
        return attrs


# ── POSSessionSerializer ────────────────────────────────────────────────


class POSSessionSerializer(serializers.ModelSerializer):
    """Serializer for POSSession with statistics and operator details."""

    operator = SimpleOperatorSerializer(source="user", read_only=True)
    terminal_detail = SimpleTerminalSerializer(
        source="terminal", read_only=True
    )
    terminal = serializers.PrimaryKeyRelatedField(
        queryset=POSTerminal.objects.all(), write_only=True
    )

    # Computed statistics
    transaction_count_computed = serializers.SerializerMethodField(
        method_name="get_transaction_count_computed"
    )
    total_sales_amount = serializers.SerializerMethodField()
    total_cash_amount = serializers.SerializerMethodField()
    total_card_amount = serializers.SerializerMethodField()
    total_other_amount = serializers.SerializerMethodField()
    session_duration = serializers.SerializerMethodField()
    average_transaction_value = serializers.SerializerMethodField()

    class Meta:
        model = POSSession
        fields = [
            "id",
            "session_number",
            "terminal",
            "terminal_detail",
            "operator",
            "status",
            "opened_at",
            "closed_at",
            # cash
            "opening_cash_amount",
            "expected_cash",
            "actual_cash_amount",
            "cash_variance",
            "closing_notes",
            "variance_reason",
            # model totals
            "total_sales",
            "total_refunds",
            "net_sales_amount",
            "transaction_count",
            "refund_count",
            "cash_sales_amount",
            "card_sales_amount",
            "other_payment_amount",
            "items_sold_count",
            # computed
            "transaction_count_computed",
            "total_sales_amount",
            "total_cash_amount",
            "total_card_amount",
            "total_other_amount",
            "session_duration",
            "average_transaction_value",
            # audit
            "created_on",
            "updated_on",
        ]
        read_only_fields = [
            "id",
            "session_number",
            "status",
            "opened_at",
            "closed_at",
            "expected_cash",
            "cash_variance",
            "total_sales",
            "total_refunds",
            "net_sales_amount",
            "transaction_count",
            "refund_count",
            "cash_sales_amount",
            "card_sales_amount",
            "other_payment_amount",
            "items_sold_count",
            "created_on",
            "updated_on",
        ]
        extra_kwargs = {
            "opening_cash_amount": {"required": False},
            "actual_cash_amount": {"required": False},
        }

    # ── computed methods ────────────────────────────────────────────

    def _completed_carts(self, obj):
        from apps.pos.cart.models import POSCart
        from apps.pos.constants import CART_STATUS_COMPLETED

        return POSCart.objects.filter(
            session=obj, status=CART_STATUS_COMPLETED
        )

    def _completed_payments(self, obj):
        return POSPayment.objects.filter(
            cart__session=obj, status=PAYMENT_STATUS_COMPLETED
        )

    def get_transaction_count_computed(self, obj):
        return self._completed_carts(obj).count()

    def get_total_sales_amount(self, obj):
        total = self._completed_carts(obj).aggregate(
            total=Sum("grand_total")
        )["total"]
        return str(total or Decimal("0.00"))

    def get_total_cash_amount(self, obj):
        total = self._completed_payments(obj).filter(
            method=PAYMENT_METHOD_CASH
        ).aggregate(total=Sum("amount"))["total"]
        return str(total or Decimal("0.00"))

    def get_total_card_amount(self, obj):
        total = self._completed_payments(obj).filter(
            method=PAYMENT_METHOD_CARD
        ).aggregate(total=Sum("amount"))["total"]
        return str(total or Decimal("0.00"))

    def get_total_other_amount(self, obj):
        total = (
            self._completed_payments(obj)
            .exclude(method__in=[PAYMENT_METHOD_CASH, PAYMENT_METHOD_CARD])
            .aggregate(total=Sum("amount"))["total"]
        )
        return str(total or Decimal("0.00"))

    def get_session_duration(self, obj):
        if not obj.opened_at:
            return None
        end = obj.closed_at or timezone.now()
        delta = end - obj.opened_at
        total_minutes = int(delta.total_seconds() // 60)
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours}:{minutes:02d}"

    def get_average_transaction_value(self, obj):
        count = self._completed_carts(obj).count()
        if not count:
            return "0.00"
        total = self._completed_carts(obj).aggregate(
            total=Sum("grand_total")
        )["total"] or Decimal("0.00")
        return str((total / count).quantize(Decimal("0.01")))

    # ── validation ──────────────────────────────────────────────────

    def validate_opening_cash_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Opening cash cannot be negative."
            )
        return value

    def validate_actual_cash_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Actual cash cannot be negative."
            )
        return value

    def validate(self, attrs):
        if not self.instance:
            # Creating / opening a session
            terminal = attrs.get("terminal")
            if terminal:
                has_open = POSSession.objects.filter(
                    terminal=terminal, status=SESSION_STATUS_OPEN
                ).exists()
                if has_open:
                    raise serializers.ValidationError(
                        {
                            "terminal": "This terminal already has an open session."
                        }
                    )
        return attrs


# ── Session Open / Close Request Serializers ────────────────────────────


class SessionOpenSerializer(serializers.Serializer):
    """Request serializer for opening a session."""

    terminal = serializers.PrimaryKeyRelatedField(
        queryset=POSTerminal.objects.all()
    )
    opening_cash_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )

    def validate_terminal(self, value):
        if value.status != TERMINAL_STATUS_ACTIVE:
            raise serializers.ValidationError(
                f"Terminal is {value.status}, must be active."
            )
        if not value.is_active:
            raise serializers.ValidationError("Terminal is disabled.")
        has_open = POSSession.objects.filter(
            terminal=value, status=SESSION_STATUS_OPEN
        ).exists()
        if has_open:
            raise serializers.ValidationError(
                "Terminal already has an open session."
            )
        return value

    def validate_opening_cash_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Opening cash cannot be negative."
            )
        return value


class SessionCloseSerializer(serializers.Serializer):
    """Request serializer for closing a session."""

    actual_cash_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2
    )

    def validate_actual_cash_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Actual cash cannot be negative."
            )
        return value
