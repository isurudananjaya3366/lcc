"""
Authentication views.

Provides JWT-based login, logout, token refresh, and current user endpoints
compatible with the frontend authService expectations.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def _user_data(user: object) -> dict:
    """Return a minimal user dict for API responses."""
    return {
        "id": str(user.pk),
        "email": getattr(user, "email", ""),
        "username": getattr(user, "username", ""),
        "firstName": getattr(user, "first_name", ""),
        "lastName": getattr(user, "last_name", ""),
        "isActive": getattr(user, "is_active", True),
        "isStaff": getattr(user, "is_staff", False),
    }


class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    Body: { "email": "...", "password": "..." }
    Returns: { "accessToken": "...", "refreshToken": "...", "user": {...} }
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login",
        description="Authenticate with email and password, receive JWT tokens.",
        request={"application/json": {"type": "object", "properties": {
            "email": {"type": "string"},
            "password": {"type": "string"},
        }, "required": ["email", "password"]}},
        responses={200: {"type": "object"}},
    )
    def post(self, request):
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Account is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "accessToken": str(refresh.access_token),
                "refreshToken": str(refresh),
                "user": _user_data(user),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Body: { "refreshToken": "..." }  (optional — blacklists the token if provided)
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Logout", description="Invalidate the refresh token.")
    def post(self, request):
        refresh_token = request.data.get("refreshToken")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass  # Token already expired/invalid — still a successful logout
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    """
    POST /api/v1/auth/refresh/
    Body: { "refreshToken": "..." }
    Returns: { "accessToken": "..." }
    """

    permission_classes = [AllowAny]

    @extend_schema(summary="Refresh token", description="Obtain a new access token using a refresh token.")
    def post(self, request):
        refresh_token = request.data.get("refreshToken")
        if not refresh_token:
            return Response(
                {"detail": "refreshToken is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(refresh_token)
            return Response(
                {"accessToken": str(refresh.access_token)},
                status=status.HTTP_200_OK,
            )
        except TokenError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    """
    GET /api/v1/auth/me/
    Returns the currently authenticated user's data.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Current user", description="Return details of the authenticated user.")
    def get(self, request):
        return Response(_user_data(request.user), status=status.HTTP_200_OK)
