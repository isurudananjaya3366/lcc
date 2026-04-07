"""
Celery tasks for reorder suggestion generation and auto-reorder processing.
"""

import logging
from decimal import Decimal

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


# ── Generate Suggestions ────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def generate_reorder_suggestions(self):
    """
    Generate reorder suggestions for all eligible products.

    Runs daily (Celery Beat) — checks every product that tracks inventory,
    creates or updates ReorderSuggestion records.
    """
    from apps.inventory.alerts.models import GlobalStockSettings

    logger.info("Starting reorder suggestion generation")
    start = timezone.now()

    settings = GlobalStockSettings.get_settings()
    if not getattr(settings, "reorder_suggestions_enabled", True):
        logger.info("Reorder suggestions disabled")
        return {"status": "disabled"}

    products = _filter_products_needing_reorder()
    logger.info("Checking %d products for reorder", len(products))

    created = updated = errors = 0
    batch_size = 50

    for i in range(0, len(products), batch_size):
        batch = products[i : i + batch_size]
        for product in batch:
            try:
                result = _process_product_reorder(product)
                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
            except Exception as exc:
                logger.error("Error processing %s: %s", product, exc)
                errors += 1

        logger.info("Processed %d/%d products", min(i + batch_size, len(products)), len(products))

    elapsed = (timezone.now() - start).total_seconds()
    result = {
        "status": "completed",
        "products_checked": len(products),
        "suggestions_created": created,
        "suggestions_updated": updated,
        "errors": errors,
        "execution_time": elapsed,
    }
    logger.info(
        "Reorder suggestions complete: %d created, %d updated, %d errors in %.2fs",
        created, updated, errors, elapsed,
    )
    return result


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def mark_expired_suggestions(self, expiry_days=30):
    """Mark old pending suggestions as expired."""
    from apps.inventory.alerts.models import ReorderSuggestion

    count = ReorderSuggestion.objects.mark_expired_suggestions(expiry_days)
    logger.info("Marked %d suggestions as expired", count)
    return {"expired": count}


# ── Auto-Reorder ────────────────────────────────────────────────

@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def process_auto_reorders(self):
    """
    Convert eligible pending suggestions into purchase orders.

    Only runs when auto_reorder_enabled is True in GlobalStockSettings.
    """
    from apps.inventory.alerts.models import GlobalStockSettings, ReorderSuggestion

    settings = GlobalStockSettings.get_settings()
    if not getattr(settings, "auto_reorder_enabled", False):
        logger.info("Auto-reorder disabled")
        return {"status": "disabled"}

    eligible = _get_eligible_auto_reorder(settings)
    logger.info("Found %d eligible suggestions for auto-reorder", len(eligible))

    pos_created = errors = 0
    total_value = Decimal("0")

    for suggestion in eligible:
        try:
            if not _validate_auto_reorder(suggestion, settings):
                continue
            po_id = _create_auto_reorder_po(suggestion, settings)
            if po_id:
                pos_created += 1
                total_value += suggestion.estimated_cost or Decimal("0")
        except Exception as exc:
            logger.error("Auto-reorder error for suggestion %s: %s", suggestion.id, exc)
            errors += 1

    result = {
        "status": "completed",
        "pos_created": pos_created,
        "total_value_lkr": float(total_value),
        "errors": errors,
    }
    logger.info("Auto-reorder complete: %d POs, LKR %s", pos_created, total_value)
    return result


# ── Weekly Report ───────────────────────────────────────────────

@shared_task
def send_weekly_reorder_report():
    """Generate and log weekly reorder report (email integration is config-dependent)."""
    from apps.inventory.alerts.services.reports import ReorderReportService

    report = ReorderReportService.generate_reorder_report()
    summary = report["summary"]
    logger.info(
        "Weekly reorder report: %d suggestions, LKR %s total cost",
        summary["total_suggestions"],
        summary["total_estimated_cost"],
    )
    return {"status": "sent", "total_suggestions": summary["total_suggestions"]}


# ── Internal Helpers ────────────────────────────────────────────

def _filter_products_needing_reorder():
    """Return active products eligible for reorder checking."""
    from apps.inventory.alerts.models import ProductStockConfig

    try:
        from apps.products.models import Product
    except ImportError:
        return []

    products = Product.objects.filter(
        is_active=True,
    ).select_related("category").prefetch_related("stock_levels")

    excluded_ids = ProductStockConfig.objects.filter(
        exclude_from_monitoring=True,
    ).values_list("product_id", flat=True)

    return list(products.exclude(id__in=excluded_ids))


