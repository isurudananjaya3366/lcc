"""KPI category enumeration."""

from django.db import models


class KPICategory(models.TextChoices):
    """Categories for organizing KPIs across the ERP system."""

    SALES = "SALES", "Sales & Revenue"
    INVENTORY = "INVENTORY", "Inventory & Stock"
    FINANCIAL = "FINANCIAL", "Financial Performance"
    HR = "HR", "Human Resources"
    CUSTOMER = "CUSTOMER", "Customer Metrics"
    OPERATIONS = "OPERATIONS", "Operations & Efficiency"
    COMPLIANCE = "COMPLIANCE", "Compliance & Regulatory"
