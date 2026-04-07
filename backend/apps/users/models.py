"""
Users models module.

Provides tenant-scoped user-related models that complement the
platform-level :class:`~apps.platform.models.PlatformUser`
(which is ``AUTH_USER_MODEL``).

Models:
    - **UserProfile**: Extended user information within a tenant
      (department, job title, avatar, phone, timezone).
    - **UserPreferences**: Per-user settings (theme, locale,
      notification preferences).
    - **LoginHistory**: Authentication audit trail (login, logout,
      failed attempts with IP / user-agent metadata).

Architecture note:
    ``AUTH_USER_MODEL = "platform.PlatformUser"`` lives in the public
    schema.  These models live in tenant schemas and link to
    ``PlatformUser`` via ``settings.AUTH_USER_MODEL``.  Business apps
    (orders, sales, inventory …) reference ``settings.AUTH_USER_MODEL``
    directly; these models add *optional* enrichment.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import SoftDeleteMixin, StatusMixin, TimestampMixin, UUIDMixin
from apps.core.managers import ActiveManager, SoftDeleteManager


# ── Constants ────────────────────────────────────────────────────────

PHONE_REGEX = r"^\+94\s?\d{2}\s?\d{3}\s?\d{4}$"
PHONE_MAX_LENGTH = 20
TIMEZONE_MAX_LENGTH = 50
LOCALE_MAX_LENGTH = 10
THEME_MAX_LENGTH = 20
DEFAULT_TIMEZONE = "Asia/Colombo"
DEFAULT_LOCALE = "en"
DEFAULT_THEME = "system"

THEME_CHOICES = [
    ("light", "Light"),
    ("dark", "Dark"),
    ("system", "System Default"),
]

LOGIN_EVENT_CHOICES = [
    ("login_success", "Successful Login"),
    ("login_failed", "Failed Login"),
    ("logout", "Logout"),
    ("token_refresh", "Token Refresh"),
    ("password_change", "Password Change"),
    ("password_reset", "Password Reset"),
    ("account_locked", "Account Locked"),
]


# ── UserProfile ──────────────────────────────────────────────────────


class UserProfile(UUIDMixin, TimestampMixin, SoftDeleteMixin, StatusMixin, models.Model):
    """
    Extended profile for a user within a tenant.

    Links to ``AUTH_USER_MODEL`` (PlatformUser) and adds
    tenant-specific fields: department, job title, avatar,
    phone, timezone, and locale.

    Table: users_userprofile
    Schema: tenant-scoped
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        help_text="The platform user this profile belongs to.",
    )

    # ── Identity ─────────────────────────────────────────────

    display_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="Preferred display name within this tenant.",
    )

    job_title = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Job title / designation within the tenant's organisation.",
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Department or team within the tenant's organisation.",
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
        help_text="Direct phone number in +94 (Sri Lanka) format.",
    )

    avatar = models.ImageField(
        upload_to="users/avatars/%Y/%m/",
        blank=True,
        null=True,
        help_text="Profile picture.",
    )

    # ── Localisation ─────────────────────────────────────────

    timezone = models.CharField(
        max_length=TIMEZONE_MAX_LENGTH,
        default=DEFAULT_TIMEZONE,
        help_text="IANA timezone identifier (e.g. 'Asia/Colombo').",
    )

    locale = models.CharField(
        max_length=LOCALE_MAX_LENGTH,
        default=DEFAULT_LOCALE,
        help_text="Locale code for formatting (e.g. 'en', 'si', 'ta').",
    )

    # ── Metadata ─────────────────────────────────────────────

    bio = models.TextField(
        blank=True,
        default="",
        help_text="Short bio or description.",
    )

    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the most recent login.",
    )

    # ── Roles ────────────────────────────────────────────────

    roles = models.ManyToManyField(
        "Role",
        through="UserRole",
        blank=True,
        related_name="user_profiles",
        help_text="Roles assigned to this user profile.",
    )

    # ── Managers ─────────────────────────────────────────────

    objects = ActiveManager()
    all_objects = SoftDeleteManager()

    class Meta:
        db_table = "users_userprofile"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["display_name"]

    def __str__(self) -> str:
        name = self.display_name or str(self.user)
        return f"Profile: {name}"


# ── UserPreferences ──────────────────────────────────────────────────


