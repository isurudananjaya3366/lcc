"""
API Documentation URLs

URL patterns for the OpenAPI 3.0 schema endpoint and interactive
documentation interfaces (Swagger UI and ReDoc).

These patterns are included at the ``/api/`` prefix from ``config.urls``::

    path("api/", include("apps.core.api_docs.urls"))

Resulting endpoints:
    /api/schema/   – Raw OpenAPI 3.0 JSON/YAML schema
    /api/docs/     – Swagger UI interactive explorer
    /api/redoc/    – ReDoc alternative documentation
"""

from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = "api_docs"

urlpatterns = [
    # OpenAPI 3.0 schema (JSON by default, ?format=yaml supported)
    path(
        "schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    # Swagger UI – interactive API explorer
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api_docs:schema"),
        name="swagger-ui",
    ),
    # ReDoc – alternative documentation interface
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="api_docs:schema"),
        name="redoc",
    ),
]
