"""
Django signals for auto-generating journal entries.

Listens for post_save signals on source document models and
dispatches Celery tasks to generate corresponding journal entries.
Source models that don't exist yet are safely skipped.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _should_generate_entry(instance):
    """Check if a journal entry should be generated for this instance."""
    status = getattr(instance, "status", None)
    return status in ("posted", "approved", "confirmed", "POSTED", "APPROVED", "CONFIRMED")


def _register_signal(model_path, task_func):
    """
    Safely register a post_save signal for a model that may not exist.

    Args:
        model_path: Dotted path like 'apps.sales.models.SalesInvoice'.
        task_func: Celery task function to dispatch.
    """
    try:
        from django.apps import apps
        parts = model_path.rsplit(".", 1)
        module_path = parts[0]
        model_name = parts[1]
        app_label = module_path.split(".")[1]
        model = apps.get_model(app_label, model_name)

        @receiver(post_save, sender=model, weak=False)
        def handler(sender, instance, created, **kwargs):
            if _should_generate_entry(instance):
                task_func.delay(str(instance.pk))

        logger.debug("Registered auto-entry signal for %s", model_path)
    except (LookupError, ImportError, ValueError):
        logger.debug("Model %s not available; signal not registered.", model_path)


def register_auto_entry_signals():
    """
    Register all auto-entry signals.

    Called from accounting app's ready() method. Safely handles
    models that don't exist yet.
    """
    from apps.accounting.tasks import (
        generate_inventory_entry,
        generate_payment_entry,
        generate_payroll_entry,
        generate_purchase_entry,
        generate_sales_entry,
    )

    signal_map = {
        "apps.sales.models.SalesInvoice": generate_sales_entry,
        "apps.purchases.models.PurchaseBill": generate_purchase_entry,
        "apps.payments.models.Payment": generate_payment_entry,
        "apps.hr.models.PayrollRun": generate_payroll_entry,
        "apps.inventory.models.InventoryAdjustment": generate_inventory_entry,
    }

    for model_path, task_func in signal_map.items():
        _register_signal(model_path, task_func)
