"""
Users API URL configuration.

Registers routed viewsets and standalone views for the users API.
"""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.api.views import (
    LoginHistoryViewSet,
    MeView,
    PermissionViewSet,
    RoleViewSet,
    UserPreferencesViewSet,
    UserProfileViewSet,
    UserRoleViewSet,
)

app_name = "users"

router = DefaultRouter()
router.register("profiles", UserProfileViewSet)
router.register("preferences", UserPreferencesViewSet)
router.register("roles", RoleViewSet)
router.register("permissions", PermissionViewSet)
router.register("login-history", LoginHistoryViewSet)
router.register("user-roles", UserRoleViewSet)

urlpatterns = [
    path("me/", MeView.as_view(), name="user-me"),
    path("", include(router.urls)),
]
