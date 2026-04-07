"""
Configuration inheritance resolver for stock alert thresholds.

Resolves effective configuration values through the inheritance chain:
    ProductStockConfig (warehouse) → ProductStockConfig (no warehouse)
    → CategoryStockConfig (recursive parents) → GlobalStockSettings
"""


class ConfigResolver:
    """Static service that resolves effective stock config for a product."""

    THRESHOLD_FIELDS = ["low_stock_threshold", "reorder_point", "reorder_quantity"]

    GLOBAL_FIELD_MAP = {
        "low_stock_threshold": "default_low_threshold",
        "reorder_point": "default_reorder_point",
        "reorder_quantity": "default_reorder_qty",
    }

    @staticmethod
    def resolve_for_product(product, warehouse=None):
        """
        Return resolved configuration dict for a product/warehouse.

        Resolution order:
        1. ProductStockConfig with specific warehouse
        2. ProductStockConfig without warehouse
        3. CategoryStockConfig (walk up category tree)
        4. GlobalStockSettings
        """
        from apps.inventory.alerts.models.global_settings import GlobalStockSettings
        from apps.inventory.alerts.models.category_config import CategoryStockConfig
        from apps.inventory.alerts.models.product_config import ProductStockConfig

        config = {}
        sources = {}
        needed = set(ConfigResolver.THRESHOLD_FIELDS)

        # 1. Product config — warehouse-specific
        if warehouse:
            prod_wh = ProductStockConfig.objects.filter(
                product=product, warehouse=warehouse
            ).first()
            if prod_wh:
                ConfigResolver._apply(prod_wh, config, sources, needed, "product_warehouse")

        # 2. Product config — generic (no warehouse)
        if needed:
            prod_global = ProductStockConfig.objects.filter(
                product=product, warehouse__isnull=True, variant__isnull=True,
            ).first()
            if prod_global:
                ConfigResolver._apply(prod_global, config, sources, needed, "product")

        # 3. Category config — walk up tree
        if needed and hasattr(product, "category_id") and product.category_id:
            category = product.category
            visited = set()
            while category and needed:
                if category.pk in visited:
                    break
                visited.add(category.pk)
                try:
                    cat_config = category.stock_config
                except CategoryStockConfig.DoesNotExist:
                    category = category.parent if hasattr(category, "parent") else None
                    continue
                source_label = f"category:{category.name}"
                ConfigResolver._apply(cat_config, config, sources, needed, source_label)
                if not cat_config.inherit_from_parent:
                    break
                category = category.parent if hasattr(category, "parent") else None

        # 4. Global settings fallback
        if needed:
            try:
                gs = GlobalStockSettings.get_settings()
            except Exception:
                gs = None
            if gs:
                for field in list(needed):
                    global_name = ConfigResolver.GLOBAL_FIELD_MAP.get(field)
                    if global_name:
                        value = getattr(gs, global_name, None)
                        if value is not None:
                            config[field] = value
                            sources[field] = "global"
                            needed.discard(field)

        config["sources"] = sources
        return config

    @staticmethod
    def _apply(obj, config, sources, needed, source_label):
        """Apply non-null fields from obj into config."""
        for field in list(needed):
            value = getattr(obj, field, None)
            if value is not None:
                config[field] = value
                sources[field] = source_label
                needed.discard(field)

    @staticmethod
    def get_config_source(product, warehouse=None):
        """Return dict mapping each field to its source."""
        result = ConfigResolver.resolve_for_product(product, warehouse)
        return result.get("sources", {})

    @staticmethod
    def resolve_field(field_name, product, warehouse=None):
        """Resolve a single field. Returns (value, source) tuple."""
        config = ConfigResolver.resolve_for_product(product, warehouse)
        value = config.get(field_name)
        source = config.get("sources", {}).get(field_name, "unknown")
        return value, source
