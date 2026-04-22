"""
Authentication URL configuration.
"""
from __future__ import annotations

from django.urls import path

from .views import LoginView, LogoutView, MeView, TokenRefreshView

app_name = "authentication"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]
