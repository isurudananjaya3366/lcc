from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.pos.constants import (
    SESSION_STATUS_CHOICES,
    SESSION_STATUS_CLOSED,
    SESSION_STATUS_FORCE_CLOSED,
    SESSION_STATUS_OPEN,
    SESSION_STATUS_SUSPENDED,
    TERMINAL_STATUS_ACTIVE,
)


class POSSessionManager(models.Manager):
    """Manager for POSSession with common queries."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_deleted=False)

    def open_sessions(self):
        return self.get_queryset().filter(status=SESSION_STATUS_OPEN)

    def for_terminal(self, terminal):
        return self.get_queryset().filter(terminal=terminal)

    def for_user(self, user):
        return self.get_queryset().filter(user=user)

    def get_open_session(self, terminal):
        """Get the currently open session for a terminal, or None."""
        return (
            self.get_queryset()
            .filter(terminal=terminal, status=SESSION_STATUS_OPEN)
            .first()
        )


class POSSession(BaseModel):
    """
    Represents a cashier shift or work session on a POS terminal.

    Tracks opening/closing cash amounts, sales totals, and
    provides cash reconciliation on session close.
    """

    # ── Session Identity ──────────────────────────────────────────────────
    terminal = models.ForeignKey(
        "pos.POSTerminal",
        on_delete=models.PROTECT,
        related_name="sessions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pos_sessions",
    )
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS_CHOICES,
        default=SESSION_STATUS_OPEN,
        db_index=True,
    )
    session_number = models.CharField(max_length=50, unique=True)

    # ── Timing Fields ─────────────────────────────────────────────────────
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    expected_close_time = models.DateTimeField(null=True, blank=True)

    # ── Opening Cash ──────────────────────────────────────────────────────
    opening_cash_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    opening_cash_counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions_cash_opened",
    )
    opening_cash_counted_at = models.DateTimeField(null=True, blank=True)
    opening_cash_notes = models.TextField(blank=True, default="")

    # ── Closing Cash ──────────────────────────────────────────────────────
    expected_cash = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    actual_cash_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    cash_variance = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    closing_cash_counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions_cash_closed",
    )
    closing_cash_counted_at = models.DateTimeField(null=True, blank=True)
    closing_notes = models.TextField(blank=True, default="")
    variance_reason = models.TextField(blank=True, default="")

    # ── Session Totals ────────────────────────────────────────────────────
    total_sales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    total_refunds = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    net_sales_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    transaction_count = models.PositiveIntegerField(default=0)
    refund_count = models.PositiveIntegerField(default=0)
    cash_sales_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    card_sales_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    other_payment_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    items_sold_count = models.PositiveIntegerField(default=0)

    # ── Managers ──────────────────────────────────────────────────────────
    objects = POSSessionManager()
    all_with_deleted = models.Manager()

    class Meta:
        db_table = "pos_session"
        verbose_name = "POS Session"
        verbose_name_plural = "POS Sessions"
        ordering = ["-opened_at"]
        indexes = [
            models.Index(
                fields=["session_number"], name="idx_pos_session_number"
            ),
            models.Index(fields=["status"], name="idx_pos_session_status"),
            models.Index(
                fields=["terminal", "status"], name="idx_pos_session_term_stat"
            ),
            models.Index(
                fields=["opened_at"], name="idx_pos_session_opened_at"
            ),
        ]

    def __str__(self):
        return f"Session {self.session_number} on {self.terminal.name}"

    # ── Properties ────────────────────────────────────────────────────────
    @property
    def duration(self):
        """Calculate session duration."""
        if self.closed_at and self.opened_at:
            return self.closed_at - self.opened_at
        elif self.opened_at:
            return timezone.now() - self.opened_at
        return None

    @property
    def is_overtime(self):
        """Check if session exceeded expected close time."""
        if self.expected_close_time and self.closed_at:
            return self.closed_at > self.expected_close_time
        return False

    @property
    def variance_percentage(self):
        """Calculate cash variance as a percentage of expected cash."""
        if self.expected_cash and self.expected_cash > 0 and self.cash_variance is not None:
            return (self.cash_variance / self.expected_cash) * Decimal("100")
        return Decimal("0.00")

    @property
    def is_variance_acceptable(self):
        """Check if cash variance is within acceptable threshold (0.1%)."""
        return abs(self.variance_percentage) <= Decimal("0.1")

    @property
    def average_transaction_value(self):
        """Calculate average sale value per transaction."""
        if self.transaction_count > 0:
            return self.total_sales / self.transaction_count
        return Decimal("0.00")

    @property
    def items_per_transaction(self):
        """Calculate average items sold per transaction."""
        if self.transaction_count > 0:
            return self.items_sold_count / self.transaction_count
        return 0

    @property
    def refund_rate(self):
        """Calculate refund rate as a percentage of transactions."""
        if self.transaction_count > 0:
            return (Decimal(str(self.refund_count)) / Decimal(str(self.transaction_count))) * Decimal("100")
        return Decimal("0.00")

    # ── Methods ───────────────────────────────────────────────────────────
    def open_session(self):
        """
        Opens the session after validating terminal status and uniqueness.

        Validates:
        - Terminal status must be ACTIVE
        - No existing OPEN session on terminal
        - Opening cash amount >= 0

        Returns:
            self: The opened session instance

        Raises:
            ValidationError: If validation fails
        """
        if self.terminal.status != TERMINAL_STATUS_ACTIVE:
            raise ValidationError(
                f"Cannot open session. Terminal is {self.terminal.status}."
            )

        existing_open = (
            POSSession.objects.filter(
                terminal=self.terminal,
                status__in=[SESSION_STATUS_OPEN, SESSION_STATUS_SUSPENDED],
            )
            .exclude(pk=self.pk)
            .exists()
        )
        if existing_open:
            raise ValidationError("Terminal already has an open session.")

        if self.opening_cash_amount is None:
            raise ValidationError("Opening cash amount is required.")

        if self.opening_cash_amount < 0:
            raise ValidationError("Opening cash cannot be negative.")

        self.status = SESSION_STATUS_OPEN
        self.total_sales = Decimal("0.00")
        self.total_refunds = Decimal("0.00")
        self.transaction_count = 0
        self.save()
        return self

    def close_session(self, actual_cash_amount, notes=None):
        """
        Closes the session with cash reconciliation.

        Args:
            actual_cash_amount: Counted cash in drawer (Decimal)
            notes: Optional reconciliation notes (str)

        Returns:
            self: The closed session instance

        Raises:
            ValidationError: If session is not open or validation fails
        """
        if self.status != SESSION_STATUS_OPEN:
            raise ValidationError("Only open sessions can be closed.")

        if actual_cash_amount is None:
            raise ValidationError(
                "Actual cash amount is required to close session."
            )

        actual_cash_amount = Decimal(str(actual_cash_amount))
        if actual_cash_amount < 0:
            raise ValidationError("Actual cash cannot be negative.")

        # Calculate expected cash and variance
        self.expected_cash = (
            self.opening_cash_amount + self.total_sales - self.total_refunds
        )
        self.actual_cash_amount = actual_cash_amount
        self.cash_variance = actual_cash_amount - self.expected_cash

        self.closed_at = timezone.now()
        self.status = SESSION_STATUS_CLOSED

        if notes:
            self.closing_notes = notes

        self.save()
        return self

    def suspend_session(self):
        """Suspend the session temporarily."""
        if self.status != SESSION_STATUS_OPEN:
            raise ValidationError("Only open sessions can be suspended.")
        self.status = SESSION_STATUS_SUSPENDED
        self.save(update_fields=["status", "updated_on"])
        return self

    def resume_session(self):
        """Resume a suspended session."""
        if self.status != SESSION_STATUS_SUSPENDED:
            raise ValidationError("Only suspended sessions can be resumed.")
        self.status = SESSION_STATUS_OPEN
        self.save(update_fields=["status", "updated_on"])
        return self

    def force_close(self):
        """Force close without cash reconciliation."""
        if self.status not in (SESSION_STATUS_OPEN, SESSION_STATUS_SUSPENDED):
            raise ValidationError(
                "Only open or suspended sessions can be force-closed."
            )
        self.status = SESSION_STATUS_FORCE_CLOSED
        self.closed_at = timezone.now()
        self.save()
        return self

    @classmethod
    def generate_session_number(cls, terminal):
        """
        Generate session number in format: SESS-{terminal_code}-{YYYYMMDD}-{sequence}.
        """
        today = timezone.now().strftime("%Y%m%d")
        prefix = f"SESS-{terminal.code}-{today}-"

        last_session = (
            cls.all_with_deleted.filter(session_number__startswith=prefix)
            .order_by("-session_number")
            .first()
        )

        if last_session:
            last_seq = int(last_session.session_number.split("-")[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:03d}"
