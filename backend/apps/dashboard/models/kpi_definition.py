"""KPIDefinition model — defines available KPIs in the system."""

from django.db import models

from apps.dashboard.enums import KPICategory, WidgetType


class KPIDefinition(models.Model):
    """Defines an available KPI with its calculation method, format, and permissions."""

    name = models.CharField(
        max_length=100,
        verbose_name="KPI Name",
        help_text="Display name of the KPI",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="KPI Code",
        help_text="Unique identifier code for the KPI (e.g., SALES_DAILY_REVENUE)",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Detailed description of what this KPI measures",
    )
    category = models.CharField(
        max_length=20,
        choices=KPICategory.choices,
        verbose_name="Category",
        help_text="KPI category for dashboard organization",
    )
    default_widget_type = models.CharField(
        max_length=20,
        choices=WidgetType.choices,
        default=WidgetType.NUMBER,
        verbose_name="Default Widget Type",
        help_text="Default widget type for displaying this KPI",
    )
    calculation_method = models.CharField(
        max_length=100,
        verbose_name="Calculation Method",
        help_text="Calculator class method reference (e.g., SalesKPICalculator.calculate_daily_revenue)",
    )
    format_type = models.CharField(
        max_length=20,
        choices=[
            ("currency", "Currency (LKR)"),
            ("number", "Number"),
            ("percent", "Percentage"),
            ("decimal", "Decimal"),
            ("count", "Count"),
        ],
        default="number",
        verbose_name="Format Type",
        help_text="Display format for the KPI value",
    )
    decimal_places = models.PositiveSmallIntegerField(
        default=2,
        verbose_name="Decimal Places",
        help_text="Number of decimal places (0-4)",
    )
    show_thousand_separator = models.BooleanField(
        default=True,
        verbose_name="Thousand Separator",
        help_text="Add separators for thousands (e.g., 1,000,000)",
    )
    required_permission = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Required Permission",
        help_text="Permission codename required to view this KPI (blank = visible to all authenticated users)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this KPI is currently active",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Sort Order",
        help_text="Display order within category",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboard_kpi_definition"
        ordering = ["category", "sort_order", "name"]
        verbose_name = "KPI Definition"
        verbose_name_plural = "KPI Definitions"

    def __str__(self):
        return f"{self.name} ({self.code})"

    def has_permission(self, user) -> bool:
        """Check if a user has permission to view this KPI.

        Returns True if no permission is required or the user has the
        required permission codename.
        """
        if not self.required_permission:
            return True
        return user.has_perm(self.required_permission)
