"""
No-pagination class for LankaCommerce Cloud API.

Disables pagination entirely, returning all results in a single
response. Use only for small, bounded datasets.
"""

from rest_framework.response import Response


class NoPagination:
    """
    Disables pagination and returns all results.

    Use **only** for small datasets (< 100 items) such as:
        - Dropdown / select options
        - Lookup tables (countries, provinces, districts)
        - Reference / settings data
        - User permission lists

    WARNING:
        Do NOT use for datasets that can grow unbounded (products,
        customers, orders). Always prefer a paginated class for those.

    Example view usage::

        class CategoryListView(ListAPIView):
            queryset = Category.objects.all()
            serializer_class = CategorySerializer
            pagination_class = NoPagination
    """

    def paginate_queryset(self, queryset, request, view=None):
        """Return ``None`` to signal DRF that pagination is disabled."""
        return None

    def get_paginated_response(self, data):
        """Return the data as-is, without any pagination wrapper."""
        return Response(data)
