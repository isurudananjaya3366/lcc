"""Vendor service for CRUD operations and business logic."""

from django.db import transaction

from apps.vendors.constants import (
    VENDOR_STATUS_ACTIVE,
    VENDOR_STATUS_BLOCKED,
    VENDOR_STATUS_INACTIVE,
    VENDOR_STATUS_PENDING_APPROVAL,
)


class VendorService:
    """Service class for vendor operations."""

    @staticmethod
    def create_vendor(data, contacts=None, addresses=None, bank_accounts=None):
        """Create a new vendor with optional related data."""
        from apps.vendors.models import Vendor, VendorContact, VendorBankAccount, VendorAddress

        with transaction.atomic():
            vendor = Vendor.objects.create(**data)

            if contacts:
                for contact_data in contacts:
                    VendorContact.objects.create(vendor=vendor, **contact_data)

            if addresses:
                for address_data in addresses:
                    VendorAddress.objects.create(vendor=vendor, **address_data)

            if bank_accounts:
                for bank_data in bank_accounts:
                    VendorBankAccount.objects.create(vendor=vendor, **bank_data)

            return vendor

    @staticmethod
    def update_vendor(vendor_id, data):
        """Update an existing vendor."""
        from apps.vendors.models import Vendor

        vendor = Vendor.objects.get(id=vendor_id)
        for key, value in data.items():
            setattr(vendor, key, value)
        vendor.save()
        return vendor

    @staticmethod
    def get_vendor(vendor_id):
        """Get vendor by ID."""
        from apps.vendors.models import Vendor
        return Vendor.objects.get(id=vendor_id)

    @staticmethod
    def list_vendors(filters=None):
        """List vendors with optional filters."""
        from apps.vendors.models import Vendor

        qs = Vendor.objects.filter(is_deleted=False)
        if filters:
            if "status" in filters:
                qs = qs.filter(status=filters["status"])
            if "vendor_type" in filters:
                qs = qs.filter(vendor_type=filters["vendor_type"])
            if "search" in filters:
                qs = qs.filter(company_name__icontains=filters["search"])
            if "is_preferred" in filters:
                qs = qs.filter(is_preferred_vendor=filters["is_preferred"])
        return qs

    @staticmethod
    def activate_vendor(vendor_id):
        """Set vendor status to active."""
        from apps.vendors.models import Vendor

        vendor = Vendor.objects.get(id=vendor_id)
        vendor.status = VENDOR_STATUS_ACTIVE
        vendor.save(update_fields=["status", "updated_on"])
        return vendor

    @staticmethod
    def deactivate_vendor(vendor_id):
        """Set vendor status to inactive."""
        from apps.vendors.models import Vendor

        vendor = Vendor.objects.get(id=vendor_id)
        vendor.status = VENDOR_STATUS_INACTIVE
        vendor.save(update_fields=["status", "updated_on"])
        return vendor

    @staticmethod
    def block_vendor(vendor_id, reason=""):
        """Block a vendor."""
        from apps.vendors.models import Vendor

        vendor = Vendor.objects.get(id=vendor_id)
        vendor.status = VENDOR_STATUS_BLOCKED
        if reason:
            vendor.internal_notes = f"{vendor.internal_notes}\nBlocked: {reason}".strip()
        vendor.save(update_fields=["status", "internal_notes", "updated_on"])
        return vendor

    @staticmethod
    def approve_vendor(vendor_id, approver=None):
        """Approve a pending vendor."""
        from django.utils import timezone
        from apps.vendors.models import Vendor

        vendor = Vendor.objects.get(id=vendor_id)
        if vendor.status != VENDOR_STATUS_PENDING_APPROVAL:
            raise ValueError("Only pending vendors can be approved.")
        vendor.status = VENDOR_STATUS_ACTIVE
        vendor.approved_at = timezone.now()
        vendor.approved_by = approver
        vendor.save(update_fields=["status", "approved_at", "approved_by", "updated_on"])
        return vendor

    @staticmethod
    def delete_vendor(vendor_id):
        """Soft-delete a vendor."""
        from django.utils import timezone
        from apps.vendors.models import Vendor

        vendor = Vendor.objects.get(id=vendor_id)
        vendor.is_deleted = True
        vendor.deleted_on = timezone.now()
        vendor.save(update_fields=["is_deleted", "deleted_on", "updated_on"])
        return vendor

    @staticmethod
    def add_contact(vendor_id, contact_data):
        """Add a contact to a vendor."""
        from apps.vendors.models import Vendor, VendorContact
        vendor = Vendor.objects.get(id=vendor_id)
        return VendorContact.objects.create(vendor=vendor, **contact_data)

    @staticmethod
    def add_bank_account(vendor_id, bank_data):
        """Add a bank account to a vendor."""
        from apps.vendors.models import Vendor, VendorBankAccount
        vendor = Vendor.objects.get(id=vendor_id)
        return VendorBankAccount.objects.create(vendor=vendor, **bank_data)

    @staticmethod
    def add_address(vendor_id, address_data):
        """Add an address to a vendor."""
        from apps.vendors.models import Vendor, VendorAddress
        vendor = Vendor.objects.get(id=vendor_id)
        return VendorAddress.objects.create(vendor=vendor, **address_data)
