"""
ReceiptTemplate views — Task 76.

ViewSet for ReceiptTemplate CRUD with set-default, clone,
preview, and usage custom actions.
"""

import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.pos.receipts.models import Receipt, ReceiptTemplate
from apps.pos.receipts.serializers.template import (
    ReceiptTemplateDetailSerializer,
    ReceiptTemplateListSerializer,
    TemplateCloneSerializer,
    TemplatePreviewSerializer,
)
from apps.pos.receipts.services import PDFGeneratorService

logger = logging.getLogger(__name__)


class ReceiptTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD for receipt templates + lifecycle actions.

    Endpoints:
      GET    /receipt-templates/                  – List templates
      POST   /receipt-templates/                  – Create template
      GET    /receipt-templates/{id}/             – Retrieve template
      PUT    /receipt-templates/{id}/             – Update template
      PATCH  /receipt-templates/{id}/             – Partial update
      DELETE /receipt-templates/{id}/             – Soft delete
      POST   /receipt-templates/{id}/set_default/ – Set as default
      POST   /receipt-templates/{id}/clone/       – Clone template
      POST   /receipt-templates/{id}/preview/     – Preview with sample data
      GET    /receipt-templates/{id}/usage/       – Show usage stats
    """

    queryset = ReceiptTemplate.objects.order_by("name")
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_on", "is_default"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReceiptTemplateListSerializer
        return ReceiptTemplateDetailSerializer

    def perform_destroy(self, instance):
        """Soft delete: deactivate instead of hard delete."""
        if instance.is_system_default:
            return  # protect system defaults silently
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_on"])

    # ── Set default ──────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="set_default")
    def set_default(self, request, pk=None):
        """Set this template as the default."""
        template = self.get_object()

        # Clear current default(s)
        ReceiptTemplate.objects.filter(is_default=True).exclude(
            pk=template.pk
        ).update(is_default=False)

        template.is_default = True
        template.save(update_fields=["is_default", "updated_on"])

        return Response(
            ReceiptTemplateDetailSerializer(template).data
        )

    # ── Clone ────────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="clone")
    def clone(self, request, pk=None):
        """Clone this template with a new name."""
        template = self.get_object()

        ser = TemplateCloneSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        clone = template.clone_template(
            new_name=ser.validated_data["new_name"]
        )

        logger.info(
            "Template cloned: %s → %s", template.name, clone.name
        )

        return Response(
            ReceiptTemplateDetailSerializer(clone).data,
            status=status.HTTP_201_CREATED,
        )

    # ── Preview ──────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="preview")
    def preview(self, request, pk=None):
        """Preview template with sample receipt data."""
        template = self.get_object()

        ser = TemplatePreviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        preview_format = ser.validated_data.get("format", "html")

        # Build sample data
        sample_data = self._build_sample_data(template)

        if preview_format == "html":
            # Return HTML preview
            try:
                from django.template.loader import render_to_string

                html = render_to_string(
                    "receipts/pdf/base_receipt.html",
                    sample_data,
                )
                return Response(
                    {"html": html, "template_name": template.name}
                )
            except Exception:
                logger.exception("Preview generation failed")
                return Response(
                    {"detail": "Preview generation failed."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"detail": f"Preview format '{preview_format}' not supported yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # ── Usage stats ──────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="usage")
    def usage(self, request, pk=None):
        """Show how many receipts use this template."""
        template = self.get_object()

        total_receipts = Receipt.objects.filter(template=template).count()
        recent_receipts = (
            Receipt.objects.filter(template=template)
            .order_by("-generated_at")[:5]
            .values_list("receipt_number", flat=True)
        )

        return Response(
            {
                "template_id": str(template.id),
                "template_name": template.name,
                "total_receipts": total_receipts,
                "recent_receipt_numbers": list(recent_receipts),
                "is_default": template.is_default,
                "child_templates": template.child_templates.filter(
                    is_active=True
                ).count(),
            }
        )

    # ── Helpers ──────────────────────────────────────────────

    def _build_sample_data(self, template):
        """Build sample receipt data for preview."""
        return {
            "header": {
                "business_name": template.business_name_override or "Sample Business",
                "header_lines": [
                    template.header_line_1 or "123 Sample Street",
                    template.header_line_2 or "Colombo 07, Sri Lanka",
                    template.header_line_3 or "Tel: +94 11 234 5678",
                ],
            },
            "transaction": {
                "receipt_number": "REC-20240101-00001",
                "date": "2024-01-01",
                "time": "14:30:00",
                "operator": "Sample Cashier",
                "terminal": "POS-001",
            },
            "items": [
                {
                    "name": "Sample Product A",
                    "quantity": "2.000",
                    "unit_price": "Rs. 1,500.00",
                    "line_total": "Rs. 3,000.00",
                },
                {
                    "name": "Sample Product B",
                    "quantity": "1.000",
                    "unit_price": "Rs. 2,500.00",
                    "line_total": "Rs. 2,500.00",
                    "discount": "10% off",
                },
            ],
            "totals": {
                "subtotal": "Rs. 5,500.00",
                "discount_total": "Rs. 250.00",
                "tax_total": "Rs. 0.00",
                "grand_total": "Rs. 5,250.00",
                "item_count": 3,
            },
            "payments": [
                {
                    "method": "Cash",
                    "amount": "Rs. 6,000.00",
                    "tendered": "Rs. 6,000.00",
                    "change": "Rs. 750.00",
                }
            ],
            "footer": {
                "footer_lines": [
                    template.footer_line_1 or "Thank you for your purchase!",
                    template.footer_line_2 or "Please visit again.",
                ],
                "return_policy": template.return_policy_text or "",
            },
            "branding": {
                "primary_color": "#333333",
            },
        }
