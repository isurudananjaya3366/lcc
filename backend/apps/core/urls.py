"""Core app URL configuration.

Health check endpoint for load balancer and monitoring integration.
"""

from django.urls import path

from apps.core.views import health_check

app_name = "core"

urlpatterns = [
    path("", health_check, name="health_check"),
]
