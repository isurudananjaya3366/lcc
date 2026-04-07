"""Employee self-service viewset for payslips."""

import logging

from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.payslip.models import Payslip
from apps.payslip.serializers.payslip import (
    PayslipDetailSerializer,
    PayslipListSerializer,
)

logger = logging.getLogger(__name__)


class EmployeePayslipViewSet(ReadOnlyModelViewSet):
    """Employee self-service viewset for viewing own payslips.

    Endpoints:
        GET  /my/             - List own payslips
        GET  /my/{id}/        - View payslip detail (tracks view)
        GET  /my/{id}/download/ - Download PDF (tracks download)
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["slip_number"]
    ordering_fields = ["generated_at", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        """Return only payslips belonging to the authenticated employee."""
        user = self.request.user
        return (
            Payslip.objects.filter(employee__user=user)
            .select_related("employee", "payroll_period", "employee_payroll")
            .prefetch_related("earnings", "deductions", "employer_contributions")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PayslipListSerializer
        return PayslipDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a payslip and record a view."""
        instance = self.get_object()
        instance.record_view()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """Download the payslip PDF and record a download."""
        payslip = self.get_object()

        if not payslip.has_pdf:
            return Response(
                {"detail": "PDF not available for this payslip."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payslip.record_download()

        response = FileResponse(
            payslip.pdf_file.open("rb"),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{payslip.slip_number}.pdf"'
        )
        return response
