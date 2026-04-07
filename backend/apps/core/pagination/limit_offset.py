"""
Limit/offset pagination for LankaCommerce Cloud API.

Provides SQL-style limit and offset query parameters for maximum
client flexibility, suited for data exports, reporting, and
third-party integrations.
"""

from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class LCCLimitOffsetPagination(LimitOffsetPagination):
    """
    SQL-style limit/offset pagination with enhanced response metadata.

    Default limit: 20 items
    Maximum limit: 100 items
    Query params: ``?limit=N&offset=M``

    Response includes:
        - count: total items
        - limit: current limit value
        - offset: current offset value
        - next: URL to next range (or null)
        - previous: URL to previous range (or null)
        - results: array of items

    Examples::

        /api/products/?offset=0             -> 20 items (default limit)
        /api/products/?limit=50&offset=0    -> 50 items
        /api/products/?limit=200&offset=0   -> 100 items (capped to max)
        /api/products/?limit=20&offset=40   -> Items 41-60

    Performance note:
        For very large offsets (> 10 000) consider using
        ``LCCCursorPagination`` instead.
    """

    default_limit = 20  # Default when no limit query param is provided
    max_limit = 100  # Cap to protect server resources

    def get_paginated_response(self, data):
        """Return enhanced response with limit/offset metadata."""
        return Response(
            OrderedDict(
                [
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        """Return OpenAPI schema for the limit/offset paginated response."""
        return {
            "type": "object",
            "required": ["count", "limit", "offset", "results"],
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 150,
                    "description": "Total number of items.",
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.com/items/?limit=20&offset=40",
                    "description": "URL to the next range, or null.",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.com/items/?limit=20&offset=0",
                    "description": "URL to the previous range, or null.",
                },
                "limit": {
                    "type": "integer",
                    "example": 20,
                    "description": "Current limit value.",
                },
                "offset": {
                    "type": "integer",
                    "example": 20,
                    "description": "Current offset value.",
                },
                "results": schema,
            },
        }
