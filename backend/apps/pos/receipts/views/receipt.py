"""
Receipt views — Tasks 71-75, 77.

ViewSet and API endpoints for Receipt CRUD, generate, print,
email, PDF download, duplicate, and search.
"""

import csv
import io
import json
import logging

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import filters as drf_filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pos.receipts.models import Receipt, ReceiptTemplate
from apps.pos.receipts.serializers.receipt import (
    ReceiptDetailSerializer,
    ReceiptDuplicateSerializer,
    ReceiptEmailSerializer,
    ReceiptExportSerializer,
    ReceiptGenerateSerializer,
    ReceiptListSerializer,
    ReceiptPrintSerializer,
    ReceiptSearchSerializer,
)
from apps.pos.receipts.services import (
    NetworkPrinter,
    PDFGeneratorService,
    PrinterConnectionError,
    ReceiptBuilder,
    ReceiptEmailService,
    ReceiptNumberGenerator,
    ThermalPrintRenderer,
)
from apps.pos.receipts.services.exceptions import (
    CartValidationError,
    ReceiptBuildError,
)

logger = logging.getLogger(__name__)


class ReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Receipt list/retrieve + custom actions for generation and delivery.

    Endpoints:
      GET    /receipts/                     – List receipts
      GET    /receipts/{id}/                – Retrieve receipt detail
      POST   /receipts/generate/            – Generate receipt from cart
      POST   /receipts/{id}/print/          – Print receipt
      POST   /receipts/{id}/email/          – Email receipt
      GET    /receipts/{id}/pdf/            – Download PDF
      POST   /receipts/{id}/duplicate/      – Create duplicate
      GET    /receipts/search/              – Search receipts
    """

    queryset = Receipt.objects.select_related(
        "cart", "template", "original_receipt"
    ).order_by("-generated_at")
    permission_classes = [IsAuthenticated]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ["receipt_number", "cart__reference_number"]
    ordering_fields = ["generated_at", "receipt_number", "receipt_type"]
    ordering = ["-generated_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReceiptListSerializer
        return ReceiptDetailSerializer

    # ── Task 72: Generate receipt ────────────────────────────

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        """Generate a receipt from a completed cart."""
        from apps.pos.models import POSCart

        ser = ReceiptGenerateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # Fetch cart
        try:
            cart = POSCart.objects.select_related("session").get(
                pk=data["cart"]
            )
        except POSCart.DoesNotExist:
            return Response(
                {"detail": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch template (optional)
        template = None
        if data.get("template"):
            try:
                template = ReceiptTemplate.objects.get(pk=data["template"])
            except ReceiptTemplate.DoesNotExist:
                return Response(
                    {"detail": "Template not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            template = ReceiptTemplate.objects.get_default()

        # Build receipt data
        try:
            builder = ReceiptBuilder(cart=cart, template=template)
            receipt_data = builder.build()
        except (CartValidationError, ReceiptBuildError) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate receipt number
        generator = ReceiptNumberGenerator()
        receipt_number = generator.generate()

        # Create Receipt record
        receipt = Receipt.objects.create(
            receipt_number=receipt_number,
            cart=cart,
            receipt_type=data["receipt_type"],
            template=template,
            generated_at=timezone.now(),
            receipt_data=receipt_data,
            generated_by=request.user,
        )

        logger.info(
            "Receipt generated: %s for cart %s",
            receipt_number,
            cart.reference_number,
        )

        response_data = ReceiptDetailSerializer(
            receipt, context={"request": request}
        ).data

        # Auto-print if requested
        if data.get("auto_print"):
            response_data["auto_print_requested"] = True

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )

    # ── Task 73: Print receipt ───────────────────────────────

    @action(detail=True, methods=["post"], url_path="print")
    def print_receipt(self, request, pk=None):
        """Queue receipt for thermal printing."""
        receipt = self.get_object()

        ser = ReceiptPrintSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        printer_ip = data.get("printer_ip")
        if not printer_ip:
            return Response(
                {"detail": "Printer IP address is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Render thermal data
        paper_width_str = data["paper_width"]
        paper_width_int = 58 if "58" in str(paper_width_str) else 80

        renderer = ThermalPrintRenderer(
            receipt_data=receipt.receipt_data,
            paper_width=paper_width_int,
            open_drawer=data.get("open_drawer", False),
        )
        print_data = renderer.render()

        # Send to printer
        try:
            printer = NetworkPrinter(
                host=printer_ip,
                port=data.get("printer_port", 9100),
            )
            for _ in range(data.get("copies", 1)):
                printer.send(print_data)
        except PrinterConnectionError as e:
            logger.error(
                "Print failed for receipt %s: %s",
                receipt.receipt_number,
                str(e),
            )
            return Response(
                {"detail": f"Printer connection failed: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        receipt.mark_as_printed()

        return Response(
            {
                "detail": "Receipt printed successfully.",
                "receipt_number": receipt.receipt_number,
                "copies": data.get("copies", 1),
            }
        )

    # ── Task 74: Email receipt ───────────────────────────────

    @action(detail=True, methods=["post"], url_path="email")
    def email_receipt(self, request, pk=None):
        """Send receipt via email."""
        receipt = self.get_object()

        ser = ReceiptEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        try:
            email_service = ReceiptEmailService(receipt=receipt)
            email_service.send_email(
                recipient_email=data["email"],
                custom_message=data.get("message", ""),
                attach_pdf=data.get("attach_pdf", True),
                cc_emails=data.get("cc", []),
                subject=data.get("subject", ""),
            )
        except Exception:
            logger.exception(
                "Email failed for receipt %s", receipt.receipt_number
            )
            return Response(
                {"detail": "Failed to send email. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "detail": "Receipt emailed successfully.",
                "receipt_number": receipt.receipt_number,
                "email": data["email"],
            }
        )

    # ── Task 75: Download PDF ────────────────────────────────

    @action(detail=True, methods=["get"], url_path="pdf")
    def download_pdf(self, request, pk=None):
        """Download receipt as PDF."""
        receipt = self.get_object()

        try:
            pdf_service = PDFGeneratorService(receipt=receipt)
            pdf_bytes = pdf_service.generate_pdf()
        except Exception:
            logger.exception(
                "PDF generation failed for receipt %s",
                receipt.receipt_number,
            )
            return Response(
                {"detail": "Failed to generate PDF."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        filename = f"Receipt_{receipt.receipt_number}.pdf"
        response = HttpResponse(
            pdf_bytes, content_type="application/pdf"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        return response

    # ── Task 34 (API): Duplicate receipt ─────────────────────

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        """Create a duplicate copy of the receipt."""
        receipt = self.get_object()

        ser = ReceiptDuplicateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            duplicate = receipt.generate_duplicate(
                requested_by=request.user
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ReceiptDetailSerializer(duplicate).data,
            status=status.HTTP_201_CREATED,
        )

    # ── Task 77: Search receipts ─────────────────────────────

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Advanced receipt search with multiple filters."""
        ser = ReceiptSearchSerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        qs = self.get_queryset()

        if data.get("query"):
            qs = qs.filter(receipt_number__icontains=data["query"])

        if data.get("receipt_type"):
            qs = qs.filter(receipt_type=data["receipt_type"])

        if data.get("cart"):
            qs = qs.filter(cart_id=data["cart"])

        if data.get("date_from"):
            qs = qs.filter(generated_at__date__gte=data["date_from"])

        if data.get("date_to"):
            qs = qs.filter(generated_at__date__lte=data["date_to"])

        if data.get("min_total") is not None:
            qs = qs.filter(
                cart__grand_total__gte=data["min_total"]
            )

        if data.get("max_total") is not None:
            qs = qs.filter(
                cart__grand_total__lte=data["max_total"]
            )

        # Additional filters
        is_printed = request.query_params.get("is_printed")
        if is_printed == "true":
            qs = qs.filter(printed_at__isnull=False)
        elif is_printed == "false":
            qs = qs.filter(printed_at__isnull=True)

        is_emailed = request.query_params.get("is_emailed")
        if is_emailed == "true":
            qs = qs.filter(emailed_at__isnull=False)
        elif is_emailed == "false":
            qs = qs.filter(emailed_at__isnull=True)

        qs = qs[:100]
        return Response(ReceiptListSerializer(qs, many=True).data)


