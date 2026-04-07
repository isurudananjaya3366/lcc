"""
Webhook notification service for stock alerts.

Task 50: Sends webhook payloads to third-party systems
when alerts are created, resolved, or acknowledged.
"""

import hashlib
import hmac
import json
import logging
import time

try:
    import requests
except ImportError:
    requests = None  # type: ignore[assignment]

from django.utils import timezone

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for sending webhook notifications to external systems."""

    @staticmethod
    def send_alert_webhook(alert, event_type):
        """
        Send a webhook notification for an alert event.

        Args:
            alert: StockAlert instance
            event_type: str — e.g. 'alert.created', 'alert.resolved'

        Returns:
            bool: True if webhook was sent successfully.
        """
        from apps.inventory.alerts.models import GlobalStockSettings

        try:
            settings = GlobalStockSettings.get_settings()
        except Exception:
            return False

        if not settings.webhook_enabled or not settings.webhook_url:
            return False

        # Check if event type is enabled
        webhook_events = settings.webhook_events or []
        if webhook_events and event_type not in webhook_events:
            return False

        payload = WebhookService.build_payload(alert, event_type)

        signature = WebhookService.generate_signature(
            payload, settings.webhook_secret
        )

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event_type,
        }

        return WebhookService.send_with_retry(
            url=settings.webhook_url,
            payload=payload,
            headers=headers,
            max_attempts=settings.webhook_retry_attempts,
            timeout=settings.webhook_timeout_seconds,
        )

    @staticmethod
    def build_payload(alert, event_type):
        """Build the webhook JSON payload."""
        payload = {
            "event": event_type,
            "timestamp": timezone.now().isoformat(),
            "alert": {
                "id": str(alert.id),
                "alert_type": alert.alert_type,
                "status": alert.status,
                "priority": alert.priority,
                "message": alert.message,
                "current_stock": alert.current_stock,
                "threshold_value": (
                    float(alert.threshold_value)
                    if alert.threshold_value is not None
                    else None
                ),
                "created_at": alert.created_at.isoformat(),
            },
            "product": {
                "id": str(alert.product_id),
                "name": alert.product.name if alert.product else "",
                "sku": getattr(alert.product, "sku", "") if alert.product else "",
            },
            "warehouse": {
                "id": str(alert.warehouse_id) if alert.warehouse_id else None,
                "name": (
                    alert.warehouse.name if alert.warehouse else None
                ),
            },
        }
        return payload

    @staticmethod
    def generate_signature(payload, secret):
        """Generate HMAC-SHA256 signature for the payload."""
        if not secret:
            return ""
        payload_json = json.dumps(payload, sort_keys=True)
        return hmac.new(
            secret.encode("utf-8"),
            payload_json.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def send_with_retry(url, payload, headers, max_attempts=3, timeout=10):
        """
        Send webhook POST with exponential backoff retry.

        Returns True on success, False if all attempts fail.
        """
        if requests is None:
            logger.error("requests library not installed — cannot send webhook")
            return False

        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout,
                )

                if response.status_code in (200, 201, 202, 204):
                    logger.info("Webhook sent successfully to %s", url)
                    return True

                logger.warning(
                    "Webhook failed (attempt %d/%d): status %d",
                    attempt + 1,
                    max_attempts,
                    response.status_code,
                )

            except requests.exceptions.RequestException as exc:
                logger.error(
                    "Webhook error (attempt %d/%d): %s",
                    attempt + 1,
                    max_attempts,
                    exc,
                )

            # Exponential backoff (skip on last attempt)
            if attempt < max_attempts - 1:
                time.sleep(2**attempt)

        logger.error(
            "Webhook failed after %d attempts: %s", max_attempts, url
        )
        return False
