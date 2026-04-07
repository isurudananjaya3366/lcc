"""
Price resolution service – determines the effective price for a product/variant
by evaluating all active pricing rules in priority order.

Priority: Flash Sale > Scheduled Price > Promotional Price > Sale Price > Base Price
"""

from decimal import Decimal

from django.utils import timezone


class PriceResolutionService:
    """
    Resolves the effective price for a product or variant considering
    all active promotions, schedules, and flash sales.
    """

    @classmethod
    def get_effective_price(
        cls,
        item,
        *,
        customer=None,
        quantity: int = 1,
        order_value=None,
        datetime_to_check=None,
    ) -> dict:
        """
        Determine the best price for *item* (Product or ProductVariant).

        Returns dict with: price, price_type, reason, original_price,
        discount_amount, discount_percentage.
        """
        now = datetime_to_check or timezone.now()
        product, variant = cls._resolve_product_variant(item)
        base_price = cls._get_base_price(product, variant)

        # 1. Flash sales (highest priority)
        flash = cls._check_flash_sales(item, now)
        if flash is not None:
            return cls._build_result(flash, "flash_sale", "Flash sale price", base_price)

        # 2. Scheduled prices
        scheduled = cls._check_scheduled_prices(item, now)
        if scheduled is not None:
            return cls._build_result(scheduled, "scheduled", "Scheduled price", base_price)

        # 3. Promotional prices
        promo = cls._check_promotional_prices(item, product, customer, quantity, order_value, base_price, now)
        if promo is not None:
            return promo

        # 4. Sale price (from ProductPrice / VariantPrice)
        sale = cls._check_sale_price(product, variant)
        if sale is not None:
            return cls._build_result(sale, "sale", "Sale price", base_price)

        # 5. Base price
        return cls._build_result(base_price, "base", "Base price", base_price)

    # ── Private checkers ───────────────────────────────────────

    @classmethod
    def _check_flash_sales(cls, item, now):
        from ..models.flash_sale import FlashSale
        from ..models.scheduled_price import ScheduledPrice

        product, variant = cls._resolve_product_variant(item)
        qs = ScheduledPrice.objects.filter(
            status=ScheduledPrice.Status.ACTIVE,
            start_datetime__lte=now,
            end_datetime__gte=now,
        )
        if variant:
            qs = qs.filter(variant=variant)
        else:
            qs = qs.filter(product=product, variant__isnull=True)

        sp = qs.filter(flash_sale_detail__isnull=False, flash_sale_detail__is_sold_out=False).order_by("-priority").first()
        return sp.sale_price if sp else None

    @classmethod
    def _check_scheduled_prices(cls, item, now):
        from ..models.scheduled_price import ScheduledPrice

        product, variant = cls._resolve_product_variant(item)
        qs = ScheduledPrice.objects.filter(
            status=ScheduledPrice.Status.ACTIVE,
            start_datetime__lte=now,
            end_datetime__gte=now,
            flash_sale_detail__isnull=True,  # exclude flash sales
        )
        if variant:
            qs = qs.filter(variant=variant)
        else:
            qs = qs.filter(product=product, variant__isnull=True)

        sp = qs.order_by("-priority").first()
        return sp.sale_price if sp else None

    @classmethod
    def _check_promotional_prices(cls, item, product, customer, quantity, order_value, base_price, now):
        from ..models.promotional_price import PromotionalPrice

        promos = PromotionalPrice.objects.filter(
            is_active=True,
            start_datetime__lte=now,
            end_datetime__gte=now,
        ).order_by("-priority")

        for promo in promos:
            result = promo.check_conditions(product, customer, quantity, order_value)
            if result:
                discounted = promo.calculate_discounted_price(base_price, quantity)
                if discounted is not None and discounted < base_price:
                    return cls._build_result(
                        discounted, "promotional", f"Promotion: {promo.name}", base_price
                    )
        return None

    @classmethod
    def _check_sale_price(cls, product, variant):
        if variant:
            from ..models.variant_price import VariantPrice
            vp = VariantPrice.objects.filter(variant=variant).first()
            if vp:
                sale = vp.get_sale_price() if hasattr(vp, "get_sale_price") else vp.sale_price
                if sale:
                    return sale
        pp = getattr(product, "product_price", None)
        if pp and pp.is_on_sale and pp.sale_price:
            return pp.sale_price
        return None

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _resolve_product_variant(item):
        from apps.products.models.product import Product
        from apps.products.models.product_variant import ProductVariant

        if isinstance(item, ProductVariant):
            return item.product, item
        if isinstance(item, Product):
            return item, None
        raise TypeError(f"Expected Product or ProductVariant, got {type(item)}")

    @staticmethod
    def _get_base_price(product, variant) -> Decimal:
        if variant:
            from ..models.variant_price import VariantPrice
            vp = VariantPrice.objects.filter(variant=variant).first()
            if vp:
                return vp.get_effective_price()
        pp = getattr(product, "product_price", None)
        if pp:
            return pp.base_price
        return Decimal("0")

    @staticmethod
    def _build_result(price: Decimal, price_type: str, reason: str, base_price: Decimal) -> dict:
        discount_amount = max(Decimal("0"), base_price - price)
        discount_pct = (
            (discount_amount / base_price * 100).quantize(Decimal("0.01"))
            if base_price
            else Decimal("0")
        )
        return {
            "price": price,
            "price_type": price_type,
            "reason": reason,
            "original_price": base_price,
            "discount_amount": discount_amount,
            "discount_percentage": discount_pct,
        }
