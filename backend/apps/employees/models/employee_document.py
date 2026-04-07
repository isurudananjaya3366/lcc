"""Employee document model for the Employees application."""

import os

from django.conf import settings
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.employees.constants import DOCUMENT_TYPE_CHOICES


def employee_document_upload_path(instance, filename):
    """Generate upload path for employee documents.

    Structure: employees/documents/<employee_id>/<document_type>/<filename>
    """
    employee_id = instance.employee.employee_id or "unknown"
    doc_type = instance.document_type or "other"
    return os.path.join("employees", "documents", employee_id, doc_type, filename)


class EmployeeDocument(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Stores employee documents such as contracts, certificates, NIC copies."""

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

    # File fields
    file = models.FileField(upload_to=employee_document_upload_path)
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="Size in bytes")
    file_type = models.CharField(max_length=100, blank=True, default="", help_text="MIME type")
    original_filename = models.CharField(max_length=255, blank=True, default="")

    # Date fields
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    # Visibility & sensitivity
    is_sensitive = models.BooleanField(default=False, help_text="Mark as sensitive/confidential")
    visible_to_employee = models.BooleanField(default=True, help_text="Visible in employee self-service portal")

    # Upload tracking
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_employee_documents",
    )

    # Verification
    is_verified = models.BooleanField(default=False, help_text="Whether the document has been verified")
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_employee_documents",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "employees_document"
        verbose_name = "Employee Document"
        verbose_name_plural = "Employee Documents"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["employee", "document_type"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.get_document_type_display()}: {self.title}"

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if document has expired."""
        if not self.expiry_date:
            return False
        from datetime import date
        return self.expiry_date < date.today()
