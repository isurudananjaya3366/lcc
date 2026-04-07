"""Vendor signals for auto-tracking history."""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

# Fields to track for change history
TRACKED_FIELDS = [
    "company_name", "vendor_type", "status", "payment_terms_days",
    "credit_limit", "rating", "primary_email", "primary_phone",
    "is_preferred_vendor", "tax_id", "business_registration",
]


@receiver(pre_save, sender="vendors.Vendor")
def capture_old_values(sender, instance, **kwargs):
    """Capture old field values before save for change tracking."""
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_values = {
                field: getattr(old_instance, field, None)
                for field in TRACKED_FIELDS
            }
        except sender.DoesNotExist:
            instance._old_values = {}
    else:
        instance._old_values = {}


@receiver(post_save, sender="vendors.Vendor")
def track_vendor_changes(sender, instance, created, **kwargs):
    """Auto-track vendor field changes."""
    from apps.vendors.services.history_service import VendorHistoryService

    if created:
        VendorHistoryService.record_creation(instance)
    else:
        old_data = getattr(instance, "_old_values", {})
        if old_data:
            VendorHistoryService.track_changes(instance, old_data)
