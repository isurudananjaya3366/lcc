"""
Platform user model for the LankaCommerce Cloud platform.

Defines the custom user model for platform-level authentication.
Platform users are super admins and platform operators who manage
the SaaS platform itself. They are distinct from tenant-scoped
users who operate within individual business tenants.

Platform users exist in the public (shared) schema and have access
to the Django admin interface and platform management tools.

Table: platform_platformuser
Schema: public (shared)
Auth: AUTH_USER_MODEL = "platform.PlatformUser"
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from apps.platform.models.managers import PlatformUserManager
from apps.platform.models.mixins import TimestampMixin, UUIDMixin

# ── Constants ────────────────────────────────────────────────

PHONE_REGEX = r"^\+94\s?\d{2}\s?\d{3}\s?\d{4}$"
EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 150
PHONE_MAX_LENGTH = 20
ROLE_MAX_LENGTH = 20

# ── Platform Roles ───────────────────────────────────────────

ROLE_SUPER_ADMIN = "super_admin"
ROLE_PLATFORM_ADMIN = "platform_admin"
ROLE_SUPPORT = "support"
ROLE_VIEWER = "viewer"

PLATFORM_ROLE_CHOICES = [
    (ROLE_SUPER_ADMIN, "Super Admin"),
    (ROLE_PLATFORM_ADMIN, "Platform Admin"),
    (ROLE_SUPPORT, "Support"),
    (ROLE_VIEWER, "Viewer"),
]

# ── Role Descriptions ────────────────────────────────────────
# Super Admin:    Full unrestricted access. Can manage all platform
#                 resources, users, billing, tenants, and system
#                 configuration. Equivalent to is_superuser=True.
#
# Platform Admin: Can manage tenants, subscription plans, and
#                 platform settings. Cannot manage other platform
#                 admins or super admins.
#
# Support:        Can view tenants, users, and subscription data
#                 for troubleshooting. Read-only access to most
#                 platform resources. Can update tenant status.
#
# Viewer:         Read-only access to platform dashboards and
#                 reports. Cannot modify any platform resources.

# ── Role Permissions Mapping ─────────────────────────────────
# Defines which permissions each role grants. Follows least-privilege
# principle — each role gets only the permissions it needs.
#
# Permission scope per role:
#
# Super Admin:
#   - All Django permissions (via is_superuser=True)
#   - User management (create, update, deactivate platform users)
#   - Tenant management (create, update, suspend, delete tenants)
#   - Billing management (plans, invoices, payment records)
#   - System configuration (platform settings, feature toggles)
#   - Audit log access (full read access)
#
# Platform Admin:
#   - Tenant management (create, update, suspend tenants)
#   - Subscription plan management (create, update plans)
#   - Platform settings management (update non-critical settings)
#   - View platform users (cannot create/modify admins)
#   - Audit log access (read-only)
#
# Support:
#   - View tenants and tenant details (read-only)
#   - View platform users (read-only)
#   - View subscription plans (read-only)
#   - Update tenant status (activate, suspend)
#   - View audit logs (read-only)
#
# Viewer:
#   - View platform dashboard (read-only)
#   - View subscription plan summaries (read-only)
#   - View tenant summaries (read-only)
#   - No modification permissions


# ── Model ────────────────────────────────────────────────────


class PlatformUser(UUIDMixin, TimestampMixin, AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for platform-level authentication.

    Uses email as the unique identifier (USERNAME_FIELD) instead of
    a traditional username. Inherits Django's authentication and
    permission system via AbstractBaseUser and PermissionsMixin.

    Platform users are NOT tenant-scoped. They exist only in the
    public schema and manage the platform itself. Tenant-scoped
    users will be defined separately in the users app.

    Roles:
        - super_admin: Full unrestricted access (is_superuser=True)
        - platform_admin: Manage tenants, plans, settings
        - support: View and troubleshoot tenant issues
        - viewer: Read-only dashboard and report access

    Inheritance:
        - UUIDMixin: UUID v4 primary key
        - TimestampMixin: created_on / updated_on audit fields
        - AbstractBaseUser: Password hashing, authentication
        - PermissionsMixin: is_superuser, groups, user_permissions
    """

    # ── Core Identity Fields ─────────────────────────────────

    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True,
        help_text="Email address used as the login identifier.",
    )

    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        blank=True,
        default="",
        help_text="User's first name.",
    )

    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        blank=True,
        default="",
        help_text="User's last name.",
    )

    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        default="",
        validators=[
            RegexValidator(
                regex=PHONE_REGEX,
                message="Enter a valid Sri Lankan phone number in +94 format.",
            ),
        ],
        help_text="Contact phone number in +94 (Sri Lanka) format.",
    )

    # ── Role Assignment ──────────────────────────────────────

    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=PLATFORM_ROLE_CHOICES,
        default=ROLE_VIEWER,
        db_index=True,
        help_text=(
            "Platform role determining the user's access level. "
            "Super Admin has full access, Viewer is read-only."
        ),
    )

    # ── Access Flags ─────────────────────────────────────────

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Designates whether this user account is active. "
            "Deactivate instead of deleting accounts."
        ),
    )

    is_staff = models.BooleanField(
        default=False,
        help_text=(
            "Designates whether this user can access the Django admin site."
        ),
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Date and time when the user account was created.",
    )

    # ── Manager ──────────────────────────────────────────────

    objects = PlatformUserManager()

    # ── Auth Configuration ───────────────────────────────────

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email is already required by USERNAME_FIELD

    # ── Meta ─────────────────────────────────────────────────

    class Meta:
        db_table = "platform_platformuser"
        verbose_name = "Platform User"
        verbose_name_plural = "Platform Users"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["email"],
                name="idx_platform_user_email",
            ),
            models.Index(
                fields=["is_active", "is_staff"],
                name="idx_platform_user_active_staff",
            ),
            models.Index(
                fields=["role"],
                name="idx_platform_user_role",
            ),
        ]

    # ── String Representation ────────────────────────────────

    def __str__(self):
        if self.full_name:
            return f"{self.full_name} ({self.email})"
        return self.email

    # ── Properties ───────────────────────────────────────────

    @property
    def full_name(self):
        """Return the user's full name, trimmed."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def short_name(self):
        """Return the user's first name or email prefix."""
        return self.first_name or self.email.split("@")[0]

    # ── Role Checks ──────────────────────────────────────────

    @property
    def is_super_admin(self):
        """Return True if user has the super_admin role."""
        return self.role == ROLE_SUPER_ADMIN

    @property
    def is_platform_admin(self):
        """Return True if user has the platform_admin role."""
        return self.role == ROLE_PLATFORM_ADMIN

    @property
    def is_support(self):
        """Return True if user has the support role."""
        return self.role == ROLE_SUPPORT

    @property
    def is_viewer(self):
        """Return True if user has the viewer role."""
        return self.role == ROLE_VIEWER

    @property
    def can_manage_tenants(self):
        """Return True if user can create and manage tenants."""
        return self.role in (ROLE_SUPER_ADMIN, ROLE_PLATFORM_ADMIN)

    @property
    def can_manage_users(self):
        """Return True if user can create and manage platform users."""
        return self.role == ROLE_SUPER_ADMIN

    @property
    def can_manage_billing(self):
        """Return True if user can manage billing and invoices."""
        return self.role == ROLE_SUPER_ADMIN

    @property
    def can_view_audit_logs(self):
        """Return True if user can access audit logs."""
        return self.role in (
            ROLE_SUPER_ADMIN, ROLE_PLATFORM_ADMIN, ROLE_SUPPORT
        )
