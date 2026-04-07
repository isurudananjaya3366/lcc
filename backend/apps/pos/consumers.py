"""
POS WebSocket consumers for real-time updates.

Provides WebSocket consumers for cart, session, and terminal events
using Django Channels. This is the infrastructure stub — actual hardware
and real-time features will be connected when Django Channels is configured.
"""

import json
import logging

logger = logging.getLogger(__name__)


try:
    from channels.generic.websocket import AsyncJsonWebsocketConsumer
except ImportError:
    # Django Channels not installed — provide a stub base class
    class AsyncJsonWebsocketConsumer:
        """Stub when Django Channels is not installed."""
        pass


class BasePOSConsumer(AsyncJsonWebsocketConsumer):
    """Base consumer with common auth and group management."""

    group_prefix = "pos"

    async def connect(self):
        self.group_name = self._get_group_name()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("WebSocket connected: %s", self.group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("WebSocket disconnected: %s", self.group_name)

    async def pos_event(self, event):
        """Handle POS events broadcast to the group."""
        await self.send_json(event.get("data", {}))

    def _get_group_name(self):
        raise NotImplementedError


class POSCartConsumer(BasePOSConsumer):
    """WebSocket consumer for cart real-time updates."""

    group_prefix = "pos_cart"

    def _get_group_name(self):
        cart_id = self.scope["url_route"]["kwargs"]["cart_id"]
        return f"{self.group_prefix}_{cart_id}"


class POSSessionConsumer(BasePOSConsumer):
    """WebSocket consumer for session real-time updates."""

    group_prefix = "pos_session"

    def _get_group_name(self):
        session_id = self.scope["url_route"]["kwargs"]["session_id"]
        return f"{self.group_prefix}_{session_id}"


class POSTerminalConsumer(BasePOSConsumer):
    """WebSocket consumer for terminal real-time updates."""

    group_prefix = "pos_terminal"

    def _get_group_name(self):
        terminal_id = self.scope["url_route"]["kwargs"]["terminal_id"]
        return f"{self.group_prefix}_{terminal_id}"


# ── Broadcasting helpers ────────────────────────────────────────────────

def _broadcast_event(group_name, event_type, data):
    """Send an event to a channel group (sync helper)."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {"type": "pos.event", "data": {"event": event_type, **data}},
            )
    except (ImportError, Exception):
        logger.debug("WebSocket broadcast skipped: Channels not available")


def broadcast_cart_update(cart_id, event_type, data=None):
    """Broadcast a cart update event."""
    _broadcast_event(f"pos_cart_{cart_id}", event_type, data or {})


def broadcast_session_update(session_id, event_type, data=None):
    """Broadcast a session update event."""
    _broadcast_event(f"pos_session_{session_id}", event_type, data or {})


def broadcast_terminal_update(terminal_id, event_type, data=None):
    """Broadcast a terminal update event."""
    _broadcast_event(f"pos_terminal_{terminal_id}", event_type, data or {})


def broadcast_payment_initiated(cart_id, payment_data):
    broadcast_cart_update(cart_id, "payment_initiated", payment_data)


def broadcast_payment_completed(cart_id, payment_data):
    broadcast_cart_update(cart_id, "payment_completed", payment_data)


def broadcast_payment_failed(cart_id, payment_data):
    broadcast_cart_update(cart_id, "payment_failed", payment_data)
