"""
Customer model tests.

Tests for the Customer, CustomerAddress, CustomerPhone, CustomerTag,
CustomerSegment, CustomerMerge, CustomerImport, CustomerHistory,
CustomerSettings, and CustomerCommunication models.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.customers.models import (
    Customer,
    CustomerAddress,
    CustomerCommunication,
    CustomerHistory,
    CustomerImport,
    CustomerMerge,
    CustomerPhone,
    CustomerSegment,
    CustomerSettings,
    CustomerTag,
    CustomerTagAssignment,
)

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════
# Customer Model
# ═══════════════════════════════════════════════════════════════════


class TestCustomerModel:
    """Tests for the core Customer model."""

    def test_create_individual_customer(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Perera",
            customer_type="INDIVIDUAL",
            email="john@example.com",
        )
        assert customer.pk is not None
        assert customer.customer_code is not None
        assert customer.display_name == "John Perera"

    def test_create_business_customer(self):
        customer = Customer.objects.create(
            business_name="Test Corp",
            customer_type="BUSINESS",
            email="info@testcorp.com",
        )
        assert customer.pk is not None
        assert customer.customer_code is not None

    def test_customer_code_auto_generated(self):
        c1 = Customer.objects.create(first_name="A", last_name="B")
        c2 = Customer.objects.create(first_name="C", last_name="D")
        assert c1.customer_code != c2.customer_code
        assert c1.customer_code.startswith("CUST")

    def test_customer_full_name(self):
        customer = Customer(first_name="Jane", last_name="Silva")
        assert customer.full_name == "Jane Silva"

    def test_display_name_auto_populated(self):
        customer = Customer.objects.create(
            first_name="Mark",
            last_name="Fernando",
        )
        assert customer.display_name == "Mark Fernando"

    def test_customer_default_status(self):
        customer = Customer.objects.create(first_name="X", last_name="Y")
        assert customer.status == "active"

    def test_soft_delete_fields(self):
        customer = Customer.objects.create(first_name="Del", last_name="Test")
        assert customer.is_deleted is False
        assert customer.deleted_on is None

    def test_financial_defaults(self):
        customer = Customer.objects.create(first_name="Fin", last_name="Test")
        assert customer.total_purchases == 0
        assert customer.outstanding_balance == 0
        assert customer.order_count == 0


# ═══════════════════════════════════════════════════════════════════
# CustomerAddress Model
# ═══════════════════════════════════════════════════════════════════


class TestCustomerAddressModel:

    def test_create_address(self):
        customer = Customer.objects.create(first_name="A", last_name="B")
        address = CustomerAddress.objects.create(
            customer=customer,
            address_type="BILLING",
            address_line_1="123 Main St",
            city="Colombo",
        )
        assert address.pk is not None
        assert address.customer == customer

    def test_address_types(self):
        customer = Customer.objects.create(first_name="A", last_name="B")
        for atype in ["BILLING", "SHIPPING", "HOME", "WORK", "OTHER"]:
            addr = CustomerAddress.objects.create(
                customer=customer,
                address_type=atype,
                address_line_1=f"{atype} St",
            )
            assert addr.address_type == atype


# ═══════════════════════════════════════════════════════════════════
# CustomerPhone Model
# ═══════════════════════════════════════════════════════════════════


class TestCustomerPhoneModel:

    def test_create_phone(self):
        customer = Customer.objects.create(first_name="A", last_name="B")
        phone = CustomerPhone.objects.create(
            customer=customer,
            phone_type="MOBILE",
            phone_number="+94712345678",
            is_primary=True,
        )
        assert phone.pk is not None
        assert phone.is_primary is True

    def test_phone_types(self):
        customer = Customer.objects.create(first_name="A", last_name="B")
        for ptype in ["MOBILE", "LANDLINE", "WHATSAPP", "WORK", "OTHER"]:
            phone = CustomerPhone.objects.create(
                customer=customer,
                phone_type=ptype,
                phone_number="+94712345678",
            )
            assert phone.phone_type == ptype


# ═══════════════════════════════════════════════════════════════════
# CustomerTag & Assignment
# ═══════════════════════════════════════════════════════════════════


class TestCustomerTagModel:

    def test_create_tag(self):
        tag = CustomerTag.objects.create(name="VIP", color="#FFD700")
        assert tag.pk is not None
        assert tag.is_active is True

    def test_tag_name_unique(self):
        CustomerTag.objects.create(name="UniqueTag")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                CustomerTag.objects.create(name="UniqueTag")

    def test_assign_tag_to_customer(self):
        customer = Customer.objects.create(first_name="A", last_name="B")
        tag = CustomerTag.objects.create(name="Test")
        assignment = CustomerTagAssignment.objects.create(
            customer=customer, tag=tag
        )
        assert assignment.pk is not None

    def test_unique_customer_tag_assignment(self):
        customer = Customer.objects.create(first_name="A", last_name="B")
        tag = CustomerTag.objects.create(name="Dup")
        CustomerTagAssignment.objects.create(customer=customer, tag=tag)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                CustomerTagAssignment.objects.create(customer=customer, tag=tag)


# ═══════════════════════════════════════════════════════════════════
# CustomerSegment
# ═══════════════════════════════════════════════════════════════════


class TestCustomerSegmentModel:

    def test_create_segment(self):
        segment = CustomerSegment.objects.create(
            name="High Value",
            rules={
                "operator": "and",
                "conditions": [
                    {"field": "total_purchases", "operator": "gte", "value": 100000}
                ],
            },
        )
        assert segment.pk is not None
        assert segment.is_active is True

    def test_segment_name_unique(self):
        CustomerSegment.objects.create(name="Seg1")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                CustomerSegment.objects.create(name="Seg1")


# ═══════════════════════════════════════════════════════════════════
# CustomerMerge
# ═══════════════════════════════════════════════════════════════════


class TestCustomerMergeModel:

    def test_create_merge_record(self):
        primary = Customer.objects.create(first_name="Primary", last_name="A")
        duplicate = Customer.objects.create(first_name="Dup", last_name="B")
        merge = CustomerMerge.objects.create(
            primary_customer=primary,
            duplicate_customer=duplicate,
            duplicate_score=90,
        )
        assert merge.pk is not None
        assert merge.orders_transferred == 0


# ═══════════════════════════════════════════════════════════════════
# CustomerImport
# ═══════════════════════════════════════════════════════════════════


class TestCustomerImportModel:

    def test_create_import_record(self):
        imp = CustomerImport.objects.create(filename="test.csv")
        assert imp.pk is not None
        assert imp.status == "PENDING"
        assert imp.progress_percent == 0.0

    def test_progress_percent(self):
        imp = CustomerImport.objects.create(
            filename="test.csv",
            total_rows=100,
            processed_rows=45,
        )
        assert imp.progress_percent == 45.0


# ═══════════════════════════════════════════════════════════════════
# CustomerHistory
# ═══════════════════════════════════════════════════════════════════


class TestCustomerHistoryModel:

    def test_create_history(self):
        customer = Customer.objects.create(first_name="H", last_name="Test")
        history = CustomerHistory.objects.create(
            customer=customer,
            field_name="status",
            old_value="active",
            new_value="inactive",
            change_type="STATUS_CHANGE",
        )
        assert history.pk is not None
        assert history.changed_at is not None


# ═══════════════════════════════════════════════════════════════════
# CustomerSettings
# ═══════════════════════════════════════════════════════════════════


class TestCustomerSettingsModel:

    def test_create_settings(self):
        settings = CustomerSettings.objects.create()
        assert settings.pk is not None
        assert settings.customer_code_prefix == "CUST"

    def test_singleton_enforcement(self):
        CustomerSettings.objects.create()
        # Second save should update, not create duplicate
        settings2 = CustomerSettings()
        settings2.save()
        assert CustomerSettings.objects.count() == 1


# ═══════════════════════════════════════════════════════════════════
# CustomerCommunication
# ═══════════════════════════════════════════════════════════════════


class TestCustomerCommunicationModel:

    def test_create_communication(self):
        customer = Customer.objects.create(first_name="C", last_name="Test")
        comm = CustomerCommunication.objects.create(
            customer=customer,
            communication_type="EMAIL",
            subject="Welcome",
            content="Hello!",
        )
        assert comm.pk is not None
        assert comm.communication_date is not None
        assert comm.follow_up_completed is False
