"""
Quote ViewSet – full CRUD + status actions + PDF generation.
"""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.quotes.constants import QuoteStatus
from apps.quotes.filters import QuoteFilter
from apps.quotes.models import Quote, QuoteLineItem
from apps.quotes.serializers import (
    QuoteCreateSerializer,
    QuoteLineItemSerializer,
    QuoteListSerializer,
    QuoteSerializer,
    QuoteStatusActionSerializer,
)
from apps.quotes.services.quote_service import (
    InvalidStatusTransition,
    QuoteLockedError,
    QuoteValidationError,
)

logger = logging.getLogger(__name__)


class QuoteViewSet(ModelViewSet):
    """
    ViewSet for Quotes.

    Endpoints
    ---------
    GET    /quotes/                           – list
    POST   /quotes/                           – create
    GET    /quotes/{id}/                       – retrieve
    PUT    /quotes/{id}/                       – update
    PATCH  /quotes/{id}/                       – partial_update
    DELETE /quotes/{id}/                       – destroy
    POST   /quotes/{id}/send/                  – send to customer
    POST   /quotes/{id}/accept/                – mark accepted
    POST   /quotes/{id}/reject/                – mark rejected
    POST   /quotes/{id}/duplicate/             – duplicate quote
    POST   /quotes/{id}/create_revision/       – create new revision
    POST   /quotes/{id}/generate_pdf/          – (re)generate PDF
    GET    /quotes/{id}/download_pdf/          – download PDF file
    GET    /quotes/{id}/line_items/            – list line items
    POST   /quotes/{id}/line_items/            – add a line item
    GET    /quotes/{id}/history/               – audit history
    GET    /quotes/{id}/available_actions/     – list available actions
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = QuoteFilter
    search_fields = ["quote_number", "title", "guest_name", "guest_email", "customer__first_name", "customer__last_name", "customer__business_name"]
    ordering_fields = ["created_on", "total", "issue_date", "valid_until", "quote_number"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            Quote.objects.select_related("customer", "created_by", "template")
            .prefetch_related("line_items")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return QuoteListSerializer
        if self.action == "create":
            return QuoteCreateSerializer
        return QuoteSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if not instance.can_delete(self.request.user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only draft quotes without linked orders can be deleted.")
        instance.delete()

    # ── Status Actions ───────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="send")
    def send_quote(self, request, pk=None):
        """Transition quote to SENT and optionally email the customer."""
        quote = self.get_object()
        action_ser = QuoteStatusActionSerializer(data=request.data)
        action_ser.is_valid(raise_exception=True)

        try:
            from apps.quotes.services import QuoteService

            quote = QuoteService.send_quote(quote, user=request.user)
        except (InvalidStatusTransition, QuoteValidationError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(QuoteSerializer(quote, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="accept")
    def accept_quote(self, request, pk=None):
        quote = self.get_object()
        action_ser = QuoteStatusActionSerializer(data=request.data)
        action_ser.is_valid(raise_exception=True)

        try:
            from apps.quotes.services import QuoteService

            quote = QuoteService.accept_quote(quote, user=request.user)
        except (InvalidStatusTransition, QuoteValidationError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(QuoteSerializer(quote, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject_quote(self, request, pk=None):
        quote = self.get_object()
        action_ser = QuoteStatusActionSerializer(data=request.data)
        action_ser.is_valid(raise_exception=True)

        reason = action_ser.validated_data.get("rejection_reason", "")
        try:
            from apps.quotes.services import QuoteService

            quote = QuoteService.reject_quote(quote, user=request.user, reason=reason)
        except (InvalidStatusTransition, QuoteValidationError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(QuoteSerializer(quote, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate_quote(self, request, pk=None):
        quote = self.get_object()
        try:
            from apps.quotes.services import QuoteService

            new_quote = QuoteService.duplicate_quote(quote, user=request.user)
        except QuoteValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            QuoteSerializer(new_quote, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="create_revision")
    def create_revision(self, request, pk=None):
        quote = self.get_object()
        try:
            from apps.quotes.services import QuoteService

            revision = QuoteService.create_revision(quote, user=request.user)
        except (QuoteValidationError, QuoteLockedError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            QuoteSerializer(revision, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    # ── Conversion (Task 75) ────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="convert_to_order")
    def convert_to_order(self, request, pk=None):
        """Convert an accepted quote into a sales order."""
        quote = self.get_object()
        allow_backorder = request.data.get("allow_backorder", False)
        try:
            from apps.quotes.services import QuoteService

            order = QuoteService.convert_to_order(
                quote, user=request.user, allow_backorder=allow_backorder,
            )
        except (InvalidStatusTransition, QuoteValidationError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        quote.refresh_from_db()
        return Response(
            {
                "detail": "Quote converted to order.",
                "order_id": str(order.id) if hasattr(order, "id") else None,
                "quote": QuoteSerializer(quote, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )

    # ── Email (Task 78) ─────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="send_email")
    def send_email(self, request, pk=None):
        """Send the quote via email (optionally async via Celery)."""
        quote = self.get_object()

        to_email = request.data.get("to_email")
        cc = request.data.get("cc")
        subject = request.data.get("subject")
        message = request.data.get("message")

        try:
            from apps.quotes.tasks.email import send_quote_email_task

            send_quote_email_task.delay(
                str(quote.id),
                to_email=to_email,
                cc=cc,
                subject=subject,
                message=message,
            )
        except Exception:
            # Fallback to synchronous send
            try:
                from apps.quotes.services.email_service import QuoteEmailService

                QuoteEmailService.send_quote_email(
                    quote, to_email=to_email, cc=cc, subject=subject, message=message,
                )
            except Exception as exc:
                logger.exception("Email send failed for %s", quote.quote_number)
                return Response(
                    {"detail": f"Email sending failed: {exc}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response({"detail": "Email sent.", "quote_number": quote.quote_number})

    # ── PDF Actions ──────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="generate_pdf")
    def generate_pdf(self, request, pk=None):
        """Generate or regenerate a PDF for the quote."""
        quote = self.get_object()
        try:
            from apps.quotes.services.pdf_generator import QuotePDFGenerator

            generator = QuotePDFGenerator(quote)
            generator.generate_and_save()
        except ImportError:
            return Response(
                {"detail": "PDF generation dependencies not installed."},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
        except Exception as exc:
            logger.exception("PDF generation failed for %s", quote.quote_number)
            return Response(
                {"detail": f"PDF generation failed: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        quote.refresh_from_db()
        return Response(QuoteSerializer(quote, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path="download_pdf")
    def download_pdf(self, request, pk=None):
        """Download the generated PDF file."""
        quote = self.get_object()
        if not quote.pdf_file:
            return Response(
                {"detail": "PDF not yet generated."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from django.http import FileResponse

        return FileResponse(
            quote.pdf_file.open("rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"{quote.quote_number}.pdf",
        )

    # ── Line Items ───────────────────────────────────────────────

    @action(detail=True, methods=["get", "post"], url_path="line_items")
    def line_items(self, request, pk=None):
        """List or add line items for a quote."""
        quote = self.get_object()

        if request.method == "GET":
            items = quote.line_items.order_by("position")
            serializer = QuoteLineItemSerializer(items, many=True)
            return Response(serializer.data)

        # POST — create
        if quote.is_locked:
            return Response(
                {"detail": "Cannot add items to a locked quote."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = QuoteLineItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(quote=quote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ── History ──────────────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Return audit log entries for the quote."""
        quote = self.get_object()
        entries = quote.history.order_by("-timestamp").values(
            "id", "event_type", "timestamp", "notes", "old_values", "new_values"
        )[:100]
        return Response(list(entries))

    # ── Available Actions ────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="available_actions")
    def available_actions(self, request, pk=None):
        """Return the actions available for the quote's current state."""
        quote = self.get_object()
        from apps.quotes.services import QuoteService

        actions = QuoteService.get_available_actions_detailed(quote)
        return Response({"actions": actions})
