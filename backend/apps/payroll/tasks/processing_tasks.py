"""Celery tasks for payroll processing."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="payroll.process_payroll",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    time_limit=3600,
    soft_time_limit=3300,
)
def process_payroll_task(self, payroll_run_id):
    """Process payroll for a given PayrollRun asynchronously.

    Args:
        payroll_run_id: UUID of the PayrollRun to process.
    """
    from apps.payroll.models import PayrollRun
    from apps.payroll.services.payroll_processor import PayrollProcessor

    try:
        payroll_run = PayrollRun.objects.get(pk=payroll_run_id)
        processor = PayrollProcessor(payroll_run)
        result = processor.process_batch()
        logger.info(
            "Payroll processing completed for run %s: %s",
            payroll_run_id, result,
        )
        return result
    except PayrollRun.DoesNotExist:
        logger.error("PayrollRun %s not found", payroll_run_id)
        return {"error": f"PayrollRun {payroll_run_id} not found"}
    except Exception as exc:
        logger.exception("Payroll processing failed for run %s", payroll_run_id)
        raise self.retry(exc=exc)


def start_async_processing(payroll_run_id):
    """Trigger async payroll processing for a run.

    Args:
        payroll_run_id: UUID of the PayrollRun.

    Returns:
        Celery AsyncResult.
    """
    return process_payroll_task.delay(str(payroll_run_id))
