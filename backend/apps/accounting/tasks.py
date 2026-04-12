"""
Celery tasks for journal entry auto-generation and recurring processing.

Asynchronous tasks that generate journal entries from business
transactions. Tasks are triggered by Django signals when source
documents are created or updated. Also includes a periodic task
for processing recurring entries via Celery Beat.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_sales_entry(self, invoice_id):
    """Generate a journal entry from a sales invoice."""
    try:
        from apps.accounting.services.auto_entry import SalesEntryGenerator

        # Lazy import — module may not exist yet
        try:
            from apps.sales.models import SalesInvoice
            invoice = SalesInvoice.objects.get(pk=invoice_id)
        except (ImportError, LookupError):
            logger.warning("SalesInvoice model not available; skipping entry generation.")
            return None

        generator = SalesEntryGenerator(invoice)
        entry = generator.generate_entry()
        logger.info("Generated sales entry %s for invoice %s", entry.entry_number, invoice_id)
        return str(entry.id)
    except Exception as exc:
        logger.exception("Failed to generate sales entry for invoice %s", invoice_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_purchase_entry(self, bill_id):
    """Generate a journal entry from a purchase bill."""
    try:
        from apps.accounting.services.auto_entry import PurchaseEntryGenerator

        try:
            from apps.purchases.models import PurchaseBill
            bill = PurchaseBill.objects.get(pk=bill_id)
        except (ImportError, LookupError):
            logger.warning("PurchaseBill model not available; skipping entry generation.")
            return None

        generator = PurchaseEntryGenerator(bill)
        entry = generator.generate_entry()
        logger.info("Generated purchase entry %s for bill %s", entry.entry_number, bill_id)
        return str(entry.id)
    except Exception as exc:
        logger.exception("Failed to generate purchase entry for bill %s", bill_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_payment_entry(self, payment_id):
    """Generate a journal entry from a payment transaction."""
    try:
        from apps.accounting.services.auto_entry import PaymentEntryGenerator

        try:
            from apps.payments.models import Payment
            payment = Payment.objects.get(pk=payment_id)
        except (ImportError, LookupError):
            logger.warning("Payment model not available; skipping entry generation.")
            return None

        generator = PaymentEntryGenerator(payment)
        entry = generator.generate_entry()
        logger.info("Generated payment entry %s for payment %s", entry.entry_number, payment_id)
        return str(entry.id)
    except Exception as exc:
        logger.exception("Failed to generate payment entry for payment %s", payment_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_payroll_entry(self, payroll_id):
    """Generate a journal entry from a payroll run."""
    try:
        from apps.accounting.services.auto_entry import PayrollEntryGenerator

        try:
            from apps.hr.models import PayrollRun
            payroll = PayrollRun.objects.get(pk=payroll_id)
        except (ImportError, LookupError):
            logger.warning("PayrollRun model not available; skipping entry generation.")
            return None

        generator = PayrollEntryGenerator(payroll)
        entry = generator.generate_entry()
        logger.info("Generated payroll entry %s for payroll %s", entry.entry_number, payroll_id)
        return str(entry.id)
    except Exception as exc:
        logger.exception("Failed to generate payroll entry for payroll %s", payroll_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_inventory_entry(self, adjustment_id):
    """Generate a journal entry from an inventory adjustment."""
    try:
        from apps.accounting.services.auto_entry import InventoryEntryGenerator

        try:
            from apps.inventory.models import InventoryAdjustment
            adjustment = InventoryAdjustment.objects.get(pk=adjustment_id)
        except (ImportError, LookupError):
            logger.warning("InventoryAdjustment model not available; skipping entry generation.")
            return None

        generator = InventoryEntryGenerator(adjustment)
        entry = generator.generate_entry()
        logger.info("Generated inventory entry %s for adjustment %s", entry.entry_number, adjustment_id)
        return str(entry.id)
    except Exception as exc:
        logger.exception("Failed to generate inventory entry for adjustment %s", adjustment_id)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_recurring_entries(self):
    """
    Process all due recurring journal entries.

    Scheduled via Celery Beat (daily at 00:30). Finds active recurring
    entries with next_run_date <= today, creates entries from templates,
    and advances schedules.
    """
    try:
        from apps.accounting.services.recurring_service import RecurringService

        entries = RecurringService.process_due_entries()
        logger.info("Processed %d recurring entries", len(entries))
        return len(entries)
    except Exception as exc:
        logger.exception("Failed to process recurring entries")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_scheduled_report(self, config_id):
    """
    Generate a financial report from a saved ReportConfig.

    Triggered by Celery Beat or on-demand scheduling. Creates the
    appropriate report generator, runs generation, stores the result,
    and optionally exports to the configured format.
    """
    try:
        from apps.accounting.models import ReportConfig
        from apps.accounting.reports.enums import ReportType
        from apps.accounting.reports.generators import (
            BalanceSheetGenerator,
            CashFlowGenerator,
            GeneralLedgerGenerator,
            ProfitLossGenerator,
            TrialBalanceGenerator,
        )

        config = ReportConfig.objects.get(pk=config_id)

        generator_map = {
            ReportType.TRIAL_BALANCE: TrialBalanceGenerator,
            ReportType.PROFIT_LOSS: ProfitLossGenerator,
            ReportType.BALANCE_SHEET: BalanceSheetGenerator,
            ReportType.CASH_FLOW: CashFlowGenerator,
            ReportType.GENERAL_LEDGER: GeneralLedgerGenerator,
        }

        generator_cls = generator_map.get(config.report_type)
        if not generator_cls:
            logger.error("Unknown report type: %s", config.report_type)
            return None

        generator = generator_cls(config)
        result = generator.generate()

        if not result.is_success:
            logger.error(
                "Report generation failed for config %s: %s",
                config_id,
                result.error_message,
            )
            return None

        logger.info(
            "Generated %s report (config=%s) in %dms",
            config.report_type,
            config_id,
            result.generation_time_ms,
        )

        # Email report if recipients are configured
        recipients = getattr(config, "email_recipients", None)
        if recipients:
            _email_report(config, result, recipients)

        return str(result.pk)

    except ReportConfig.DoesNotExist:
        logger.error("ReportConfig %s not found", config_id)
        return None
    except Exception as exc:
        logger.exception("Failed to generate report for config %s", config_id)
        raise self.retry(exc=exc)


def _email_report(config, result, recipients):
    """Email the generated report to specified recipients."""
    from django.core.mail import EmailMessage

    subject = f"Financial Report: {config.get_report_type_display()}"
    body = (
        f"Your {config.get_report_type_display()} report has been "
        f"generated successfully.\n\n"
        f"Report: {config.name}\n"
        f"Generated in: {result.generation_time_ms}ms\n"
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        to=recipients if isinstance(recipients, list) else [recipients],
    )

    try:
        from apps.accounting.reports.exporters.pdf_exporter import PDFReportExporter

        exporter = PDFReportExporter()
        response = exporter.to_pdf_response(
            result.report_type, result.report_data,
        )
        filename = f"{config.report_type}_report.pdf"
        email.attach(filename, response.content, "application/pdf")
    except Exception:
        logger.warning("Could not attach PDF to email for config %s", config.pk)

    try:
        email.send(fail_silently=True)
        logger.info("Report emailed to %s for config %s", recipients, config.pk)
    except Exception:
        logger.warning("Failed to email report for config %s", config.pk)


# ── Tax Filing Deadline Reminders ──────────────────────────────────


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_tax_filing_deadlines(self):
    """Daily task: check pending tax filings and send reminders.

    Scheduled via Celery Beat to run at 08:00 every day.
    """
    from apps.accounting.services.filing_reminder import FilingReminderService

    logger.info("Starting tax filing deadline check …")
    service = FilingReminderService()
    pending = service.get_pending_filings()

    reminders_sent = 0
    errors = []

    for period in pending:
        try:
            urgency = service.get_urgency_level(period.due_date)
            days = service.get_days_remaining(period.due_date)

            if not service.should_send_reminder(period.due_date):
                continue

            reminder_data = {
                "tax_type": period.tax_type,
                "period": f"{period.year}/{period.period_number:02d}",
                "due_date": str(period.due_date),
                "days_remaining": days,
                "urgency": urgency,
                "period_id": str(period.pk),
            }
            if service.send_reminder_email(reminder_data):
                reminders_sent += 1
        except Exception as exc:
            logger.exception("Error processing period %s", period.pk)
            errors.append(str(exc))

    logger.info("Tax deadline check done — %d reminders sent.", reminders_sent)
    return {
        "reminders_sent": reminders_sent,
        "pending_filings": pending.count(),
        "errors": errors,
    }
