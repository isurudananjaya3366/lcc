"""
Stock monitoring Celery tasks.

Tasks 35-40: Periodic stock level monitoring, threshold checks,
and alert generation for products across all warehouses.
"""

import logging
import time
import traceback as tb_module

from celery import shared_task
from django.utils import timezone

from apps.inventory.alerts.constants import (
    ALERT_STATUS_ACTIVE,
    ALERT_STATUS_RESOLVED,
    ALERT_TYPE_BACK_IN_STOCK,
    ALERT_TYPE_CRITICAL_STOCK,
    ALERT_TYPE_LOW_STOCK,
    ALERT_TYPE_OUT_OF_STOCK,
)

logger = logging.getLogger(__name__)

MONITORING_BATCH_SIZE = 100


# ── Main Celery Task (Task 35) ──────────────────────────────────


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_stock_monitoring(self, tenant_id=None):
    """
    Main stock monitoring task.

    Runs periodically via Celery Beat to check stock levels
    against thresholds and generate alerts as needed.
    Uses a cache-based lock to prevent concurrent runs.
    """
    from django.core.cache import cache

    from apps.inventory.alerts.models import MonitoringLog

    # Concurrency lock — skip if another run is already active
    lock_key = "stock_monitoring_lock"
    if not cache.add(lock_key, "running", timeout=3600):
        logger.warning("Stock monitoring skipped — another run is in progress")
        return {"skipped": True, "reason": "concurrent_run"}

    # Check monitoring window
    try:
        from apps.inventory.alerts.models import GlobalStockSettings

        settings = GlobalStockSettings.get_settings()
        if not settings.is_within_monitoring_window():
            cache.delete(lock_key)
            logger.info("Stock monitoring skipped — outside monitoring window")
            return {"skipped": True, "reason": "outside_window"}
    except Exception:
        pass  # If settings unavailable, proceed anyway

    log = MonitoringLog.objects.create(status=MonitoringLog.STATUS_RUNNING)
    start_time = time.monotonic()

    try:
        stats = monitor_stock(log)
        elapsed = round(time.monotonic() - start_time, 2)
        stats["execution_time"] = elapsed

        log.mark_completed(stats)

        logger.info(
            "Stock monitoring completed: %d checked, %d created, "
            "%d resolved in %.2fs",
            stats.get("products_checked", 0),
            stats.get("alerts_created", 0),
            stats.get("alerts_resolved", 0),
            elapsed,
        )
        return stats

    except Exception as exc:
        elapsed = round(time.monotonic() - start_time, 2)
        log.mark_failed(str(exc), tb_module.format_exc())
        logger.exception("Stock monitoring failed after %.2fs", elapsed)
        raise self.retry(exc=exc)
    finally:
        cache.delete(lock_key)


# ── Core Monitoring Logic (Task 36) ─────────────────────────────


def monitor_stock(log):
    """
    Monitor stock levels for all eligible products.

    Returns aggregated statistics dict.
    """
    stats = {
        "products_checked": 0,
        "alerts_created": 0,
        "alerts_updated": 0,
        "alerts_resolved": 0,
        "errors": 0,
    }

    for batch in batch_process_products():
        for product in batch:
            try:
                result = generate_alerts_for_product(product)
                stats["products_checked"] += 1
                stats["alerts_created"] += result.get("created", 0)
                stats["alerts_updated"] += result.get("updated", 0)
                stats["alerts_resolved"] += result.get("resolved", 0)
            except Exception:
                stats["errors"] += 1
                logger.exception(
                    "Error monitoring product %s", getattr(product, "name", product)
                )

    return stats


def batch_process_products():
    """
    Yield batches of products eligible for monitoring.

    Respects exclusion settings and monitoring_enabled flags.
    """
    products = filter_monitorable_products()
    total = products.count()

    for offset in range(0, total, MONITORING_BATCH_SIZE):
        yield products[offset : offset + MONITORING_BATCH_SIZE]


