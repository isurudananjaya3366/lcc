"""KPI period enumeration."""

from django.db import models


class KPIPeriod(models.TextChoices):
    """Time periods for KPI calculation and display."""

    TODAY = "TODAY", "Today"
    YESTERDAY = "YESTERDAY", "Yesterday"
    WEEK = "WEEK", "This Week"
    LAST_WEEK = "LAST_WEEK", "Last Week"
    MONTH = "MONTH", "This Month"
    LAST_MONTH = "LAST_MONTH", "Last Month"
    QUARTER = "QUARTER", "This Quarter"
    YEAR = "YEAR", "This Year"
    LAST_YEAR = "LAST_YEAR", "Last Year"
    CUSTOM = "CUSTOM", "Custom Range"
