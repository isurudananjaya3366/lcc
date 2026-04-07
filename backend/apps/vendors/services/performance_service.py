"""Performance service for calculating vendor metrics."""

from decimal import Decimal

from django.utils import timezone


class PerformanceService:
    """Service for calculating and recording vendor performance metrics."""

    @staticmethod
    def calculate_delivery_rate(vendor_id, period_start, period_end):
        """Calculate on-time delivery rate for a vendor in a period."""
        from apps.vendors.models import VendorPerformance

        perf = VendorPerformance.objects.filter(
            vendor_id=vendor_id,
            period_start=period_start,
            period_end=period_end,
        ).first()

        if not perf or perf.total_orders_count == 0:
            return Decimal("0.00")
        return Decimal(perf.orders_on_time) / Decimal(perf.total_orders_count) * 100

    @staticmethod
    def calculate_quality_score(vendor_id, period_start, period_end):
        """Calculate quality score for a vendor in a period."""
        from apps.vendors.models import VendorPerformance

        perf = VendorPerformance.objects.filter(
            vendor_id=vendor_id,
            period_start=period_start,
            period_end=period_end,
        ).first()

        if not perf or perf.items_received == 0:
            return Decimal("0.00")
        good_items = perf.items_received - perf.items_defective
        return Decimal(good_items) / Decimal(perf.items_received) * 100

    @staticmethod
    def calculate_response_time(vendor_id, period_start, period_end):
        """Get average response time for a vendor in a period."""
        from apps.vendors.models import VendorPerformance

        perf = VendorPerformance.objects.filter(
            vendor_id=vendor_id,
            period_start=period_start,
            period_end=period_end,
        ).first()

        if not perf:
            return Decimal("0.00")
        return perf.avg_response_time_hours

    @staticmethod
    def calculate_overall_rating(vendor_id, period_start, period_end):
        """
        Calculate overall vendor rating (0-5 scale).
        Weighted: 40% delivery + 30% quality + 15% response + 15% price.
        """
        from apps.vendors.models import VendorPerformance

        perf = VendorPerformance.objects.filter(
            vendor_id=vendor_id,
            period_start=period_start,
            period_end=period_end,
        ).first()

        if not perf:
            return Decimal("0.00")

        delivery = perf.on_time_delivery_rate / Decimal("20")  # 0-5 scale
        quality = perf.quality_score / Decimal("20")
        # Response time: lower is better, cap at 5
        if perf.avg_response_time_hours > 0:
            response_score = max(
                Decimal("0"),
                Decimal("5") - perf.avg_response_time_hours / Decimal("24"),
            )
        else:
            response_score = Decimal("5.00")
        # Price competitiveness: placeholder score (5.0 = best price)
        price_score = Decimal("3.00")

        overall = (
            delivery * Decimal("0.40")
            + quality * Decimal("0.30")
            + response_score * Decimal("0.15")
            + price_score * Decimal("0.15")
        )
        return min(Decimal("5.00"), round(overall, 2))

    @staticmethod
    def record_performance(vendor_id, period_start, period_end, metrics, user=None):
        """Create or update a vendor performance record."""
        from apps.vendors.models import VendorPerformance

        perf, _ = VendorPerformance.objects.update_or_create(
            vendor_id=vendor_id,
            period_start=period_start,
            period_end=period_end,
            defaults={
                **metrics,
                "calculated_at": timezone.now(),
                "calculated_by": user,
            },
        )
        return perf

    @staticmethod
    def update_vendor_rating(vendor_id):
        """Update the denormalized rating on the Vendor model from latest performance."""
        from apps.vendors.models import Vendor, VendorPerformance

        latest = VendorPerformance.objects.filter(vendor_id=vendor_id).order_by("-period_end").first()
        if latest:
            Vendor.objects.filter(id=vendor_id).update(
                rating=latest.overall_rating,
                last_rating_update=timezone.now(),
            )
