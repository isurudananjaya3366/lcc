"""
Reorder calculator service for determining optimal reorder quantities.

Implements EOQ, safety-stock, reorder-point, days-until-stockout,
urgency classification, and cost estimation.
"""

import logging
import math
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


class ReorderCalculator:
    """
    Calculate reorder suggestions for products.

    Orchestrates velocity, safety-stock, EOQ, and urgency logic.
    """

    # ── Main Orchestrator ───────────────────────────────────────

    @staticmethod
    def calculate_reorder_suggestion(product, warehouse=None):
        """
        Build a complete reorder-suggestion dict for *product*.

        Returns ``None`` when no reorder is needed.
        """
        from apps.inventory.alerts.services.config_resolver import ConfigResolver
        from apps.inventory.alerts.services.sales_velocity import SalesVelocityService

        config = ConfigResolver.resolve_for_product(product, warehouse=warehouse)

        # Get current stock
        current_stock = ReorderCalculator._get_current_stock(product, warehouse)

        # Calculate velocity
        velocity_data = SalesVelocityService.calculate_velocity(
            product, days=config.get("days_of_history_for_velocity", 30),
            warehouse=warehouse,
        )
        daily_velocity = velocity_data["avg_daily_velocity"] if velocity_data else Decimal("0")

        if daily_velocity <= 0:
            return None  # Not selling – skip

        # Safety stock & reorder point
        safety = ReorderCalculator.calculate_safety_stock(
            product, daily_velocity, config,
        )
        reorder_point = ReorderCalculator.get_reorder_point(
            daily_velocity, config, safety,
        )

        # Check if reorder is needed
        if current_stock > reorder_point:
            return None

        # Suggested quantity
        suggested_qty = ReorderCalculator.calculate_suggested_quantity(
            product, daily_velocity, config, safety,
        )

        # Days until stockout
        days_until = ReorderCalculator.calculate_days_until_stockout(
            current_stock, daily_velocity, product=product, warehouse=warehouse,
        )

        # Urgency
        urgency = ReorderCalculator.determine_urgency(days_until)

        # Cost
        estimated_cost, unit_cost = ReorderCalculator.calculate_estimated_cost(
            product, suggested_qty,
        )

        # Preferred supplier
        supplier = ReorderCalculator._get_preferred_supplier(product, warehouse)

        return {
            "product": product,
            "warehouse": warehouse,
            "suggested_qty": suggested_qty,
            "minimum_order_qty": Decimal(str(config.get("minimum_order_qty", 1))),
            "current_stock": current_stock,
            "suggested_supplier": supplier,
            "urgency": urgency,
            "days_until_stockout": days_until,
            "daily_velocity": daily_velocity,
            "safety_stock": safety,
            "reorder_point": reorder_point,
            "estimated_cost": estimated_cost,
            "unit_cost": unit_cost,
            "calculation_details": {
                "velocity_source": velocity_data.get("source", "unknown") if velocity_data else "none",
                "eoq": float(ReorderCalculator.calculate_eoq(product, daily_velocity, config) or 0),
                "safety_stock": float(safety),
                "reorder_point": float(reorder_point),
                "days_of_history": config.get("days_of_history_for_velocity", 30),
            },
        }

    # ── Reorder Point ───────────────────────────────────────────

    @staticmethod
    def get_reorder_point(daily_velocity, config, safety_stock):
        """
        Reorder Point = (Daily Velocity × Lead Time) + Safety Stock
        """
        lead_time = Decimal(str(config.get("lead_time_days", 7)))
        demand_during_lead = daily_velocity * lead_time
        return (demand_during_lead + safety_stock).quantize(Decimal("0.001"))

    # ── Suggested Quantity ──────────────────────────────────────

    @staticmethod
    def calculate_suggested_quantity(product, daily_velocity, config, safety_stock):
        """
        Determine how much to order.

        Priority: EOQ → configured reorder_quantity → 30-day supply.
        Respects MOQ.
        """
        eoq = ReorderCalculator.calculate_eoq(product, daily_velocity, config)
        if eoq and eoq > 0:
            qty = eoq
        elif config.get("reorder_quantity"):
            qty = Decimal(str(config["reorder_quantity"]))
        else:
            qty = daily_velocity * Decimal("30")  # 30-day supply

        moq = Decimal(str(config.get("minimum_order_qty", 1)))
        if qty < moq:
            qty = moq

        return qty.quantize(Decimal("0.001"))

    # ── Urgency ─────────────────────────────────────────────────

    @staticmethod
    def determine_urgency(days_until_stockout):
        """
        Map days-until-stockout to urgency level.

        critical  <  5 days
        high      < 15 days
        medium    < 30 days
        low       >= 30 days
        """
        from apps.inventory.alerts.constants import (
            URGENCY_CRITICAL,
            URGENCY_HIGH,
            URGENCY_LOW,
            URGENCY_MEDIUM,
        )

        if days_until_stockout is None:
            return URGENCY_LOW

        d = float(days_until_stockout)
        if d < 5:
            return URGENCY_CRITICAL
        if d < 15:
            return URGENCY_HIGH
        if d < 30:
            return URGENCY_MEDIUM
        return URGENCY_LOW

    # ── Cost Estimation ─────────────────────────────────────────

    @staticmethod
    def calculate_estimated_cost(product, quantity):
        """
        Return (total_cost, unit_cost) in LKR.
        """
        unit_cost = getattr(product, "cost_price", None) or Decimal("0")
        total_cost = unit_cost * quantity
        return total_cost, unit_cost

    # ── EOQ ─────────────────────────────────────────────────────

    @staticmethod
    def calculate_eoq(product, daily_velocity, config):
        """
        Economic Order Quantity: √(2DS / H)

        D = annual demand, S = ordering cost, H = holding cost/unit/year.
        Returns None if EOQ is disabled or parameters are invalid.
        """
        from apps.inventory.alerts.models import GlobalStockSettings

        settings = GlobalStockSettings.get_settings()

        if not getattr(settings, "use_eoq_calculation", True):
            return None

        annual_demand = ReorderCalculator.calculate_annual_demand(daily_velocity)
        if annual_demand <= 0:
            return None

        ordering_cost = ReorderCalculator.get_ordering_cost(settings)
        holding_cost = ReorderCalculator.get_holding_cost(product, settings)

        valid, msg = ReorderCalculator.validate_eoq_parameters(
            annual_demand, ordering_cost, holding_cost,
        )
        if not valid:
            logger.warning("EOQ invalid for %s: %s", product, msg)
            return None

        eoq = math.sqrt(
            float(2 * annual_demand * ordering_cost) / float(holding_cost)
        )
        return Decimal(str(round(eoq, 3)))

    @staticmethod
    def calculate_annual_demand(daily_velocity):
        return daily_velocity * Decimal("365")

    @staticmethod
    def get_ordering_cost(settings):
        return getattr(settings, "ordering_cost_lkr", None) or Decimal("5000.00")

    @staticmethod
    def get_holding_cost(product, settings):
        unit_cost = getattr(product, "cost_price", None) or Decimal("0")
        if unit_cost <= 0:
            return Decimal("0")
        pct = getattr(settings, "holding_cost_percent", None) or Decimal("25.00")
        return unit_cost * (pct / Decimal("100"))

    @staticmethod
    def validate_eoq_parameters(annual_demand, ordering_cost, holding_cost):
        if annual_demand <= 0:
            return False, "Annual demand must be > 0"
        if ordering_cost <= 0:
            return False, "Ordering cost must be > 0"
        if holding_cost <= 0:
            return False, "Holding cost must be > 0"
        return True, "Valid"

    # ── Safety Stock ────────────────────────────────────────────

    @staticmethod
    def calculate_safety_stock(product, daily_velocity, config):
        """
        Full formula: Z × √(LT × σ_d² + D² × σ_LT²)
        Falls back to simplified: daily_velocity × safety_days.
        """
        from apps.inventory.alerts.models import GlobalStockSettings
        from apps.inventory.alerts.services.sales_velocity import SalesVelocityService

        settings = GlobalStockSettings.get_settings()
        lead_time = float(config.get("lead_time_days", 7))
        z_score = ReorderCalculator.get_service_level_factor(settings)

        vel_detail = SalesVelocityService.calculate_daily_velocity(product, days=30)
        if vel_detail and vel_detail.get("confidence_interval"):
            sd_demand = vel_detail["confidence_interval"]["std_dev"]
            sd_lt = lead_time * 0.2  # estimate 20% variability
            safety = ReorderCalculator._full_safety_stock(
                z_score, lead_time, sd_demand, float(daily_velocity), sd_lt,
            )
        else:
            safety_days = getattr(settings, "safety_stock_days", 7) or 7
            safety = ReorderCalculator.simplified_safety_stock(
                daily_velocity, safety_days,
            )
        return safety

    @staticmethod
    def _full_safety_stock(z, lt, sd_d, avg_d, sd_lt):
        """Z × √(LT × σ_d² + D² × σ_LT²)"""
        variance = lt * (sd_d ** 2) + (avg_d ** 2) * (sd_lt ** 2)
        return Decimal(str(round(z * math.sqrt(variance), 3)))

    @staticmethod
    def simplified_safety_stock(daily_velocity, safety_days=7):
        return daily_velocity * Decimal(str(safety_days))

    @staticmethod
    def get_service_level_factor(settings):
        level = getattr(settings, "target_service_level", None) or Decimal("95.00")
        z_map = {
            Decimal("90.00"): 1.28,
            Decimal("95.00"): 1.65,
            Decimal("99.00"): 2.33,
        }
        return z_map.get(level, 1.65)

    # ── Days Until Stockout ─────────────────────────────────────

    @staticmethod
    def calculate_days_until_stockout(
        current_stock, daily_velocity, product=None, warehouse=None
    ):
        """(Current Stock + Incoming) / Daily Velocity."""
        if current_stock <= 0:
            return Decimal("0")
        if daily_velocity <= 0:
            return Decimal("999")

        effective = current_stock
        if product:
            incoming = ReorderCalculator.get_incoming_stock(product, warehouse)
            effective += incoming

        return (effective / daily_velocity).quantize(Decimal("0.01"))

    @staticmethod
    def get_incoming_stock(product, warehouse=None):
        """Sum quantities from pending purchase orders (defensive import)."""
        try:
            from apps.purchasing.models import PurchaseOrderItem
        except ImportError:
            return Decimal("0")

        qs = PurchaseOrderItem.objects.filter(
            product=product,
            purchase_order__status__in=["pending", "approved", "sent"],
        )
        if warehouse:
            qs = qs.filter(purchase_order__destination_warehouse=warehouse)

        total = qs.aggregate(total=Sum("quantity"))["total"]
        return total or Decimal("0")

    @staticmethod
    def get_stockout_date(current_stock, daily_velocity, product=None, warehouse=None):
        """Return estimated datetime of stock-out, or None if infinite."""
        from datetime import timedelta as td

        days = ReorderCalculator.calculate_days_until_stockout(
            current_stock, daily_velocity, product=product, warehouse=warehouse,
        )
        if days >= Decimal("999"):
            return None
        return timezone.now() + td(days=float(days))

    # ── Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _get_current_stock(product, warehouse):
        """Return available stock for the product (possibly per warehouse)."""
        try:
            if warehouse:
                sl = product.stock_levels.filter(warehouse=warehouse).first()
            else:
                agg = product.stock_levels.aggregate(total=Sum("available_quantity"))
                return Decimal(str(agg["total"] or 0))
            return Decimal(str(sl.available_quantity)) if sl else Decimal("0")
        except Exception:
            return Decimal("0")

    @staticmethod
    def _get_preferred_supplier(product, warehouse):
        """Look up preferred supplier from ProductStockConfig or product."""
        from apps.inventory.alerts.models import ProductStockConfig

        try:
            cfg = ProductStockConfig.objects.filter(
                product=product,
            ).first()
            if warehouse:
                w_cfg = ProductStockConfig.objects.filter(
                    product=product, warehouse=warehouse,
                ).first()
                if w_cfg:
                    cfg = w_cfg
        except Exception:
            cfg = None
        if cfg and cfg.preferred_supplier_id:
            return cfg.preferred_supplier
        # Fallback to product-level supplier if available
        return getattr(product, "default_supplier", None)
