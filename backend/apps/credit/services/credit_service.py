"""
CreditService for credit operations business logic.

Handles credit purchases, payments, balance calculations,
aging analysis, statements, interest, and suspension.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone

from apps.credit.constants import CreditStatus, TransactionType
from apps.credit.models.credit_transaction import CreditTransaction, CreditTransactionStatus

logger = logging.getLogger(__name__)


class InsufficientCreditError(Exception):
    """Raised when available credit is insufficient."""
    pass


class CreditAccountError(Exception):
    """Raised for credit account state errors."""
    pass


class CreditService:
    """
    Main service for credit operations.

    Encapsulates business logic for credit purchases, payments,
    balance tracking, aging analysis, and statement generation.
    """

    def __init__(self, credit_account):
        self.credit_account = credit_account

    # ── Transaction Number ──────────────────────────────────────────

    @staticmethod
    def generate_transaction_number():
        """Generate a unique transaction number: CT-YYYY-NNNNN."""
        year = timezone.now().year
        prefix = f"CT-{year}-"
        last_txn = (
            CreditTransaction.objects
            .filter(transaction_number__startswith=prefix)
            .order_by("-transaction_number")
            .first()
        )
        if last_txn:
            try:
                seq = int(last_txn.transaction_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:05d}"

    # ── Validation Helpers ──────────────────────────────────────────

    def _validate_amount(self, amount):
        """Ensure amount is a positive Decimal."""
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        return amount

    def _validate_active_account(self):
        """Ensure the credit account is active."""
        if self.credit_account.status != CreditStatus.ACTIVE:
            raise CreditAccountError(
                f"Credit account is {self.credit_account.get_status_display()}. "
                f"Only active accounts can transact."
            )

    # ── Task 23: Credit Purchase ────────────────────────────────────

    @transaction.atomic
    def record_purchase(self, amount, reference_type="", reference_id=None, notes="", user=None):
        """
        Record a purchase on credit.

        Creates a transaction and updates the credit account balance.
        """
        amount = self._validate_amount(amount)
        self._validate_active_account()

        if amount > self.credit_account.available_credit:
            raise InsufficientCreditError(
                f"Insufficient credit. Available: {self.credit_account.available_credit}, "
                f"Required: {amount}"
            )

        due_date = self.credit_account.calculate_due_date()
        new_balance = self.credit_account.outstanding_balance + amount

        txn = CreditTransaction.objects.create(
            credit_account=self.credit_account,
            transaction_number=self.generate_transaction_number(),
            transaction_type=TransactionType.CREDIT_PURCHASE,
            amount=amount,
            balance_after=new_balance,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            processed_by=user,
            transaction_date=timezone.now(),
            due_date=due_date,
            effective_date=date.today(),
        )

        self.credit_account.outstanding_balance = new_balance
        self.credit_account.available_credit = (
            self.credit_account.credit_limit - new_balance
        )
        self.credit_account.last_purchase_date = date.today()
        if not self.credit_account.next_payment_due or due_date < self.credit_account.next_payment_due:
            self.credit_account.next_payment_due = due_date
        self.credit_account.save()

        logger.info(
            "Credit purchase Rs. %s for %s (txn %s)",
            amount, self.credit_account.customer, txn.transaction_number,
        )
        return txn

    # ── Task 24: Credit Payment ─────────────────────────────────────

    @transaction.atomic
    def record_payment(self, amount, payment_method="", payment_reference="", notes="", user=None):
        """
        Record a payment received from customer.

        Creates a payment transaction and updates the credit account.
        """
        amount = self._validate_amount(amount)

        if amount > self.credit_account.outstanding_balance:
            amount = self.credit_account.outstanding_balance

        new_balance = self.credit_account.outstanding_balance - amount

        txn = CreditTransaction.objects.create(
            credit_account=self.credit_account,
            transaction_number=self.generate_transaction_number(),
            transaction_type=TransactionType.PAYMENT,
            amount=amount,
            balance_after=new_balance,
            notes=notes,
            processed_by=user,
            payment_method=payment_method,
            payment_reference=payment_reference,
            transaction_date=timezone.now(),
            paid_date=date.today(),
            effective_date=date.today(),
        )

        self.credit_account.outstanding_balance = new_balance
        self.credit_account.available_credit = (
            self.credit_account.credit_limit - new_balance
        )
        self.credit_account.last_payment_date = date.today()
        self.credit_account.total_payments_made += 1
        self.credit_account.save()

        logger.info(
            "Credit payment Rs. %s from %s (txn %s)",
            amount, self.credit_account.customer, txn.transaction_number,
        )
        return txn

    # ── Task 25: Credit Limit Check ─────────────────────────────────

    @staticmethod
    def check_credit_limit(credit_account, amount):
        """
        Check if a purchase amount is within credit limit.

        Returns (bool, str) - (can_purchase, message).
        """
        amount = Decimal(str(amount))

        if credit_account.status != CreditStatus.ACTIVE:
            return False, f"Credit account is {credit_account.get_status_display()}."

        if amount > credit_account.available_credit:
            return False, (
                f"Insufficient credit. Available: Rs. {credit_account.available_credit:,.2f}, "
                f"Required: Rs. {amount:,.2f}"
            )

        return True, "Credit available."

    # ── Task 26: Balance Calculator ─────────────────────────────────

    def calculate_balance(self):
        """
        Calculate outstanding balance from transactions.

        Returns calculated balance for verification against stored value.
        """
        purchases = (
            self.credit_account.transactions
            .filter(
                transaction_type__in=[
                    TransactionType.CREDIT_PURCHASE,
                    TransactionType.INTEREST,
                ],
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        payments = (
            self.credit_account.transactions
            .filter(
                transaction_type__in=[
                    TransactionType.PAYMENT,
                    TransactionType.WRITE_OFF,
                ],
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        adjustments = (
            self.credit_account.transactions
            .filter(
                transaction_type=TransactionType.ADJUSTMENT,
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        return purchases - payments + adjustments

    # ── Task 27: Aging Buckets Calculator ───────────────────────────

    def calculate_aging_buckets(self):
        """
        Calculate aging buckets: Current, 1-30, 31-60, 61-90, 90+ days.

        Returns dict with bucket amounts based on due dates.
        """
        today = date.today()
        purchase_txns = (
            self.credit_account.transactions
            .filter(
                transaction_type=TransactionType.CREDIT_PURCHASE,
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
                due_date__isnull=False,
            )
        )

        buckets = {
            "current": Decimal("0.00"),
            "days_1_30": Decimal("0.00"),
            "days_31_60": Decimal("0.00"),
            "days_61_90": Decimal("0.00"),
            "days_over_90": Decimal("0.00"),
            "total": Decimal("0.00"),
        }

        for txn in purchase_txns:
            days_overdue = (today - txn.due_date).days
            if days_overdue <= 0:
                buckets["current"] += txn.amount
            elif days_overdue <= 30:
                buckets["days_1_30"] += txn.amount
            elif days_overdue <= 60:
                buckets["days_31_60"] += txn.amount
            elif days_overdue <= 90:
                buckets["days_61_90"] += txn.amount
            else:
                buckets["days_over_90"] += txn.amount

        buckets["total"] = sum(
            v for k, v in buckets.items() if k != "total"
        )
        return buckets

    # ── Task 28: Credit Statement ───────────────────────────────────

    def get_statement(self, start_date=None, end_date=None):
        """
        Generate a credit statement for the given date range.

        Returns dict with opening balance, transactions, and closing balance.
        """
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        transactions = (
            self.credit_account.transactions
            .filter(
                effective_date__gte=start_date,
                effective_date__lte=end_date,
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
            )
            .order_by("transaction_date")
        )

        # Calculate opening balance from transactions before start_date
        prior_purchases = (
            self.credit_account.transactions
            .filter(
                effective_date__lt=start_date,
                transaction_type__in=[
                    TransactionType.CREDIT_PURCHASE,
                    TransactionType.INTEREST,
                ],
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        prior_payments = (
            self.credit_account.transactions
            .filter(
                effective_date__lt=start_date,
                transaction_type__in=[
                    TransactionType.PAYMENT,
                    TransactionType.WRITE_OFF,
                ],
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        opening_balance = prior_purchases - prior_payments

        return {
            "customer": str(self.credit_account.customer),
            "credit_limit": self.credit_account.credit_limit,
            "start_date": start_date,
            "end_date": end_date,
            "opening_balance": opening_balance,
            "transactions": list(transactions.values(
                "transaction_number",
                "transaction_type",
                "amount",
                "balance_after",
                "transaction_date",
                "due_date",
                "paid_date",
                "notes",
            )),
            "closing_balance": self.credit_account.outstanding_balance,
        }

    # ── Task 29: Interest Calculation ───────────────────────────────

    @transaction.atomic
    def calculate_interest(self, user=None):
        """
        Calculate and apply interest on overdue amounts.

        Returns the interest transaction or None if no interest due.
        """
        if not self.credit_account.interest_rate_annual:
            return None

        overdue_txns = (
            self.credit_account.transactions
            .filter(
                transaction_type=TransactionType.CREDIT_PURCHASE,
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
                due_date__lt=date.today(),
            )
        )

        total_interest = Decimal("0.00")
        daily_rate = self.credit_account.interest_rate_annual / Decimal("365") / Decimal("100")

        for txn in overdue_txns:
            days_overdue = max(
                0,
                (date.today() - txn.due_date).days
                - self.credit_account.grace_period_days,
            )
            if days_overdue <= 0:
                continue
            interest = txn.amount * daily_rate * days_overdue
            total_interest += interest

        if total_interest <= Decimal("0.01"):
            return None

        total_interest = total_interest.quantize(Decimal("0.01"))
        new_balance = self.credit_account.outstanding_balance + total_interest

        interest_txn = CreditTransaction.objects.create(
            credit_account=self.credit_account,
            transaction_number=self.generate_transaction_number(),
            transaction_type=TransactionType.INTEREST,
            amount=total_interest,
            balance_after=new_balance,
            notes=f"Interest charge at {self.credit_account.interest_rate_annual}% p.a.",
            processed_by=user,
            interest_amount=total_interest,
            interest_rate_applied=self.credit_account.interest_rate_annual,
            transaction_date=timezone.now(),
            effective_date=date.today(),
        )

        self.credit_account.outstanding_balance = new_balance
        self.credit_account.available_credit = (
            self.credit_account.credit_limit - new_balance
        )
        self.credit_account.save()

        logger.info(
            "Interest Rs. %s charged to %s",
            total_interest, self.credit_account.customer,
        )
        return interest_txn

    # ── Task 32: Credit Suspension ──────────────────────────────────

    @transaction.atomic
    def suspend_account(self, reason="", user=None):
        """Suspend the credit account."""
        self.credit_account.status = CreditStatus.SUSPENDED
        self.credit_account.suspended_by = user
        self.credit_account.suspended_at = timezone.now()
        self.credit_account.suspended_reason = reason
        self.credit_account.save()
        logger.info("Credit account suspended for %s: %s", self.credit_account.customer, reason)

    @transaction.atomic
    def reactivate_account(self, user=None):
        """Reactivate a suspended credit account."""
        self.credit_account.status = CreditStatus.ACTIVE
        self.credit_account.suspended_by = None
        self.credit_account.suspended_at = None
        self.credit_account.suspended_reason = ""
        self.credit_account.save()
        logger.info("Credit account reactivated for %s", self.credit_account.customer)

    def check_auto_suspension(self):
        """Check if account should be auto-suspended based on risk."""
        from apps.credit.models.credit_settings import CreditSettings

        try:
            from django.db import connection
            tenant = connection.tenant
            settings = CreditSettings.objects.get_or_create_for_tenant(tenant)
        except Exception:
            return False

        if (
            self.credit_account.late_payment_count
            >= settings.auto_suspend_after_late_payments
        ):
            self.suspend_account(reason="Exceeded maximum late payments.")
            return True

        if self.credit_account.risk_score >= settings.auto_suspend_risk_score:
            self.suspend_account(reason="Risk score exceeded threshold.")
            return True

        # Over-limit check
        if (
            self.credit_account.outstanding_balance
            > self.credit_account.credit_limit
        ):
            self.suspend_account(reason="Outstanding balance exceeds credit limit.")
            return True

        # Severe overdue check (90+ days)
        severe_overdue = (
            self.credit_account.transactions
            .filter(
                transaction_type=TransactionType.CREDIT_PURCHASE,
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
                due_date__lt=date.today() - timedelta(days=90),
            )
            .exists()
        )
        if severe_overdue:
            self.suspend_account(reason="Transaction(s) overdue by 90+ days.")
            return True

        return False

    # ── Adjustment & Write-off ──────────────────────────────────────

    @transaction.atomic
    def record_adjustment(self, amount, notes="", user=None):
        """Record a manual balance adjustment (positive increases, negative decreases)."""
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        new_balance = self.credit_account.outstanding_balance + amount

        txn = CreditTransaction.objects.create(
            credit_account=self.credit_account,
            transaction_number=self.generate_transaction_number(),
            transaction_type=TransactionType.ADJUSTMENT,
            amount=amount,
            balance_after=new_balance,
            notes=notes,
            processed_by=user,
            transaction_date=timezone.now(),
            effective_date=date.today(),
        )

        self.credit_account.outstanding_balance = new_balance
        self.credit_account.available_credit = (
            self.credit_account.credit_limit - new_balance
        )
        self.credit_account.save()

        logger.info(
            "Credit adjustment Rs. %s for %s (txn %s)",
            amount, self.credit_account.customer, txn.transaction_number,
        )
        return txn

    @transaction.atomic
    def write_off(self, amount, notes="", user=None):
        """Write off bad debt."""
        amount = self._validate_amount(amount)

        if amount > self.credit_account.outstanding_balance:
            amount = self.credit_account.outstanding_balance

        new_balance = self.credit_account.outstanding_balance - amount

        txn = CreditTransaction.objects.create(
            credit_account=self.credit_account,
            transaction_number=self.generate_transaction_number(),
            transaction_type=TransactionType.WRITE_OFF,
            amount=amount,
            balance_after=new_balance,
            notes=notes,
            processed_by=user,
            transaction_date=timezone.now(),
            effective_date=date.today(),
        )

        self.credit_account.outstanding_balance = new_balance
        # Write-off does not increase available credit
        self.credit_account.credit_limit -= amount
        self.credit_account.available_credit = (
            self.credit_account.credit_limit - new_balance
        )
        self.credit_account.save()

        logger.info(
            "Credit write-off Rs. %s for %s (txn %s)",
            amount, self.credit_account.customer, txn.transaction_number,
        )
        return txn

    def get_overdue_amount(self):
        """Calculate total overdue amount."""
        overdue_txns = (
            self.credit_account.transactions
            .filter(
                transaction_type=TransactionType.CREDIT_PURCHASE,
                is_reversed=False,
                status=CreditTransactionStatus.COMPLETED,
                due_date__lt=date.today(),
            )
            .aggregate(total=Sum("amount"))
        )
        return overdue_txns["total"] or Decimal("0.00")
