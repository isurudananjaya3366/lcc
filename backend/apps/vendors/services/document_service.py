"""Document service for vendor document management."""

import os


ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "jpg", "jpeg", "png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class DocumentService:
    """Service class for vendor document operations."""

    @staticmethod
    def upload_document(vendor_id, document_type, name, file, uploaded_by, expiry_date=None, notes=""):
        """Upload a vendor document after validating file type and size."""
        from apps.vendors.models import VendorDocument

        ext = os.path.splitext(file.name)[1].lstrip(".").lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type '{ext}' is not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        if file.size > MAX_FILE_SIZE:
            raise ValueError(
                f"File size {file.size} bytes exceeds maximum allowed size of {MAX_FILE_SIZE} bytes (10 MB)."
            )

        document = VendorDocument.objects.create(
            vendor_id=vendor_id,
            document_type=document_type,
            name=name,
            file=file,
            uploaded_by=uploaded_by,
            expiry_date=expiry_date,
            notes=notes,
        )
        return document

    @staticmethod
    def get_vendor_documents(vendor_id, document_type=None):
        """Get documents for a vendor, optionally filtered by type."""
        from apps.vendors.models import VendorDocument

        qs = VendorDocument.objects.filter(vendor_id=vendor_id).select_related("uploaded_by")
        if document_type:
            qs = qs.filter(document_type=document_type)
        return qs

    @staticmethod
    def delete_document(document_id):
        """Delete a vendor document and its file from storage."""
        from apps.vendors.models import VendorDocument

        document = VendorDocument.objects.get(id=document_id)
        if document.file:
            document.file.delete(save=False)
        document.delete()

    @staticmethod
    def get_expiring_documents(days=30):
        """Get documents expiring within the given number of days."""
        from django.utils import timezone
        from apps.vendors.models import VendorDocument

        deadline = timezone.now().date() + timezone.timedelta(days=days)
        return VendorDocument.objects.filter(
            expiry_date__isnull=False,
            expiry_date__lte=deadline,
            expiry_date__gte=timezone.now().date(),
        ).select_related("vendor")