def filter_monitorable_products():
    """
    Get products eligible for stock monitoring.

    Excludes products with monitoring disabled or with
    active exclusion settings (Task 46).
    """
    from apps.products.models import Product

    from apps.inventory.alerts.models import ProductStockConfig

    products = Product.objects.filter(
        is_active=True,
    )

    # Exclude products with monitoring disabled
    disabled_ids = ProductStockConfig.objects.filter(
        monitoring_enabled=False,
    ).values_list("product_id", flat=True)
    products = products.exclude(id__in=disabled_ids)

    # Exclude products with active exclusion (Task 46)
    today = timezone.now().date()
    excluded_ids = ProductStockConfig.objects.filter(
        exclude_from_monitoring=True,
    ).exclude(
        # Not yet started
        exclusion_start_date__gt=today,
    ).exclude(
        # Already ended
        exclusion_end_date__lt=today,
    ).values_list("product_id", flat=True)

    products = products.exclude(id__in=excluded_ids)

    return products.order_by("id")


# ── Alert Generation Orchestration (Task 40) ────────────────────


def generate_alerts_for_product(product):
    """
    Generate appropriate alerts for a product.

    Checks all thresholds across stock levels and creates,
    updates, or resolves alerts as needed.
    """
    from apps.inventory.alerts.services.config_resolver import ConfigResolver
    from apps.inventory.stock.models.stock_level import StockLevel

    stats = {"created": 0, "updated": 0, "resolved": 0}

    config = ConfigResolver.resolve_for_product(product)

    stock_levels = StockLevel.objects.filter(product=product)

    if not stock_levels.exists():
        return stats

    for stock_level in stock_levels:
        result = process_stock_level(product, stock_level, config)
        stats["created"] += result.get("created", 0)
        stats["updated"] += result.get("updated", 0)
        stats["resolved"] += result.get("resolved", 0)

    return stats


def process_stock_level(product, stock_level, config):
    """
    Process a single stock level and generate/resolve alerts.

    Priority order: OOS > Critical > Low > Resolve.
    """
    result = {"created": 0, "updated": 0, "resolved": 0}

    oos_check = check_out_of_stock(product, stock_level)
    critical_check = check_critical_stock(product, stock_level, config)
    low_check = check_low_stock(product, stock_level, config)

    alert_type = determine_alert_type(oos_check, critical_check, low_check)

    if alert_type:
        alert, created = create_alert_for_type(
            alert_type, product, stock_level, config
        )
        if alert:
            if created:
                result["created"] = 1
            else:
                result["updated"] = 1

            # Detect back-in-stock
            if not oos_check["is_out_of_stock"]:
                if detect_back_in_stock(product, stock_level):
                    result["created"] += 1
    else:
        # No alert needed — resolve existing alerts and check back-in-stock
        resolved = auto_resolve_alerts(product, stock_level)
        result["resolved"] = resolved

        if detect_back_in_stock(product, stock_level):
            result["created"] += 1

    return result


def determine_alert_type(oos_check, critical_check, low_check):
    """Determine highest-priority alert type based on threshold checks."""
    if oos_check["is_out_of_stock"]:
        return ALERT_TYPE_OUT_OF_STOCK
    elif critical_check["is_critical"]:
        return ALERT_TYPE_CRITICAL_STOCK
    elif low_check["is_low"]:
        return ALERT_TYPE_LOW_STOCK
    return None


# ── Low Stock Check (Task 37) ───────────────────────────────────


def check_low_stock(product, stock_level, config):
    """
    Check if product is below low stock threshold.

    Returns dict with check results including severity calculation.
    """
    threshold = config.get("low_stock_threshold", 10)
    current_stock = getattr(stock_level, "available_quantity", 0) or 0
    is_low = current_stock <= threshold and current_stock > 0

    # Severity calculation: how far below threshold (0.0 = at threshold, 1.0 = at zero)
    severity = 0.0
    severity_level = "none"
    if is_low and threshold > 0:
        severity = round(float(1 - (float(current_stock) / float(threshold))), 4)
        if severity >= 0.75:
            severity_level = "critical"
        elif severity >= 0.50:
            severity_level = "high"
        elif severity >= 0.25:
            severity_level = "medium"
        else:
            severity_level = "low"

    return {
        "is_low": is_low,
        "current_stock": current_stock,
        "threshold": threshold,
        "severity": severity,
        "severity_level": severity_level,
    }


