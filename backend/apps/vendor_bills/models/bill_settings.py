"""BillSettings model for the vendor_bills application.

Stores tenant-specific configuration for the vendor bills module.
"""

from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class BillSettings(UUIDMixin, TimestampMixin, models.Model):
    """Configuration settings for the vendor bills module."""

    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bill_settings",
    )

    # Bill Number Configuration
    bill_number_prefix = models.CharField(
        max_length=10,
        default="BILL",
        help_text="Prefix for auto-generated bill numbers",
    )
    bill_number_sequence = models.PositiveIntegerField(
        default=1,
        help_text="Next bill sequence number",
    )
    bill_number_padding = models.PositiveSmallIntegerField(
        default=5,
        help_text="Zero-padding length for bill numbers",
    )
    include_year_in_number = models.BooleanField(
        default=True,
        help_text="Include year in bill number (BILL-2026-00001)",
    )

    # Approval Settings
    require_approval = models.BooleanField(
        default=True,
        help_text="Require approval before payment",
    )
    approval_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Bills above this amount require approval. 0 = all bills.",
    )
    auto_approve_matched = models.BooleanField(
        default=False,
        help_text="Auto-approve perfectly matched bills",
    )

    # Tolerance Settings
    quantity_tolerance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5,
        help_text="Acceptable quantity variance percentage",
    )
    price_tolerance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=2,
        help_text="Acceptable price variance percentage",
    )

    # Payment Defaults
    default_payment_terms = models.PositiveIntegerField(
        default=30,
        help_text="Default payment terms in days",
    )
    allow_early_payment_discount = models.BooleanField(
        default=False,
        help_text="Enable early payment discount tracking",
    )
    early_payment_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,
        help_text="Discount percentage for early payment",
    )
    early_payment_discount_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        help_text="Days within which early payment discount applies",
    )

    # Workflow Settings
    require_po_reference = models.BooleanField(
        default=False,
        help_text="Require PO reference for manual bills",
    )
    enable_dispute_workflow = models.BooleanField(
        default=True,
        help_text="Enable bill dispute functionality",
    )

    class Meta:
        verbose_name = "Bill Settings"
        verbose_name_plural = "Bill Settings"

    def __str__(self):
        return f"Bill Settings (prefix={self.bill_number_prefix})"

    @classmethod
    def get_for_tenant(cls, tenant=None):
        """Get or create BillSettings for the given tenant."""
        if tenant:
            settings, _ = cls.objects.get_or_create(tenant=tenant)
        else:
            settings = cls.objects.first()
            if not settings:
                settings = cls.objects.create()
        return settings

    def get_next_bill_number(self):
        """Generate the next bill number and increment the sequence."""
        from django.utils import timezone

        seq = self.bill_number_sequence
        padded = str(seq).zfill(self.bill_number_padding)

        if self.include_year_in_number:
            year = timezone.now().year
            number = f"{self.bill_number_prefix}-{year}-{padded}"
        else:
            number = f"{self.bill_number_prefix}-{padded}"

        self.bill_number_sequence = seq + 1
        self.save(update_fields=["bill_number_sequence"])
        return number

    def is_approval_required(self, bill_total):
        """Check if approval is required for a given bill total."""
        if not self.require_approval:
            return False
        if self.approval_threshold == 0:
            return True
        return bill_total >= self.approval_threshold

    def save(self, *args, **kwargs):
        """Ensure only one settings instance per tenant."""
        if not self.tenant_id:
            existing = BillSettings.objects.filter(
                tenant__isnull=True
            ).exclude(pk=self.pk).first()
            if existing:
                BillSettings.objects.filter(pk=existing.pk).update(
                    bill_number_prefix=self.bill_number_prefix,
                    bill_number_sequence=self.bill_number_sequence,
                    bill_number_padding=self.bill_number_padding,
                    include_year_in_number=self.include_year_in_number,
                    require_approval=self.require_approval,
                    approval_threshold=self.approval_threshold,
                    auto_approve_matched=self.auto_approve_matched,
                    quantity_tolerance_percentage=self.quantity_tolerance_percentage,
                    price_tolerance_percentage=self.price_tolerance_percentage,
                    default_payment_terms=self.default_payment_terms,
                    allow_early_payment_discount=self.allow_early_payment_discount,
                    early_payment_discount_percentage=self.early_payment_discount_percentage,
                    early_payment_discount_days=self.early_payment_discount_days,
                    require_po_reference=self.require_po_reference,
                    enable_dispute_workflow=self.enable_dispute_workflow,
                )
                self.pk = existing.pk
                return
        super().save(*args, **kwargs)
