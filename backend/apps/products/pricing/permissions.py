"""
Pricing-specific permission classes.
"""

from rest_framework.permissions import BasePermission


class HasPricingPermission(BasePermission):
    """
    Grants access to users who have the ``manage_pricing`` permission
    (from ProductPrice Meta).  Read-only access is allowed for any
    authenticated user.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Safe methods (GET, HEAD, OPTIONS) require only authentication
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        # Write methods require the manage_pricing permission
        return (
            request.user.is_superuser
            or request.user.has_perm("pricing.manage_pricing")
        )


class CanViewCostPrice(BasePermission):
    """Restrict cost-price visibility to users with ``view_cost_price``."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser
            or request.user.has_perm("pricing.view_cost_price")
        )


class CanCreatePromotions(BasePermission):
    """Allow promotion creation for users with ``create_promotions``."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return (
            request.user.is_superuser
            or request.user.has_perm("pricing.create_promotions")
        )
