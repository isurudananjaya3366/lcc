"""
Basic demand forecasting service for inventory planning.

Supports simple moving average, weighted moving average,
and exponential smoothing methods with seasonal adjustment.
"""

import logging
from datetime import timedelta
from decimal import Decimal
from statistics import mean

from django.utils import timezone

logger = logging.getLogger(__name__)


class DemandForecastService:
    """
    Short-term demand forecasting for products.

    Methods available: ``moving_average``, ``weighted``, ``exponential_smoothing``.
    """

    @staticmethod
    def forecast_demand(product, days_ahead=30, method="exponential_smoothing"):
        """
        Forecast demand for *product* over the next *days_ahead* days.

        Returns dict with forecast data or None when insufficient history.
        """
        from apps.inventory.alerts.services.sales_velocity import SalesVelocityService

        historical = SalesVelocityService.get_sales_data(product, days=90)
        if not historical:
            logger.warning("No historical data for %s", product)
            return None

        if method == "moving_average":
            forecast = DemandForecastService.calculate_moving_average(
                historical, days_ahead,
            )
        elif method == "weighted":
            forecast = DemandForecastService.weighted_moving_average(
                historical, days_ahead,
            )
        else:
            forecast = DemandForecastService.exponential_smoothing(
                historical, days_ahead,
            )

        if SalesVelocityService.detect_seasonality(product):
            forecast = DemandForecastService.apply_seasonal_adjustment(
                forecast, product,
            )

        return forecast

    # ── Moving Average ──────────────────────────────────────────

    @staticmethod
    def calculate_moving_average(historical, days_ahead, window=30):
        """Simple moving average of last *window* days."""
        if len(historical) < window:
            window = len(historical)

        recent = historical[-window:]
        quantities = [float(d["quantity"]) for d in recent]
        avg_daily = mean(quantities)
        forecast_total = avg_daily * days_ahead

        return {
            "method": "moving_average",
            "window_days": window,
            "avg_daily": Decimal(str(round(avg_daily, 3))),
            "forecast_total": Decimal(str(round(forecast_total, 3))),
            "forecast_days": days_ahead,
            "confidence": "medium",
        }

    # ── Weighted Moving Average ─────────────────────────────────

    @staticmethod
    def weighted_moving_average(historical, days_ahead, window=30):
        """Linearly-weighted moving average (more weight to recent days)."""
        if len(historical) < window:
            window = len(historical)

        recent = historical[-window:]
        quantities = [float(d["quantity"]) for d in recent]
        weights = list(range(1, len(quantities) + 1))
        total_weight = sum(weights)

        weighted_sum = sum(q * w for q, w in zip(quantities, weights))
        weighted_avg = weighted_sum / total_weight
        forecast_total = weighted_avg * days_ahead

        return {
            "method": "weighted_moving_average",
            "window_days": window,
            "avg_daily": Decimal(str(round(weighted_avg, 3))),
            "forecast_total": Decimal(str(round(forecast_total, 3))),
            "forecast_days": days_ahead,
            "confidence": "medium",
        }

    # ── Exponential Smoothing ───────────────────────────────────

    @staticmethod
    def exponential_smoothing(historical, days_ahead, alpha=0.3):
        """
        Single exponential smoothing.

        S_t = α × X_t + (1 − α) × S_{t−1}
        """
        quantities = [float(d["quantity"]) for d in historical]
        smoothed = [quantities[0]]
        for i in range(1, len(quantities)):
            s_t = alpha * quantities[i] + (1 - alpha) * smoothed[i - 1]
            smoothed.append(s_t)

        forecast_daily = smoothed[-1]
        forecast_total = forecast_daily * days_ahead

        return {
            "method": "exponential_smoothing",
            "alpha": alpha,
            "avg_daily": Decimal(str(round(forecast_daily, 3))),
            "forecast_total": Decimal(str(round(forecast_total, 3))),
            "forecast_days": days_ahead,
            "confidence": "high",
        }

    # ── Seasonal Adjustment ─────────────────────────────────────

    @staticmethod
    def apply_seasonal_adjustment(forecast, product):
        """Multiply forecast by current-month seasonal factor."""
        from apps.inventory.alerts.services.sales_velocity import SalesVelocityService

        factor = SalesVelocityService.get_seasonal_factor(product)
        forecast["avg_daily"] *= Decimal(str(factor))
        forecast["forecast_total"] *= Decimal(str(factor))
        forecast["seasonal_adjusted"] = True
        forecast["seasonal_factor"] = factor
        return forecast

    # ── Forecast Accuracy (placeholder) ─────────────────────────

    @staticmethod
    def calculate_forecast_accuracy(product, days=30):
        """
        Compare earlier forecast to actual sales (MAPE).

        Placeholder — requires stored forecasts to compare.
        """
        return {
            "mape": None,
            "message": "Forecast accuracy tracking not yet implemented",
        }
