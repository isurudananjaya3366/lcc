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
