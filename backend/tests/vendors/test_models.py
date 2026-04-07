"""Tests for vendor models."""

from decimal import Decimal

import pytest
from django.core.files.base import ContentFile

pytestmark = pytest.mark.django_db


class TestVendorModel:
    """Test Vendor model."""

    def test_create_vendor(self, vendor):
        assert vendor.pk is not None
        assert vendor.company_name == "Test Vendor Co"
        assert vendor.vendor_type == "manufacturer"
        assert vendor.status == "active"

    def test_vendor_code_auto_generated(self, vendor):
        assert vendor.vendor_code is not None
        assert vendor.vendor_code.startswith("VND-")

    def test_vendor_str_with_code(self, vendor):
        result = str(vendor)
        assert vendor.vendor_code in result
        assert vendor.company_name in result

    def test_vendor_str_without_code(self, tenant_context):
        from apps.vendors.models import Vendor

        v = Vendor.__new__(Vendor)
        v.vendor_code = ""
        v.company_name = "No Code Vendor"
        assert str(v) == "No Code Vendor"

    def test_vendor_soft_delete_fields(self, vendor):
        assert vendor.is_deleted is False
        assert vendor.deleted_on is None

    def test_vendor_timestamps(self, vendor):
        assert vendor.created_on is not None
        assert vendor.updated_on is not None

    def test_vendor_default_status(self, tenant_context):
        from apps.vendors.models import Vendor

        v = Vendor.objects.create(
            company_name="Default Status Vendor", vendor_type="manufacturer"
        )
        assert v.status == "pending_approval"
        assert v.vendor_code is not None

    def test_vendor_meta_db_table(self):
        from apps.vendors.models import Vendor

        assert Vendor._meta.db_table == "vendors_vendor"

    def test_vendor_update(self, vendor):
        vendor.company_name = "Updated Vendor Co"
        vendor.save(update_fields=["company_name"])
        vendor.refresh_from_db()
        assert vendor.company_name == "Updated Vendor Co"

    def test_vendor_uuid_pk(self, vendor):
        import uuid

        assert isinstance(vendor.pk, uuid.UUID)

    def test_vendor_full_address_property(self, tenant_context):
        from apps.vendors.models import Vendor

        v = Vendor.objects.create(
            company_name="Address Vendor",
            vendor_type="manufacturer",
            address_line_1="10 Main St",
            city="Kandy",
            province="Central",
            country="Sri Lanka",
        )
        full = v.full_address
        assert "10 Main St" in full
        assert "Kandy" in full
        assert "Sri Lanka" in full

    def test_vendor_credit_limit(self, vendor):
        assert vendor.credit_limit == Decimal("100000.00")

    def test_vendor_with_user(self, vendor_with_user, user):
        assert vendor_with_user.created_by == user
        assert vendor_with_user.company_name == "Test Vendor With User"


class TestVendorContactModel:
    """Test VendorContact model."""

    def test_create_contact(self, vendor_contact):
        assert vendor_contact.pk is not None
        assert vendor_contact.first_name == "John"
        assert vendor_contact.last_name == "Doe"

    def test_contact_full_name(self, vendor_contact):
        assert vendor_contact.full_name == "John Doe"

    def test_contact_str(self, vendor_contact):
        result = str(vendor_contact)
        assert "John" in result
        assert "Doe" in result

    def test_contact_vendor_relationship(self, vendor_contact, vendor):
        assert vendor_contact.vendor == vendor
        assert vendor.contacts.count() == 1

    def test_contact_is_primary(self, vendor_contact):
        assert vendor_contact.is_primary is True

    def test_contact_meta_db_table(self):
        from apps.vendors.models import VendorContact

        assert VendorContact._meta.db_table == "vendors_vendor_contact"


