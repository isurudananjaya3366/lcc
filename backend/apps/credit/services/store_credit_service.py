"""
Store Credit service layer.

Provides atomic operations for issuing, redeeming, and checking
store credit balances with full transaction audit trail.
"""

from decimal import Decimal

from django.db import transaction as db_transaction
from django.utils import timezone

from apps.credit.constants import StoreCreditSource, StoreCreditTransactionType
from apps.credit.models.store_credit import StoreCredit, StoreCreditTransaction


class InsufficientStoreCreditError(Exception):
    """Raised when a redemption exceeds the available balance."""


class StoreCreditError(Exception):
    """General store-credit error."""


class StoreCreditService:
    """Business logic for store credit operations."""

    # ── Issue ───────────────────────────────────────────────────────

    @staticmethod
    def issue_credit(
        customer_id,
        amount,
        source=StoreCreditSource.ADJUSTMENT,
        reference="",
        issued_by=None,
        expiry_days=None,
        notes="",
    ):
        """
        Issue store credit to a customer.

        Creates or updates the customer's StoreCredit account, updates
        the balance, and records an ISSUE transaction.

        Args:
            customer_id: UUID of the customer.
            amount: Decimal amount to issue (must be > 0).
            source: StoreCreditSource choice.
            reference: Order/invoice reference string.
            issued_by: User who issued the credit (nullable).
            expiry_days: Optional int – set expiry N days from today.
            notes: Free-text notes.

        Returns:
            dict with success, credit, transaction, new_balance, message.

        Raises:
            StoreCreditError on validation failures.
        """
        if amount <= 0:
            raise StoreCreditError("Amount must be positive.")

        with db_transaction.atomic():
            from datetime import date, timedelta

            credit, _created = StoreCredit.objects.select_for_update().get_or_create(
                customer_id=customer_id,
                defaults={
                    "balance": Decimal("0.00"),
                    "created_from": source,
                    "issued_by": issued_by,
                },
            )

            balance_before = credit.balance

            credit.balance += amount
            credit.total_issued += amount
            credit.last_transaction_at = timezone.now()

            if expiry_days is not None:
                credit.expiry_date = date.today() + timedelta(days=expiry_days)

            credit.save()

            txn = StoreCreditTransaction.objects.create(
                store_credit=credit,
                transaction_type=StoreCreditTransactionType.ISSUE,
                amount=amount,
                balance_before=balance_before,
                balance_after=credit.balance,
                reference=reference,
                performed_by=issued_by,
                notes=notes,
            )

            return {
                "success": True,
                "credit": credit,
                "transaction": txn,
                "new_balance": credit.balance,
                "message": f"Successfully issued Rs. {amount} credit.",
            }

    # ── Redeem ──────────────────────────────────────────────────────

    @staticmethod
    def redeem_credit(
        customer_id,
        amount,
        order_id=None,
        performed_by=None,
        notes="",
    ):
        """
        Redeem store credit for an order or other purpose.

        Validates balance, checks expiry, deducts amount, and records
        a REDEEM transaction.

        Args:
            customer_id: UUID of the customer.
            amount: Decimal amount to redeem (must be > 0).
            order_id: Optional UUID of the related order.
            performed_by: User performing redemption (nullable).
            notes: Free-text notes.

        Returns:
            dict with success, credit, transaction, redeemed_amount,
            remaining_balance, message.

        Raises:
            InsufficientStoreCreditError on insufficient balance.
            StoreCreditError on other validation failures.
        """
        if amount <= 0:
            raise StoreCreditError("Amount must be positive.")

        with db_transaction.atomic():
            try:
                credit = StoreCredit.objects.select_for_update().get(
                    customer_id=customer_id,
                )
            except StoreCredit.DoesNotExist:
                raise StoreCreditError("No store credit account found.")

            if credit.is_expired:
                raise StoreCreditError("Store credit has expired.")

            available = credit.get_available_balance()
            if amount > available:
                raise InsufficientStoreCreditError(
                    f"Insufficient credit. Available: Rs. {available}"
                )

            balance_before = credit.balance

            credit.balance -= amount
            credit.total_used += amount
            credit.last_transaction_at = timezone.now()
            credit.save()

            reference = str(order_id) if order_id else ""
            txn = StoreCreditTransaction.objects.create(
                store_credit=credit,
                transaction_type=StoreCreditTransactionType.REDEEM,
                amount=-amount,
                balance_before=balance_before,
                balance_after=credit.balance,
                reference=reference,
                performed_by=performed_by,
                notes=notes or (f"Redeemed for order {order_id}" if order_id else ""),
            )

            return {
                "success": True,
                "credit": credit,
                "transaction": txn,
                "redeemed_amount": amount,
                "remaining_balance": credit.balance,
                "message": f"Successfully redeemed Rs. {amount} credit.",
            }

    # ── Balance Check ───────────────────────────────────────────────

    @staticmethod
    def check_balance(customer_id):
        """
        Return a detailed balance breakdown for a customer.

        Returns:
            dict with current_balance, available_balance, total_issued,
            total_used, expiry_date, days_until_expiry, is_expired.
        """
        try:
            credit = StoreCredit.objects.get(customer_id=customer_id)
        except StoreCredit.DoesNotExist:
            return {
                "has_credit": False,
                "current_balance": Decimal("0.00"),
                "available_balance": Decimal("0.00"),
                "total_issued": Decimal("0.00"),
                "total_used": Decimal("0.00"),
                "expiry_date": None,
                "days_until_expiry": None,
                "is_expired": False,
            }

        return {
            "has_credit": credit.balance > 0,
            "current_balance": credit.balance,
            "available_balance": credit.get_available_balance(),
            "total_issued": credit.total_issued,
            "total_used": credit.total_used,
            "expiry_date": credit.expiry_date,
            "days_until_expiry": credit.days_until_expiry,
            "is_expired": credit.is_expired,
        }

    @staticmethod
    def calculate_max_redemption(customer_id, order_total):
        """Return the maximum amount redeemable against an order."""
        try:
            credit = StoreCredit.objects.get(customer_id=customer_id)
            available = credit.get_available_balance()
            return min(available, order_total)
        except StoreCredit.DoesNotExist:
            return Decimal("0.00")

    @staticmethod
    def can_redeem(customer_id, amount):
        """Quick boolean check: can the customer redeem this amount?"""
        try:
            credit = StoreCredit.objects.get(customer_id=customer_id)
            return credit.has_balance(amount)
        except StoreCredit.DoesNotExist:
            return False

    @staticmethod
    def needs_expiry_reminder(customer_id, days_before=7):
        """Check if the customer should receive an expiry reminder."""
        try:
            credit = StoreCredit.objects.get(customer_id=customer_id)
            return credit.should_send_expiry_reminder(days_before=days_before)
        except StoreCredit.DoesNotExist:
            return False
