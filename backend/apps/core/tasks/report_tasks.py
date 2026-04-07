"""
LankaCommerce Cloud - Report Generation Celery Tasks.

Stub implementations for asynchronous report generation.
Actual report engine integration will be added in later phases.
"""

import logging

from celery import shared_task

from apps.core.tasks.base import TenantAwareTask

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    base=TenantAwareTask,
    name="apps.core.tasks.report_tasks.generate_report_task",
    max_retries=2,
    retry_backoff=True,
)
def generate_report_task(
    self,
    *,
    tenant_id: int,
    report_type: str,
    params: dict | None = None,
):
    """Generate a report for the specified tenant.

    This is a **stub** — the actual report engine is not yet implemented.
    The task logs the request and returns a placeholder result.

    Args:
        tenant_id: PK of the target :class:`~apps.tenants.models.Tenant`.
        report_type: Identifier for the report to generate
                     (e.g. ``"daily_sales"``, ``"inventory_summary"``).
        params: Optional parameters controlling report scope / filters.
    """
    params = params or {}
    logger.info(
        "Generating report '%s' for tenant %s with params %s",
        report_type,
        tenant_id,
        params,
    )

    # TODO: Integrate actual report generation engine.
    result = {
        "status": "generated",
        "report_type": report_type,
        "tenant_id": tenant_id,
        "params": params,
        "message": "Stub — report engine not yet implemented.",
    }

    logger.info("Report '%s' generation complete (stub)", report_type)
    return result