# ── Critical Stock Check (Task 38) ──────────────────────────────


def check_critical_stock(product, stock_level, config):
    """
    Check if product is at critical stock level.

    Critical = low_stock_threshold × critical_threshold_multiplier (default 0.5).
    Also checks if an existing LOW_STOCK alert should be escalated.
    """
    low_threshold = config.get("low_stock_threshold", 10)
    multiplier = float(config.get("critical_threshold_multiplier", 0.5))
    critical_threshold = int(low_threshold * multiplier)

    current_stock = getattr(stock_level, "available_quantity", 0) or 0
    is_critical = current_stock <= critical_threshold and current_stock > 0

    # Check if escalation from LOW_STOCK is needed
    needs_escalation = False
    if is_critical:
        needs_escalation = _check_escalation_needed(product, stock_level)

    return {
        "is_critical": is_critical,
        "current_stock": current_stock,
        "critical_threshold": critical_threshold,
        "needs_escalation": needs_escalation,
    }


def _check_escalation_needed(product, stock_level):
    """Check if an existing LOW_STOCK alert should be escalated to CRITICAL."""
    from apps.inventory.alerts.models import StockAlert

    warehouse = getattr(stock_level, "warehouse", None)
    return StockAlert.objects.filter(
        product=product,
        warehouse=warehouse,
        alert_type=ALERT_TYPE_LOW_STOCK,
        status=ALERT_STATUS_ACTIVE,
    ).exists()


# ── Out of Stock Check (Task 39) ────────────────────────────────


def check_out_of_stock(product, stock_level):
    """
    Check if product is out of stock.

    OOS = available_quantity <= 0.
    """
    available = getattr(stock_level, "available_quantity", 0) or 0
    is_oos = available <= 0

    return {
        "is_out_of_stock": is_oos,
        "available_quantity": available,
    }


# ── Alert Creation Helpers ──────────────────────────────────────


def create_alert_for_type(alert_type, product, stock_level, config):
    """Create or update an alert of the specified type."""
    if alert_type == ALERT_TYPE_OUT_OF_STOCK:
        return create_out_of_stock_alert(product, stock_level, config)
    elif alert_type == ALERT_TYPE_CRITICAL_STOCK:
        return create_critical_stock_alert(product, stock_level, config)
    elif alert_type == ALERT_TYPE_LOW_STOCK:
        return create_low_stock_alert(product, stock_level, config)
    return None, False


def create_low_stock_alert(product, stock_level, config):
    """Create or update a LOW_STOCK alert."""
    from apps.inventory.alerts.models import StockAlert
    from apps.inventory.alerts.services.notification import AlertNotificationService

    threshold = config.get("low_stock_threshold", 10)
    warehouse = getattr(stock_level, "warehouse", None)

    if is_alert_throttled(product, warehouse, ALERT_TYPE_LOW_STOCK):
        return None, False

    alert, created = StockAlert.create_or_update(
        product=product,
        alert_type=ALERT_TYPE_LOW_STOCK,
        warehouse=warehouse,
        current_stock=getattr(stock_level, "available_quantity", 0) or 0,
        threshold_value=threshold,
        threshold_type="low_stock_threshold",
        threshold_source=config.get("source", "global"),
        priority=2,
    )

    if created:
        AlertNotificationService.send_alert_notification(alert)
        logger.info("Created LOW_STOCK alert for %s", product.name)

    return alert, created


