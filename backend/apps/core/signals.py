"""
Core model signals for tenant-schema models.

Provides auto-creation signals that fire when related records are
created. These ensure that dependent objects (like TenantSettings
and Stock entries) are automatically set up when their parent record
is created.

Signals:
    auto_create_tenant_settings:
        Creates a TenantSettings record when a new Tenant is created.
        Ensures every tenant has default configuration from day one.
        Trigger: post_save on Tenant (created=True).

    auto_create_stock_for_product:
        Creates a Stock entry (quantity=0) for a newly created Product
        at every active StockLocation in the tenant schema.
        Trigger: post_save on Product (created=True).

    auto_create_stock_for_location:
        Creates a Stock entry (quantity=0) at a newly created
        StockLocation for every existing Product in the tenant schema.
        Trigger: post_save on StockLocation (created=True).

Usage:
    Signals are connected in the CoreConfig.ready() method via
    connect_signals(). No manual registration is needed — simply
    import this module from CoreConfig.ready().
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def connect_signals():
    """
    Connect all model signals.

    Called from CoreConfig.ready() to ensure signals are registered
    after all apps and models are loaded. Each signal block is wrapped
    in a try/except ImportError so that missing models (during initial
    migrations or test runs) do not prevent startup.
    """

    # ── Signal 1: Auto-create TenantSettings on new Tenant ───────────
    try:
        from apps.tenants.models import Tenant, TenantSettings  # noqa: F401

        @receiver(post_save, sender=Tenant)
        def auto_create_tenant_settings(sender, instance, created, **kwargs):
            """
            Auto-create TenantSettings when a new Tenant is created.

            Uses get_or_create to be idempotent — safe if called multiple
            times or if the settings record was already created elsewhere.
            """
            if created:
                _, settings_created = TenantSettings.objects.get_or_create(
                    tenant=instance,
                )
                if settings_created:
                    logger.info(
                        "Auto-created TenantSettings for tenant: %s",
                        instance.name,
                    )

    except ImportError:
        logger.debug(
            "TenantSettings model not available — "
            "skipping auto_create_tenant_settings signal."
        )

    # ── Signal 2: Auto-create Stock entries for a new Product ─────────
    try:
        from apps.inventory.models import Stock, StockLocation  # noqa: F401
        from apps.products.models import Product  # noqa: F401

        @receiver(post_save, sender=Product)
        def auto_create_stock_for_product(sender, instance, created, **kwargs):
            """
            Auto-create Stock entries for a new Product at all StockLocations.

            Fires when a Product is first created (created=True). Creates a
            Stock record with quantity=0 for every StockLocation so that stock
            levels can be tracked from day one without manual setup. Uses
            get_or_create to be safe against duplicates.
            """
            if not created:
                return
            locations = StockLocation.objects.all()
            count = 0
            for location in locations:
                _, stock_created = Stock.objects.get_or_create(
                    product=instance,
                    location=location,
                    defaults={"quantity": 0},
                )
                if stock_created:
                    count += 1
            if count:
                logger.info(
                    "Auto-created %d Stock entries for product '%s'.",
                    count,
                    instance.name,
                )

    except ImportError:
        logger.debug(
            "Stock/StockLocation/Product models not available — "
            "skipping auto_create_stock_for_product signal."
        )

    # ── Signal 3: Auto-create Stock entries for a new StockLocation ───
    try:
        from apps.inventory.models import Stock, StockLocation  # noqa: F401
        from apps.products.models import Product  # noqa: F401

        @receiver(post_save, sender=StockLocation)
        def auto_create_stock_for_location(sender, instance, created, **kwargs):
            """
            Auto-create Stock entries at a new StockLocation for all Products.

            Fires when a StockLocation is first created (created=True). Creates
            a Stock record with quantity=0 for every existing Product so that
            stock tracking at the new location is available immediately.
            Uses get_or_create to be safe against duplicates.
            """
            if not created:
                return
            products = Product.objects.all()
            count = 0
            for product in products:
                _, stock_created = Stock.objects.get_or_create(
                    product=product,
                    location=instance,
                    defaults={"quantity": 0},
                )
                if stock_created:
                    count += 1
            if count:
                logger.info(
                    "Auto-created %d Stock entries for location '%s'.",
                    count,
                    instance.name,
                )

    except ImportError:
        logger.debug(
            "Stock/StockLocation/Product models not available — "
            "skipping auto_create_stock_for_location signal."
        )

    logger.debug("Core model signals connected.")
