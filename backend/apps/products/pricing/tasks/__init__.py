"""
Celery tasks for pricing – schedule activation, cleanup, analytics aggregation.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


# ── Schedule status management ─────────────────────────────────────


@shared_task(name="pricing.update_scheduled_prices")
def update_scheduled_prices():
    """
    Activate/deactivate scheduled prices based on current time.
    Runs every 5 minutes.
    """
    from .models.scheduled_price import ScheduledPrice

    now = timezone.now()
    activated = 0
    deactivated = 0
    errors = 0

    pending_to_activate = ScheduledPrice.objects.filter(
        status=ScheduledPrice.Status.PENDING,
        start_datetime__lte=now,
    )
    active_to_expire = ScheduledPrice.objects.filter(
        status=ScheduledPrice.Status.ACTIVE,
        end_datetime__lte=now,
    )

    for sp in pending_to_activate:
        try:
            if sp.update_status():
                activated += 1
                logger.info("Activated scheduled price: %s (pk=%s)", sp.name, sp.pk)
        except Exception:
            errors += 1
            logger.exception("Error activating scheduled price pk=%s", sp.pk)

    for sp in active_to_expire:
        try:
            if sp.update_status():
                deactivated += 1
                logger.info("Deactivated scheduled price: %s (pk=%s)", sp.name, sp.pk)
        except Exception:
            errors += 1
            logger.exception("Error deactivating scheduled price pk=%s", sp.pk)

    result = {
        "activated": activated,
        "deactivated": deactivated,
        "errors": errors,
        "timestamp": now.isoformat(),
    }
    logger.info("update_scheduled_prices complete: %s", result)
    return result


# ── Cleanup tasks ──────────────────────────────────────────────────


@shared_task(name="pricing.cleanup_expired_schedules")
def cleanup_expired_schedules(days_old=90):
    """Delete expired schedules older than *days_old*. Monday 2 AM."""
    from .models.scheduled_price import ScheduledPrice

    cutoff = timezone.now() - timedelta(days=days_old)
    qs = ScheduledPrice.objects.filter(
        status=ScheduledPrice.Status.EXPIRED,
        end_datetime__lt=cutoff,
    )
    count = qs.count()
    qs.delete()
    logger.info("cleanup_expired_schedules: deleted %d (cutoff=%s)", count, cutoff)
    return count


@shared_task(name="pricing.archive_expired_schedules")
def archive_expired_schedules(days_old=30):
    """Archive then delete expired schedules. Daily 3 AM."""
    from .models.scheduled_price import ScheduledPrice
    from .models.scheduled_price_history import ScheduledPriceHistory

    cutoff = timezone.now() - timedelta(days=days_old)
    expired = ScheduledPrice.objects.filter(
        status=ScheduledPrice.Status.EXPIRED,
        end_datetime__lt=cutoff,
    )
    archived = 0
    for sp in expired:
        ScheduledPriceHistory.objects.create(
            original_id=sp.pk,
            product=sp.product,
            variant=sp.variant,
            name=sp.name,
            description=sp.description,
            sale_price=sp.sale_price,
            start_datetime=sp.start_datetime,
            end_datetime=sp.end_datetime,
            priority=sp.priority,
            created_by=sp.created_by,
        )
        sp.delete()
        archived += 1
    logger.info("archive_expired_schedules: archived %d (cutoff=%s)", archived, cutoff)
    return {"archived": archived, "cutoff_date": cutoff.isoformat()}


@shared_task(name="pricing.cleanup_promotional_prices")
def cleanup_promotional_prices(days_old=60):
    """Delete inactive promotions older than *days_old*. Sunday 3:30 AM."""
    from .models.promotional_price import PromotionalPrice

    cutoff = timezone.now() - timedelta(days=days_old)
    qs = PromotionalPrice.objects.filter(
        is_active=False,
        end_datetime__lt=cutoff,
    )
    count = qs.count()
    qs.delete()
    logger.info("cleanup_promotional_prices: deleted %d (cutoff=%s)", count, cutoff)
    return count


@shared_task(name="pricing.cleanup_flash_sales")
def cleanup_flash_sales(days_old=14):
    """Delete expired flash sales older than *days_old*. Sunday 3:45 AM."""
    from .models.flash_sale import FlashSale
    from .models.scheduled_price import ScheduledPrice

    cutoff = timezone.now() - timedelta(days=days_old)
    # Flash sales whose parent ScheduledPrice is expired
    expired_sp_ids = ScheduledPrice.objects.filter(
        status=ScheduledPrice.Status.EXPIRED,
        end_datetime__lt=cutoff,
        flash_sale_detail__isnull=False,
    ).values_list("pk", flat=True)
    count = FlashSale.objects.filter(scheduled_price_id__in=expired_sp_ids).count()
    FlashSale.objects.filter(scheduled_price_id__in=expired_sp_ids).delete()
    logger.info("cleanup_flash_sales: deleted %d (cutoff=%s)", count, cutoff)
    return count


# ── Analytics aggregation ──────────────────────────────────────────


@shared_task(name="pricing.aggregate_promotion_analytics")
def aggregate_promotion_analytics():
    """Recalculate metrics for all analytics records. Daily 4 AM."""
    from .models.promotion_analytics import PromotionAnalytics

    updated = 0
    for analytics in PromotionAnalytics.objects.all():
        analytics.calculate_metrics()
        analytics.save(update_fields=["conversion_rate", "average_order_value", "last_aggregated_at", "updated_on"])
        updated += 1
    logger.info("aggregate_promotion_analytics: updated %d records", updated)
    return updated