class UserPreferences(UUIDMixin, TimestampMixin, models.Model):
    """
    Per-user application preferences.

    Stores UI/UX preferences such as theme, notification settings,
    and dashboard layout.

    Table: users_userpreferences
    Schema: tenant-scoped
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
        help_text="The platform user whose preferences these are.",
    )

    # ── Display ──────────────────────────────────────────────

    theme = models.CharField(
        max_length=THEME_MAX_LENGTH,
        choices=THEME_CHOICES,
        default=DEFAULT_THEME,
        help_text="UI colour-scheme preference.",
    )

    items_per_page = models.PositiveSmallIntegerField(
        default=25,
        help_text="Default number of rows to display in list views.",
    )

    # ── Notifications ────────────────────────────────────────

    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive email notifications for important events.",
    )

    push_notifications = models.BooleanField(
        default=True,
        help_text="Receive browser push notifications.",
    )

    # ── Dashboard ────────────────────────────────────────────

    dashboard_layout = models.JSONField(
        default=dict,
        blank=True,
        help_text="Serialised dashboard widget layout (JSON).",
    )

    sidebar_collapsed = models.BooleanField(
        default=False,
        help_text="Whether the sidebar is collapsed by default.",
    )

    class Meta:
        db_table = "users_userpreferences"
        verbose_name = "User Preferences"
        verbose_name_plural = "User Preferences"

    def __str__(self) -> str:
        return f"Preferences: {self.user}"


# ── LoginHistory ─────────────────────────────────────────────────────


class LoginHistory(UUIDMixin, models.Model):
    """
    Authentication audit trail.

    Records login/logout events with IP addresses, user-agent strings,
    and success/failure status for security monitoring and compliance.

    Table: users_loginhistory
    Schema: tenant-scoped
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_history",
        help_text="The user who performed this authentication event.",
    )

    event_type = models.CharField(
        max_length=20,
        choices=LOGIN_EVENT_CHOICES,
        db_index=True,
        help_text="Type of authentication event.",
    )

    # ── Request Metadata ─────────────────────────────────────

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="Client IP address at the time of the event.",
    )

    user_agent = models.TextField(
        blank=True,
        default="",
        help_text="Browser / client user-agent string.",
    )

    # ── Result ───────────────────────────────────────────────

    success = models.BooleanField(
        default=True,
        help_text="Whether the authentication event was successful.",
    )

    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Reason for failure (when success=False).",
    )

    # ── Timestamps ───────────────────────────────────────────

    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the authentication event occurred.",
    )

    class Meta:
        db_table = "users_loginhistory"
        verbose_name = "Login History"
        verbose_name_plural = "Login History"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(
                fields=["user", "-timestamp"],
                name="idx_login_history_user_time",
            ),
            models.Index(
                fields=["event_type", "-timestamp"],
                name="idx_login_history_event_time",
            ),
            models.Index(
                fields=["ip_address"],
                name="idx_login_history_ip",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_type}: {self.user} @ {self.timestamp:%Y-%m-%d %H:%M}"


# ── Permission ───────────────────────────────────────────────────────


class Permission(UUIDMixin, TimestampMixin, models.Model):
    """
    Granular permission for the RBAC system.

    Permissions follow the pattern: "{resource}.{action}"
    e.g. "orders.create", "inventory.view", "reports.export"

    Table: users_permission
    Schema: tenant-scoped
    """

    codename = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique permission identifier (e.g. 'orders.create').",
    )
    name = models.CharField(
        max_length=200,
        help_text="Human-readable permission name.",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed description of what this permission grants.",
    )
    resource = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Resource this permission applies to (e.g. 'orders', 'inventory').",
    )
    action = models.CharField(
        max_length=50,
        help_text="Action this permission grants (e.g. 'create', 'view', 'update', 'delete', 'export').",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this permission is currently active.",
    )

    class Meta:
        db_table = "users_permission"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ["resource", "action"]
        indexes = [
            models.Index(
                fields=["resource", "action"],
                name="idx_perm_resource_action",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.resource}.{self.action}"

    def save(self, *args, **kwargs):
        if not self.codename:
            self.codename = f"{self.resource}.{self.action}"
        super().save(*args, **kwargs)


# ── Role ─────────────────────────────────────────────────────────────


class Role(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Tenant-scoped role for RBAC.

    Each tenant defines its own roles (e.g. "Cashier", "Manager", "Admin").
    Roles group permissions and are assigned to UserProfile instances.

    Table: users_role
    Schema: tenant-scoped
    """

    name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Human-readable role name.",
    )
    slug = models.SlugField(
        max_length=100,
        db_index=True,
        help_text="URL-safe role identifier.",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Description of this role's purpose and scope.",
    )
    is_system_role = models.BooleanField(
        default=False,
        help_text="System roles cannot be deleted by tenants.",
    )
    permissions = models.ManyToManyField(
        "Permission",
        blank=True,
        related_name="roles",
        help_text="Permissions granted to this role.",
    )

    # ── Managers ─────────────────────────────────────────────

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "users_role"
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(is_deleted=False),
                name="unique_active_role_slug",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def has_permission(self, permission_codename: str) -> bool:
        """Check whether this role grants the given permission."""
        return self.permissions.filter(codename=permission_codename).exists()


# ── UserRole (through model) ─────────────────────────────────────────


class UserRole(UUIDMixin, TimestampMixin, models.Model):
    """
    Through model linking UserProfile to Role.

    Tracks when a role was assigned and by whom.

    Table: users_userrole
    Schema: tenant-scoped
    """

    user_profile = models.ForeignKey(
        "UserProfile",
        on_delete=models.CASCADE,
        related_name="user_roles",
        help_text="The user profile this role is assigned to.",
    )
    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="user_roles",
        help_text="The role assigned to the user.",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_assignments_made",
        help_text="The user who assigned this role.",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this role was assigned.",
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the user's primary role.",
    )

    class Meta:
        db_table = "users_userrole"
        verbose_name = "User Role Assignment"
        verbose_name_plural = "User Role Assignments"
        constraints = [
            models.UniqueConstraint(
                fields=["user_profile", "role"],
                name="unique_user_role",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_profile} \u2192 {self.role}"
