"""
POS Payment API views.

Provides endpoints for payment initiation, processing, split payments,
transaction completion, refunds, and payment history.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pos.cart.models import POSCart
from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    PAYMENT_METHOD_CARD,
    PAYMENT_METHOD_CASH,
    PAYMENT_STATUS_COMPLETED,
    PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_REFUNDED,
    SESSION_STATUS_OPEN,
)
from apps.pos.payment.models import POSPayment
from apps.pos.payment.serializers import (
    PaymentCompleteRequestSerializer,
    PaymentRefundRequestSerializer,
    PaymentRequestSerializer,
    POSPaymentSerializer,
    SplitPaymentRequestSerializer,
)
from apps.pos.payment.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


# ── helpers ─────────────────────────────────────────────────────────────


def _get_active_cart(cart_id):
    """Fetch an active cart or return None."""
    try:
        return POSCart.objects.select_related(
            "session", "session__terminal"
        ).get(pk=cart_id, status=CART_STATUS_ACTIVE)
    except POSCart.DoesNotExist:
        return None


# ── Payment Initiate / Process ──────────────────────────────────────────


class PaymentProcessView(APIView):
    """
    POST /api/v1/pos/payment/process/

    Accepts a full payment for a cart (cash, card, mobile, etc.)
    and completes the transaction if fully paid.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = PaymentRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        cart = _get_active_cart(data["cart"])
        if not cart:
            return Response(
                {"detail": "Active cart not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if cart.session.status != SESSION_STATUS_OPEN:
            return Response(
                {"detail": "Session is not open."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        svc = PaymentService(cart=cart, user=request.user)
        method = data["payment_method"]
        amount = data["amount"]

        try:
            with transaction.atomic():
                if method == PAYMENT_METHOD_CASH:
                    tendered = data.get("tendered_amount") or amount
                    payment = svc.process_cash_payment(
                        amount_tendered=tendered
                    )
                elif method == PAYMENT_METHOD_CARD:
                    payment = svc.process_card_payment(
                        amount=amount,
                        authorization_code=data.get(
                            "authorization_code", ""
                        ),
                        reference_number=data.get("reference_number", ""),
                    )
                else:
                    # Mobile or other methods
                    payment = svc.process_mobile_payment(
                        amount=amount,
                        reference_number=data.get("reference_number", ""),
                        method=method,
                    )

                # Auto-complete if fully paid
                if svc.can_complete_cart():
                    result = svc.complete_transaction()
                    return Response(
                        {
                            "payment": POSPaymentSerializer(payment).data,
                            "cart_status": "COMPLETED",
                            "receipt": result.get("receipt_data"),
                            "message": "Transaction completed successfully.",
                        },
                        status=status.HTTP_200_OK,
                    )

            remaining = svc.get_remaining_amount()
            return Response(
                {
                    "payment": POSPaymentSerializer(payment).data,
                    "cart_status": cart.status,
                    "remaining_amount": str(remaining),
                    "message": "Payment recorded. Balance remaining.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception("Payment processing failed for cart %s", cart.pk)
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── Split Payment ───────────────────────────────────────────────────────


class SplitPaymentView(APIView):
    """
    POST /api/v1/pos/payment/split/

    Process multiple payments against a single cart.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = SplitPaymentRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        cart = _get_active_cart(data["cart"])
        if not cart:
            return Response(
                {"detail": "Active cart not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        svc = PaymentService(cart=cart, user=request.user)
        payment_dicts = [
            {
                "method": p["payment_method"],
                "amount": p["amount"],
                "tendered_amount": p.get("tendered_amount"),
                "reference_number": p.get("reference_number", ""),
                "authorization_code": p.get("authorization_code", ""),
            }
            for p in data["payments"]
        ]

        try:
            with transaction.atomic():
                payments = svc.split_payment(payment_dicts)
                if svc.can_complete_cart():
                    result = svc.complete_transaction()
                    return Response(
                        {
                            "payments": POSPaymentSerializer(
                                payments, many=True
                            ).data,
                            "cart_status": "COMPLETED",
                            "receipt": result.get("receipt_data"),
                            "message": "Split payment completed.",
                        }
                    )

            return Response(
                {
                    "payments": POSPaymentSerializer(
                        payments, many=True
                    ).data,
                    "cart_status": cart.status,
                    "remaining_amount": str(svc.get_remaining_amount()),
                    "message": "Split payment recorded. Balance remaining.",
                }
            )
        except Exception as exc:
            logger.exception("Split payment failed for cart %s", cart.pk)
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── Transaction Complete ────────────────────────────────────────────────


class PaymentCompleteView(APIView):
    """
    POST /api/v1/pos/payment/complete/

    Explicitly finalize a fully-paid cart.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = PaymentCompleteRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payment_id = ser.validated_data["payment_id"]

        try:
            payment = POSPayment.objects.select_related("cart").get(
                pk=payment_id
            )
        except POSPayment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart = payment.cart
        svc = PaymentService(cart=cart, user=request.user)

        if not svc.can_complete_cart():
            return Response(
                {
                    "detail": "Cart is not fully paid.",
                    "remaining_amount": str(svc.get_remaining_amount()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                result = svc.complete_transaction()
            return Response(
                {
                    "cart_status": "COMPLETED",
                    "receipt": result.get("receipt_data"),
                    "message": "Transaction completed successfully.",
                }
            )
        except Exception as exc:
            logger.exception("Complete transaction failed for cart %s", cart.pk)
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── Refund ──────────────────────────────────────────────────────────────


class PaymentRefundView(APIView):
    """
    POST /api/v1/pos/payment/{id}/refund/

    Refund a completed payment (full or partial).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        ser = PaymentRefundRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        refund_amount = ser.validated_data["refund_amount"]
        reason = ser.validated_data.get("reason", "")

        try:
            payment = POSPayment.objects.select_related("cart").get(pk=pk)
        except POSPayment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if payment.status != PAYMENT_STATUS_COMPLETED:
            return Response(
                {"detail": "Only completed payments can be refunded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if refund_amount > payment.amount:
            return Response(
                {"detail": "Refund amount exceeds payment amount."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                payment.status = PAYMENT_STATUS_REFUNDED
                payment.refunded_at = timezone.now()
                payment.notes = (
                    f"{payment.notes}\nRefund: {refund_amount} — {reason}"
                ).strip()
                payment.save(update_fields=["status", "refunded_at", "notes", "updated_on"])
            logger.info("Payment %s refunded: %s", pk, refund_amount)
            return Response(
                {
                    "payment": POSPaymentSerializer(payment).data,
                    "refund_amount": str(refund_amount),
                    "message": "Refund processed successfully.",
                }
            )
        except Exception as exc:
            logger.exception("Refund failed for payment %s", pk)
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── Payment History ─────────────────────────────────────────────────────


class PaymentHistoryView(APIView):
    """
    GET /api/v1/pos/payment/history/?session={id}
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.query_params.get("session")
        cart_id = request.query_params.get("cart")

        qs = POSPayment.objects.select_related(
            "cart", "processed_by"
        ).order_by("-created_on")

        if session_id:
            qs = qs.filter(cart__session_id=session_id)
        elif cart_id:
            qs = qs.filter(cart_id=cart_id)
        else:
            # Default: current user's payments today
            qs = qs.filter(processed_by=request.user)

        qs = qs[:100]
        return Response(POSPaymentSerializer(qs, many=True).data)


# ── Payment Status Check ───────────────────────────────────────────────


class PaymentStatusView(APIView):
    """
    GET /api/v1/pos/payment/{id}/status/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            payment = POSPayment.objects.get(pk=pk)
        except POSPayment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "id": str(payment.pk),
                "status": payment.status,
                "amount": str(payment.amount),
                "method": payment.method,
            }
        )
