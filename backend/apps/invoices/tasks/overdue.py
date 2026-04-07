"""
Celery task for checking and marking overdue invoices.
"""

import logging
from datetime import datetime

from celery import shared_task
from django_tenants.utils import schema_context

logger = logging.getLogger(__name__)


@shared_task(name="invoices.check_overdue", bind=True, max_retries=3)
def check_overdue_invoices_task(self):
    """Daily task to mark overdue invoices across all tenants."""
    from apps.invoices.services.invoice_service import InvoiceService

    start_time = datetime.now()
    try:
        from django_tenants.utils import get_tenant_model
        TenantModel = get_tenant_model()
        results = []

        for tenant in TenantModel.objects.filter(is_active=True):
            with schema_context(tenant.schema_name):
                try:
                    count = InvoiceService.check_and_mark_overdue()
                    results.append({
                        "tenant": tenant.name,
                        "overdue_count": count,
                    })
                except Exception as e:
                    logger.error("Error checking overdue for %s: %s", tenant.name, e)

        total_overdue = sum(r["overdue_count"] for r in results)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            "Overdue check complete: %d invoices marked in %.1fs across %d tenants",
            total_overdue, duration, len(results),
        )
        return results

    except Exception as exc:
        logger.error("Overdue task failed: %s", exc)
        raise self.retry(exc=exc, countdown=300)
