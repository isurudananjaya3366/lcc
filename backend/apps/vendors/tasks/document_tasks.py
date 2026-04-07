"""Celery tasks for vendor document management."""

from celery import shared_task


@shared_task
def check_expiring_documents():
    """Check for vendor documents approaching expiry and flag them by urgency."""
    from django.utils import timezone
    from apps.vendors.models import VendorDocument

    today = timezone.now().date()
    results = {"expired": 0, "critical": 0, "urgent": 0, "warning": 0, "info": 0}

    docs_with_expiry = VendorDocument.objects.filter(
        expiry_date__isnull=False,
    ).select_related("vendor")

    for doc in docs_with_expiry:
        days_until = (doc.expiry_date - today).days
        if days_until <= 0:
            results["expired"] += 1
        elif days_until <= 1:
            results["critical"] += 1
        elif days_until <= 7:
            results["urgent"] += 1
        elif days_until <= 14:
            results["warning"] += 1
        elif days_until <= 30:
            results["info"] += 1

    total = sum(results.values())
    return (
        f"Document expiry check: {total} documents flagged — "
        f"expired={results['expired']}, critical={results['critical']}, "
        f"urgent={results['urgent']}, warning={results['warning']}, info={results['info']}"
    )
