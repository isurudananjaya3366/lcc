"""
Customer services module.

Contains business logic services for the customers application
including code generation, search, history, cache, communication,
purchase history, activity feed, tagging, segmentation,
duplicate detection / merge, and CSV import/export.
"""

from apps.customers.services.activity_service import CustomerActivityService
from apps.customers.services.cache_service import CustomerCacheService
from apps.customers.services.communication_service import CommunicationService
from apps.customers.services.customer_service import CustomerService
from apps.customers.services.duplicate_service import DuplicateDetectionService
from apps.customers.services.export_service import CustomerExportService
from apps.customers.services.history_service import HistoryService
from apps.customers.services.import_service import CustomerImportService
from apps.customers.services.purchase_history_service import PurchaseHistoryService
from apps.customers.services.search_service import CustomerSearchService
from apps.customers.services.segment_service import CustomerSegmentService
from apps.customers.services.tag_service import CustomerTagService

__all__ = [
    "CommunicationService",
    "CustomerActivityService",
    "CustomerCacheService",
    "CustomerExportService",
    "CustomerImportService",
    "CustomerSearchService",
    "CustomerSegmentService",
    "CustomerService",
    "CustomerTagService",
    "DuplicateDetectionService",
    "HistoryService",
    "PurchaseHistoryService",
]