def create_critical_stock_alert(product, stock_level, config):
    """Create or update a CRITICAL_STOCK alert."""
    from apps.inventory.alerts.models import StockAlert
    from apps.inventory.alerts.services.notification import AlertNotificationService

    low_threshold = config.get("low_stock_threshold", 10)
    multiplier = float(config.get("critical_threshold_multiplier", 0.5))
    threshold = int(low_threshold * multiplier)
    warehouse = getattr(stock_level, "warehouse", None)

    if is_alert_throttled(product, warehouse, ALERT_TYPE_CRITICAL_STOCK):
        return None, False

    # Resolve any existing LOW_STOCK alerts (escalation)
    StockAlert.objects.filter(
        product=product,
        warehouse=warehouse,
        alert_type=ALERT_TYPE_LOW_STOCK,
        status=ALERT_STATUS_ACTIVE,
    ).update(status=ALERT_STATUS_RESOLVED, resolved_at=timezone.now())

    alert, created = StockAlert.create_or_update(
        product=product,
        alert_type=ALERT_TYPE_CRITICAL_STOCK,
        warehouse=warehouse,
        current_stock=getattr(stock_level, "available_quantity", 0) or 0,
        threshold_value=threshold,
        threshold_type="critical_threshold",
        threshold_source=config.get("source", "global"),
        priority=3,
    )

    if created:
        AlertNotificationService.send_alert_notification(alert)
        logger.warning("Created CRITICAL_STOCK alert for %s", product.name)

    return alert, created


def create_out_of_stock_alert(product, stock_level, config):
    """Create or update an OUT_OF_STOCK alert."""
    from apps.inventory.alerts.models import StockAlert
    from apps.inventory.alerts.services.notification import AlertNotificationService

    warehouse = getattr(stock_level, "warehouse", None)

    if is_alert_throttled(product, warehouse, ALERT_TYPE_OUT_OF_STOCK):
        if not should_bypass_throttle(
            product, warehouse, ALERT_TYPE_OUT_OF_STOCK,
            getattr(stock_level, "available_quantity", 0) or 0,
        ):
            return None, False

    # Resolve existing lower-priority alerts
    StockAlert.objects.filter(
        product=product,
        warehouse=warehouse,
        alert_type__in=[ALERT_TYPE_LOW_STOCK, ALERT_TYPE_CRITICAL_STOCK],
        status=ALERT_STATUS_ACTIVE,
    ).update(status=ALERT_STATUS_RESOLVED, resolved_at=timezone.now())

    alert, created = StockAlert.create_or_update(
        product=product,
        alert_type=ALERT_TYPE_OUT_OF_STOCK,
        warehouse=warehouse,
        current_stock=getattr(stock_level, "available_quantity", 0) or 0,
        threshold_value=0,
        threshold_type="out_of_stock",
        threshold_source="system",
        priority=4,
    )

    if created:
        AlertNotificationService.send_alert_notification(alert)

        # Hide from webstore if configured
        try:
            from apps.inventory.alerts.models import ProductStockConfig

            psc = ProductStockConfig.objects.for_product(
                product, warehouse=warehouse
            )
            if psc and psc.auto_hide_when_oos:
                logger.info("Would hide %s from webstore (OOS)", product.name)
        except Exception:
            pass

        logger.critical("Product %s is OUT OF STOCK", product.name)

    return alert, created


# ── Alert Resolution (Task 41) ──────────────────────────────────


def auto_resolve_alerts(product, stock_level):
    """
    Auto-resolve alerts when stock levels improve above thresholds.

    Returns count of resolved alerts.
    """
    from apps.inventory.alerts.models import StockAlert

    warehouse = getattr(stock_level, "warehouse", None)
    active_alerts = StockAlert.objects.get_active().filter(
        product=product,
        warehouse=warehouse,
    )

    resolved_count = 0

    for alert in active_alerts:
        if should_resolve_alert(alert, stock_level):
            alert.resolve(auto=True)
            resolved_count += 1
            logger.info(
                "Auto-resolved %s alert for %s",
                alert.get_alert_type_display(),
                product.name,
            )

    return resolved_count


def should_resolve_alert(alert, stock_level):
    """Determine if an alert should be auto-resolved."""
    current_stock = getattr(stock_level, "available_quantity", 0) or 0

    resolution_criteria = {
        ALERT_TYPE_OUT_OF_STOCK: current_stock > 0,
        ALERT_TYPE_CRITICAL_STOCK: current_stock > (alert.threshold_value or 0),
        ALERT_TYPE_LOW_STOCK: current_stock > (alert.threshold_value or 0),
    }

    return resolution_criteria.get(alert.alert_type, False)


# ── Back in Stock Detection (Task 42) ───────────────────────────


