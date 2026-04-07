"""
Quote URL routing.

URL structure:
    /api/v1/quotes/quotes/                                    – list / create
    /api/v1/quotes/quotes/{id}/                                – detail / update / delete
    /api/v1/quotes/quotes/{id}/send/                           – send
    /api/v1/quotes/quotes/{id}/accept/                         – accept
    /api/v1/quotes/quotes/{id}/reject/                         – reject
    /api/v1/quotes/quotes/{id}/duplicate/                      – duplicate
    /api/v1/quotes/quotes/{id}/create_revision/                – revision
    /api/v1/quotes/quotes/{id}/generate_pdf/                   – generate PDF
    /api/v1/quotes/quotes/{id}/download_pdf/                   – download PDF
    /api/v1/quotes/quotes/{id}/line_items/                     – line items
    /api/v1/quotes/quotes/{id}/history/                        – audit history
    /api/v1/quotes/quotes/{id}/available_actions/              – available actions

    /api/v1/quotes/public/{token}/                             – public view
    /api/v1/quotes/public/{token}/pdf/                         – public PDF
    /api/v1/quotes/public/{token}/accept/                      – public accept
    /api/v1/quotes/public/{token}/reject/                      – public reject
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.quotes.views import (
    PublicQuoteAcceptView,
    PublicQuotePDFView,
    PublicQuoteRejectView,
    PublicQuoteView,
    QuoteViewSet,
)

app_name = "quotes"

router = DefaultRouter()
router.register(r"quotes", QuoteViewSet, basename="quote")

urlpatterns = [
    # Public (unauthenticated) endpoints
    path(
        "public/<uuid:token>/",
        PublicQuoteView.as_view(),
        name="public-quote-detail",
    ),
    path(
        "public/<uuid:token>/pdf/",
        PublicQuotePDFView.as_view(),
        name="public-quote-pdf",
    ),
    path(
        "public/<uuid:token>/accept/",
        PublicQuoteAcceptView.as_view(),
        name="public-quote-accept",
    ),
    path(
        "public/<uuid:token>/reject/",
        PublicQuoteRejectView.as_view(),
        name="public-quote-reject",
    ),
] + router.urls
