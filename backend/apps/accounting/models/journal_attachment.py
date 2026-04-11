"""
JournalEntryAttachment model for the accounting application.

Stores document attachments associated with journal entries.
Supports S3-compatible storage for uploaded files.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin


def journal_attachment_upload_path(instance, filename):
    """Generate S3-compatible upload path for journal attachments."""
    entry_number = instance.journal_entry.entry_number if instance.journal_entry_id else "draft"
    return f"accounting/journal-entries/{entry_number}/{filename}"


class JournalEntryAttachment(UUIDMixin, models.Model):
    """
    Document attachment for a journal entry.

    Stores supporting documents (invoices, receipts, contracts, etc.)
    linked to a specific journal entry for audit trail purposes.
    """

    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Journal Entry",
        help_text="The journal entry this attachment belongs to.",
    )

    file = models.FileField(
        upload_to=journal_attachment_upload_path,
        verbose_name="File",
        help_text="Uploaded document file.",
    )

    original_filename = models.CharField(
        max_length=255,
        verbose_name="Original Filename",
        help_text="Original name of the uploaded file.",
    )

    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name="File Size",
        help_text="File size in bytes.",
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="MIME Type",
        help_text="MIME type of the uploaded file.",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Optional description of the attachment.",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_attachments",
        verbose_name="Uploaded By",
        help_text="User who uploaded this attachment.",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Uploaded At",
        help_text="Timestamp when this attachment was uploaded.",
    )

    class Meta:
        db_table = "accounting_journal_entry_attachment"
        verbose_name = "Journal Entry Attachment"
        verbose_name_plural = "Journal Entry Attachments"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_filename} ({self.journal_entry.entry_number})"
