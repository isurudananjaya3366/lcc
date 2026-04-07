"""
Users managers package.

Provides custom managers and QuerySets for user-related models.
"""

from __future__ import annotations

from django.db import models


class LoginHistoryQuerySet(models.QuerySet):
    """Custom QuerySet for LoginHistory."""

    def successful(self) -> "LoginHistoryQuerySet":
        """Filter to successful authentication events only."""
        return self.filter(success=True)

    def failed(self) -> "LoginHistoryQuerySet":
        """Filter to failed authentication events only."""
        return self.filter(success=False)

    def logins(self) -> "LoginHistoryQuerySet":
        """Filter to login events (successful or failed)."""
        return self.filter(event_type__in=("login_success", "login_failed"))

    def for_user(self, user) -> "LoginHistoryQuerySet":
        """Filter to events for a specific user."""
        return self.filter(user=user)

    def for_ip(self, ip_address: str) -> "LoginHistoryQuerySet":
        """Filter to events from a specific IP address."""
        return self.filter(ip_address=ip_address)

    def recent(self, limit: int = 50) -> "LoginHistoryQuerySet":
        """Return the most recent N events."""
        return self.order_by("-timestamp")[:limit]


class LoginHistoryManager(models.Manager):
    """Manager for LoginHistory using LoginHistoryQuerySet."""

    def get_queryset(self) -> LoginHistoryQuerySet:
        return LoginHistoryQuerySet(self.model, using=self._db)

    def successful(self) -> LoginHistoryQuerySet:
        return self.get_queryset().successful()

    def failed(self) -> LoginHistoryQuerySet:
        return self.get_queryset().failed()

    def logins(self) -> LoginHistoryQuerySet:
        return self.get_queryset().logins()


class RoleQuerySet(models.QuerySet):
    """Custom QuerySet for Role."""

    def system_roles(self) -> "RoleQuerySet":
        """Filter to system-defined roles only."""
        return self.filter(is_system_role=True)

    def custom_roles(self) -> "RoleQuerySet":
        """Filter to tenant-defined (non-system) roles only."""
        return self.filter(is_system_role=False)

    def with_permission(self, codename: str) -> "RoleQuerySet":
        """Filter to roles that include the given permission codename."""
        return self.filter(permissions__codename=codename)

    def with_users(self) -> "RoleQuerySet":
        """Filter to roles that have at least one user assigned."""
        return self.filter(user_roles__isnull=False).distinct()


class RoleManager(models.Manager):
    """Manager for Role using RoleQuerySet."""

    def get_queryset(self) -> RoleQuerySet:
        return RoleQuerySet(self.model, using=self._db)

    def system_roles(self) -> RoleQuerySet:
        return self.get_queryset().system_roles()

    def custom_roles(self) -> RoleQuerySet:
        return self.get_queryset().custom_roles()

    def with_permission(self, codename: str) -> RoleQuerySet:
        return self.get_queryset().with_permission(codename)


__all__ = [
    "LoginHistoryQuerySet",
    "LoginHistoryManager",
    "RoleQuerySet",
    "RoleManager",
]
