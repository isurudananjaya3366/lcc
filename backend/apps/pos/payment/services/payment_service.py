"""
PaymentService — processes payments against a POS cart.

Supports cash (with change calculation), card, mobile, store credit,
split payments, transaction completion, and voiding.
"""

import logging
from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    CART_STATUS_COMPLETED,
    CART_STATUS_VOIDED,
    PAYMENT_METHOD_CASH,
    PAYMENT_METHOD_CARD,
    PAYMENT_METHOD_STORE_CREDIT,
    PAYMENT_STATUS_COMPLETED,
    PAYMENT_STATUS_FAILED,
    PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_VOIDED,
)
from apps.pos.payment.models import POSPayment

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Service for processing POS payments.

    Usage::

        svc = PaymentService(cart=cart, user=request.user)
        payment = svc.process_cash_payment(amount_tendered=Decimal('2000.00'))
        remaining = svc.get_remaining_amount()
        if remaining == 0:
            result = svc.complete_transaction()
    """

    def __init__(self, cart, user):
        self.cart = cart
        self.user = user
        self._validate_cart()

    # ── internal ────────────────────────────────────────────────────

    def _validate_cart(self):
        if not self.cart:
            raise ValueError("Cart is required")
        if self.cart.status != CART_STATUS_ACTIVE:
            raise ValueError(
                f"Cart must be ACTIVE to accept payments, current: {self.cart.status}"
            )
        if not self.cart.items.exists():
            raise ValueError("Cart has no items")
        if self.cart.grand_total <= 0:
            raise ValueError("Cart total must be positive")

    def _create_payment(self, method, amount, status=PAYMENT_STATUS_PENDING, **extra):
        return POSPayment.objects.create(
            cart=self.cart,
            method=method,
            amount=amount,
            status=status,
            processed_by=self.user,
            **extra,
        )

    # ── queries ─────────────────────────────────────────────────────

    def get_remaining_amount(self) -> Decimal:
        total_paid = (
            self.cart.payments.filter(status=PAYMENT_STATUS_COMPLETED).aggregate(
                total=models.Sum("amount")
            )["total"]
            or Decimal("0.00")
        )
        return max(self.cart.grand_total - total_paid, Decimal("0.00"))

    def get_cart_payments(self, status=None):
        qs = self.cart.payments.all()
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("created_on")

    def can_complete_cart(self) -> bool:
        has_pending = self.cart.payments.filter(
            status=PAYMENT_STATUS_PENDING
        ).exists()
        if has_pending:
            return False
        return self.get_remaining_amount() == Decimal("0.00")

    # ── payment processors ──────────────────────────────────────────

    @transaction.atomic
    def process_cash_payment(self, amount_tendered: Decimal) -> POSPayment:
        """Process a cash payment with change calculation."""
        if not amount_tendered or amount_tendered <= 0:
            raise ValueError("Amount tendered must be positive")

        remaining = self.get_remaining_amount()
        if amount_tendered < remaining:
            raise ValueError(
                f"Insufficient cash. Required: LKR {remaining}, "
                f"Tendered: LKR {amount_tendered}"
            )

        payment_amount = remaining
        change_due = amount_tendered - payment_amount

        return self._create_payment(
            method=PAYMENT_METHOD_CASH,
            amount=payment_amount,
            status=PAYMENT_STATUS_COMPLETED,
            amount_tendered=amount_tendered,
            change_due=change_due,
            paid_at=timezone.now(),
        )

    @transaction.atomic
    def process_card_payment(
        self,
        amount: Decimal,
        *,
        authorization_code: str = "",
        reference_number: str = "",
    ) -> POSPayment:
        """Process a card payment (gateway integration is a placeholder)."""
        if not amount or amount <= 0:
            raise ValueError("Amount must be positive")
        remaining = self.get_remaining_amount()
        if amount > remaining:
            raise ValueError(
                f"Amount exceeds remaining: LKR {remaining}"
            )

        payment = self._create_payment(
            method=PAYMENT_METHOD_CARD,
            amount=amount,
            status=PAYMENT_STATUS_COMPLETED,
            authorization_code=authorization_code,
            reference_number=reference_number,
            paid_at=timezone.now(),
        )
        return payment

    @transaction.atomic
    def process_mobile_payment(
        self,
        amount: Decimal,
        *,
        reference_number: str = "",
        method: str = "mobile_frimi",
    ) -> POSPayment:
        """Process a mobile payment (FriMi, Genie, etc.)."""
        if not amount or amount <= 0:
            raise ValueError("Amount must be positive")
        remaining = self.get_remaining_amount()
        if amount > remaining:
            raise ValueError(f"Amount exceeds remaining: LKR {remaining}")

        return self._create_payment(
            method=method,
            amount=amount,
            status=PAYMENT_STATUS_COMPLETED,
            reference_number=reference_number,
            paid_at=timezone.now(),
        )

    @transaction.atomic
    def process_store_credit(self, amount: Decimal) -> POSPayment:
        """Deduct from customer store credit balance."""
        if not self.cart.customer:
            raise ValueError("Cart has no customer for store credit")
        if not amount or amount <= 0:
            raise ValueError("Amount must be positive")
        remaining = self.get_remaining_amount()
        if amount > remaining:
            raise ValueError(f"Amount exceeds remaining: LKR {remaining}")

        # Validate sufficient credit balance
        customer = self.cart.customer
        credit_balance = getattr(customer, "store_credit_balance", None)
        if credit_balance is not None and credit_balance < amount:
            raise ValueError(
                f"Insufficient store credit. Available: LKR {credit_balance}"
            )

        payment = self._create_payment(
            method=PAYMENT_METHOD_STORE_CREDIT,
            amount=amount,
            status=PAYMENT_STATUS_COMPLETED,
            paid_at=timezone.now(),
            notes=f"Store credit: balance {credit_balance} -> {credit_balance - amount}" if credit_balance is not None else "",
        )

        # Deduct balance atomically
        if credit_balance is not None:
            from django.db.models import F

            customer.__class__.objects.filter(pk=customer.pk).update(
                store_credit_balance=F("store_credit_balance") - amount
            )

        return payment

    @transaction.atomic
    def split_payment(self, payments: list[dict]) -> list[POSPayment]:
        """
        Process multiple payments in one go.

        ``payments`` is a list of dicts, each with at least ``method``
        and ``amount`` (Decimal).  Extra keys are passed through as
        keyword arguments to the per-method processor.
        """
        results: list[POSPayment] = []
        for pay_spec in payments:
            method = pay_spec["method"]
            amount = Decimal(str(pay_spec["amount"]))

            if method == PAYMENT_METHOD_CASH:
                amt_tendered = Decimal(str(pay_spec.get("tendered_amount", pay_spec.get("amount_tendered", amount))))
                results.append(self.process_cash_payment(amt_tendered))
            elif method == PAYMENT_METHOD_CARD:
                results.append(
                    self.process_card_payment(
                        amount,
                        authorization_code=pay_spec.get("authorization_code", ""),
                        reference_number=pay_spec.get("reference_number", ""),
                    )
                )
            elif method == PAYMENT_METHOD_STORE_CREDIT:
                results.append(self.process_store_credit(amount))
            else:
                results.append(
                    self.process_mobile_payment(
                        amount,
                        reference_number=pay_spec.get("reference_number", ""),
                        method=method,
                    )
                )
        return results

    # ── transaction lifecycle ───────────────────────────────────────

    @transaction.atomic
    def complete_transaction(self) -> dict:
        """
        Finalise the cart after full payment.

        Updates cart status to COMPLETED, increments session counters,
        and returns receipt data.  Inventory deduction and order creation
        are handled by downstream modules when available.
        """
        if not self.can_complete_cart():
            raise ValueError(
                "Cannot complete — outstanding balance: "
                f"LKR {self.get_remaining_amount()}"
            )

        # Mark cart completed
        self.cart.status = CART_STATUS_COMPLETED
        self.cart.completed_at = timezone.now()
        self.cart.save(update_fields=["status", "completed_at", "updated_on"])

        # Update session counters
        session = self.cart.session
        from django.db.models import F

        session.__class__.objects.filter(pk=session.pk).update(
            transaction_count=F("transaction_count") + 1,
            total_sales=F("total_sales") + self.cart.grand_total,
        )

        receipt_data = self.generate_receipt_data()
        return {
            "cart": self.cart,
            "receipt_data": receipt_data,
        }

    def validate_payment_amount(self, amount: Decimal) -> None:
        """Validate that a payment amount is positive and within remaining."""
        if not amount or amount <= 0:
            raise ValueError("Payment amount must be positive")
        remaining = self.get_remaining_amount()
        if amount > remaining:
            raise ValueError(
                f"Amount LKR {amount} exceeds remaining LKR {remaining}"
            )

    def get_payment_summary(self) -> dict:
        """Return a comprehensive summary of all payments for this cart."""
        payments = self.cart.payments.all()
        summary = {
            "total_completed": Decimal("0.00"),
            "total_pending": Decimal("0.00"),
            "total_failed": Decimal("0.00"),
            "total_voided": Decimal("0.00"),
            "total_refunded": Decimal("0.00"),
            "by_method": {},
            "by_status": {},
            "payment_count": payments.count(),
            "remaining": self.get_remaining_amount(),
            "can_complete": self.can_complete_cart(),
        }
        for payment in payments:
            amount = payment.amount or Decimal("0.00")
            # By status
            if payment.status == PAYMENT_STATUS_COMPLETED:
                summary["total_completed"] += amount
            elif payment.status == PAYMENT_STATUS_PENDING:
                summary["total_pending"] += amount
            elif payment.status == PAYMENT_STATUS_FAILED:
                summary["total_failed"] += amount
            elif payment.status == PAYMENT_STATUS_VOIDED:
                summary["total_voided"] += amount
            # By method
            method_key = payment.method
            if method_key not in summary["by_method"]:
                summary["by_method"][method_key] = Decimal("0.00")
            if payment.status == PAYMENT_STATUS_COMPLETED:
                summary["by_method"][method_key] += amount
            # By status counts
            if payment.status not in summary["by_status"]:
                summary["by_status"][payment.status] = 0
            summary["by_status"][payment.status] += 1

        return summary

    def get_failed_payments(self):
        """Return failed payments for potential retry."""
        return self.cart.payments.filter(
            status=PAYMENT_STATUS_FAILED
        ).order_by("-created_on")

    @transaction.atomic
    def void_transaction(self, reason: str = "") -> "POSPayment":
        """Void all payments and mark the cart as VOIDED."""
        if self.cart.status == CART_STATUS_COMPLETED:
            raise ValueError("Cannot void completed transaction — use refund.")
        if self.cart.status != CART_STATUS_ACTIVE:
            raise ValueError(f"Cannot void cart with status: {self.cart.status}")

        void_reason = reason or "Transaction voided"

        # Reverse store credit for completed store_credit payments
        from django.db.models import F

        for payment in self.cart.payments.filter(
            method=PAYMENT_METHOD_STORE_CREDIT,
            status=PAYMENT_STATUS_COMPLETED,
        ):
            if self.cart.customer:
                self.cart.customer.__class__.objects.filter(
                    pk=self.cart.customer.pk
                ).update(
                    store_credit_balance=F("store_credit_balance") + payment.amount
                )

        # Void payments individually to retain notes
        for payment in self.cart.payments.filter(
            status__in=[PAYMENT_STATUS_COMPLETED, PAYMENT_STATUS_PENDING]
        ):
            payment.status = PAYMENT_STATUS_VOIDED
            payment.voided_at = timezone.now()
            payment.notes = f"{payment.notes}\nVoided: {void_reason}".strip()
            payment.save(update_fields=["status", "voided_at", "notes", "updated_on"])

        # Void cart
        self.cart.status = CART_STATUS_VOIDED
        self.cart.voided_at = timezone.now()
        self.cart.notes = f"{self.cart.notes}\nVoided: {void_reason}".strip()
        self.cart.save(update_fields=["status", "voided_at", "notes", "updated_on"])
        return self.cart

    # ── receipt data ────────────────────────────────────────────────

    def generate_receipt_data(self) -> dict:
        """Build a dict suitable for receipt rendering / printing."""
        terminal = self.cart.session.terminal
        payments = list(
            self.cart.payments.filter(status=PAYMENT_STATUS_COMPLETED).values(
                "method", "amount", "amount_tendered", "change_due", "paid_at"
            )
        )
        items = list(
            self.cart.items.select_related("product").values(
                "product__name",
                "quantity",
                "unit_price",
                "line_total",
                "discount_amount",
                "tax_amount",
            )
        )

        # Store information
        store_info = {}
        currency = "LKR"
        try:
            from django.conf import settings as django_settings

            store_info = {
                "store_name": getattr(django_settings, "STORE_NAME", ""),
                "store_address": getattr(django_settings, "STORE_ADDRESS", ""),
                "store_phone": getattr(django_settings, "STORE_PHONE", ""),
                "business_reg": getattr(django_settings, "BUSINESS_REG_NUMBER", ""),
                "tax_id": getattr(django_settings, "TAX_IDENTIFICATION_NUMBER", ""),
            }
            currency = getattr(django_settings, "DEFAULT_CURRENCY", "LKR")
        except Exception:
            pass

        # Customer information
        customer_info = None
        if self.cart.customer:
            customer_info = {
                "name": str(self.cart.customer),
                "phone": getattr(self.cart.customer, "phone", ""),
                "email": getattr(self.cart.customer, "email", ""),
            }

        return {
            "store": store_info,
            "terminal_name": terminal.name,
            "terminal_code": terminal.code,
            "receipt_header": terminal.receipt_header,
            "receipt_footer": terminal.receipt_footer,
            "session_number": self.cart.session.session_number,
            "reference_number": self.cart.reference_number,
            "cashier": str(self.user),
            "customer": customer_info,
            "items": items,
            "subtotal": str(self.cart.subtotal),
            "discount_total": str(self.cart.discount_total),
            "tax_total": str(self.cart.tax_total),
            "grand_total": str(self.cart.grand_total),
            "payments": payments,
            "completed_at": (
                self.cart.completed_at.isoformat() if self.cart.completed_at else None
            ),
            "currency": currency,
            "print_time": timezone.now().isoformat(),
        }
