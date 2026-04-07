"""
Standard page-number pagination for LankaCommerce Cloud API.

Provides the default pagination class used across most API endpoints,
returning paginated results with comprehensive metadata.
"""

from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Standard page number pagination with enhanced response metadata.

    Default: 20 items per page
    Maximum: 100 items per page
    Query param: ``?page_size=N`` to override default

    Response includes:
        - count: total items across all pages
        - total_pages: number of pages
        - current_page: current page number
        - page_size: items per page
        - next: URL to next page (or null)
        - previous: URL to previous page (or null)
        - results: array of paginated items

    Examples::

        /api/products/                -> 20 items (default)
        /api/products/?page_size=50   -> 50 items
        /api/products/?page=2         -> Page 2, 20 items
        /api/products/?page_size=200  -> 100 items (capped to max)
    """

    page_size = 20  # Default items per page — balances response size with UX
    max_page_size = 100  # Cap to prevent excessive API load / DoS
    page_size_query_param = "page_size"  # Allow clients to override via ?page_size=N

    def get_paginated_response(self, data):
        """Return enhanced response with total count and page metadata."""
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("total_pages", self.page.paginator.num_pages),
                    ("current_page", self.page.number),
                    ("page_size", self.page.paginator.per_page),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        """Return OpenAPI schema for the enhanced paginated response."""
        return {
            "type": "object",
            "required": [
                "count",
                "total_pages",
                "current_page",
                "page_size",
                "results",
            ],
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 150,
                    "description": "Total number of items across all pages.",
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.com/items/?page=3",
                    "description": "URL to the next page, or null.",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.com/items/?page=1",
                    "description": "URL to the previous page, or null.",
                },
                "total_pages": {
                    "type": "integer",
                    "example": 8,
                    "description": "Total number of pages.",
                },
                "current_page": {
                    "type": "integer",
                    "example": 2,
                    "description": "Current page number.",
                },
                "page_size": {
                    "type": "integer",
                    "example": 20,
                    "description": "Number of items per page.",
                },
                "results": schema,
            },
        }
