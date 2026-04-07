"""
Payment service.

Central business logic layer for all payment operations including
recording, validation, status management, and invoice allocation.
"""

import logging
from decimal import Decimal, InvalidOperation

from django.db import models, transaction
from django.utils import timezone

from apps.payments.constants import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATES,
    PaymentMethod,
    PaymentStatus,
)
from apps.payments.exceptions import (
    DuplicatePaymentError,
    InsufficientPaymentError,
    InvalidPaymentStatusTransition,
    PaymentValidationError,
)

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Service layer for payment recording and management.

    Handles all payment operations with proper transaction management,
    validation, and audit logging.
    """

    # ── Base Operations ─────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def create_payment(
        amount,
        method,
        invoice=None,
        order=None,
        customer=None,
        user=None,
        payment_date=None,
        currency="LKR",
        exchange_rate=None,
        method_details=None,
        reference_number="",
        transaction_id="",
        notes="",
        internal_notes="",
        status=None,
    ):
        """
        Create a new payment record.

        Args:
            amount: Payment amount (Decimal).
            method: PaymentMethod choice.
            invoice: Optional Invoice instance.
            order: Optional Order instance.
            customer: Optional Customer instance.
            user: User recording the payment.
            payment_date: Date of payment (defaults to today).
            currency: ISO 4217 currency code.
            exchange_rate: Exchange rate to LKR.
            method_details: Dict of method-specific details.
            reference_number: External reference.
            transaction_id: Gateway transaction ID.
            notes: Customer-visible notes.
            internal_notes: Internal notes.
            status: Override initial status (defaults to PENDING).

        Returns:
            Payment: The created payment instance.
        """
        from apps.payments.models import Payment
        from apps.payments.services.number_generator import PaymentNumberGenerator

        if payment_date is None:
            payment_date = timezone.now().date()

        if status is None:
            status = PaymentStatus.PENDING

        amount_in_base = None
        if exchange_rate and currency != "LKR":
            amount_in_base = (amount * exchange_rate).quantize(Decimal("0.01"))

        payment = Payment.objects.create(
            payment_number=PaymentNumberGenerator.generate(),
            amount=amount,
            method=method,
            status=status,
            invoice=invoice,
            order=order,
            customer=customer,
            payment_date=payment_date,
            processed_at=timezone.now() if status == PaymentStatus.COMPLETED else None,
            currency=currency,
            exchange_rate=exchange_rate,
            amount_in_base_currency=amount_in_base,
            method_details=method_details,
            reference_number=reference_number,
            transaction_id=transaction_id,
            received_by=user,
            notes=notes,
            internal_notes=internal_notes,
        )

        PaymentService._log_history(
            payment, "CREATED", user=user, new_value={"status": status, "amount": str(amount)}
        )

        logger.info("Payment created: %s for %s via %s", payment.payment_number, amount, method)
        return payment

    @staticmethod
    def get_payment(payment_id):
        """Retrieve a payment by ID with related objects."""
        from apps.payments.models import Payment

        return (
            Payment.objects.select_related("customer", "invoice", "order", "received_by", "approved_by")
            .filter(id=payment_id)
            .first()
        )

    # ── Method-Specific Recording ───────────────────────────────────

    @staticmethod
    @transaction.atomic
    def record_cash_payment(
        amount,
        user,
        amount_tendered=None,
        invoice=None,
        order=None,
        customer=None,
        register_id=None,
        notes="",
    ):
        """
        Record a cash payment with immediate completion.

        Args:
            amount: Payment amount.
            user: Cashier/user recording the payment.
            amount_tendered: Amount given by customer (optional, defaults to exact amount).
            invoice: Optional linked invoice.
            order: Optional linked order.
            customer: Optional customer.
            register_id: Optional POS register ID.
            notes: Optional notes.

        Returns:
            dict: {payment, change_given}
        """
        if amount_tendered is None:
            amount_tendered = amount

        if amount_tendered < amount:
            raise InsufficientPaymentError(
                f"Amount tendered ({amount_tendered}) is less than payment amount ({amount})."
            )

        change_given = amount_tendered - amount

        method_details = {
            "amount_tendered": str(amount_tendered),
            "change_given": str(change_given),
        }
        if register_id:
            method_details["register_id"] = register_id

        payment = PaymentService.create_payment(
            amount=amount,
            method=PaymentMethod.CASH,
            status=PaymentStatus.COMPLETED,
            invoice=invoice,
            order=order,
            customer=customer,
            user=user,
            method_details=method_details,
            notes=notes,
        )

        return {"payment": payment, "change_given": change_given}

    @staticmethod
    @transaction.atomic
    def record_card_payment(
        amount,
        card_details,
        user,
        invoice=None,
        order=None,
        customer=None,
        immediate_approval=True,
        notes="",
    ):
        """
        Record a card payment (Visa/MasterCard/AMEX).

        Args:
            amount: Payment amount.
            card_details: Dict with card_type, last_four, approval_code.
            user: User recording the payment.
            invoice: Optional linked invoice.
            order: Optional linked order.
            customer: Optional customer.
            immediate_approval: If True, mark completed immediately.
            notes: Optional notes.

        Returns:
            Payment instance.
        """
        required = ["card_type", "last_four"]
        missing = [f for f in required if f not in card_details]
        if missing:
            raise PaymentValidationError(f"Missing card details: {', '.join(missing)}")

        safe_details = {
            "card_type": card_details.get("card_type", ""),
            "last_four": card_details.get("last_four", ""),
            "approval_code": card_details.get("approval_code", ""),
            "terminal_id": card_details.get("terminal_id", ""),
        }

        status = PaymentStatus.COMPLETED if immediate_approval else PaymentStatus.PENDING

        return PaymentService.create_payment(
            amount=amount,
            method=PaymentMethod.CARD,
            status=status,
            invoice=invoice,
            order=order,
            customer=customer,
            user=user,
            method_details=safe_details,
            reference_number=card_details.get("approval_code", ""),
            notes=notes,
        )

    @staticmethod
    @transaction.atomic
    def record_bank_transfer(
        amount,
        bank_details,
        user,
        invoice=None,
        order=None,
        customer=None,
        notes="",
    ):
        """
        Record a bank transfer payment.

        Args:
            amount: Payment amount.
            bank_details: Dict with bank_name, reference_number.
            user: User recording the payment.
            invoice: Optional linked invoice.
            order: Optional linked order.
            customer: Optional customer.
            notes: Optional notes.

        Returns:
            Payment instance.
        """
        safe_details = {
            "bank_name": bank_details.get("bank_name", ""),
            "account_number": bank_details.get("account_number", ""),
            "branch": bank_details.get("branch", ""),
        }

        return PaymentService.create_payment(
            amount=amount,
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
            invoice=invoice,
            order=order,
            customer=customer,
            user=user,
            method_details=safe_details,
            reference_number=bank_details.get("reference_number", ""),
            notes=notes,
        )

    @staticmethod
    @transaction.atomic
    def record_mobile_payment(
        amount,
        mobile_details,
        user,
        invoice=None,
        order=None,
        customer=None,
        notes="",
    ):
        """
        Record a mobile payment (FriMi, etc.).

        Args:
            amount: Payment amount.
            mobile_details: Dict with provider, transaction_id.
            user: User recording the payment.
            invoice: Optional linked invoice.
            order: Optional linked order.
            customer: Optional customer.
            notes: Optional notes.

        Returns:
            Payment instance.
        """
        safe_details = {
            "provider": mobile_details.get("provider", ""),
            "mobile_number": mobile_details.get("mobile_number", ""),
        }

        return PaymentService.create_payment(
            amount=amount,
            method=PaymentMethod.MOBILE,
            status=PaymentStatus.PENDING,
            invoice=invoice,
            order=order,
            customer=customer,
            user=user,
            method_details=safe_details,
            transaction_id=mobile_details.get("transaction_id", ""),
            notes=notes,
        )

    @staticmethod
    @transaction.atomic
    def record_check_payment(
        amount,
        check_details,
        user,
        invoice=None,
        order=None,
        customer=None,
        notes="",
    ):
        """
        Record a check payment.

        Args:
            amount: Payment amount.
            check_details: Dict with check_number, bank_name, check_date.
            user: User recording the payment.
            invoice: Optional linked invoice.
            order: Optional linked order.
            customer: Optional customer.
            notes: Optional notes.

        Returns:
            Payment instance.
        """
        if not check_details.get("check_number"):
            raise PaymentValidationError("Check number is required.")

        safe_details = {
            "check_number": check_details["check_number"],
            "bank_name": check_details.get("bank_name", ""),
            "check_date": check_details.get("check_date", ""),
        }

        return PaymentService.create_payment(
            amount=amount,
            method=PaymentMethod.CHECK,
            status=PaymentStatus.PENDING,
            invoice=invoice,
            order=order,
            customer=customer,
            user=user,
            method_details=safe_details,
            reference_number=check_details["check_number"],
            notes=notes,
        )

    @staticmethod
    @transaction.atomic
    def record_store_credit_payment(
        amount,
        customer,
        user,
        invoice=None,
        order=None,
        notes="",
    ):
        """
        Record a store credit payment, deducting from customer balance.

        Args:
            amount: Payment amount.
            customer: Customer whose credit will be used.
            user: User recording the payment.
            invoice: Optional linked invoice.
            order: Optional linked order.
            notes: Optional notes.

        Returns:
            Payment instance.
        """
        if not customer:
            raise PaymentValidationError("Customer is required for store credit payments.")

        if hasattr(customer, "current_balance") and customer.current_balance < amount:
            raise InsufficientPaymentError(
                f"Insufficient store credit. Available: {customer.current_balance}, Required: {amount}"
            )

        payment = PaymentService.create_payment(
            amount=amount,
            method=PaymentMethod.STORE_CREDIT,
            status=PaymentStatus.COMPLETED,
            invoice=invoice,
            order=order,
            customer=customer,
            user=user,
            method_details={"previous_balance": str(getattr(customer, "current_balance", 0))},
            notes=notes,
        )

        # Deduct from customer balance
        if hasattr(customer, "current_balance"):
            customer.current_balance -= amount
            customer.save(update_fields=["current_balance"])

        return payment

    # ── Order Payment Recording ─────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def record_order_payment(
        order,
        amount,
        method,
        user,
        payment_type="FULL_PAYMENT",
        method_details=None,
        notes="",
    ):
        """
        Record payment for an order.

        Args:
            order: Order instance.
            amount: Payment amount.
            method: PaymentMethod choice.
            user: User recording the payment.
            payment_type: FULL_PAYMENT, DEPOSIT, BALANCE, or COD.
            method_details: Optional method-specific details dict.
            notes: Optional notes.

        Returns:
            dict: {payment, order_payment_status, outstanding_balance, ...}
        """
        from apps.payments.models import Payment

        # Validate order not cancelled
        order_status = getattr(order, "status", "")
        if order_status == "CANCELLED":
            raise PaymentValidationError(f"Order is cancelled.")

        # Calculate total already paid for this order
        total_paid = (
            Payment.objects.filter(
                order=order,
                status__in=[PaymentStatus.PENDING, PaymentStatus.COMPLETED],
            ).aggregate(total=models.Sum("amount"))["total"]
            or Decimal("0.00")
        )

        order_total = getattr(order, "total_amount", None) or getattr(order, "total", Decimal("0"))
        outstanding = order_total - total_paid

        if amount > outstanding:
            raise PaymentValidationError(
                f"Payment amount ({amount}) exceeds order outstanding balance ({outstanding})."
            )

        # Determine status
        status = PaymentStatus.COMPLETED

        payment = PaymentService.create_payment(
            amount=amount,
            method=method,
            status=status,
            order=order,
            customer=getattr(order, "customer", None),
            user=user,
            method_details=method_details,
            notes=notes,
        )

        # Update order payment status if the order has the field
        new_total_paid = total_paid + amount
        new_outstanding = order_total - new_total_paid

        if hasattr(order, "payment_status"):
            if new_total_paid == Decimal("0"):
                order.payment_status = "UNPAID"
            elif new_total_paid < order_total:
                order.payment_status = "DEPOSIT_PAID" if payment_type == "DEPOSIT" else "PARTIALLY_PAID"
            elif new_total_paid >= order_total:
                order.payment_status = "PAID"

            order.save(update_fields=["payment_status"])

        logger.info(
            "Order payment recorded: %s for Order %s, Amount: %s, Type: %s",
            payment.payment_number,
            getattr(order, "order_number", order.pk),
            amount,
            payment_type,
        )

        return {
            "payment": payment,
            "payment_number": payment.payment_number,
            "payment_type": payment_type,
            "amount_paid": amount,
            "total_paid": new_total_paid,
            "outstanding_balance": new_outstanding,
            "order_payment_status": getattr(order, "payment_status", None),
        }

    # ── Multi-Invoice Payment ───────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def record_multi_invoice_payment(
        amount,
        method,
        allocations,
        user,
        customer=None,
        strategy="CUSTOM",
        method_details=None,
        notes="",
    ):
        """
        Record a single payment applied to multiple invoices.

        Args:
            amount: Total payment amount.
            method: PaymentMethod choice.
            allocations: List of dicts [{'invoice': invoice_obj, 'amount': Decimal}, ...].
            user: User recording the payment.
            customer: Optional customer (inferred from invoices if not given).
            strategy: Allocation strategy (CUSTOM, OLDEST_FIRST, PROPORTIONAL, EQUAL).
            method_details: Optional method-specific details dict.
            notes: Optional notes.

        Returns:
            dict: {payment, allocations, ...}
        """
        if not allocations:
            raise PaymentValidationError("At least one invoice allocation is required.")

        total_allocated = sum(Decimal(str(a["amount"])) for a in allocations)

        if total_allocated != amount:
            raise PaymentValidationError(
                f"Total allocations ({total_allocated}) must equal payment amount ({amount})."
            )

        # Validate each allocation
        for alloc in allocations:
            invoice = alloc["invoice"]
            alloc_amount = Decimal(str(alloc["amount"]))
            if hasattr(invoice, "balance_due") and alloc_amount > invoice.balance_due:
                raise PaymentValidationError(
                    f"Allocation to invoice exceeds outstanding balance."
                )

        # Infer customer from invoices if not provided
        if not customer:
            for alloc in allocations:
                inv_customer = getattr(alloc["invoice"], "customer", None)
                if inv_customer:
                    customer = inv_customer
                    break

        # Create the payment (not linked to one specific invoice)
        payment = PaymentService.create_payment(
            amount=amount,
            method=method,
            status=PaymentStatus.COMPLETED,
            customer=customer,
            user=user,
            method_details=method_details,
            notes=notes,
        )

        # Allocate to each invoice
        allocation_results = PaymentService.allocate_to_multiple_invoices(
            payment=payment, allocations=allocations, strategy=strategy
        )

        logger.info(
            "Multi-invoice payment recorded: %s, Amount: %s, Invoices: %d, Strategy: %s",
            payment.payment_number,
            amount,
            len(allocations),
            strategy,
        )

        return {
            "payment": payment,
            "payment_number": payment.payment_number,
            "total_amount": amount,
            "invoice_count": len(allocations),
            "allocations": allocation_results,
        }

    # ── Partial Payment ─────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def record_partial_payment(
        amount,
        method,
        invoice,
        user,
        customer=None,
        method_details=None,
        notes="",
    ):
        """
        Record a partial payment against an invoice.

        Validates amount is positive and does not exceed outstanding balance.
        Creates a Payment, allocates to invoice, and returns result.

        Args:
            amount: Partial payment amount (must be <= outstanding).
            method: PaymentMethod choice.
            invoice: Invoice being partially paid.
            user: User recording the payment.
            customer: Optional customer.
            method_details: Optional method-specific details.
            notes: Optional notes.

        Returns:
            dict: {payment, allocation, invoice_balance}
        """
        amount = Decimal(str(amount))

        if amount <= 0:
            raise PaymentValidationError("Partial payment amount must be positive.")

        outstanding = getattr(invoice, "balance_due", None)
        if outstanding is not None and amount > outstanding:
            raise InsufficientPaymentError(
                f"Partial payment amount ({amount}) exceeds outstanding "
                f"balance ({outstanding})."
            )

        if not customer:
            customer = getattr(invoice, "customer", None)

        payment = PaymentService.create_payment(
            amount=amount,
            method=method,
            invoice=invoice,
            customer=customer,
            user=user,
            status=PaymentStatus.COMPLETED,
            method_details=method_details,
            notes=notes or "Partial payment",
        )

        allocation = PaymentService.allocate_to_invoice(
            payment=payment, invoice=invoice, amount=amount,
        )

        new_outstanding = getattr(invoice, "balance_due", None)

        logger.info(
            "Partial payment recorded: %s for %s against invoice, "
            "remaining balance: %s",
            payment.payment_number,
            amount,
            new_outstanding,
        )

        return {
            "payment": payment,
            "allocation": allocation,
            "invoice_balance": new_outstanding,
        }

    # ── Validation ──────────────────────────────────────────────────

    @staticmethod
    def validate_payment_data(amount, method, invoice=None, customer=None):
        """
        Comprehensive payment validation.

        Args:
            amount: Payment amount.
            method: PaymentMethod choice.
            invoice: Optional invoice to check balance.
            customer: Optional customer for credit checks.

        Raises:
            PaymentValidationError: If validation fails.
        """
        # Validate amount
        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            raise PaymentValidationError("Invalid payment amount.")

        if amount <= 0:
            raise PaymentValidationError("Payment amount must be greater than zero.")

        # Validate method
        valid_methods = [m.value for m in PaymentMethod]
        if method not in valid_methods:
            raise PaymentValidationError(f"Invalid payment method: {method}")

        # Check method is active (if config exists)
        from apps.payments.models import PaymentMethodConfig

        config = PaymentMethodConfig.objects.filter(method=method).first()
        if config:
            if not config.is_active:
                raise PaymentValidationError(f"Payment method '{method}' is not currently active.")
            if config.min_amount and amount < config.min_amount:
                raise PaymentValidationError(
                    f"Amount below minimum ({config.min_amount}) for {method}."
                )
            if config.max_amount and amount > config.max_amount:
                raise PaymentValidationError(
                    f"Amount above maximum ({config.max_amount}) for {method}."
                )

    @staticmethod
    def validate_payment_before_recording(
        amount,
        method,
        customer=None,
        invoice=None,
        method_specific_data=None,
    ):
        """
        Comprehensive payment validation before recording.

        Checks amount, method configuration, daily limits, invoice status,
        store credit balance, and duplicate detection.

        Args:
            amount: Payment amount.
            method: PaymentMethod choice.
            customer: Optional customer.
            invoice: Optional invoice.
            method_specific_data: Optional dict with method-specific fields.

        Returns:
            dict: {'valid': bool, 'errors': list of error messages}
        """
        from apps.payments.models import Payment, PaymentMethodConfig

        errors = []

        # 1. Basic amount validation
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                errors.append("Payment amount must be greater than zero")
            if amount.as_tuple().exponent < -2:
                errors.append("Amount can have maximum 2 decimal places")
            if amount > Decimal("10000000.00"):
                errors.append("Payment amount exceeds maximum limit of Rs. 10,000,000")
        except (InvalidOperation, TypeError, ValueError):
            errors.append("Invalid payment amount format")
            return {"valid": False, "errors": errors}

        # 2. Method configuration validation
        config = PaymentMethodConfig.objects.filter(method=method).first()
        if config:
            if hasattr(config, "is_enabled") and not config.is_enabled:
                errors.append(f"{method} payment method is not enabled")
                return {"valid": False, "errors": errors}

            if not config.is_active:
                errors.append(f"{method} payment method is not active")
                return {"valid": False, "errors": errors}

            if config.min_amount and amount < config.min_amount:
                errors.append(
                    f"Amount is below minimum of Rs. {config.min_amount} for {method}"
                )
            if config.max_amount and amount > config.max_amount:
                errors.append(
                    f"Amount exceeds maximum of Rs. {config.max_amount} for {method}"
                )

            # Daily limit checking
            if hasattr(config, "daily_limit") and config.daily_limit:
                today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_total = (
                    Payment.objects.filter(
                        method=method,
                        created_on__gte=today_start,
                        status__in=[PaymentStatus.PENDING, PaymentStatus.COMPLETED],
                    ).aggregate(total=models.Sum("amount"))["total"]
                    or Decimal("0.00")
                )
                if today_total + amount > config.daily_limit:
                    remaining = config.daily_limit - today_total
                    errors.append(
                        f"Daily limit for {method} would be exceeded. "
                        f"Remaining today: Rs. {remaining}"
                    )

        # 3. Invoice validation
        if invoice:
            inv_status = getattr(invoice, "status", "")
            if inv_status in ("PAID",):
                errors.append(f"Invoice is already paid")
            if inv_status in ("CANCELLED", "VOID"):
                errors.append(f"Invoice is cancelled/void")

        # 4. Store credit balance check
        if method == PaymentMethod.STORE_CREDIT:
            if not customer:
                errors.append("Customer is required for store credit payment")
            elif hasattr(customer, "current_balance") and customer.current_balance < amount:
                errors.append(
                    f"Insufficient store credit. Available: Rs. {customer.current_balance}"
                )

        # 5. Duplicate detection
        if invoice:
            duplicate = PaymentService.check_duplicate_payment(
                amount=amount, method=method, invoice=invoice
            )
            if duplicate:
                errors.append(
                    "Potential duplicate payment detected. "
                    "A similar payment was recorded in the last 5 minutes."
                )

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def check_duplicate_payment(amount, method, invoice=None, minutes=5):
        """
        Check for potential duplicate payment within a time window.

        Returns:
            Payment or None: The potential duplicate if found.
        """
        from apps.payments.models import Payment

        cutoff = timezone.now() - timezone.timedelta(minutes=minutes)
        qs = Payment.objects.filter(
            amount=amount,
            method=method,
            created_on__gte=cutoff,
        ).exclude(status__in=[PaymentStatus.CANCELLED, PaymentStatus.FAILED])

        if invoice:
            qs = qs.filter(invoice=invoice)

        return qs.first()

    # ── Invoice Allocation ──────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def allocate_to_invoice(payment, invoice, amount=None):
        """
        Allocate a payment (or partial amount) to an invoice.

        Args:
            payment: Payment instance.
            invoice: Invoice instance.
            amount: Amount to allocate (defaults to full payment amount).

        Returns:
            PaymentAllocation instance.
        """
        from apps.payments.models import PaymentAllocation

        if amount is None:
            amount = payment.amount

        if amount <= 0:
            raise PaymentValidationError("Allocation amount must be positive.")

        # Check invoice balance
        if hasattr(invoice, "balance_due") and amount > invoice.balance_due:
            raise PaymentValidationError(
                f"Allocation ({amount}) exceeds invoice balance ({invoice.balance_due})."
            )

        allocation = PaymentAllocation.objects.create(
            payment=payment,
            invoice=invoice,
            amount=amount,
        )

        # Update invoice payment tracking
        if hasattr(invoice, "amount_paid"):
            invoice.amount_paid += amount
            invoice.balance_due = invoice.total - invoice.amount_paid
            update_fields = ["amount_paid", "balance_due"]

            # Update invoice status
            if invoice.balance_due <= 0:
                from apps.invoices.constants import InvoiceStatus

                invoice.status = InvoiceStatus.PAID
                update_fields.append("status")
            elif invoice.amount_paid > 0:
                from apps.invoices.constants import InvoiceStatus

                if invoice.status not in ("PAID", "VOID", "CANCELLED"):
                    invoice.status = InvoiceStatus.PARTIAL
                    update_fields.append("status")

            invoice.save(update_fields=update_fields)

        PaymentService._log_history(
            payment,
            "ALLOCATED",
            new_value={
                "invoice_number": getattr(invoice, "invoice_number", str(invoice.pk)),
                "allocated_amount": str(amount),
            },
        )

        logger.info(
            "Allocated %s to invoice %s from payment %s",
            amount,
            getattr(invoice, "invoice_number", invoice.pk),
            payment.payment_number,
        )

        return allocation

    @staticmethod
    @transaction.atomic
    def allocate_to_multiple_invoices(payment, allocations, strategy="CUSTOM"):
        """
        Allocate a single payment to multiple invoices.

        Supports allocation strategies:
            CUSTOM: Use user-specified amounts from allocations list.
            OLDEST_FIRST: Apply to oldest invoices first until funds exhausted.
            PROPORTIONAL: Split proportionally by invoice outstanding amounts.
            EQUAL: Divide equally among invoices.

        Args:
            payment: Payment instance.
            allocations: List of dicts [{invoice, amount}, ...].
                For strategies other than CUSTOM, 'amount' in each dict
                may be omitted; the strategy will calculate amounts.
            strategy: Allocation strategy string.

        Returns:
            list: PaymentAllocation instances.
        """
        if strategy == "OLDEST_FIRST":
            # Sort by creation date / due date ascending (oldest first)
            sorted_allocs = sorted(
                allocations,
                key=lambda a: getattr(a["invoice"], "created_on", getattr(a["invoice"], "issue_date", timezone.now())),
            )
            remaining = payment.amount
            computed = []
            for alloc in sorted_allocs:
                if remaining <= 0:
                    break
                invoice = alloc["invoice"]
                balance = getattr(invoice, "balance_due", payment.amount)
                to_allocate = min(remaining, balance)
                computed.append({"invoice": invoice, "amount": to_allocate})
                remaining -= to_allocate
            allocations = computed

        elif strategy == "PROPORTIONAL":
            total_outstanding = sum(
                getattr(a["invoice"], "balance_due", Decimal("0")) for a in allocations
            )
            if total_outstanding > 0:
                computed = []
                for alloc in allocations:
                    invoice = alloc["invoice"]
                    balance = getattr(invoice, "balance_due", Decimal("0"))
                    proportion = balance / total_outstanding
                    to_allocate = (payment.amount * proportion).quantize(Decimal("0.01"))
                    computed.append({"invoice": invoice, "amount": to_allocate})
                allocations = computed

        elif strategy == "EQUAL":
            count = len(allocations)
            if count > 0:
                per_invoice = (payment.amount / count).quantize(Decimal("0.01"))
                computed = [
                    {"invoice": a["invoice"], "amount": per_invoice}
                    for a in allocations
                ]
                allocations = computed

        # Validate total
        total_allocated = sum(a["amount"] for a in allocations)
        if total_allocated > payment.amount:
            raise PaymentValidationError(
                f"Total allocations ({total_allocated}) exceed payment amount ({payment.amount})."
            )

        results = []
        for alloc in allocations:
            result = PaymentService.allocate_to_invoice(
                payment=payment,
                invoice=alloc["invoice"],
                amount=alloc["amount"],
            )
            results.append(result)

        return results

    # ── Status Updates ──────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def complete_payment(payment, user=None):
        """Mark a payment as completed."""
        PaymentService._transition_status(payment, PaymentStatus.COMPLETED, user)
        payment.processed_at = timezone.now()
        payment.save(update_fields=["status", "processed_at", "updated_on"])
        return payment

    @staticmethod
    @transaction.atomic
    def fail_payment(payment, reason="", user=None):
        """Mark a payment as failed."""
        PaymentService._transition_status(payment, PaymentStatus.FAILED, user)
        payment.internal_notes = (
            f"{payment.internal_notes}\nFailed: {reason}".strip() if reason else payment.internal_notes
        )
        payment.save(update_fields=["status", "internal_notes", "updated_on"])
        return payment

    @staticmethod
    @transaction.atomic
    def cancel_payment(payment, reason="", user=None):
        """Cancel a payment."""
        PaymentService._transition_status(payment, PaymentStatus.CANCELLED, user)
        payment.cancelled_at = timezone.now()
        payment.internal_notes = (
            f"{payment.internal_notes}\nCancelled: {reason}".strip() if reason else payment.internal_notes
        )
        payment.save(update_fields=["status", "cancelled_at", "internal_notes", "updated_on"])
        return payment

    @staticmethod
    @transaction.atomic
    def approve_payment(payment, user):
        """Approve a pending payment."""
        if payment.status != PaymentStatus.PENDING:
            raise InvalidPaymentStatusTransition(payment.status, "APPROVED")
        payment.approved_by = user
        payment.save(update_fields=["approved_by", "updated_on"])
        PaymentService._log_history(
            payment, "APPROVED", user=user, new_value={"approved_by": str(user.pk)}
        )
        return payment

    # ── Fee Calculation ─────────────────────────────────────────────

    @staticmethod
    def calculate_processing_fee(method, amount):
        """
        Calculate processing fee for a payment method.

        Returns:
            Decimal: Fee amount (0.00 if no config).
        """
        from apps.payments.models import PaymentMethodConfig

        config = PaymentMethodConfig.objects.filter(method=method).first()
        if not config or not config.settings:
            return Decimal("0.00")

        fee_type = config.settings.get("fee_type")
        fee_value = config.settings.get("fee_value")

        if not fee_type or not fee_value:
            return Decimal("0.00")

        fee_value = Decimal(str(fee_value))
        if fee_type == "PERCENTAGE":
            return (amount * fee_value / 100).quantize(Decimal("0.01"))
        elif fee_type == "FIXED":
            return fee_value.quantize(Decimal("0.01"))
        return Decimal("0.00")

    # ── Internal Helpers ────────────────────────────────────────────

    @staticmethod
    def _transition_status(payment, new_status, user=None):
        """Validate and perform a status transition."""
        old_status = payment.status
        allowed = ALLOWED_TRANSITIONS.get(old_status, [])

        if new_status not in allowed:
            raise InvalidPaymentStatusTransition(old_status, new_status)

        payment.status = new_status
        PaymentService._log_history(
            payment,
            "STATUS_CHANGE",
            user=user,
            old_value={"status": old_status},
            new_value={"status": new_status},
        )

    @staticmethod
    def _log_history(payment, action, user=None, old_value=None, new_value=None, description=""):
        """Create a history entry for a payment event."""
        from apps.payments.models import PaymentHistory

        PaymentHistory.objects.create(
            payment=payment,
            action=action,
            old_value=old_value,
            new_value=new_value,
            changed_by=user,
            description=description,
        )