def detect_back_in_stock(product, stock_level):
    """
    Detect when an out-of-stock product is restocked.

    Creates a BACK_IN_STOCK alert if the product was recently OOS.
    """
    from datetime import timedelta

    from apps.inventory.alerts.models import StockAlert
    from apps.inventory.alerts.services.notification import AlertNotificationService

    warehouse = getattr(stock_level, "warehouse", None)
    available = getattr(stock_level, "available_quantity", 0) or 0

    if available <= 0:
        return False

    recent_cutoff = timezone.now() - timedelta(days=7)

    was_oos = StockAlert.objects.filter(
        product=product,
        warehouse=warehouse,
        alert_type=ALERT_TYPE_OUT_OF_STOCK,
        created_at__gte=recent_cutoff,
    ).exists()

    if not was_oos:
        return False

    # Prevent duplicate back-in-stock alerts
    already_notified = StockAlert.objects.filter(
        product=product,
        warehouse=warehouse,
        alert_type=ALERT_TYPE_BACK_IN_STOCK,
        created_at__gte=recent_cutoff,
    ).exists()

    if already_notified:
        return False

    alert = StockAlert.objects.create(
        product=product,
        warehouse=warehouse,
        alert_type=ALERT_TYPE_BACK_IN_STOCK,
        status=ALERT_STATUS_ACTIVE,
        current_stock=available,
        priority=1,
        message=f"{product.name} is back in stock ({available} units)",
    )

    AlertNotificationService.send_alert_notification(alert)

    # Restore webstore visibility if configured (Task 42)
    _show_back_on_webstore(product, warehouse)

    # Notify waiting customers (Task 42)
    _notify_waiting_customers(product, warehouse, available)

    logger.info("Created BACK_IN_STOCK alert for %s", product.name)

    return True


def _show_back_on_webstore(product, warehouse):
    """Restore product webstore visibility after back-in-stock event."""
    try:
        from apps.inventory.alerts.models import ProductStockConfig

        psc = ProductStockConfig.objects.for_product(product, warehouse=warehouse)
        if psc and getattr(psc, "auto_show_when_restocked", False):
            logger.info(
                "Would show %s on webstore (back in stock)", product.name
            )
            # Webstore visibility integration point
    except Exception:
        logger.debug("Webstore visibility update skipped for %s", product.name)


def _notify_waiting_customers(product, warehouse, available_qty):
    """Notify customers on the waitlist that a product is back in stock."""
    try:
        # Backorder/waitlist notification integration point
        logger.debug(
            "Would notify waiting customers for %s (%d units available)",
            product.name,
            available_qty,
        )
    except Exception:
        logger.debug("Waiting customer notification skipped for %s", product.name)


# ── Throttling (Task 48) ────────────────────────────────────────


def is_alert_throttled(product, warehouse, alert_type):
    """Check if alert creation is throttled for this product/type."""
    from datetime import timedelta

    from apps.inventory.alerts.models import GlobalStockSettings, StockAlert

    try:
        settings = GlobalStockSettings.get_settings()
    except Exception:
        return False

    throttle_hours = _get_throttle_period(settings, alert_type)
    window_start = timezone.now() - timedelta(hours=throttle_hours)

    recent_count = StockAlert.objects.filter(
        product=product,
        warehouse=warehouse,
        alert_type=alert_type,
        created_at__gte=window_start,
    ).count()

    if recent_count > 0:
        logger.debug(
            "Alert throttled: %s (%s) - %d in last %d hours",
            product.name,
            alert_type,
            recent_count,
            throttle_hours,
        )
        return True

    return False


def should_bypass_throttle(product, warehouse, alert_type, current_stock):
    """Check if throttle should be bypassed due to significant stock drop."""
    from apps.inventory.alerts.models import GlobalStockSettings, StockAlert

    try:
        settings = GlobalStockSettings.get_settings()
    except Exception:
        return False

    last_alert = (
        StockAlert.objects.filter(
            product=product,
            warehouse=warehouse,
            alert_type=alert_type,
        )
        .order_by("-created_at")
        .first()
    )

    if not last_alert or not last_alert.current_stock:
        return False

    if last_alert.current_stock > 0:
        drop_percent = (
            (last_alert.current_stock - current_stock)
            / last_alert.current_stock
            * 100
        )
        bypass_threshold = float(
            getattr(settings, "throttle_bypass_threshold", 50)
        )

        if drop_percent >= bypass_threshold:
            logger.warning(
                "Throttle bypassed: %s - Stock dropped %.1f%%",
                product.name,
                drop_percent,
            )
            return True

    return False