def _process_product_reorder(product):
    """Process single product – returns 'created', 'updated', or 'none'."""
    from apps.inventory.alerts.models import ReorderSuggestion
    from apps.inventory.alerts.services.reorder_calculator import ReorderCalculator

    data = ReorderCalculator.calculate_reorder_suggestion(product)
    if not data:
        return "none"

    existing = ReorderSuggestion.objects.filter(
        product=product, status="pending",
    ).first()

    if existing:
        _update_suggestion(existing, data)
        return "updated"

    _create_suggestion(data)
    return "created"


def _create_suggestion(data):
    from apps.inventory.alerts.models import ReorderSuggestion

    ReorderSuggestion.objects.create(
        product=data["product"],
        warehouse=data.get("warehouse"),
        suggested_qty=data["suggested_qty"],
        minimum_order_qty=data.get("minimum_order_qty", Decimal("1")),
        current_stock=data["current_stock"],
        suggested_supplier=data.get("suggested_supplier"),
        urgency=data["urgency"],
        days_until_stockout=data.get("days_until_stockout"),
        daily_velocity=data.get("daily_velocity"),
        safety_stock=data.get("safety_stock"),
        eoq=data.get("calculation_details", {}).get("eoq"),
        reorder_point=data.get("reorder_point"),
        estimated_cost=data.get("estimated_cost"),
        unit_cost=data.get("unit_cost"),
        calculation_details=data.get("calculation_details", {}),
        auto_generated=True,
    )


def _update_suggestion(existing, data):
    existing.suggested_qty = data["suggested_qty"]
    existing.current_stock = data["current_stock"]
    existing.urgency = data["urgency"]
    existing.days_until_stockout = data.get("days_until_stockout")
    existing.daily_velocity = data.get("daily_velocity")
    existing.safety_stock = data.get("safety_stock")
    existing.reorder_point = data.get("reorder_point")
    existing.estimated_cost = data.get("estimated_cost")
    existing.calculation_details = data.get("calculation_details", {})
    existing.save()


def _get_eligible_auto_reorder(settings):
    from apps.inventory.alerts.models import ProductStockConfig, ReorderSuggestion

    urgency_levels = {
        "critical": ["critical"],
        "high": ["critical", "high"],
        "medium": ["critical", "high", "medium"],
    }
    min_urgency = getattr(settings, "auto_reorder_min_urgency", "high")
    allowed = urgency_levels.get(min_urgency, ["critical"])

    suggestions = (
        ReorderSuggestion.objects.filter(status="pending", urgency__in=allowed)
        .select_related("product", "suggested_supplier")
        .filter(suggested_supplier__isnull=False)
    )

    allowed_product_ids = ProductStockConfig.objects.filter(
        allow_auto_reorder=True,
    ).values_list("product_id", flat=True)

    return list(suggestions.filter(product_id__in=allowed_product_ids))


def _validate_auto_reorder(suggestion, settings):
    max_val = getattr(settings, "auto_reorder_max_value_lkr", Decimal("100000.00"))
    if suggestion.estimated_cost and suggestion.estimated_cost > max_val:
        logger.warning("Suggestion %s exceeds max value", suggestion.id)
        return False
    if not getattr(suggestion.suggested_supplier, "is_active", True):
        logger.warning("Supplier inactive for suggestion %s", suggestion.id)
        return False
    if not getattr(suggestion.product, "is_active", True):
        logger.warning("Product inactive for suggestion %s", suggestion.id)
        return False
    return True


def _create_auto_reorder_po(suggestion, settings):
    """
    Create a draft PO from the suggestion.

    Returns created PO's ID or None if purchasing module unavailable.
    """
    try:
        from apps.purchasing.models import PurchaseOrder, PurchaseOrderItem
    except ImportError:
        logger.warning("Purchasing module not available – skipping auto PO")
        return None

    require_approval = getattr(settings, "auto_reorder_require_approval", True)
    initial_status = "draft" if require_approval else "approved"

    po = PurchaseOrder.objects.create(
        supplier=suggestion.suggested_supplier,
        destination_warehouse=suggestion.warehouse,
        status=initial_status,
        notes=(
            f"AUTO-GENERATED from reorder suggestion {suggestion.id}\n"
            f"Urgency: {suggestion.urgency.upper()}\n"
            f"Days until stockout: {suggestion.days_until_stockout}"
        ),
    )

    PurchaseOrderItem.objects.create(
        purchase_order=po,
        product=suggestion.product,
        variant=suggestion.variant,
        quantity=suggestion.suggested_qty,
        unit_price=suggestion.unit_cost or getattr(suggestion.product, "cost_price", Decimal("0")),
    )

    suggestion.mark_converted(po.id)
    logger.info("Created auto-reorder PO %s for %s", po.id, suggestion.product)
    return po.id
