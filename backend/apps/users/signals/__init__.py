"""
Users signals package.

Signal handlers for user-related events:
- Auto-create UserProfile and UserPreferences when a PlatformUser is created.
- Log authentication events (login success/failure) to LoginHistory.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger("apps.users.signals")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile_and_preferences(sender, instance, created, **kwargs):
    """
    Auto-create UserProfile and UserPreferences when a new user is created.

    This ensures every PlatformUser has a profile and preferences record
    available immediately after creation, avoiding NoneType errors in
    views and serializers.
    """
    if not created:
        return

    from apps.users.models import UserPreferences, UserProfile

    try:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                "display_name": getattr(instance, "full_name", "") or "",
            },
        )
        UserPreferences.objects.get_or_create(user=instance)
        logger.debug("Created profile & preferences for user %s", instance.pk)
    except Exception:
        logger.exception("Failed to create profile/preferences for user %s", instance.pk)


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    """Record a successful login in LoginHistory."""
    from apps.users.models import LoginHistory

    try:
        LoginHistory.objects.create(
            user=user,
            event_type="login_success",
            ip_address=_get_client_ip(request) if request else None,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500] if request else "",
            success=True,
        )
    except Exception:
        logger.exception("Failed to log successful login for user %s", getattr(user, "pk", "?"))


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Record a failed login attempt in LoginHistory."""
    from apps.users.models import LoginHistory

    # Try to resolve the user from the email (might not exist).
    from django.contrib.auth import get_user_model

    User = get_user_model()
    email = credentials.get("email") or credentials.get("username", "")
    user = None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        pass

    try:
        if user:
            LoginHistory.objects.create(
                user=user,
                event_type="login_failed",
                ip_address=_get_client_ip(request) if request else None,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500] if request else "",
                success=False,
                failure_reason=f"Invalid credentials for {email}",
            )
        else:
            logger.warning("Failed login attempt for unknown email: %s", email)
    except Exception:
        logger.exception("Failed to log failed login for email %s", email)


def _get_client_ip(request) -> str | None:
    """Extract client IP from request."""
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
