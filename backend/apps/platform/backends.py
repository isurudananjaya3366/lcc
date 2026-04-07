"""
Authentication backends for the LankaCommerce Cloud platform.

Provides custom authentication backends that align with the
platform's email-based user model. Platform users authenticate
using their email address instead of a username.

Backend: EmailBackend
    Authenticates platform users by email and password. Extends
    Django's ModelBackend to leverage its built-in permission
    checking while using email as the lookup field.

Schema: public (shared)
Model: PlatformUser (AUTH_USER_MODEL = "platform.PlatformUser")
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """
    Custom authentication backend using email and password.

    Authenticates users by looking up their email address in the
    PlatformUser model. Inherits permission checks and inactive
    user rejection from Django's ModelBackend.

    This backend supports the platform's email-based authentication
    design where USERNAME_FIELD is set to 'email' on PlatformUser.

    Usage:
        Configured in AUTHENTICATION_BACKENDS in settings/base.py.
        Works seamlessly with Django's authenticate() function,
        the admin login form, and any view using LoginRequiredMixin.

    Security:
        - Rejects inactive users (is_active=False) via ModelBackend
        - Password comparison uses constant-time hashing
        - Failed lookups return None (no information leakage)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user by email and password.

        Accepts 'username' parameter for compatibility with Django's
        auth forms and the admin login page, but treats it as an
        email address.

        Args:
            request: The current HTTP request (may be None).
            username: The email address to authenticate (str).
            password: The password to verify (str).
            **kwargs: Additional keyword arguments (ignored).

        Returns:
            PlatformUser instance if authentication succeeds, None otherwise.
        """
        UserModel = get_user_model()
        email = username

        if email is None:
            email = kwargs.get(UserModel.USERNAME_FIELD)

        if email is None or password is None:
            return None

        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            # Run the default password hasher to prevent timing attacks
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
