"""Document ViewSet for employee document management."""

from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.employees.filters import EmployeeDocumentFilter
from apps.employees.models import EmployeeDocument
from apps.employees.serializers import EmployeeDocumentSerializer


class DocumentViewSet(ModelViewSet):
    """ViewSet for Employee Documents with upload support."""

    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeDocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EmployeeDocumentFilter
    search_fields = ["title", "description", "employee__first_name", "employee__last_name"]
    ordering_fields = ["created_on", "expiry_date", "document_type"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            EmployeeDocument.objects.filter(is_deleted=False)
            .select_related("employee", "uploaded_by")
        )

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete — mark as deleted instead of permanent removal."""
        instance.is_deleted = True
        instance.deleted_on = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_on"])

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """Download the document file."""
        document = self.get_object()
        if not document.file:
            return Response(
                {"detail": "No file attached to this document."},
                status=status.HTTP_404_NOT_FOUND,
            )
        response = FileResponse(
            document.file.open("rb"),
            content_type=document.file_type or "application/octet-stream",
        )
        filename = document.original_filename or document.title
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        """Mark a document as verified."""
        document = self.get_object()
        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.save(update_fields=["is_verified", "verified_by", "verified_at"])
        return Response(EmployeeDocumentSerializer(document).data)

    @action(detail=True, methods=["post"], url_path="unverify")
    def unverify(self, request, pk=None):
        """Remove verification from a document."""
        document = self.get_object()
        document.is_verified = False
        document.verified_by = None
        document.verified_at = None
        document.save(update_fields=["is_verified", "verified_by", "verified_at"])
        return Response(EmployeeDocumentSerializer(document).data)
