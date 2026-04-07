"""
ASGI config for LankaCommerce Cloud.

Configures the ASGI application with protocol-based routing:
- HTTP requests → Django ASGI handler
- WebSocket connections → Django Channels with auth middleware

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
https://channels.readthedocs.io/en/latest/deploying.html
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django ASGI application early to ensure AppRegistry is populated
# before importing any Channels routing or consumers.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    # WebSocket routes will be added here as consumers are created.
                    # Example:
                    #   path("ws/pos/", POSConsumer.as_asgi()),
                    #   path("ws/notifications/", NotificationConsumer.as_asgi()),
                ]
            )
        ),
    }
)
