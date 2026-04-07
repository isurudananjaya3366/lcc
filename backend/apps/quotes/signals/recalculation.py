"""
Signals for quote recalculation and history logging.

Task 35: Auto-recalculation on line item changes.
Task 49: History logging on quote save.
"""

import logging
from contextlib import contextmanager

from django.db.models.signals import post_delete, post_save, pre_save

logger = logging.getLogger(__name__)

_recalculating = False


def recalculate_on_line_save(sender, instance, created, **kwargs):
    """Recalculate quote totals when a line item is saved."""
    global _recalculating
    if _recalculating:
        return

    from apps.quotes.constants import EDITABLE_STATES
    from apps.quotes.services.calculation import QuoteCalculationService

    quote = instance.quote
    if quote.status not in EDITABLE_STATES:
        return

    _recalculating = True
    try:
        QuoteCalculationService(quote).calculate_all(save=True)
        _regenerate_pdf_if_exists(quote)
    except Exception:
        logger.exception("Error recalculating quote %s", quote.quote_number)
    finally:
        _recalculating = False


def recalculate_on_line_delete(sender, instance, **kwargs):
    """Recalculate quote totals when a line item is deleted."""
    global _recalculating
    if _recalculating:
        return

    from apps.quotes.constants import EDITABLE_STATES
    from apps.quotes.services.calculation import QuoteCalculationService

    quote = instance.quote
    if quote.status not in EDITABLE_STATES:
        return

    _recalculating = True
    try:
        QuoteCalculationService(quote).calculate_all(save=True)
        _regenerate_pdf_if_exists(quote)
    except Exception:
        logger.exception("Error recalculating quote %s after line delete", quote.quote_number)
    finally:
        _recalculating = False


def _regenerate_pdf_if_exists(quote):
    """Re-generate PDF if the quote already has one (Task 67)."""
    if getattr(quote, "pdf_file", None) and quote.pdf_file.name:
        try:
            from apps.quotes.services.pdf_generator import QuotePDFGenerator
            QuotePDFGenerator(quote).generate_and_save()
            logger.info("Regenerated PDF for quote %s", quote.quote_number)
        except Exception:
            logger.exception("Failed to regenerate PDF for quote %s", quote.quote_number)


# ── Quote History Signals (Task 49) ──────────────────────────────

_TRACKED_FIELDS = ("status", "total", "discount_value", "valid_until")


def capture_quote_pre_save(sender, instance, **kwargs):
    """Capture the pre-save state for change tracking."""
    if instance.pk:
        try:
            instance._pre_save_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._pre_save_instance = None
    else:
        instance._pre_save_instance = None


def log_quote_post_save(sender, instance, created, **kwargs):
    """Log history entries when a quote is created or updated."""
    from apps.quotes.models.history import QuoteHistory

    if created:
        # Creation is logged by QuoteService.create_quote, skip auto-log
        return

    old = getattr(instance, "_pre_save_instance", None)
    if not old:
        return

    old_values = {}
    new_values = {}
    for field in _TRACKED_FIELDS:
        old_val = str(getattr(old, field, None))
        new_val = str(getattr(instance, field, None))
        if old_val != new_val:
            old_values[field] = old_val
            new_values[field] = new_val

    if old_values:
        QuoteHistory.objects.create(
            quote=instance,
            event_type=QuoteHistory.STATUS_CHANGED if "status" in old_values else QuoteHistory.UPDATED,
            old_values=old_values,
            new_values=new_values,
        )


def connect_signals():
    """Connect all quote signals."""
    from apps.quotes.models.line_item import QuoteLineItem
    from apps.quotes.models.quote import Quote

    post_save.connect(recalculate_on_line_save, sender=QuoteLineItem)
    post_delete.connect(recalculate_on_line_delete, sender=QuoteLineItem)
    pre_save.connect(capture_quote_pre_save, sender=Quote)
    post_save.connect(log_quote_post_save, sender=Quote)


@contextmanager
def disable_quote_signals():
    """Temporarily disable recalculation signals (e.g., for bulk ops)."""
    from apps.quotes.models.line_item import QuoteLineItem

    post_save.disconnect(recalculate_on_line_save, sender=QuoteLineItem)
    post_delete.disconnect(recalculate_on_line_delete, sender=QuoteLineItem)
    try:
        yield
    finally:
        post_save.connect(recalculate_on_line_save, sender=QuoteLineItem)
        post_delete.connect(recalculate_on_line_delete, sender=QuoteLineItem)
