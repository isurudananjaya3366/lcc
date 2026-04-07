"""Catalog service for managing vendor product catalog."""

from django.db import transaction


class CatalogService:
    """Service for vendor product catalog operations."""

    @staticmethod
    def add_product_to_vendor(vendor_id, product_id, data=None):
        """Link a product to a vendor with pricing details."""
        from apps.vendors.models import Vendor, VendorProduct

        vendor = Vendor.objects.get(id=vendor_id)
        if vendor.status != "active":
            raise ValueError("Can only add products to active vendors.")

        if VendorProduct.objects.filter(vendor_id=vendor_id, product_id=product_id).exists():
            raise ValueError("Product already linked to this vendor.")

        product_data = data or {}
        product_data["vendor_id"] = vendor_id
        product_data["product_id"] = product_id
        return VendorProduct.objects.create(**product_data)

    @staticmethod
    def update_vendor_product(vendor_product_id, update_data):
        """Update a vendor product's pricing and terms."""
        from apps.vendors.models import VendorProduct

        vp = VendorProduct.objects.get(id=vendor_product_id)

        # Track price changes
        if "unit_cost" in update_data and update_data["unit_cost"] != vp.unit_cost:
            vp.last_cost = vp.unit_cost

        for key, value in update_data.items():
            setattr(vp, key, value)
        vp.save()
        return vp

    @staticmethod
    def remove_product_from_vendor(vendor_product_id):
        """Deactivate a vendor product link."""
        from apps.vendors.models import VendorProduct

        vp = VendorProduct.objects.get(id=vendor_product_id)
        vp.is_active = False
        vp.save(update_fields=["is_active", "updated_on"])
        return vp

    @staticmethod
    def get_vendor_products(vendor_id, active_only=True):
        """Get all products supplied by a vendor."""
        from apps.vendors.models import VendorProduct

        qs = VendorProduct.objects.filter(vendor_id=vendor_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.select_related("product")

    @staticmethod
    def get_product_vendors(product_id, active_only=True):
        """Get all vendors that supply a product."""
        from apps.vendors.models import VendorProduct

        qs = VendorProduct.objects.filter(product_id=product_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.select_related("vendor")

    @staticmethod
    def get_preferred_vendor(product_id):
        """Get the preferred vendor for a product based on multiple criteria."""
        from apps.vendors.models import VendorProduct

        vps = VendorProduct.objects.filter(
            product_id=product_id,
            is_active=True,
            vendor__status="active",
            vendor__is_deleted=False,
        ).select_related("vendor")

        if not vps.exists():
            return None

        # 1. Check is_preferred
        preferred = vps.filter(is_preferred=True)
        if preferred.count() == 1:
            return preferred.first()

        # 2. If multiple preferred or none, sort by criteria
        candidates = preferred if preferred.exists() else vps
        best = candidates.order_by("unit_cost", "lead_time_days", "-vendor__rating").first()
        return best

    @staticmethod
    def compare_prices(product_id):
        """Compare prices across all vendors for a product."""
        from apps.vendors.models import VendorProduct

        vps = VendorProduct.objects.filter(
            product_id=product_id,
            is_active=True,
            vendor__status="active",
            vendor__is_deleted=False,
        ).select_related("vendor").order_by("unit_cost")

        return [
            {
                "vendor_id": str(vp.vendor_id),
                "vendor_name": vp.vendor.company_name,
                "vendor_code": vp.vendor.vendor_code,
                "unit_cost": vp.unit_cost,
                "bulk_price": vp.bulk_price,
                "bulk_qty": vp.bulk_qty,
                "min_order_qty": vp.min_order_qty,
                "lead_time_days": vp.lead_time_days,
                "currency": vp.currency,
                "is_preferred": vp.is_preferred,
                "vendor_rating": vp.vendor.rating,
            }
            for vp in vps
        ]
