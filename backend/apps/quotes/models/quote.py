"""
Quote Model

Represents a sales quote/quotation in the system.
Tracks lifecycle from draft through sending, acceptance, and conversion.
"""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.quotes.constants import (
    CURRENCY_SYMBOLS,
    CurrencyChoice,
    DiscountType,
    EDITABLE_STATES,
    QuoteStatus,
    TERMINAL_STATES,
)


def quote_pdf_path(instance, filename):
    """
    Generate file path for quote PDF.

    Returns path: quotes/pdfs/{year}/{quote_number}.pdf
    Example: quotes/pdfs/2026/QT-2026-00001.pdf
    """
    year = instance.created_on.year if instance.created_on else timezone.now().year
    return f"quotes/pdfs/{year}/{instance.quote_number}.pdf"


class QuoteManager(models.Manager):
    """Custom manager for Quote model."""

    def drafts(self):
        return self.filter(status=QuoteStatus.DRAFT)

    def sent(self):
        return self.filter(status=QuoteStatus.SENT)

    def accepted(self):
        return self.filter(status=QuoteStatus.ACCEPTED)

    def converted(self):
        return self.filter(status=QuoteStatus.CONVERTED)

    def expired(self):
        return self.filter(status=QuoteStatus.EXPIRED)

    def active(self):
        """Return non-terminal quotes."""
        return self.exclude(status__in=TERMINAL_STATES)


