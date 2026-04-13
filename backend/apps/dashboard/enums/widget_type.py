"""KPI widget type enumeration."""

from django.db import models


class WidgetType(models.TextChoices):
    """Widget types for displaying KPI data on the dashboard."""

    NUMBER = "NUMBER", "Single Number"
    CHART = "CHART", "Chart Display"
    TABLE = "TABLE", "Table Display"
    GAUGE = "GAUGE", "Gauge / Meter"
    TREND = "TREND", "Trend with Sparkline"
