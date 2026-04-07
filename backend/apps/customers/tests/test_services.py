"""
Customer service tests.

Tests for CustomerService, TagService, SegmentService,
DuplicateDetectionService, HistoryService, SearchService,
CacheService, ImportService, and ExportService.
"""

import io

import pytest

from apps.customers.models import (
    Customer,
    CustomerHistory,
    CustomerMerge,
    CustomerSegment,
    CustomerTag,
    CustomerTagAssignment,
)
from apps.customers.services import (
    CustomerExportService,
    CustomerImportService,
    CustomerSearchService,
    CustomerSegmentService,
    CustomerTagService,
    DuplicateDetectionService,
    HistoryService,
)

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════
# HistoryService
# ═══════════════════════════════════════════════════════════════════


class TestHistoryService:

    def test_log_creation(self):
        customer = Customer.objects.create(first_name="H", last_name="S")
        HistoryService.log_creation(customer)
        assert CustomerHistory.objects.filter(
            customer=customer, change_type="create"
        ).exists()

    def test_log_change(self):
        customer = Customer.objects.create(first_name="H", last_name="S")
        HistoryService.log_change(
            customer, "status", "active", "inactive"
        )
        history = CustomerHistory.objects.filter(
            customer=customer, field_name="status"
        ).first()
        assert history is not None
        assert history.old_value == "active"
        assert history.new_value == "inactive"

    def test_log_changes_multiple(self):
        customer = Customer.objects.create(first_name="H", last_name="S")
        HistoryService.log_changes(
            customer,
            {"first_name": "H", "last_name": "S"},
            {"first_name": "Harry", "last_name": "Smith"},
        )
        assert CustomerHistory.objects.filter(customer=customer).count() >= 2


# ═══════════════════════════════════════════════════════════════════
# CustomerTagService
# ═══════════════════════════════════════════════════════════════════


class TestTagService:

    def test_assign_tag(self):
        customer = Customer.objects.create(first_name="T", last_name="S")
        tag = CustomerTag.objects.create(name="VIP")
        assignment = CustomerTagService.assign_tag(customer.pk, tag.pk)
        assert assignment.pk is not None

    def test_assign_tag_idempotent(self):
        customer = Customer.objects.create(first_name="T", last_name="S")
        tag = CustomerTag.objects.create(name="Idem")
        a1 = CustomerTagService.assign_tag(customer.pk, tag.pk)
        a2 = CustomerTagService.assign_tag(customer.pk, tag.pk)
        assert a1.pk == a2.pk

    def test_remove_tag(self):
        customer = Customer.objects.create(first_name="T", last_name="S")
        tag = CustomerTag.objects.create(name="Remove")
        CustomerTagService.assign_tag(customer.pk, tag.pk)
        removed = CustomerTagService.remove_tag(customer.pk, tag.pk)
        assert removed is True

    def test_remove_nonexistent_tag(self):
        customer = Customer.objects.create(first_name="T", last_name="S")
        import uuid
        removed = CustomerTagService.remove_tag(customer.pk, uuid.uuid4())
        assert removed is False

    def test_bulk_assign_tags(self):
        c1 = Customer.objects.create(first_name="B1", last_name="T")
        c2 = Customer.objects.create(first_name="B2", last_name="T")
        tag = CustomerTag.objects.create(name="Bulk")
        count = CustomerTagService.bulk_assign_tags(
            [c1.pk, c2.pk], tag.pk
        )
        assert count == 2

    def test_get_customer_tags(self):
        customer = Customer.objects.create(first_name="G", last_name="T")
        t1 = CustomerTag.objects.create(name="T1")
        t2 = CustomerTag.objects.create(name="T2")
        CustomerTagService.assign_tag(customer.pk, t1.pk)
        CustomerTagService.assign_tag(customer.pk, t2.pk)
        tags = CustomerTagService.get_customer_tags(customer.pk)
        assert tags.count() == 2

    def test_filter_by_tag(self):
        c1 = Customer.objects.create(first_name="F", last_name="1")
        c2 = Customer.objects.create(first_name="F", last_name="2")
        tag = CustomerTag.objects.create(name="Filter")
        CustomerTagService.assign_tag(c1.pk, tag.pk)
        qs = CustomerTagService.filter_by_tag(tag.pk)
        assert c1 in qs
        assert c2 not in qs

    def test_filter_by_tags_any(self):
        c = Customer.objects.create(first_name="Multi", last_name="T")
        t1 = CustomerTag.objects.create(name="M1")
        t2 = CustomerTag.objects.create(name="M2")
        CustomerTagService.assign_tag(c.pk, t1.pk)
        qs = CustomerTagService.filter_by_tags([t1.pk, t2.pk], match_all=False)
        assert c in qs

    def test_get_tag_statistics(self):
        tag = CustomerTag.objects.create(name="Stats")
        stats = CustomerTagService.get_tag_statistics()
        assert stats.filter(pk=tag.pk).exists()


