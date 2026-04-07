"""Vendor code auto-generation service."""


def generate_vendor_code() -> str:
    """Generate unique vendor code in format VND-NNNNN."""
    from django.db import transaction

    from apps.vendors.models import Vendor

    with transaction.atomic():
        last_vendor = (
            Vendor.objects.select_for_update()
            .filter(vendor_code__startswith="VND-")
            .order_by("-vendor_code")
            .first()
        )

        if last_vendor and last_vendor.vendor_code:
            try:
                last_num = int(last_vendor.vendor_code.split("-")[1])
            except (IndexError, ValueError):
                last_num = 0
        else:
            last_num = 0

        for attempt in range(10):
            next_num = last_num + 1 + attempt
            code = f"VND-{next_num:05d}"
            if not Vendor.objects.filter(vendor_code=code).exists():
                return code

        raise ValueError("Unable to generate unique vendor code after 10 attempts")