def _get_throttle_period(settings, alert_type):
    """Get the throttle period in hours for an alert type."""
    throttle_map = {
        ALERT_TYPE_LOW_STOCK: getattr(
            settings, "throttle_low_stock_hours", 24
        ),
        ALERT_TYPE_CRITICAL_STOCK: getattr(
            settings, "throttle_critical_stock_hours", 12
        ),
        ALERT_TYPE_OUT_OF_STOCK: getattr(
            settings, "throttle_oos_hours", 6
        ),
        ALERT_TYPE_BACK_IN_STOCK: 24,
    }
    return throttle_map.get(alert_type, 24)


# ── Warehouse-Specific Monitoring (Task 47) ─────────────────────


def monitor_warehouse_stock(product):
    """
    Monitor stock levels per warehouse for a product.

    Creates warehouse-specific alerts and detects transfer opportunities.
    """
    from apps.inventory.alerts.services.config_resolver import ConfigResolver
    from apps.inventory.stock.models.stock_level import StockLevel

    config = ConfigResolver.resolve_for_product(product)
    stock_levels = StockLevel.objects.filter(product=product)

    alerts_created = []
    out_of_stock_count = 0
    total_warehouses = stock_levels.count()

    for stock_level in stock_levels:
        available = getattr(stock_level, "available_quantity", 0) or 0

        if available <= 0:
            out_of_stock_count += 1

        result = process_stock_level(product, stock_level, config)
        if result.get("created", 0) > 0:
            alerts_created.append(result)

    # Company-wide OOS alert if out in all warehouses
    if total_warehouses > 0 and out_of_stock_count == total_warehouses:
        _create_company_wide_oos_alert(product, total_warehouses)

    # Check transfer opportunities between warehouses
    _check_transfer_opportunities(product, stock_levels, config)

    return alerts_created


def _create_company_wide_oos_alert(product, total_warehouses):
    """Create a company-wide OOS alert when product is out in all warehouses."""
    from apps.inventory.alerts.models import StockAlert
    from apps.inventory.alerts.services.notification import AlertNotificationService

    alert, created = StockAlert.create_or_update(
        product=product,
        alert_type=ALERT_TYPE_OUT_OF_STOCK,
        warehouse=None,  # Company-wide (no specific warehouse)
        current_stock=0,
        threshold_value=0,
        threshold_type="company_wide_oos",
        threshold_source="system",
        priority=5,  # Highest urgency
    )

    if created:
        alert.message = (
            f"{product.name} is OUT OF STOCK in ALL {total_warehouses} warehouses"
        )
        alert.save(update_fields=["message"])
        AlertNotificationService.send_alert_notification(alert)
        logger.critical(
            "Company-wide OOS alert for %s (%d warehouses)",
            product.name,
            total_warehouses,
        )


def _check_transfer_opportunities(product, stock_levels, config):
    """Check if stock can be transferred between warehouses to alleviate shortages."""
    threshold = config.get("low_stock_threshold", 10)
    low_warehouses = []
    surplus_warehouses = []

    for sl in stock_levels:
        available = getattr(sl, "available_quantity", 0) or 0
        wh = getattr(sl, "warehouse", None)
        if available <= threshold:
            low_warehouses.append({"warehouse": wh, "stock": available})
        elif available > threshold * 2:
            surplus_warehouses.append({"warehouse": wh, "stock": available})

    if low_warehouses and surplus_warehouses:
        for low_wh in low_warehouses:
            logger.info(
                "Transfer opportunity: %s low in %s (%d), surplus in %s",
                product.name,
                getattr(low_wh["warehouse"], "name", "Unknown"),
                low_wh["stock"],
                ", ".join(
                    getattr(s["warehouse"], "name", "Unknown")
                    for s in surplus_warehouses
                ),
            )
