"""Dashboard signals — cache invalidation on model changes."""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.dashboard.services.cache_service import invalidate_kpi_cache

logger = logging.getLogger(__name__)


def _invalidate_sales_cache(sender, instance, **kwargs):
    """Invalidate sales KPI cache when orders change."""
    invalidate_kpi_cache("dashboard:sales")
    invalidate_kpi_cache("dashboard:all")
    logger.debug("Sales KPI cache invalidated due to %s change", sender.__name__)


def _invalidate_inventory_cache(sender, instance, **kwargs):
    """Invalidate inventory KPI cache when stock changes."""
    invalidate_kpi_cache("dashboard:inventory")
    invalidate_kpi_cache("dashboard:all")
    logger.debug("Inventory KPI cache invalidated due to %s change", sender.__name__)


def _invalidate_financial_cache(sender, instance, **kwargs):
    """Invalidate financial KPI cache when journal entries change."""
    invalidate_kpi_cache("dashboard:financial")
    invalidate_kpi_cache("dashboard:all")
    logger.debug("Financial KPI cache invalidated due to %s change", sender.__name__)


def _invalidate_hr_cache(sender, instance, **kwargs):
    """Invalidate HR KPI cache when employee data changes."""
    invalidate_kpi_cache("dashboard:hr")
    invalidate_kpi_cache("dashboard:all")
    logger.debug("HR KPI cache invalidated due to %s change", sender.__name__)


def register_cache_invalidation_signals():
    """Register cache invalidation signal handlers.

    Called from DashboardConfig.ready() to connect signals lazily,
    avoiding import-time side effects.
    """
    try:
        from apps.orders.models import Order, OrderItem

        post_save.connect(_invalidate_sales_cache, sender=Order)
        post_delete.connect(_invalidate_sales_cache, sender=Order)
        post_save.connect(_invalidate_sales_cache, sender=OrderItem)
        post_delete.connect(_invalidate_sales_cache, sender=OrderItem)
    except ImportError:
        logger.debug("Order models not available for signal registration")

    try:
        from apps.inventory.models import Product, StockMovement

        post_save.connect(_invalidate_inventory_cache, sender=StockMovement)
        post_delete.connect(_invalidate_inventory_cache, sender=StockMovement)
        post_save.connect(_invalidate_inventory_cache, sender=Product)
    except ImportError:
        logger.debug("Inventory models not available for signal registration")

    try:
        from apps.accounting.models import JournalEntry, JournalEntryLine

        post_save.connect(_invalidate_financial_cache, sender=JournalEntry)
        post_delete.connect(_invalidate_financial_cache, sender=JournalEntry)
        post_save.connect(_invalidate_financial_cache, sender=JournalEntryLine)
        post_delete.connect(_invalidate_financial_cache, sender=JournalEntryLine)
    except ImportError:
        logger.debug("Accounting models not available for signal registration")

    try:
        from apps.employees.models import Employee

        post_save.connect(_invalidate_hr_cache, sender=Employee)
        post_delete.connect(_invalidate_hr_cache, sender=Employee)
    except ImportError:
        logger.debug("Employee models not available for signal registration")
