"""
Tax submission tracking model.

Records filed tax returns with Sri Lankan tax authorities
(Inland Revenue Department, CBSL, ETF Board). Stores submission
details including acknowledgment numbers, filing dates, and
confirmation documents for audit compliance.
"""

import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin

from ..tax.enums import FilingStatus


def tax_submission_upload_path(instance, filename):
    """Dynamic upload path: tax_submissions/{year}/{month}/{filename}."""
    now = timezone.now()
    ext = os.path.splitext(filename)[1]
    safe_name = (instance.submission_reference or str(instance.pk)) + ext
    return f"tax_submissions/{now.year}/{now.month:02d}/{safe_name}"


class TaxSubmission(UUIDMixin, models.Model):
    """
    Tracks a filed tax return submission.

    Each record represents one submission of a tax return to the
    relevant Sri Lankan authority (IRD for VAT/PAYE, CBSL for EPF,
    ETF Board for ETF). Linked to a TaxPeriodRecord to associate
    submissions with specific filing periods.
    """

    class SubmissionStatus(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Return Filed"
        ACCEPTED = "ACCEPTED", "Accepted & Processed"
        REJECTED = "REJECTED", "Rejected"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"

    # ── Relationships ───────────────────────────────────────────────
    tax_period = models.ForeignKey(
        "accounting.TaxPeriodRecord",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tax_submissions",
    )

    # ── Submission Details ──────────────────────────────────────────
    # Reference formats by authority:
    #   IRD VAT:  VAT-YYYY-NNNNNN
    #   IRD PAYE: PAYE-YYYY-NNNNNN
    #   CBSL EPF: EPF-C-YYYY-NNNNN
    #   ETF Board: ETF-YYYY-NNNNN
    submission_reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Acknowledgment number from tax authority.",
    )

    # submitted_at = when filed with authority
    # created_at   = when record created in this system (may differ)
    submitted_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Date and time the return was filed with the authority.",
    )

    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.SUBMITTED,
        db_index=True,
    )

    confirmation_document = models.FileField(
        upload_to=tax_submission_upload_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "png", "tiff"]),
        ],
        help_text="Official confirmation document from tax authority (max 10 MB).",
    )

    notes = models.TextField(blank=True, default="")

    # ── Timestamps ──────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_tax_submission"
        verbose_name = "Tax Submission"
        verbose_name_plural = "Tax Submissions"
        ordering = ["-submitted_at"]

    # ── String Representation ───────────────────────────────────────
    def __str__(self):
        ref = f" - {self.submission_reference}" if self.submission_reference else ""
        return (
            f"{self.tax_period.tax_type} "
            f"{self.tax_period.year}/{self.tax_period.period_number}"
            f"{ref} - {self.get_status_display()}"
        )

    # ── Validation ──────────────────────────────────────────────────
    def clean(self):
        super().clean()
        if (
            self.status == self.SubmissionStatus.ACCEPTED
            and not self.submission_reference
        ):
            raise ValidationError(
                {"submission_reference": "Accepted submissions must have a reference number."}
            )
        if self.confirmation_document and self.confirmation_document.size > 10 * 1024 * 1024:
            raise ValidationError(
                {"confirmation_document": "File size must not exceed 10 MB."}
            )

    # ── Status Properties ───────────────────────────────────────────
    @property
    def is_accepted(self):
        return self.status == self.SubmissionStatus.ACCEPTED

    @property
    def is_pending(self):
        return self.status in (
            self.SubmissionStatus.SUBMITTED,
            self.SubmissionStatus.UNDER_REVIEW,
        )

    @property
    def can_resubmit(self):
        return self.status == self.SubmissionStatus.REJECTED

    # ── Deadline helpers ────────────────────────────────────────────
    @property
    def is_submitted_on_time(self):
        if not self.tax_period.due_date:
            return True
        return self.submitted_at.date() <= self.tax_period.due_date

    def get_days_late(self):
        if not self.tax_period.due_date:
            return 0
        delta = (self.submitted_at.date() - self.tax_period.due_date).days
        return max(delta, 0)

    def get_days_early(self):
        if not self.tax_period.due_date:
            return 0
        delta = (self.tax_period.due_date - self.submitted_at.date()).days
        return max(delta, 0)

    # ── Lookup ──────────────────────────────────────────────────────
    @classmethod
    def get_by_reference(cls, reference):
        """Return submission matching the given authority reference, or None."""
        try:
            return cls.objects.get(submission_reference=reference)
        except cls.DoesNotExist:
            return None

    # ── Document helpers ────────────────────────────────────────────
    @property
    def has_confirmation_document(self):
        return bool(self.confirmation_document)

    def get_document_url(self):
        if self.confirmation_document:
            return self.confirmation_document.url
        return None

    def delete(self, *args, **kwargs):
        if self.confirmation_document:
            storage = self.confirmation_document.storage
            name = self.confirmation_document.name
            super().delete(*args, **kwargs)
            storage.delete(name)
        else:
            super().delete(*args, **kwargs)