# ═══════════════════════════════════════════════════════════════════
# CustomerSegmentService
# ═══════════════════════════════════════════════════════════════════


class TestSegmentService:

    def test_evaluate_customer_match(self):
        customer = Customer.objects.create(
            first_name="Seg", last_name="T", total_purchases=200000
        )
        segment = CustomerSegment.objects.create(
            name="High",
            rules={
                "operator": "and",
                "conditions": [
                    {"field": "total_purchases", "operator": "gte", "value": 100000}
                ],
            },
        )
        assert CustomerSegmentService.evaluate_customer(customer, segment) is True

    def test_evaluate_customer_no_match(self):
        customer = Customer.objects.create(
            first_name="Seg", last_name="T", total_purchases=5000
        )
        segment = CustomerSegment.objects.create(
            name="Expensive",
            rules={
                "operator": "and",
                "conditions": [
                    {"field": "total_purchases", "operator": "gte", "value": 100000}
                ],
            },
        )
        assert CustomerSegmentService.evaluate_customer(customer, segment) is False

    def test_get_segment_customers(self):
        Customer.objects.create(
            first_name="S1", last_name="T", status="active"
        )
        segment = CustomerSegment.objects.create(
            name="Active",
            rules={
                "operator": "and",
                "conditions": [
                    {"field": "status", "operator": "eq", "value": "active"}
                ],
            },
        )
        qs = CustomerSegmentService.get_segment_customers(segment)
        assert qs.count() >= 1

    def test_evaluate_all_segments(self):
        CustomerSegment.objects.create(
            name="All",
            rules={
                "operator": "and",
                "conditions": [
                    {"field": "status", "operator": "eq", "value": "active"}
                ],
            },
        )
        results = CustomerSegmentService.evaluate_all_segments()
        assert isinstance(results, dict)

    def test_or_logic(self):
        customer = Customer.objects.create(
            first_name="Or", last_name="T",
            status="inactive", customer_type="VIP",
        )
        segment = CustomerSegment.objects.create(
            name="OrTest",
            rules={
                "operator": "or",
                "conditions": [
                    {"field": "status", "operator": "eq", "value": "active"},
                    {"field": "customer_type", "operator": "eq", "value": "VIP"},
                ],
            },
        )
        assert CustomerSegmentService.evaluate_customer(customer, segment) is True


# ═══════════════════════════════════════════════════════════════════
# DuplicateDetectionService
# ═══════════════════════════════════════════════════════════════════


class TestDuplicateDetectionService:

    def test_find_duplicate_by_email(self):
        Customer.objects.create(
            first_name="D", last_name="E", email="dup@test.com"
        )
        qs = DuplicateDetectionService.find_duplicate_by_email("dup@test.com")
        assert qs.count() == 1

    def test_find_duplicate_by_email_case_insensitive(self):
        Customer.objects.create(
            first_name="D", last_name="E", email="DUP@TEST.COM"
        )
        qs = DuplicateDetectionService.find_duplicate_by_email("dup@test.com")
        assert qs.count() == 1

    def test_find_duplicates_by_email_match(self):
        c1 = Customer.objects.create(
            first_name="A", last_name="B", email="same@test.com"
        )
        Customer.objects.create(
            first_name="C", last_name="D", email="same@test.com"
        )
        matches = DuplicateDetectionService.find_duplicates(c1, min_score=50)
        assert len(matches) >= 1
        assert matches[0].score >= 90

    def test_merge_customers(self):
        primary = Customer.objects.create(
            first_name="Primary", last_name="M",
            total_purchases=10000, total_payments=5000,
            outstanding_balance=5000, order_count=5,
        )
        duplicate = Customer.objects.create(
            first_name="Dup", last_name="M",
            total_purchases=3000, total_payments=2000,
            outstanding_balance=1000, order_count=2,
        )
        merge = DuplicateDetectionService.merge_customers(
            primary, duplicate, merge_reason="Test merge"
        )
        assert merge.pk is not None
        primary.refresh_from_db()
        duplicate.refresh_from_db()
        assert primary.total_purchases == 13000
        assert primary.order_count == 7
        assert duplicate.is_deleted is True
        assert duplicate.status == "archived"

    def test_get_merge_preview(self):
        primary = Customer.objects.create(first_name="P", last_name="V")
        duplicate = Customer.objects.create(first_name="D", last_name="V")
        preview = DuplicateDetectionService.get_merge_preview(primary, duplicate)
        assert "orders_to_transfer" in preview


