"""
URL configuration for LankaCommerce Cloud.

Root URL configuration with organized sections for admin, API, and health checks.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # ──────────────────────────────────────────────
    # Admin
    # ──────────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ──────────────────────────────────────────────
    # API v1
    # ──────────────────────────────────────────────
    path("api/v1/users/", include("apps.users.api.urls", namespace="users")),
    path("api/v1/", include("apps.products.api.urls", namespace="products")),
    path("api/v1/", include("apps.attributes.urls", namespace="attributes")),
    # path("api/v1/auth/", include("apps.authentication.urls")),
    # path("api/v1/tenants/", include("apps.tenants.urls")),
    path("api/v1/warehouse/", include("apps.inventory.warehouses.api.urls", namespace="warehouse")),
    path("api/v1/stock/", include("apps.inventory.stock.api.urls", namespace="stock")),
    path("api/v1/alerts/", include("apps.inventory.alerts.urls", namespace="alerts")),
    path("api/v1/pos/", include("apps.pos.urls", namespace="pos")),
    path("api/v1/quotes/", include("apps.quotes.urls", namespace="quotes")),
    path("api/v1/", include("apps.orders.urls", namespace="orders")),
    path("api/v1/", include("apps.invoices.urls", namespace="invoices")),
    path("api/v1/", include("apps.payments.urls", namespace="payments")),
    path("api/v1/", include("apps.customers.urls", namespace="customers")),
    path("api/v1/", include("apps.credit.urls", namespace="credit")),
    path("api/v1/", include("apps.vendors.urls", namespace="vendors")),
    path("api/v1/", include("apps.purchases.urls", namespace="purchases")),
    path("api/v1/", include("apps.employees.urls", namespace="employees")),
    path("api/v1/organization/", include("apps.organization.urls", namespace="organization")),
    path("api/v1/attendance/", include("apps.attendance.urls", namespace="attendance")),
    path("api/v1/leave/", include("apps.leave.urls", namespace="leave")),
    path("api/v1/payroll/", include("apps.payroll.urls", namespace="payroll")),
    path("api/v1/payslips/", include("apps.payslip.urls", namespace="payslip")),
    path("api/v1/accounting/", include("apps.accounting.urls", namespace="accounting")),

    # ──────────────────────────────────────────────
    # API Documentation — drf-spectacular (SP11)
    # ──────────────────────────────────────────────
    path("api/", include("apps.core.api_docs.urls")),

    # ──────────────────────────────────────────────
    # Health Checks
    # ──────────────────────────────────────────────
    path("health/", include("apps.core.urls")),
]

# ──────────────────────────────────────────────────────────────────────
# Media file serving (development only)
# ──────────────────────────────────────────────────────────────────────
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
