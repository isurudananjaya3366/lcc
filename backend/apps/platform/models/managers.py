"""
Platform user manager for the LankaCommerce Cloud platform.

Provides custom user manager for creating platform users (super admins
and platform operators). Uses email as the unique identifier instead
of a username.

Table context: platform_platformuser
Schema: public (shared)
"""

from django.contrib.auth.models import BaseUserManager


class PlatformUserManager(BaseUserManager):
    """
    Custom manager for PlatformUser.

    Creates platform-level users with email as the primary identifier.
    All created users exist in the public schema and are distinct
    from tenant-scoped users in the users app.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular platform user.

        Args:
            email: The user's email address (required, used as login).
            password: The user's password (optional, hashed on save).
            **extra_fields: Additional fields to set on the user.

        Returns:
            PlatformUser: The newly created user instance.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError("Platform users must have an email address.")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a platform superuser.

        Superusers have full access to the Django admin and all
        platform-level operations. Both is_staff and is_superuser
        are forced to True.

        Args:
            email: The superuser's email address (required).
            password: The superuser's password (required for admin access).
            **extra_fields: Additional fields to set on the user.

        Returns:
            PlatformUser: The newly created superuser instance.

        Raises:
            ValueError: If is_staff or is_superuser is explicitly set to False.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "super_admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
