"""
POS WebSocket URL routing.

Defines WebSocket URL patterns for cart, session, and terminal consumers.
Requires Django Channels to be installed and configured.
"""

try:
    from django.urls import re_path

    from apps.pos.consumers import (
        POSCartConsumer,
        POSSessionConsumer,
        POSTerminalConsumer,
    )

    websocket_urlpatterns = [
        re_path(
            r"ws/pos/cart/(?P<cart_id>[0-9a-f-]+)/$",
            POSCartConsumer.as_asgi(),
        ),
        re_path(
            r"ws/pos/session/(?P<session_id>[0-9a-f-]+)/$",
            POSSessionConsumer.as_asgi(),
        ),
        re_path(
            r"ws/pos/terminal/(?P<terminal_id>[0-9a-f-]+)/$",
            POSTerminalConsumer.as_asgi(),
        ),
    ]
except ImportError:
    # Django Channels not installed
    websocket_urlpatterns = []
