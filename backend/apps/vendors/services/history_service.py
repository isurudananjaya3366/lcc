"""Vendor history service for tracking field-level changes."""


class VendorHistoryService:
    """Service class for vendor change history operations."""

    @staticmethod
    def record_change(vendor_id, field_name, old_value, new_value, change_type, changed_by=None):
        """Record a single field change for a vendor."""
        from apps.vendors.models import VendorHistory

        return VendorHistory.objects.create(
            vendor_id=vendor_id,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else "",
            new_value=str(new_value) if new_value is not None else "",
            change_type=change_type,
            changed_by=changed_by,
        )

    @staticmethod
    def record_creation(vendor, changed_by=None):
        """Record CREATE history entries for key fields of a new vendor."""
        from apps.vendors.models import VendorHistory
        from apps.vendors.constants import CHANGE_TYPE_CREATE

        key_fields = ["company_name", "vendor_type", "status"]
        records = []
        for field in key_fields:
            value = getattr(vendor, field, "")
            records.append(
                VendorHistory(
                    vendor=vendor,
                    field_name=field,
                    old_value="",
                    new_value=str(value) if value is not None else "",
                    change_type=CHANGE_TYPE_CREATE,
                    changed_by=changed_by,
                )
            )
        VendorHistory.objects.bulk_create(records)

    @staticmethod
    def get_vendor_history(vendor_id, field_name=None, limit=100):
        """Get history records for a vendor, optionally filtered by field."""
        from apps.vendors.models import VendorHistory

        qs = VendorHistory.objects.filter(vendor_id=vendor_id)
        if field_name:
            qs = qs.filter(field_name=field_name)
        return qs[:limit]

    @staticmethod
    def track_changes(vendor, old_data, changed_by=None):
        """Compare old_data dict with current vendor fields and record changes."""
        from apps.vendors.models import VendorHistory
        from apps.vendors.constants import CHANGE_TYPE_UPDATE

        records = []
        for field, old_value in old_data.items():
            new_value = getattr(vendor, field, None)
            if str(old_value) != str(new_value):
                records.append(
                    VendorHistory(
                        vendor=vendor,
                        field_name=field,
                        old_value=str(old_value) if old_value is not None else "",
                        new_value=str(new_value) if new_value is not None else "",
                        change_type=CHANGE_TYPE_UPDATE,
                        changed_by=changed_by,
                    )
                )
        if records:
            VendorHistory.objects.bulk_create(records)
