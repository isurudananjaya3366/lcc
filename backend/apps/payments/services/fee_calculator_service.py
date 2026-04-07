"""
Fee calculator service.

Centralizes fee calculation logic for processing fees,
late fees, and early payment discounts.
"""

import logging
from datetime import date
from decimal import Decimal

logger = logging.getLogger(__name__)


class FeeCalculatorService:
    """
    Service for calculating payment-related fees.

    Centralizes fee calculation logic for processing fees,
    late fees, and early payment discounts.
    """

    @staticmethod
    def calculate_processing_fee(method, amount):
        """
        Calculate processing fee for a payment method.

        Uses PaymentMethodConfig explicit fields (processing_fee_type,
        processing_fee_value) rather than the JSON settings field.

        Args:
            method: PaymentMethod choice value.
            amount: Payment amount (Decimal).

        Returns:
            Decimal: Processing fee amount.
        """
        from apps.payments.models import PaymentMethodConfig

        try:
            config = PaymentMethodConfig.objects.filter(method=method, is_active=True).first()
            if not config:
                return Decimal("0.00")

            fee_type = getattr(config, "processing_fee_type", None)
            fee_value = getattr(config, "processing_fee_value", None)

            if not fee_type or not fee_value:
                return Decimal("0.00")

            if fee_type == "PERCENTAGE":
                fee = amount * (fee_value / 100)
            elif fee_type == "FIXED":
                fee = fee_value
            else:
                fee = Decimal("0.00")

            return fee.quantize(Decimal("0.01"))

        except Exception:
            logger.exception("Error calculating processing fee for method=%s", method)
            return Decimal("0.00")

    @staticmethod
    def calculate_late_fee(invoice, as_of_date=None):
        """
        Calculate late fee for an overdue invoice.

        Args:
            invoice: Invoice instance (must have due_date, total, amount_paid or similar).
            as_of_date: Date to calculate as of (defaults to today).

        Returns:
            dict with fee_amount, days_overdue, grace_period_expired, calculation_details.
        """
        from apps.payments.models import PaymentSettings

        default_result = {
            "fee_amount": Decimal("0.00"),
            "days_overdue": 0,
            "grace_period_expired": False,
            "calculation_details": "",
        }

        try:
            settings = PaymentSettings.objects.first()
        except PaymentSettings.DoesNotExist:
            default_result["calculation_details"] = "Settings not configured"
            return default_result

        if not settings or not settings.enable_late_fees:
            default_result["calculation_details"] = "Late fees not enabled"
            return default_result

        comparison_date = as_of_date or date.today()
        due_date = getattr(invoice, "due_date", None)

        if not due_date or due_date >= comparison_date:
            default_result["calculation_details"] = "Invoice not yet due"
            return default_result

        days_overdue = (comparison_date - due_date).days
        effective_overdue_days = max(0, days_overdue - settings.grace_period_days)
        grace_period_expired = days_overdue > settings.grace_period_days

        if effective_overdue_days <= 0:
            return {
                "fee_amount": Decimal("0.00"),
                "days_overdue": days_overdue,
                "grace_period_expired": False,
                "calculation_details": f"Within {settings.grace_period_days}-day grace period",
            }

        # Calculate outstanding amount
        total_amount = getattr(invoice, "total", None) or getattr(invoice, "total_amount", Decimal("0"))
        paid_amount = getattr(invoice, "amount_paid", None) or getattr(invoice, "paid_amount", Decimal("0"))
        outstanding = total_amount - paid_amount

        if outstanding <= 0:
            return {
                "fee_amount": Decimal("0.00"),
                "days_overdue": days_overdue,
                "grace_period_expired": True,
                "calculation_details": "Invoice fully paid",
            }

        # Calculate fee based on frequency
        base_fee = settings.calculate_late_fee(outstanding)
        frequency = settings.late_fee_frequency

        if frequency == "ONCE":
            fee = base_fee
            details = f"One-time late fee on Rs. {outstanding}"
        elif frequency == "MONTHLY":
            months_overdue = Decimal(str(effective_overdue_days)) / Decimal("30")
            fee = base_fee * months_overdue
            details = f"Monthly late fee for {float(months_overdue):.1f} months on Rs. {outstanding}"
        elif frequency == "WEEKLY":
            weeks_overdue = Decimal(str(effective_overdue_days)) / Decimal("7")
            fee = base_fee * weeks_overdue
            details = f"Weekly late fee for {float(weeks_overdue):.1f} weeks on Rs. {outstanding}"
        elif frequency == "DAILY":
            fee = base_fee * effective_overdue_days
            details = f"Daily late fee for {effective_overdue_days} days on Rs. {outstanding}"
        else:
            fee = Decimal("0.00")
            details = "Unknown fee frequency"

        return {
            "fee_amount": fee.quantize(Decimal("0.01")),
            "days_overdue": days_overdue,
            "effective_overdue_days": effective_overdue_days,
            "grace_period_expired": grace_period_expired,
            "calculation_details": details,
        }

    @staticmethod
    def calculate_early_payment_discount(invoice, payment_date=None):
        """
        Calculate early payment discount if applicable.

        Args:
            invoice: Invoice instance.
            payment_date: Payment date (defaults to today).

        Returns:
            dict with discount_amount, discount_percentage, days_early, eligible.
        """
        default_result = {
            "discount_amount": Decimal("0.00"),
            "discount_percentage": Decimal("0.00"),
            "days_early": 0,
            "eligible": False,
        }

        due_date = getattr(invoice, "due_date", None)
        if not due_date:
            return default_result

        payment_date = payment_date or date.today()
        if payment_date >= due_date:
            return default_result

        days_early = (due_date - payment_date).days
        default_result["days_early"] = days_early
        return default_result

    @staticmethod
    def get_fee_breakdown(method, amount, invoice=None):
        """
        Get detailed breakdown of all fees.

        Args:
            method: PaymentMethod choice value.
            amount: Payment amount.
            invoice: Optional invoice for late fee calculation.

        Returns:
            dict with payment_amount, processing_fee, late_fee, total_amount, details.
        """
        breakdown = {
            "payment_amount": amount,
            "processing_fee": Decimal("0.00"),
            "late_fee": Decimal("0.00"),
            "early_payment_discount": Decimal("0.00"),
            "total_amount": amount,
            "details": [],
        }

        processing_fee = FeeCalculatorService.calculate_processing_fee(method, amount)
        breakdown["processing_fee"] = processing_fee

        if processing_fee > 0:
            breakdown["details"].append({
                "type": "processing_fee",
                "description": f"{method} processing fee",
                "amount": float(processing_fee),
            })

        if invoice:
            late_fee_result = FeeCalculatorService.calculate_late_fee(invoice)
            breakdown["late_fee"] = late_fee_result["fee_amount"]

            if late_fee_result["fee_amount"] > 0:
                breakdown["details"].append({
                    "type": "late_fee",
                    "description": late_fee_result["calculation_details"],
                    "amount": float(late_fee_result["fee_amount"]),
                    "days_overdue": late_fee_result["days_overdue"],
                })

        breakdown["total_amount"] = (
            amount
            + breakdown["processing_fee"]
            + breakdown["late_fee"]
            - breakdown["early_payment_discount"]
        )

        return breakdown
