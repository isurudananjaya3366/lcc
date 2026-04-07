"""
Users API views.

ViewSets and views for user profiles, preferences, roles,
permissions, login history, role assignments, and current user.
"""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import (
    LoginHistorySerializer,
    PermissionSerializer,
    RoleListSerializer,
    RoleSerializer,
    UserPreferencesSerializer,
    UserProfileListSerializer,
    UserProfileSerializer,
    UserRoleSerializer,
)
from apps.users.models import (
    LoginHistory,
    Permission,
    Role,
    UserPreferences,
    UserProfile,
    UserRole,
)


# ── UserProfile ──────────────────────────────────────────────────────


@extend_schema_view(
    list=extend_schema(summary="List user profiles"),
    retrieve=extend_schema(summary="Retrieve a user profile"),
    create=extend_schema(summary="Create a user profile"),
    update=extend_schema(summary="Update a user profile"),
    partial_update=extend_schema(summary="Partially update a user profile"),
    destroy=extend_schema(summary="Delete a user profile"),
)
class UserProfileViewSet(viewsets.ModelViewSet):
    """CRUD operations for user profiles."""

    queryset = UserProfile.objects.select_related("user").prefetch_related("roles")
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department", "is_active"]
    search_fields = ["display_name", "job_title", "department"]
    ordering_fields = ["display_name", "created_on"]
    ordering = ["display_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return UserProfileListSerializer
        return UserProfileSerializer


# ── UserPreferences ──────────────────────────────────────────────────


@extend_schema_view(
    retrieve=extend_schema(summary="Retrieve user preferences"),
    update=extend_schema(summary="Update user preferences"),
    partial_update=extend_schema(summary="Partially update user preferences"),
)
class UserPreferencesViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Retrieve and update user preferences (auto-created by signal)."""

    queryset = UserPreferences.objects.select_related("user")
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]


# ── Role ─────────────────────────────────────────────────────────────


@extend_schema_view(
    list=extend_schema(summary="List roles"),
    retrieve=extend_schema(summary="Retrieve a role"),
    create=extend_schema(summary="Create a role"),
    update=extend_schema(summary="Update a role"),
    partial_update=extend_schema(summary="Partially update a role"),
    destroy=extend_schema(summary="Delete a role"),
)
class RoleViewSet(viewsets.ModelViewSet):
    """Full CRUD for roles."""

    queryset = Role.objects.prefetch_related("permissions")
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "created_on"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return RoleListSerializer
        return RoleSerializer


# ── Permission ───────────────────────────────────────────────────────


@extend_schema_view(
    list=extend_schema(summary="List permissions"),
    retrieve=extend_schema(summary="Retrieve a permission"),
    create=extend_schema(summary="Create a permission"),
    update=extend_schema(summary="Update a permission"),
    partial_update=extend_schema(summary="Partially update a permission"),
)
class PermissionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """List, retrieve, create, and update permissions."""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["resource", "is_active"]
    search_fields = ["codename", "name", "resource"]
    ordering_fields = ["resource", "action", "created_on"]
    ordering = ["resource", "action"]


# ── LoginHistory ─────────────────────────────────────────────────────


@extend_schema_view(
    list=extend_schema(summary="List login history"),
    retrieve=extend_schema(summary="Retrieve a login history entry"),
)
class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to login history for auditing."""

    queryset = LoginHistory.objects.select_related("user")
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["event_type", "user", "success"]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]


# ── UserRole ─────────────────────────────────────────────────────────


@extend_schema_view(
    create=extend_schema(summary="Assign a role to a user"),
    destroy=extend_schema(summary="Revoke a role from a user"),
)
class UserRoleViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Assign and revoke user roles."""

    queryset = UserRole.objects.select_related("user_profile", "role")
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user_profile", "role"]


# ── Me ───────────────────────────────────────────────────────────────


@extend_schema(tags=["users"])
class MeView(APIView):
    """Return or update the current authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get current user profile and preferences")
    def get(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        preferences = UserPreferences.objects.filter(user=request.user).first()

        data = {
            "profile": UserProfileSerializer(profile).data if profile else None,
            "preferences": (
                UserPreferencesSerializer(preferences).data if preferences else None
            ),
        }
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(summary="Update current user profile")
    def patch(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response(
                {"detail": "Profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
