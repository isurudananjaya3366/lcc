"""
Customer API URL routing.

Registers all customer ViewSets with DRF DefaultRouter.

URL structure:
    /api/v1/customers/                         — list / create
    /api/v1/customers/{id}/                    — retrieve / update / delete
    /api/v1/customers/search/                  — full-text search
    /api/v1/customers/{id}/addresses/          — addresses
    /api/v1/customers/{id}/phones/             — phones
    /api/v1/customers/{id}/communications/     — communications
    /api/v1/customers/{id}/history/            — purchase history
    /api/v1/customers/{id}/statistics/         — customer statistics
    /api/v1/customers/{id}/activity/           — activity feed
    /api/v1/customers/{id}/tags/               — tag management
    /api/v1/customers/{id}/tags/{tag_id}/      — remove tag
    /api/v1/customers/import/                  — CSV import
    /api/v1/customers/export/                  — CSV export
    /api/v1/customers/{id}/duplicates/         — duplicate detection
    /api/v1/customers/merge/                   — merge customers
"""

from rest_framework.routers import DefaultRouter

from apps.customers.views import CustomerViewSet

app_name = "customers"

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")

urlpatterns = router.urls
