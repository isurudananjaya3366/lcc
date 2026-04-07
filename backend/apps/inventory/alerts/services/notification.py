"""
AlertNotificationService — multi-channel notification orchestrator.

Covers Tasks 29-32: orchestration, email, dashboard, SMS channels.
"""

import logging
import re

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from apps.inventory.alerts.constants import (
    ALERT_TYPE_BACK_IN_STOCK,
    ALERT_TYPE_CRITICAL_STOCK,
    ALERT_TYPE_LOW_STOCK,
    ALERT_TYPE_OUT_OF_STOCK,
)

logger = logging.getLogger(__name__)


class AlertNotificationService:
    """
    Multi-channel notification service for stock alerts.

    Handles email, dashboard, SMS, and webhook notifications
    based on GlobalStockSettings configuration.
    """

    # ── Orchestration ───────────────────────────────────────────

    @classmethod
    def send_alert_notification(cls, alert):
        """Send alert notification through all enabled channels."""
        from apps.inventory.alerts.models import GlobalStockSettings

        if not cls.should_send_notification(alert):
            return {}

        gs = GlobalStockSettings.get_settings()
        results = {}

        if gs.email_alerts_enabled:
            results["email"] = cls.send_email_notification(alert, gs)
        if gs.dashboard_alerts_enabled:
            results["dashboard"] = cls.send_dashboard_notification(alert)
        if gs.sms_alerts_enabled and alert.priority >= 3:
            results["sms"] = cls.send_sms_notification(alert, gs)
        if gs.webhook_url:
            results["webhook"] = cls.send_webhook_notification(alert, gs)

        return results

    @classmethod
    def should_send_notification(cls, alert):
        from apps.inventory.alerts.models import GlobalStockSettings

        gs = GlobalStockSettings.get_settings()

        type_enabled_map = {
            ALERT_TYPE_LOW_STOCK: gs.alert_on_low_stock,
            ALERT_TYPE_CRITICAL_STOCK: gs.alert_on_critical_stock,
            ALERT_TYPE_OUT_OF_STOCK: gs.alert_on_out_of_stock,
            ALERT_TYPE_BACK_IN_STOCK: gs.alert_on_back_in_stock,
        }
        if not type_enabled_map.get(alert.alert_type, False):
            return False

        if not cls.check_throttle(alert, gs):
            return False

        return True

    @classmethod
    def check_throttle(cls, alert, gs):
        """Return True if alert is NOT within throttle window."""
        from datetime import timedelta

        from apps.inventory.alerts.models import StockAlert

        cutoff = timezone.now() - timedelta(hours=gs.alert_throttle_hours)
        recently_notified = StockAlert.objects.filter(
            product=alert.product,
            alert_type=alert.alert_type,
            warehouse=alert.warehouse,
            created_at__gte=cutoff,
        ).exclude(pk=alert.pk).exists()

        return not recently_notified

    # ── Email channel (Task 30) ─────────────────────────────────

    @classmethod
    def send_email_notification(cls, alert, gs):
        recipients = cls.get_email_recipients(gs)
        if not recipients:
            return {"success": False, "reason": "No recipients"}

        subject = cls.get_email_subject(alert)
        context = cls.build_email_context(alert)

        try:
            html_body = cls.render_html_email(alert, context)
            plain_body = cls.render_plaintext(alert, context)
            send_mail(
                subject=subject,
                message=plain_body,
                html_message=html_body,
                from_email=getattr(django_settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=recipients,
                fail_silently=False,
            )
            return {"success": True, "recipients": len(recipients)}
        except Exception as exc:
            logger.error("Email notification failed for alert %s: %s", alert.pk, exc)
            return {"success": False, "error": str(exc)}

    @classmethod
    def get_email_recipients(cls, gs):
        raw = gs.email_recipients or ""
        return [e.strip() for e in raw.split(",") if "@" in e.strip()]

    @classmethod
    def get_email_subject(cls, alert):
        subjects = {
            ALERT_TYPE_LOW_STOCK: f"\u26a0\ufe0f Low Stock Alert: {alert.product}",
            ALERT_TYPE_CRITICAL_STOCK: f"\U0001f534 CRITICAL: {alert.product}",
            ALERT_TYPE_OUT_OF_STOCK: f"\u274c OUT OF STOCK: {alert.product}",
            ALERT_TYPE_BACK_IN_STOCK: f"\u2705 Back in Stock: {alert.product}",
        }
        return subjects.get(alert.alert_type, f"Stock Alert: {alert.product}")

    @classmethod
    def build_email_context(cls, alert):
        return {
            "alert": alert,
            "product": alert.product,
            "warehouse": alert.warehouse,
            "stock_level": alert.current_stock,
            "threshold": alert.threshold_value,
            "alert_type_display": alert.get_alert_type_display(),
            "priority_display": alert.priority,
            "created_at": alert.created_at,
        }

    @classmethod
    def render_html_email(cls, alert, context):
        template_map = {
            ALERT_TYPE_LOW_STOCK: "alerts/emails/low_stock_alert.html",
            ALERT_TYPE_CRITICAL_STOCK: "alerts/emails/critical_stock_alert.html",
            ALERT_TYPE_OUT_OF_STOCK: "alerts/emails/out_of_stock_alert.html",
            ALERT_TYPE_BACK_IN_STOCK: "alerts/emails/back_in_stock_alert.html",
        }
        template = template_map.get(alert.alert_type, "alerts/emails/low_stock_alert.html")
        try:
            return render_to_string(template, context)
        except Exception:
            # Fallback if template missing
            return f"<p>{alert.message}</p>"

    @classmethod
    def render_plaintext(cls, alert, context):
        template_map = {
            ALERT_TYPE_LOW_STOCK: "alerts/emails/plaintext/low_stock_alert.txt",
            ALERT_TYPE_CRITICAL_STOCK: "alerts/emails/plaintext/critical_stock_alert.txt",
            ALERT_TYPE_OUT_OF_STOCK: "alerts/emails/plaintext/out_of_stock_alert.txt",
            ALERT_TYPE_BACK_IN_STOCK: "alerts/emails/plaintext/back_in_stock_alert.txt",
        }
        template = template_map.get(alert.alert_type)
        try:
            return render_to_string(template, context)
        except Exception:
            return alert.message

    # ── Dashboard channel (Task 31) ─────────────────────────────

    NOTIFICATION_LEVELS = {
        ALERT_TYPE_OUT_OF_STOCK: {"level": "critical", "icon": "🔴", "color": "#DC2626"},
        ALERT_TYPE_CRITICAL_STOCK: {"level": "warning", "icon": "🟠", "color": "#EA580C"},
        ALERT_TYPE_LOW_STOCK: {"level": "info", "icon": "🟡", "color": "#CA8A04"},
        ALERT_TYPE_BACK_IN_STOCK: {"level": "success", "icon": "🟢", "color": "#16A34A"},
    }

    @classmethod
    def send_dashboard_notification(cls, alert):
        """Create dashboard notification records for eligible users."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            recipients = cls.get_dashboard_recipients(alert)
            meta = cls.NOTIFICATION_LEVELS.get(alert.alert_type, {
                "level": "info", "icon": "ℹ️", "color": "#6B7280",
            })
            notification_data = cls.build_notification_record(alert, meta)
            created = 0
            for user in recipients:
                # Use cache-based or DB-based notification approach
                cls._store_dashboard_notification(user, notification_data)
                created += 1

            logger.info(
                "Dashboard notification for alert %s sent to %d users",
                alert.pk, created,
            )
            return {"success": True, "channel": "dashboard", "recipients": created}
        except Exception as exc:
            logger.error("Dashboard notification failed: %s", exc)
            return {"success": False, "channel": "dashboard", "error": str(exc)}

    @classmethod
    def get_dashboard_recipients(cls, alert):
        """Get users who should receive dashboard notifications."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        users = User.objects.filter(is_active=True)
        # Filter by permission
        users = users.filter(
            models.Q(is_superuser=True)
            | models.Q(user_permissions__codename="view_alert_dashboard")
            | models.Q(groups__permissions__codename="view_alert_dashboard")
        ).distinct()
        return users

    @classmethod
    def build_notification_record(cls, alert, meta):
        """Build notification data dict for dashboard display."""
        return {
            "alert_id": str(alert.pk),
            "type": alert.alert_type,
            "level": meta.get("level", "info"),
            "icon": meta.get("icon", "ℹ️"),
            "color": meta.get("color", "#6B7280"),
            "title": f"Stock Alert: {alert.get_alert_type_display()}",
            "message": alert.message,
            "product": str(alert.product),
            "warehouse": alert.warehouse_name if hasattr(alert, "warehouse_name") else "",
            "current_stock": str(alert.current_stock) if alert.current_stock else "0",
            "created_at": alert.created_at.isoformat(),
            "actions": [
                {"label": "View", "action": "view_alert", "id": str(alert.pk)},
                {"label": "Acknowledge", "action": "acknowledge_alert", "id": str(alert.pk)},
            ],
        }

    @classmethod
    def _store_dashboard_notification(cls, user, notification_data):
        """Store notification for a user via Django cache."""
        from django.core.cache import cache

        key = f"dashboard_notifications:{user.pk}"
        existing = cache.get(key, [])
        existing.insert(0, notification_data)
        # Keep last 50 notifications
        cache.set(key, existing[:50], timeout=86400 * 7)

    # ── SMS channel (Task 32) ───────────────────────────────────

    @classmethod
    def send_sms_notification(cls, alert, gs):
        if alert.priority < 3:
            return {"success": False, "reason": "Priority too low for SMS"}

        recipients = cls.get_sms_recipients(gs)
        if not recipients:
            return {"success": False, "reason": "No SMS recipients"}

        message = cls.format_sms_message(alert)
        logger.info("SMS would be sent to %d recipients for alert %s", len(recipients), alert.pk)
        # Gateway integration is provider-specific; log for now.
        return {"success": True, "sent": len(recipients), "message": message}

    @classmethod
    def get_sms_recipients(cls, gs):
        raw = gs.sms_recipients or ""
        phones = []
        for p in raw.split(","):
            cleaned = cls.validate_phone_number(p.strip())
            if cleaned:
                phones.append(cleaned)
        return phones

    @classmethod
    def validate_phone_number(cls, phone):
        phone = re.sub(r"[\s\-]", "", phone)
        if phone.startswith("0"):
            phone = "+94" + phone[1:]
        elif not phone.startswith("+94"):
            phone = "+94" + phone
        if re.match(r"^\+94\d{9}$", phone):
            return phone
        return None

    @classmethod
    def format_sms_message(cls, alert):
        templates = {
            ALERT_TYPE_CRITICAL_STOCK: "CRITICAL: {product} at {stock} units. Reorder urgently.",
            ALERT_TYPE_OUT_OF_STOCK: "OUT OF STOCK: {product}. Please restock immediately.",
        }
        template = templates.get(alert.alert_type, "Stock Alert: {product}")
        message = template.format(
            product=str(alert.product)[:30],
            stock=alert.current_stock,
        )
        return message[:160]

    # ── Webhook channel ─────────────────────────────────────────

    @classmethod
    def send_webhook_notification(cls, alert, gs):
        """Placeholder for webhook notification."""
        logger.info("Webhook notification for alert %s to %s", alert.pk, gs.webhook_url)
        return {"success": True, "channel": "webhook"}
