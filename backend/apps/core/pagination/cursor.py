"""
Cursor-based pagination for LankaCommerce Cloud API.

Provides efficient, consistent pagination for large and frequently
changing datasets such as activity feeds, notifications, and audit logs.
"""

from rest_framework.pagination import CursorPagination


class LCCCursorPagination(CursorPagination):
    """
    Cursor-based pagination for large, frequently changing datasets.

    Uses opaque cursor tokens for forward/backward navigation. Results
    remain consistent even when the underlying data changes between
    requests.

    Default ordering: ``-created_on`` (newest first)
    Default page size: 20
    Query param: ``?cursor=<token>``

    Ideal for:
        - Activity feeds
        - Notifications
        - Audit logs
        - Inventory updates
        - Real-time data streams

    Limitations:
        - No page jumping — next/previous navigation only
        - Ordering field must be indexed in the database
        - Views can override ``ordering`` if a different field is needed

    Note:
        The ordering field uses ``created_on`` which matches the project's
        ``TimeStampedModel`` convention (not ``created_at``).
    """

    page_size = 20  # Consistent with StandardPagination
    ordering = "-created_on"  # Newest first — matches TimeStampedModel field name
    cursor_query_param = "cursor"  # DRF default, explicit for clarity
