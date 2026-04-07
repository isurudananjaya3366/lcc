"""
Public (unauthenticated) views for quote access via public_token.
"""

from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.quotes.constants import QuoteStatus
from apps.quotes.models import Quote
from apps.quotes.serializers import PublicQuoteSerializer


class PublicQuoteView(APIView):
    """GET a quote's public details using the public_token UUID."""

    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            quote = Quote.objects.select_related("customer").prefetch_related(
                "line_items"
            ).get(public_token=token)
        except Quote.DoesNotExist:
            return Response(
                {"detail": "Quote not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Track view (Task 80)
        Quote.objects.filter(pk=quote.pk).update(
            view_count=quote.view_count + 1,
            last_viewed_at=timezone.now(),
        )

        return Response(PublicQuoteSerializer(quote).data)


class PublicQuotePDFView(APIView):
    """Download the PDF for a quote using the public_token UUID."""

    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            quote = Quote.objects.get(public_token=token)
        except Quote.DoesNotExist:
            return Response(
                {"detail": "Quote not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not quote.pdf_file:
            return Response(
                {"detail": "PDF not available."}, status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            quote.pdf_file.open("rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"{quote.quote_number}.pdf",
        )


class PublicQuoteAcceptView(APIView):
    """Accept a quote via public_token (customer self-service)."""

    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            quote = Quote.objects.get(public_token=token)
        except Quote.DoesNotExist:
            return Response(
                {"detail": "Quote not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if quote.status != QuoteStatus.SENT:
            return Response(
                {"detail": f"Quote cannot be accepted (current status: {quote.status})."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Expiry check (Task 81)
        if quote.valid_until and quote.valid_until < timezone.now().date():
            return Response(
                {"detail": "This quote has expired and can no longer be accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.quotes.services import QuoteService

        try:
            QuoteService.accept_quote(quote, user=None)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Quote accepted.", "quote_number": quote.quote_number})


class PublicQuoteRejectView(APIView):
    """Reject a quote via public_token (customer self-service)."""

    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            quote = Quote.objects.get(public_token=token)
        except Quote.DoesNotExist:
            return Response(
                {"detail": "Quote not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if quote.status != QuoteStatus.SENT:
            return Response(
                {"detail": f"Quote cannot be rejected (current status: {quote.status})."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Expiry check (Task 81)
        if quote.valid_until and quote.valid_until < timezone.now().date():
            return Response(
                {"detail": "This quote has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = request.data.get("reason", "")
        if not reason:
            return Response(
                {"detail": "Rejection reason is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.quotes.services import QuoteService

        try:
            QuoteService.reject_quote(quote, user=None, reason=reason)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Quote rejected.", "quote_number": quote.quote_number})
