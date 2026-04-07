"""
Permission decorators for view-level access control.

Provides function-based view decorators that enforce RBAC checks
against the user's assigned roles and permissions.

Usage::

    @require_permission("orders.create")
    def create_order(request):
        ...

    @require_any_permission("reports.view", "reports.export")
    def view_reports(request):
        ...

    @require_all_permissions("orders.view", "orders.export")
    def export_orders(request):
        ...

    @require_role("admin")
    def admin_dashboard(request):
        ...
"""

from __future__ import annotations

import functools

from django.http import JsonResponse


def require_permission(permission_codename: str):
    """
    Decorator that checks if the user has a specific permission via
    their roles.

    Returns 401 if unauthenticated, 403 if the permission is missing.
    Superusers bypass all permission checks.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required"}, status=401
                )
            # Superuser bypass
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            # Check via UserProfile roles
            profile = getattr(user, "profile", None)
            if profile and hasattr(profile, "roles"):
                has_perm = profile.roles.filter(
                    permissions__codename=permission_codename,
                    is_deleted=False,
                ).exists()
                if has_perm:
                    return view_func(request, *args, **kwargs)
            return JsonResponse(
                {"error": "Permission denied", "required": permission_codename},
                status=403,
            )

        return wrapper

    return decorator


def require_any_permission(*permission_codenames: str):
    """
    Decorator that checks if the user has **any** of the specified
    permissions.

    Returns 401 if unauthenticated, 403 if none of the permissions
    are present.  Superusers bypass all permission checks.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required"}, status=401
                )
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            profile = getattr(user, "profile", None)
            if profile and hasattr(profile, "roles"):
                has_perm = profile.roles.filter(
                    permissions__codename__in=permission_codenames,
                    is_deleted=False,
                ).exists()
                if has_perm:
                    return view_func(request, *args, **kwargs)
            return JsonResponse(
                {
                    "error": "Permission denied",
                    "required_any": list(permission_codenames),
                },
                status=403,
            )

        return wrapper

    return decorator


def require_all_permissions(*permission_codenames: str):
    """
    Decorator that checks if the user has **all** of the specified
    permissions.

    Returns 401 if unauthenticated, 403 (with the first missing
    permission) if any are absent.  Superusers bypass all checks.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required"}, status=401
                )
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            profile = getattr(user, "profile", None)
            if profile and hasattr(profile, "roles"):
                for codename in permission_codenames:
                    has_perm = profile.roles.filter(
                        permissions__codename=codename,
                        is_deleted=False,
                    ).exists()
                    if not has_perm:
                        return JsonResponse(
                            {"error": "Permission denied", "missing": codename},
                            status=403,
                        )
                return view_func(request, *args, **kwargs)
            return JsonResponse(
                {"error": "Permission denied"}, status=403
            )

        return wrapper

    return decorator


def require_role(role_slug: str):
    """
    Decorator that checks if the user has a specific role (by slug).

    Returns 401 if unauthenticated, 403 if the role is missing.
    Superusers bypass the check.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required"}, status=401
                )
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            profile = getattr(user, "profile", None)
            if profile and hasattr(profile, "roles"):
                has_role = profile.roles.filter(
                    slug=role_slug, is_deleted=False
                ).exists()
                if has_role:
                    return view_func(request, *args, **kwargs)
            return JsonResponse(
                {"error": "Role required", "required_role": role_slug},
                status=403,
            )

        return wrapper

    return decorator
