"""Tax filing views — ViewSets, calendar, and reminders widget."""

from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounting.models import (
    EPFReturn,
    ETFReturn,
    PAYEReturn,
    TaxConfiguration,
    TaxPeriodRecord,
    TaxSubmission,
    VATReturn,
)
from apps.accounting.serializers.tax import (
    EPFReturnSerializer,
    ETFReturnSerializer,
    PAYEReturnSerializer,
    TaxConfigurationSerializer,
    TaxPeriodRecordSerializer,
    TaxSubmissionSerializer,
    VATReturnSerializer,
)
from apps.accounting.services.filing_reminder import FilingReminderService

# ── Tax Configuration ───────────────────────────────────────────


class TaxConfigurationViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Manage tenant tax configuration (VAT/PAYE/EPF/ETF settings)."""

    serializer_class = TaxConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaxConfiguration.objects.filter(is_active=True)


# ── Tax Period ──────────────────────────────────────────────────


class TaxPeriodViewSet(viewsets.ModelViewSet):
    """CRUD for tax filing periods."""

    serializer_class = TaxPeriodRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaxPeriodRecord.objects.select_related("tax_configuration").order_by(
            "-year", "-period_number"
        )


# ── Return ViewSets ────────────────────────────────────────────


class VATReturnViewSet(viewsets.ModelViewSet):
    serializer_class = VATReturnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VATReturn.objects.select_related("period").order_by("-created_at")

    @action(detail=True, methods=["get"])
    def csv(self, request, pk=None):
        """Export VAT return as CSV."""
        from apps.accounting.services.vat_return_generator import VATReturnGenerator

        vat = self.get_object()
        gen = VATReturnGenerator(vat.period)
        return gen.export_csv()

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        """Render VAT return PDF HTML."""
        from apps.accounting.services.vat_return_generator import VATReturnGenerator

        vat = self.get_object()
        gen = VATReturnGenerator(vat.period)
        html = gen.render_pdf_html()
        return Response({"html": html})


class PAYEReturnViewSet(viewsets.ModelViewSet):
    serializer_class = PAYEReturnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PAYEReturn.objects.select_related("period").order_by("-created_at")


class EPFReturnViewSet(viewsets.ModelViewSet):
    serializer_class = EPFReturnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EPFReturn.objects.select_related("period").order_by("-created_at")


class ETFReturnViewSet(viewsets.ModelViewSet):
    serializer_class = ETFReturnSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ETFReturn.objects.select_related("period").order_by("-created_at")


# ── Submissions ─────────────────────────────────────────────────


class TaxSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = TaxSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaxSubmission.objects.select_related(
            "tax_period", "submitted_by"
        ).order_by("-submitted_at")


# ── Calendar ────────────────────────────────────────────────────


class TaxCalendarView(APIView):
    """Tax filing calendar with upcoming deadlines."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = FilingReminderService()
        now = timezone.now()

        pending = service.get_pending_filings(days_ahead=60)
        deadlines = []
        overdue = []

        for p in pending:
            entry = {
                "tax_type": p.tax_type,
                "period": f"{p.year}/{p.period_number:02d}",
                "due_date": p.due_date.isoformat(),
                "status": p.filing_status,
                "days_remaining": service.get_days_remaining(p.due_date),
            }
            if service.get_days_remaining(p.due_date) < 0:
                overdue.append(entry)
            else:
                deadlines.append(entry)

        return Response(
            {
                "current_month": now.strftime("%B %Y"),
                "deadlines": deadlines,
                "overdue": overdue,
            }
        )


# ── Reminders Widget ───────────────────────────────────────────


class TaxRemindersWidgetView(APIView):
    """Dashboard widget: pending tax filings and urgency summary."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = FilingReminderService()
        return Response(service.get_widget_data())