class Quote(models.Model):
    """
    Sales Quote Model.

    Represents a quotation sent to customers with pricing and terms.
    Tracks lifecycle from draft through sending, acceptance, and conversion.

    Financial Calculation:
        total = subtotal - discount_amount + tax_amount
    """

    # Core identification
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    quote_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        db_index=True,
        help_text="Auto-generated quote number (QT-YYYY-NNNNN)",
    )
    status = models.CharField(
        max_length=20,
        choices=QuoteStatus.choices,
        default=QuoteStatus.DRAFT,
        db_index=True,
        help_text="Current status of the quote",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional descriptive title for the quote",
    )

    # Timestamps (auto-managed)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(auto_now=True)

    # Customer relationship
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="quotes",
        null=True,
        blank=True,
        db_index=True,
        help_text="Registered customer for this quote",
    )

    # Guest customer details (alternative to customer FK)
    guest_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Name for guest customer (if not registered)",
    )
    guest_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email for guest customer",
    )
    guest_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone for guest customer",
    )
    guest_company = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Company name for B2B guest customers",
    )

    # Date tracking fields
    issue_date = models.DateField(
        default=timezone.now,
        db_index=True,
        help_text="Date the quote was issued",
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date the quote expires",
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When quote was sent to customer (DRAFT → SENT)",
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When customer accepted the quote",
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When customer rejected the quote",
    )
    expired_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the quote expired",
    )
    converted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When quote was converted to order",
    )

    # Financial summary fields
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Sum of all line items before discount and tax",
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total discount amount (calculated from discount fields)",
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total tax/VAT amount",
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_index=True,
        help_text="Final total (subtotal - discount + tax)",
    )

    # Metadata fields
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes for customer (shown in PDF)",
    )
    terms = models.TextField(
        blank=True,
        null=True,
        help_text="Terms and conditions (shown in PDF)",
    )
    internal_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes (staff only, not visible to customer)",
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Comma-separated tags for categorization",
    )
    attachment_count = models.IntegerField(
        default=0,
        help_text="Number of attachments (denormalized count)",
    )

    # User references
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="quotes_created",
        null=True,
        blank=True,
        db_index=True,
        help_text="User who created this quote",
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="quotes_sent",
        null=True,
        blank=True,
        help_text="User who sent this quote to customer",
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="quotes_accepted_by",
        null=True,
        blank=True,
        help_text="User who marked this quote as accepted",
    )

    # Currency field
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoice.choices,
        default=CurrencyChoice.LKR,
        db_index=True,
        help_text="Currency for all amounts in this quote",
    )

    # Discount fields
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        null=True,
        blank=True,
        help_text="Type of header-level discount (percentage or fixed)",
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Discount value (percentage amount or fixed currency amount)",
    )

    # Template link
    template = models.ForeignKey(
        "quotes.QuoteTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
        help_text="PDF template used for this quote",
    )

    # PDF storage fields
    pdf_file = models.FileField(
        upload_to=quote_pdf_path,
        max_length=500,
        null=True,
        blank=True,
        help_text="Generated PDF file for this quote",
    )
    pdf_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when PDF was last generated",
    )
    pdf_file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Size of generated PDF in bytes",
    )
    pdf_regeneration_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times PDF has been regenerated",
    )
    public_token = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
        help_text="Public token for unauthenticated quote access / download",
    )

    # Email tracking fields
    email_sent_to = models.EmailField(
        null=True,
        blank=True,
        help_text="Email address where quote was sent",
    )
    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when quote email was last sent",
    )
    email_sent_count = models.IntegerField(
        default=0,
        help_text="Number of times quote email has been sent",
    )
    email_opened_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when quote email was first opened",
    )
    email_opened_count = models.IntegerField(
        default=0,
        help_text="Number of times quote email has been opened",
    )
    email_last_error = models.TextField(
        null=True,
        blank=True,
        help_text="Last error message if email send failed",
    )

    # Public view tracking (Task 80)
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times the public quote has been viewed",
    )
    last_viewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the public quote was last viewed",
    )

    # Conversion tracking
    converted_to_order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        related_name="converted_from_quote",
        null=True,
        blank=True,
        db_index=True,
        help_text="Sales order created from this quote (if converted)",
    )

    # Rejection details
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="quotes_rejected_by",
        null=True,
        blank=True,
        help_text="User who rejected this quote",
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for quote rejection",
    )

    # Revision tracking
    revision_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revisions",
        help_text="Original quote this is a revision of",
    )
    revision_number = models.PositiveIntegerField(
        default=1,
        help_text="Revision number (1 = original)",
    )
    is_latest_revision = models.BooleanField(
        default=True,
        help_text="Whether this is the latest revision",
    )

    objects = QuoteManager()

    class Meta:
        db_table = "quotes"
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["customer", "status"],
                name="quotes_customer_status_idx",
            ),
            models.Index(
                fields=["status", "-created_on"],
                name="quotes_status_created_idx",
            ),
            models.Index(
                fields=["status", "valid_until"],
                name="quotes_status_valid_idx",
            ),
            models.Index(
                fields=["created_by", "status"],
                name="quotes_creator_status_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(subtotal__gte=0),
                name="quotes_subtotal_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(discount_amount__gte=0),
                name="quotes_discount_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(tax_amount__gte=0),
                name="quotes_tax_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(total__gte=0),
                name="quotes_total_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(discount_value__gte=0),
                name="quotes_discount_value_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(email_sent_count__gte=0),
                name="quotes_email_sent_count_non_negative",
            ),
        ]

    def __str__(self):
        return self.quote_number or "New Quote"

    def __repr__(self):
        return f"<Quote: {self.quote_number} ({self.status})>"

    def save(self, *args, **kwargs):
        if not self.quote_number:
            from apps.quotes.services.quote_number_generator import (
                QuoteNumberGenerator,
            )

            self.quote_number = QuoteNumberGenerator.generate()
        super().save(*args, **kwargs)

    def clean(self):
        """Validate model constraints."""
        super().clean()
        if self.valid_until and self.issue_date and self.valid_until < self.issue_date:
            raise ValidationError(
                {"valid_until": "Expiry date must be after issue date."}
            )
        if self.status in TERMINAL_STATES and self.pk:
            try:
                old = Quote.objects.get(pk=self.pk)
                if old.status in TERMINAL_STATES and old.status != self.status:
                    raise ValidationError(
                        {"status": f"Cannot change status from terminal state '{old.status}'."}
                    )
            except Quote.DoesNotExist:
                pass

    @property
    def is_editable(self):
        """Check if the quote can be edited."""
        return self.status in EDITABLE_STATES

    @property
    def is_expired(self):
        """Check if the quote has passed its validity date."""
        if self.valid_until:
            return timezone.now().date() > self.valid_until
        return False

    @property
    def currency_symbol(self):
        """Return the display symbol for the quote currency."""
        return CURRENCY_SYMBOLS.get(self.currency, self.currency)

    @property
    def customer_display_name(self):
        """Return the display name for the customer (registered or guest)."""
        if self.customer:
            return str(self.customer)
        return self.guest_name or "Unknown Customer"

    @property
    def customer_email_address(self):
        """Return the email address for the customer."""
        if self.customer and hasattr(self.customer, "email"):
            return self.customer.email
        return self.guest_email

    @property
    def days_until_expiry(self):
        """Return the number of days until the quote expires."""
        if self.valid_until:
            delta = self.valid_until - timezone.now().date()
            return delta.days
        return None

    # ── Locking (Task 47) ────────────────────────────────────────

    @property
    def is_locked(self):
        """A quote is locked once it leaves DRAFT status."""
        return self.status not in EDITABLE_STATES

    def can_edit(self, user=None):
        """Check if quote can be edited by the given user."""
        if self.is_locked:
            return False
        if user and hasattr(user, "has_perm") and not user.has_perm("quotes.change_quote"):
            return False
        return True

    def can_delete(self, user=None):
        """Only DRAFT quotes without linked orders may be deleted."""
        if self.status != QuoteStatus.DRAFT:
            return False
        if self.converted_to_order_id:
            return False
        return True

    # ── Revision Helpers (Task 46) ───────────────────────────────

    def get_revision_history(self):
        """Return all revisions including the root quote."""
        from django.db.models import Q

        root = self.revision_of or self
        return Quote.objects.filter(
            Q(id=root.id) | Q(revision_of=root)
        ).order_by("revision_number")

    def get_latest_revision(self):
        """Return the latest revision of this quote chain."""
        if self.is_latest_revision:
            return self
        root = self.revision_of or self
        latest = root.revisions.filter(is_latest_revision=True).first()
        return latest or self

    # ── Default Validity (Task 51) ───────────────────────────────

    @classmethod
    def get_default_validity_days(cls, tenant=None):
        """Get the default validity days from tenant settings."""
        if tenant:
            try:
                from apps.quotes.models.settings import QuoteSettings

                return QuoteSettings.objects.get(tenant=tenant).default_validity_days
            except Exception:
                pass
        return 30

    @classmethod
    def calculate_valid_until(cls, issue_date, validity_days):
        """Calculate valid_until date from issue_date and days."""
        from datetime import timedelta

        return issue_date + timedelta(days=validity_days)

    # ── PDF Helpers (Task 58) ────────────────────────────────────

    @property
    def needs_regeneration(self):
        """True if the quote has been modified after the last PDF was generated."""
        if not self.pdf_generated_at:
            return True
        return self.updated_on > self.pdf_generated_at

    def get_public_url(self, request=None):
        """Return the public download URL using the public_token."""
        if not self.public_token:
            return None
        path = f"/api/v1/quotes/public/{self.public_token}/pdf/"
        if request:
            return request.build_absolute_uri(path)
        return path

    def regenerate_pdf(self, force=False):
        """Regenerate the PDF for this quote."""
        if not force and not self.needs_regeneration:
            return self.pdf_file

        from apps.quotes.services.pdf_generator import QuotePDFGenerator

        generator = QuotePDFGenerator(self)
        return generator.generate_and_save()