class ReceiptExportView(APIView):
    """
    Task 78: Export receipts as CSV or JSON.

    GET /receipts/export/?format=csv&date_from=2024-01-01&date_to=2024-12-31
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        ser = ReceiptExportSerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        qs = Receipt.objects.select_related("cart").order_by("-generated_at")

        if data.get("date_from"):
            qs = qs.filter(generated_at__date__gte=data["date_from"])
        if data.get("date_to"):
            qs = qs.filter(generated_at__date__lte=data["date_to"])
        if data.get("receipt_type"):
            qs = qs.filter(receipt_type=data["receipt_type"])

        qs = qs[:5000]

        export_format = data.get("format", "csv")
        if export_format == "json":
            return self._export_json(qs)
        return self._export_csv(qs)

    def _export_csv(self, queryset):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Receipt Number",
            "Type",
            "Cart Reference",
            "Subtotal",
            "Tax Total",
            "Discount Total",
            "Grand Total",
            "Generated At",
            "Printed",
            "Emailed",
            "Reprint Count",
            "Cashier",
            "Terminal",
            "Items Count",
        ])

        for receipt in queryset:
            txn = receipt.receipt_data.get("transaction", {})
            items = receipt.receipt_data.get("items", [])
            totals = receipt.receipt_data.get("totals", {})
            writer.writerow([
                receipt.receipt_number,
                receipt.receipt_type,
                receipt.cart.reference_number if receipt.cart else "",
                totals.get("subtotal", ""),
                totals.get("tax_total", ""),
                totals.get("discount_total", ""),
                str(receipt.cart.grand_total) if receipt.cart else "",
                receipt.generated_at.isoformat() if receipt.generated_at else "",
                "Yes" if receipt.was_printed else "No",
                "Yes" if receipt.was_emailed else "No",
                receipt.reprint_count,
                txn.get("cashier_name", ""),
                txn.get("terminal_id", ""),
                len(items),
            ])

        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        response = HttpResponse(
            output.getvalue(), content_type="text/csv"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="receipts_export_{timestamp}.csv"'
        )
        return response

    def _export_json(self, queryset):
        records = []
        for receipt in queryset:
            txn = receipt.receipt_data.get("transaction", {})
            items = receipt.receipt_data.get("items", [])
            totals = receipt.receipt_data.get("totals", {})
            records.append({
                "receipt_number": receipt.receipt_number,
                "receipt_type": receipt.receipt_type,
                "cart_reference": (
                    receipt.cart.reference_number if receipt.cart else None
                ),
                "subtotal": totals.get("subtotal"),
                "tax_total": totals.get("tax_total"),
                "discount_total": totals.get("discount_total"),
                "grand_total": (
                    str(receipt.cart.grand_total) if receipt.cart else None
                ),
                "generated_at": (
                    receipt.generated_at.isoformat()
                    if receipt.generated_at
                    else None
                ),
                "was_printed": receipt.was_printed,
                "was_emailed": receipt.was_emailed,
                "reprint_count": receipt.reprint_count,
                "cashier": txn.get("cashier_name"),
                "terminal": txn.get("terminal_id"),
                "items_count": len(items),
            })

        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        response = HttpResponse(
            json.dumps(records, indent=2),
            content_type="application/json",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="receipts_export_{timestamp}.json"'
        )
        return response
