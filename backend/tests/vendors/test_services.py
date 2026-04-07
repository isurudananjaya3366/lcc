"""Tests for vendor services."""

import io
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


class TestVendorService:
    """Test VendorService."""

    def test_create_vendor(self, tenant_context):
        from apps.vendors.services.vendor_service import VendorService

        v = VendorService.create_vendor(
            {
                "company_name": "Service Created Vendor",
                "vendor_type": "wholesaler",
            }
        )
        assert v.pk is not None
        assert v.company_name == "Service Created Vendor"
        assert v.vendor_code.startswith("VND-")

    def test_create_vendor_with_contacts(self, tenant_context):
        from apps.vendors.services.vendor_service import VendorService

        v = VendorService.create_vendor(
            {"company_name": "Vendor With Contacts", "vendor_type": "manufacturer"},
            contacts=[
                {"first_name": "Alice", "last_name": "Smith", "role": "sales"},
            ],
        )
        assert v.pk is not None
        assert v.contacts.count() == 1

    def test_get_vendor(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        fetched = VendorService.get_vendor(vendor.pk)
        assert fetched.pk == vendor.pk
        assert fetched.company_name == vendor.company_name

    def test_update_vendor(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        updated = VendorService.update_vendor(
            vendor.pk, {"company_name": "Updated Via Service"}
        )
        assert updated.company_name == "Updated Via Service"

    def test_list_vendors(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        vendors = VendorService.list_vendors()
        assert vendors.count() >= 1

    def test_list_vendors_with_status_filter(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        vendors = VendorService.list_vendors(filters={"status": "active"})
        assert vendors.filter(pk=vendor.pk).exists()

    def test_list_vendors_with_type_filter(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        vendors = VendorService.list_vendors(
            filters={"vendor_type": "manufacturer"}
        )
        assert vendors.filter(pk=vendor.pk).exists()

    def test_deactivate_vendor(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        v = VendorService.deactivate_vendor(vendor.pk)
        assert v.status == "inactive"

    def test_activate_vendor(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        vendor.status = "inactive"
        vendor.save(update_fields=["status"])
        v = VendorService.activate_vendor(vendor.pk)
        assert v.status == "active"

    def test_block_vendor(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        v = VendorService.block_vendor(vendor.pk, reason="Quality issues")
        assert v.status == "blocked"
        assert "Quality issues" in v.internal_notes

    def test_approve_vendor(self, tenant_context):
        from apps.vendors.models import Vendor
        from apps.vendors.services.vendor_service import VendorService

        v = Vendor.objects.create(
            company_name="Pending Vendor",
            vendor_type="manufacturer",
            status="pending_approval",
        )
        approved = VendorService.approve_vendor(v.pk)
        assert approved.status == "active"
        assert approved.approved_at is not None

    def test_approve_non_pending_vendor_raises(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        with pytest.raises(ValueError, match="pending"):
            VendorService.approve_vendor(vendor.pk)

    def test_delete_vendor_soft(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        v = VendorService.delete_vendor(vendor.pk)
        assert v.is_deleted is True
        assert v.deleted_on is not None

    def test_add_contact(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        contact = VendorService.add_contact(
            vendor.pk,
            {"first_name": "Bob", "last_name": "Jones", "role": "accounts"},
        )
        assert contact.pk is not None
        assert contact.vendor == vendor

    def test_add_bank_account(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        bank = VendorService.add_bank_account(
            vendor.pk,
            {
                "bank_name": "Service Bank",
                "account_name": "Test",
                "account_number": "9999999",
            },
        )
        assert bank.pk is not None
        assert bank.vendor == vendor

    def test_add_address(self, vendor):
        from apps.vendors.services.vendor_service import VendorService

        addr = VendorService.add_address(
            vendor.pk,
            {
                "address_type": "shipping",
                "address_line_1": "50 Harbor Rd",
                "city": "Galle",
            },
        )
        assert addr.pk is not None
        assert addr.vendor == vendor


class TestCommunicationService:
    """Test CommunicationService."""

    def test_log_communication(self, vendor):
        from apps.vendors.services.communication_service import CommunicationService

        comm = CommunicationService.log_communication(
            vendor_id=vendor.pk,
            data={
                "communication_type": "email",
                "subject": "Test Subject",
                "content": "Test content",
                "contact_date": timezone.now(),
            },
        )
        assert comm.pk is not None
        assert comm.subject == "Test Subject"

    def test_get_communication_timeline(self, vendor):
        from apps.vendors.services.communication_service import CommunicationService

        CommunicationService.log_communication(
            vendor_id=vendor.pk,
            data={
                "communication_type": "phone",
                "subject": "Call",
                "contact_date": timezone.now(),
            },
        )
        timeline = CommunicationService.get_communication_timeline(vendor.pk)
        assert len(timeline) >= 1

    def test_get_pending_follow_ups(self, vendor):
        from apps.vendors.services.communication_service import CommunicationService

        CommunicationService.log_communication(
            vendor_id=vendor.pk,
            data={
                "communication_type": "email",
                "subject": "Follow-up needed",
                "contact_date": timezone.now(),
                "follow_up_date": date.today(),
            },
        )
        pending = CommunicationService.get_pending_follow_ups()
        assert pending.count() >= 1


class TestDocumentService:
    """Test DocumentService."""

    def test_upload_invalid_file_type(self, vendor):
        from apps.vendors.services.document_service import DocumentService

        mock_file = MagicMock()
        mock_file.name = "test.exe"
        mock_file.size = 1024
        with pytest.raises(ValueError, match="not allowed"):
            DocumentService.upload_document(
                vendor_id=vendor.pk,
                document_type="contract",
                name="Evil File",
                file=mock_file,
                uploaded_by=None,
            )

    def test_upload_file_too_large(self, vendor):
        from apps.vendors.services.document_service import DocumentService

        mock_file = MagicMock()
        mock_file.name = "big.pdf"
        mock_file.size = 20 * 1024 * 1024  # 20MB exceeds 10MB limit
        with pytest.raises(ValueError, match="exceeds maximum"):
            DocumentService.upload_document(
                vendor_id=vendor.pk,
                document_type="contract",
                name="Big File",
                file=mock_file,
                uploaded_by=None,
            )

    def test_get_expiring_documents(self, vendor):
        from django.core.files.base import ContentFile
        from apps.vendors.models import VendorDocument
        from apps.vendors.services.document_service import DocumentService

        dummy_file = ContentFile(b"expiring doc", name="expiring_license.pdf")
        VendorDocument.objects.create(
            vendor=vendor,
            document_type="license",
            name="Expiring License",
            file=dummy_file,
            expiry_date=date.today() + timedelta(days=15),
        )
        expiring = DocumentService.get_expiring_documents(days=30)
        assert expiring.count() >= 1

    def test_get_vendor_documents(self, vendor):
        from django.core.files.base import ContentFile
        from apps.vendors.models import VendorDocument
        from apps.vendors.services.document_service import DocumentService

        dummy_file = ContentFile(b"doc content", name="test.pdf")
        VendorDocument.objects.create(
            vendor=vendor,
            document_type="contract",
            name="Test Doc",
            file=dummy_file,
        )
        docs = DocumentService.get_vendor_documents(vendor.pk)
        assert docs.count() >= 1

    def test_get_vendor_documents_filtered(self, vendor):
        from django.core.files.base import ContentFile
        from apps.vendors.models import VendorDocument
        from apps.vendors.services.document_service import DocumentService

        dummy_file = ContentFile(b"cert content", name="cert.pdf")
        VendorDocument.objects.create(
            vendor=vendor,
            document_type="certificate",
            name="Cert",
            file=dummy_file,
        )
        docs = DocumentService.get_vendor_documents(
            vendor.pk, document_type="certificate"
        )
        assert docs.count() >= 1


class TestImportExportService:
    """Test import/export services."""

    def test_import_vendors_from_csv(self, tenant_context):
        from apps.vendors.services.import_service import VendorImportService

        csv_content = (
            "company_name,vendor_type,email,phone\n"
            "Imported Co,manufacturer,import@test.com,+94771234567\n"
        )
        csv_file = io.StringIO(csv_content)
        result = VendorImportService.import_vendors_from_csv(csv_file)
        assert result["total"] == 1
        assert result["created"] == 1
        assert result["failed"] == 0

    def test_import_missing_required_field(self, tenant_context):
        from apps.vendors.services.import_service import VendorImportService

        csv_content = "company_name,vendor_type\n,manufacturer\n"
        csv_file = io.StringIO(csv_content)
        result = VendorImportService.import_vendors_from_csv(csv_file)
        assert result["failed"] == 1

    def test_export_vendors_to_csv(self, vendor):
        from apps.vendors.services.export_service import VendorExportService

        output = VendorExportService.export_vendors_to_csv()
        content = output.getvalue()
        assert "vendor_code" in content
        assert "Test Vendor Co" in content

    @pytest.mark.skip(reason="Requires quotes module tables in tenant schema")
    def test_export_with_custom_fields(self, vendor):
        from apps.vendors.services.export_service import VendorExportService

        output = VendorExportService.export_vendors_to_csv(
            fields=["vendor_code", "company_name"]
        )
        content = output.getvalue()
        assert "vendor_code" in content
        assert "company_name" in content
