"""
POSettings model for the purchases application.

Stores configurable settings for the purchase order module.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class POSettings(UUIDMixin, TimestampMixin, models.Model):
    """Configuration settings for the purchase order module."""

    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="po_settings",
    )

    # PO Number Configuration
    po_number_prefix = models.CharField(
        max_length=10,
        default="PO",
        help_text="Prefix for auto-generated PO numbers",
    )

    # GRN Number Configuration
    grn_number_prefix = models.CharField(
        max_length=10,
        default="GRN",
        help_text="Prefix for auto-generated GRN numbers",
    )
    grn_number_sequence = models.PositiveIntegerField(
        default=1,
        help_text="Next GRN sequence number",
    )

    # Approval Settings
    requires_approval_above = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="POs above this amount require approval. 0 = no approval required.",
    )

    # Default Values
    default_payment_terms = models.CharField(
        max_length=50,
        blank=True,
        default="Net 30",
    )
    default_payment_terms_days = models.PositiveIntegerField(default=30)
    default_currency = models.CharField(max_length=3, default="LKR")
    default_shipping_method = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Default shipping method for new POs",
    )

    # Receiving Settings
    allow_partial_receiving = models.BooleanField(
        default=True,
        help_text="Allow partial receiving on purchase orders",
    )
    require_vendor_reference = models.BooleanField(
        default=False,
        help_text="Require vendor reference before acknowledging a PO",
    )
    auto_close_on_full_receive = models.BooleanField(
        default=False,
        help_text="Automatically close PO when fully received",
    )

    # Email/Notification Settings
    auto_send_email = models.BooleanField(
        default=False,
        help_text="Automatically send PO to vendor on approval/send",
    )
    notify_on_approval = models.BooleanField(
        default=True,
        help_text="Send notification when PO is approved",
    )
    notify_on_acknowledgment = models.BooleanField(
        default=True,
        help_text="Send notification when vendor acknowledges PO",
    )
    overdue_reminder_days = models.PositiveIntegerField(
        default=3,
        help_text="Days past expected delivery to send overdue reminders",
    )

    class Meta:
        verbose_name = "PO Settings"
        verbose_name_plural = "PO Settings"

    def __str__(self):
        return f"PO Settings (prefix={self.po_number_prefix})"

    @classmethod
    def get_for_tenant(cls, tenant=None):
        """
        Get or create POSettings for the given tenant.

        Args:
            tenant: Tenant instance (optional, uses first settings if None).

        Returns:
            POSettings instance.
        """
        if tenant:
            settings, _ = cls.objects.get_or_create(tenant=tenant)
        else:
            settings = cls.objects.first()
            if not settings:
                settings = cls.objects.create()
        return settings

    def save(self, *args, **kwargs):
        """Ensure only one settings instance per tenant."""
        if not self.tenant_id:
            existing = POSettings.objects.filter(
                tenant__isnull=True
            ).exclude(pk=self.pk).first()
            if existing:
                POSettings.objects.filter(pk=existing.pk).update(
                    po_number_prefix=self.po_number_prefix,
                    grn_number_prefix=self.grn_number_prefix,
                    grn_number_sequence=self.grn_number_sequence,
                    requires_approval_above=self.requires_approval_above,
                    default_payment_terms=self.default_payment_terms,
                    default_payment_terms_days=self.default_payment_terms_days,
                    default_currency=self.default_currency,
                    default_shipping_method=self.default_shipping_method,
                    allow_partial_receiving=self.allow_partial_receiving,
                    require_vendor_reference=self.require_vendor_reference,
                    auto_close_on_full_receive=self.auto_close_on_full_receive,
                    auto_send_email=self.auto_send_email,
                    notify_on_approval=self.notify_on_approval,
                    notify_on_acknowledgment=self.notify_on_acknowledgment,
                    overdue_reminder_days=self.overdue_reminder_days,
                )
                self.pk = existing.pk
                return
        super().save(*args, **kwargs)