# ═══════════════════════════════════════════════════════════════════
# SearchService
# ═══════════════════════════════════════════════════════════════════


class TestSearchService:

    def test_search_by_name(self):
        Customer.objects.create(first_name="Searchable", last_name="Name")
        results = CustomerSearchService.search("Searchable")
        assert results.count() >= 1

    def test_search_by_email(self):
        Customer.objects.create(
            first_name="E", last_name="S", email="searchme@example.com"
        )
        results = CustomerSearchService.search("searchme@example.com")
        assert results.count() >= 1

    def test_quick_search_code(self):
        c = Customer.objects.create(first_name="QS", last_name="T")
        results = CustomerSearchService.quick_search(c.customer_code)
        assert results.count() >= 1

    def test_lookup_by_email(self):
        Customer.objects.create(
            first_name="L", last_name="E", email="lookup@example.com"
        )
        results = CustomerSearchService.lookup_by_email("lookup@example.com")
        assert results.count() >= 1


# ═══════════════════════════════════════════════════════════════════
# ImportService
# ═══════════════════════════════════════════════════════════════════


class TestImportService:

    def test_auto_detect_mapping(self):
        headers = ["First Name", "Last Name", "Email", "Phone"]
        mapping = CustomerImportService.auto_detect_mapping(headers)
        # Normalisation maps "First Name" → first_name
        assert mapping["First Name"] == "first_name"
        assert mapping["Email"] == "email"
        # Underscore-separated versions also work
        headers2 = ["first_name", "last_name", "email", "phone"]
        mapping2 = CustomerImportService.auto_detect_mapping(headers2)
        assert mapping2["first_name"] == "first_name"
        assert mapping2["email"] == "email"

    def test_validate_row_valid(self):
        result = CustomerImportService.validate_row(
            {"first_name": "John", "email": "john@test.com"},
            row_number=1,
        )
        assert result["valid"] is True

    def test_validate_row_invalid_email(self):
        result = CustomerImportService.validate_row(
            {"email": "not-an-email"},
            row_number=1,
        )
        assert result["valid"] is False

    def test_import_from_csv(self):
        csv_content = "first_name,last_name,email,status\nJohn,Doe,jd@test.com,active\nJane,Smith,js@test.com,active\n"
        csv_file = io.StringIO(csv_content)
        summary = CustomerImportService.import_from_csv(csv_file)
        assert summary["total_rows"] == 2
        assert summary["successful"] == 2
        assert summary["failed"] == 0

    def test_import_skip_invalid(self):
        csv_content = "first_name,last_name,email,customer_type\nA,B,a@b.com,INVALID_TYPE\nC,D,c@d.com,INDIVIDUAL\n"
        csv_file = io.StringIO(csv_content)
        summary = CustomerImportService.import_from_csv(csv_file, mode="skip_invalid")
        assert summary["failed"] == 1
        assert summary["successful"] == 1

    def test_import_strict_mode_fails(self):
        csv_content = "first_name,last_name,email,customer_type\nA,B,a@b.com,BAD\n"
        csv_file = io.StringIO(csv_content)
        with pytest.raises(ValueError):
            CustomerImportService.import_from_csv(csv_file, mode="strict")


# ═══════════════════════════════════════════════════════════════════
# ExportService
# ═══════════════════════════════════════════════════════════════════


class TestExportService:

    def test_export_to_csv_default_columns(self):
        Customer.objects.create(
            first_name="Export", last_name="Test", email="exp@test.com"
        )
        qs = Customer.objects.filter(is_deleted=False)
        csv_output = CustomerExportService.export_to_csv(qs)
        assert "Customer Code" in csv_output
        assert "Export" in csv_output

    def test_export_to_csv_custom_columns(self):
        Customer.objects.create(first_name="X", last_name="Y")
        qs = Customer.objects.filter(is_deleted=False)
        csv_output = CustomerExportService.export_to_csv(
            qs, columns=["customer_code", "first_name"]
        )
        assert "Customer Code" in csv_output
        assert "Email" not in csv_output

    def test_export_no_headers(self):
        Customer.objects.create(first_name="N", last_name="H")
        qs = Customer.objects.filter(is_deleted=False)
        csv_output = CustomerExportService.export_to_csv(
            qs, include_headers=False
        )
        assert "Customer Code" not in csv_output

    def test_get_available_columns(self):
        cols = CustomerExportService.get_available_columns()
        assert len(cols) > 0
        assert any(c["field"] == "customer_code" for c in cols)
