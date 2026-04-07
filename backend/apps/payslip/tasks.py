"""Celery tasks for bulk payslip generation and email distribution."""

import logging
import time

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

# Email throttle: minimum seconds between sends
EMAIL_THROTTLE_SECONDS = 1


@shared_task(bind=True, max_retries=3, soft_time_limit=3600)
def bulk_generate_payslips(self, batch_id):
    """Generate PDF payslips for all payslips in a batch.

    Args:
        batch_id: UUID of the PayslipBatch record.
    """
    from apps.payslip.constants import PayslipStatus
    from apps.payslip.models import Payslip, PayslipBatch
    from apps.payslip.models.payslip_batch import BatchStatus
    from apps.payslip.services.generator import (
        PayslipGenerationError,
        PayslipGenerator,
    )

    try:
        batch = PayslipBatch.objects.get(pk=batch_id)
    except PayslipBatch.DoesNotExist:
        logger.error("Batch %s not found", batch_id)
        return

    batch.status = BatchStatus.PROCESSING
    batch.started_at = timezone.now()
    batch.save(update_fields=["status", "started_at"])

    payslips = Payslip.objects.filter(
        payroll_period=batch.payroll_period,
        status=PayslipStatus.DRAFT,
    )
    batch.total_count = payslips.count()
    batch.save(update_fields=["total_count"])

    generator = PayslipGenerator()
    errors = []

    for payslip in payslips.iterator():
        try:
            generator.generate(payslip.pk, user=batch.initiated_by)
            batch.success_count += 1
        except PayslipGenerationError as exc:
            batch.failed_count += 1
            errors.append(f"{payslip.slip_number}: {exc}")
            logger.warning(
                "Failed to generate %s: %s", payslip.slip_number, exc
            )
        except Exception as exc:
            batch.failed_count += 1
            errors.append(f"{payslip.slip_number}: {exc}")
            logger.exception(
                "Unexpected error generating %s", payslip.slip_number
            )

        # Save progress periodically
        if (batch.success_count + batch.failed_count) % 10 == 0:
            batch.save(update_fields=["success_count", "failed_count"])

    # Finalize batch
    batch.completed_at = timezone.now()
    if errors:
        batch.error_log = "\n".join(errors)
    batch.status = (
        BatchStatus.COMPLETED
        if batch.failed_count == 0
        else (
            BatchStatus.FAILED
            if batch.success_count == 0
            else BatchStatus.PARTIAL
        )
    )
    batch.save()

    logger.info(
        "Batch %s completed: %d success, %d failed of %d total",
        batch_id,
        batch.success_count,
        batch.failed_count,
        batch.total_count,
    )


@shared_task(bind=True, max_retries=3, soft_time_limit=3600)
def bulk_send_payslip_emails(self, batch_id):
    """Send payslip emails for all generated payslips in a batch.

    Args:
        batch_id: UUID of the PayslipBatch record.
    """
    from apps.payslip.constants import PayslipStatus
    from apps.payslip.models import Payslip, PayslipBatch
    from apps.payslip.models.payslip_batch import BatchStatus
    from apps.payslip.services.emailer import (
        PayslipEmailer,
        PayslipEmailError,
    )

    try:
        batch = PayslipBatch.objects.get(pk=batch_id)
    except PayslipBatch.DoesNotExist:
        logger.error("Email batch %s not found", batch_id)
        return

    batch.status = BatchStatus.PROCESSING
    batch.started_at = timezone.now()
    batch.save(update_fields=["status", "started_at"])

    payslips = Payslip.objects.filter(
        payroll_period=batch.payroll_period,
        status=PayslipStatus.GENERATED,
        email_sent=False,
    ).select_related("employee")

    batch.total_count = payslips.count()
    batch.save(update_fields=["total_count"])

    emailer = PayslipEmailer()
    errors = []

    for payslip in payslips.iterator():
        try:
            emailer.send(payslip)
            batch.success_count += 1
        except PayslipEmailError as exc:
            batch.failed_count += 1
            errors.append(f"{payslip.slip_number}: {exc}")
            logger.warning(
                "Failed to email %s: %s", payslip.slip_number, exc
            )
        except Exception as exc:
            batch.failed_count += 1
            errors.append(f"{payslip.slip_number}: {exc}")
            logger.exception(
                "Unexpected error emailing %s", payslip.slip_number
            )

        # Throttle email sending
        time.sleep(EMAIL_THROTTLE_SECONDS)

        # Save progress periodically
        if (batch.success_count + batch.failed_count) % 10 == 0:
            batch.save(update_fields=["success_count", "failed_count"])

    # Finalize batch
    batch.completed_at = timezone.now()
    if errors:
        batch.error_log = "\n".join(errors)
    batch.status = (
        BatchStatus.COMPLETED
        if batch.failed_count == 0
        else (
            BatchStatus.FAILED
            if batch.success_count == 0
            else BatchStatus.PARTIAL
        )
    )
    batch.save()

    logger.info(
        "Email batch %s completed: %d success, %d failed of %d total",
        batch_id,
        batch.success_count,
        batch.failed_count,
        batch.total_count,
    )
