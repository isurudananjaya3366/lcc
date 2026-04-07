"""Communication service for logging vendor interactions."""

from django.utils import timezone

from apps.vendors.constants import COMMUNICATION_TYPE_CHOICES


class CommunicationService:
    """Service for managing vendor communications."""

    @staticmethod
    def log_communication(vendor_id, data):
        """Log a new vendor communication with validation."""
        from apps.vendors.models import Vendor, VendorCommunication

        # Validate vendor exists
        if not Vendor.objects.filter(pk=vendor_id).exists():
            raise ValueError(f"Vendor with id {vendor_id} does not exist.")

        # Validate communication type if provided
        valid_types = [choice[0] for choice in COMMUNICATION_TYPE_CHOICES]
        comm_type = data.get("communication_type")
        if comm_type and comm_type not in valid_types:
            raise ValueError(
                f"Invalid communication type '{comm_type}'. Must be one of: {valid_types}"
            )

        # Validate contacted_by is a User instance if provided
        contacted_by = data.get("contacted_by")
        if contacted_by is not None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not isinstance(contacted_by, User):
                raise ValueError("contacted_by must be a User instance.")

        return VendorCommunication.objects.create(vendor_id=vendor_id, **data)

    @staticmethod
    def get_communication_timeline(
        vendor_id,
        limit=50,
        date_from=None,
        date_to=None,
        comm_type=None,
        user=None,
        follow_up_status=None,
    ):
        """Get chronological communication history for a vendor with filters."""
        from apps.vendors.models import VendorCommunication

        qs = VendorCommunication.objects.filter(
            vendor_id=vendor_id,
        ).select_related("contacted_by")

        if date_from:
            qs = qs.filter(contact_date__gte=date_from)
        if date_to:
            qs = qs.filter(contact_date__lte=date_to)
        if comm_type:
            qs = qs.filter(communication_type=comm_type)
        if user:
            qs = qs.filter(contacted_by=user)
        if follow_up_status == "pending":
            qs = qs.filter(
                follow_up_date__isnull=False,
                is_follow_up_complete=False,
            )
        elif follow_up_status == "complete":
            qs = qs.filter(is_follow_up_complete=True)

        return qs.order_by("-contact_date")[:limit]

    @staticmethod
    def get_pending_follow_ups():
        """Get all communications with pending follow-ups."""
        from apps.vendors.models import VendorCommunication

        today = timezone.now().date()
        return VendorCommunication.objects.filter(
            follow_up_date__lte=today,
            is_follow_up_complete=False,
        ).select_related("vendor", "contacted_by").order_by("follow_up_date")
