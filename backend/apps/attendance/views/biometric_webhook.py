"""Biometric Webhook View for external device integration."""

import hashlib
import hmac
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.services.biometric_service import BiometricIntegrationService

logger = logging.getLogger(__name__)


class BiometricWebhookView(APIView):
    """
    Webhook endpoint for biometric devices.

    Accepts POST requests from registered devices with check-in/check-out events.
    Authentication is done via a device token in the Authorization header.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        # ── HMAC Signature Verification ──────────────────────
        signature = request.META.get("HTTP_X_SIGNATURE", "")
        if signature:
            raw_body = request.body
            if not BiometricIntegrationService.verify_signature(raw_body, signature):
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid webhook signature.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # ── Validate required fields ─────────────────────────
        device_id = request.data.get("device_id")
        event_type = request.data.get("event_type")
        employee_biometric_id = request.data.get("employee_biometric_id")
        timestamp = request.data.get("timestamp")

        if not all([device_id, event_type, employee_biometric_id, timestamp]):
            return Response(
                {
                    "status": "error",
                    "message": "Missing required fields: device_id, event_type, "
                               "employee_biometric_id, timestamp.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Validate event type ──────────────────────────────
        valid_events = {"PUNCH_IN", "PUNCH_OUT", "check_in", "check_out"}
        if event_type not in valid_events:
            return Response(
                {
                    "status": "error",
                    "message": f"Invalid event_type. Must be one of: {', '.join(sorted(valid_events))}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Map event types ──────────────────────────────────
        event_map = {
            "check_in": "PUNCH_IN",
            "check_out": "PUNCH_OUT",
            "PUNCH_IN": "PUNCH_IN",
            "PUNCH_OUT": "PUNCH_OUT",
        }
        normalised_event = event_map[event_type]

        # ── Process through biometric service ────────────────
        try:
            result = BiometricIntegrationService.process_event(
                device_id=device_id,
                event_type=normalised_event,
                employee_identifier=employee_biometric_id,
                timestamp=timestamp,
                location=request.data.get("location"),
            )
            return Response(
                {
                    "status": "success",
                    "message": f"{'Check-in' if normalised_event == 'PUNCH_IN' else 'Check-out'} recorded.",
                    "data": result,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            logger.exception("Biometric webhook processing failed for device %s", device_id)
            return Response(
                {
                    "status": "error",
                    "message": "Failed to process biometric event.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