class TestVendorBankAccountModel:
    """Test VendorBankAccount model."""

    def test_create_bank_account(self, vendor_bank):
        assert vendor_bank.pk is not None
        assert vendor_bank.bank_name == "Test Bank"

    def test_bank_str(self, vendor_bank):
        result = str(vendor_bank)
        assert "Test Bank" in result
        assert "1234567890" in result

    def test_bank_vendor_relationship(self, vendor_bank, vendor):
        assert vendor_bank.vendor == vendor
        assert vendor.bank_accounts.count() == 1

    def test_bank_is_default(self, vendor_bank):
        assert vendor_bank.is_default is True

    def test_bank_meta_db_table(self):
        from apps.vendors.models import VendorBankAccount

        assert VendorBankAccount._meta.db_table == "vendors_vendor_bank_account"


class TestVendorAddressModel:
    """Test VendorAddress model."""

    def test_create_address(self, vendor_address):
        assert vendor_address.pk is not None
        assert vendor_address.city == "Colombo"

    def test_address_full_address(self, vendor_address):
        full = vendor_address.full_address
        assert "123 Test Street" in full
        assert "Colombo" in full

    def test_address_str(self, vendor_address):
        result = str(vendor_address)
        assert "Colombo" in result

    def test_address_is_default(self, vendor_address):
        assert vendor_address.is_default is True

    def test_address_meta_db_table(self):
        from apps.vendors.models import VendorAddress

        assert VendorAddress._meta.db_table == "vendors_vendor_address"


class TestVendorDocumentModel:
    """Test VendorDocument model."""

    def test_create_document(self, vendor, tenant_context):
        from apps.vendors.models import VendorDocument

        dummy_file = ContentFile(b"test content", name="test_contract.pdf")
        doc = VendorDocument.objects.create(
            vendor=vendor,
            document_type="contract",
            name="Test Contract",
            file=dummy_file,
        )
        assert doc.pk is not None
        assert doc.document_type == "contract"
        assert doc.name == "Test Contract"

    def test_document_str(self, vendor, tenant_context):
        from apps.vendors.models import VendorDocument

        dummy_file = ContentFile(b"license content", name="business_license.pdf")
        doc = VendorDocument.objects.create(
            vendor=vendor,
            document_type="license",
            name="Business License",
            file=dummy_file,
        )
        assert "Business License" in str(doc)

    def test_document_meta_db_table(self):
        from apps.vendors.models import VendorDocument

        assert VendorDocument._meta.db_table == "vendors_vendor_document"


class TestVendorHistoryModel:
    """Test VendorHistory model."""

    def test_create_history(self, vendor, tenant_context):
        from apps.vendors.models import VendorHistory

        h = VendorHistory.objects.create(
            vendor=vendor,
            field_name="status",
            old_value="pending_approval",
            new_value="active",
            change_type="update",
        )
        assert h.pk is not None
        assert h.field_name == "status"
        assert h.changed_at is not None

    def test_history_str(self, vendor, tenant_context):
        from apps.vendors.models import VendorHistory

        h = VendorHistory.objects.create(
            vendor=vendor,
            field_name="company_name",
            old_value="Old Name",
            new_value="New Name",
            change_type="update",
        )
        result = str(h)
        assert "company_name" in result

    def test_history_meta_db_table(self):
        from apps.vendors.models import VendorHistory

        assert VendorHistory._meta.db_table == "vendors_vendor_history"


class TestVendorCommunicationModel:
    """Test VendorCommunication model."""

    def test_create_communication(self, vendor, tenant_context):
        from django.utils import timezone
        from apps.vendors.models import VendorCommunication

        comm = VendorCommunication.objects.create(
            vendor=vendor,
            communication_type="email",
            subject="Test Subject",
            content="Test content body",
            contact_date=timezone.now(),
        )
        assert comm.pk is not None
        assert comm.subject == "Test Subject"

    def test_communication_str(self, vendor, tenant_context):
        from django.utils import timezone
        from apps.vendors.models import VendorCommunication

        comm = VendorCommunication.objects.create(
            vendor=vendor,
            communication_type="phone",
            subject="Phone Call",
            contact_date=timezone.now(),
        )
        result = str(comm)
        assert "Phone Call" in result

    def test_communication_meta_db_table(self):
        from apps.vendors.models import VendorCommunication

        assert VendorCommunication._meta.db_table == "vendors_vendor_communication"
