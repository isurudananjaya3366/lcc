"""Payment receipt model."""

from django.conf import settings
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin


def receipt_pdf_path(instance, filename):
    """Generate upload path for receipt PDF using receipt number."""
    year = instance.receipt_date.year
    month = instance.receipt_date.month
    return f"receipts/pdfs/{year}/{month:02d}/{instance.receipt_number}.pdf"


class PaymentReceipt(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Stores generated payment receipts."""

    receipt_number = models.CharField(max_length=30, unique=True, db_index=True)
    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.PROTECT,
        related_name="receipt",
    )
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_receipts",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="payment_receipts",
    )
    receipt_date = models.DateField()
    receipt_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    reference_number = models.CharField(max_length=100, blank=True, default="")
    currency = models.CharField(max_length=3, default="LKR")
    exchange_rate = models.DecimalField(
        max_digits=12, decimal_places=6, null=True, blank=True
    )

    # PDF fields
    pdf_file = models.FileField(
        upload_to=receipt_pdf_path, null=True, blank=True
    )
    pdf_generated_at = models.DateTimeField(null=True, blank=True)

    # Delivery fields
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_to = models.EmailField(null=True, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_receipts",
    )

    # Generation tracking
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_generated_receipts",
    )

    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-receipt_date", "-created_on"]
        indexes = [
            models.Index(fields=["customer", "-receipt_date"]),
            models.Index(fields=["payment"]),
            models.Index(fields=["invoice"]),
            models.Index(fields=["-receipt_date"]),
            models.Index(fields=["is_sent", "-sent_at"]),
        ]

    def __str__(self):
        return f"{self.receipt_number} - {self.receipt_amount} {self.currency}"

    def has_pdf(self):
        """Check if PDF file has been generated."""
        return bool(self.pdf_file)

    def get_pdf_url(self):
        """Get the PDF download URL."""
        if self.pdf_file:
            return self.pdf_file.url
        return None

    def mark_as_sent(self, sent_to, sent_by=None):
        """Mark receipt as sent to the given email."""
        from django.utils import timezone

        self.is_sent = True
        self.sent_at = timezone.now()
        self.sent_to = sent_to
        self.sent_by = sent_by
        self.save(update_fields=["is_sent", "sent_at", "sent_to", "sent_by", "updated_on"])

    def get_display_method(self):
        """Return human-readable payment method name."""
        from apps.payments.constants import PaymentMethod

        return PaymentMethod(self.payment_method).label
