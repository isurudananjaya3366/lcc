"""
Platform audit log model for the LankaCommerce Cloud platform.

Defines the AuditLog model for recording platform-level administrative
actions. Every significant action performed by platform staff is logged
with the actor, action type, target resource, IP address, and optional
structured metadata.

Audit logs are immutable records — once created, they cannot be
modified or deleted through the application. The admin interface uses
ReadOnlyPlatformAdmin to enforce this at the UI level, and the model
does not provide update or delete methods.

Table: platform_auditlog
Schema: public (shared)

Action categories:
    CRUD: create, update, delete
    Authentication: login, logout, login_failed
    Lifecycle: activate, deactivate
    Data: import_data, export_data
    Configuration: config_change

Resource types identify the model or subsystem that was acted upon.
The resource_id field stores the primary key of the affected object
as a string, accommodating both UUID and integer keys.

Retention:
    Audit logs are retained indefinitely. Platform administrators
    can view but not modify or delete audit entries. Future phases
    may implement archival or export for long-term storage.
"""

from django.db import models

from apps.platform.models.mixins import TimestampMixin, UUIDMixin

# ── Constants ────────────────────────────────────────────────

DESCRIPTION_MAX_LENGTH = 1000
RESOURCE_TYPE_MAX_LENGTH = 100
RESOURCE_ID_MAX_LENGTH = 255
ACTOR_EMAIL_MAX_LENGTH = 254
USER_AGENT_MAX_LENGTH = 500

# ── Action Choices ───────────────────────────────────────────

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"
ACTION_LOGIN = "login"
ACTION_LOGOUT = "logout"
ACTION_LOGIN_FAILED = "login_failed"
ACTION_ACTIVATE = "activate"
ACTION_DEACTIVATE = "deactivate"
ACTION_IMPORT = "import_data"
ACTION_EXPORT = "export_data"
ACTION_CONFIG_CHANGE = "config_change"

ACTION_CHOICES = [
    ("CRUD", (
        (ACTION_CREATE, "Create"),
        (ACTION_UPDATE, "Update"),
        (ACTION_DELETE, "Delete"),
    )),
    ("Authentication", (
        (ACTION_LOGIN, "Login"),
        (ACTION_LOGOUT, "Logout"),
        (ACTION_LOGIN_FAILED, "Login Failed"),
    )),
    ("Lifecycle", (
        (ACTION_ACTIVATE, "Activate"),
        (ACTION_DEACTIVATE, "Deactivate"),
    )),
    ("Data", (
        (ACTION_IMPORT, "Import Data"),
        (ACTION_EXPORT, "Export Data"),
    )),
    ("Configuration", (
        (ACTION_CONFIG_CHANGE, "Config Change"),
    )),
]

# Flat list of valid action values for validation
VALID_ACTIONS = [
    ACTION_CREATE,
    ACTION_UPDATE,
    ACTION_DELETE,
    ACTION_LOGIN,
    ACTION_LOGOUT,
    ACTION_LOGIN_FAILED,
    ACTION_ACTIVATE,
    ACTION_DEACTIVATE,
    ACTION_IMPORT,
    ACTION_EXPORT,
    ACTION_CONFIG_CHANGE,
]


# ── Model ────────────────────────────────────────────────────


class AuditLog(UUIDMixin, TimestampMixin, models.Model):
    """
    Immutable audit log for platform administrative actions.

    Records every significant action performed by platform staff,
    including the actor, action type, target resource, IP address,
    and optional structured metadata.

    Audit logs are append-only — records are never updated or
    deleted. This ensures a complete and tamper-evident audit
    trail for compliance and security purposes.

    Inheritance:
        - UUIDMixin: UUID v4 primary key
        - TimestampMixin: created_on / updated_on audit fields

    Does not use StatusMixin (audit entries are always active)
    or SoftDeleteMixin (audit entries are never deleted).
    """

    # ── Event Fields (Task 74) ───────────────────────────────

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text=(
            "The type of action performed. Categorized into CRUD, "
            "Authentication, Lifecycle, Data, and Configuration."
        ),
    )

    resource_type = models.CharField(
        max_length=RESOURCE_TYPE_MAX_LENGTH,
        db_index=True,
        help_text=(
            "The type of resource acted upon (e.g. subscription_plan, "
            "feature_flag, tenant, platform_user, platform_setting)."
        ),
    )

    resource_id = models.CharField(
        max_length=RESOURCE_ID_MAX_LENGTH,
        blank=True,
        default="",
        help_text=(
            "The primary key of the affected resource, stored as a "
            "string to accommodate both UUID and integer keys."
        ),
    )

    description = models.TextField(
        max_length=DESCRIPTION_MAX_LENGTH,
        blank=True,
        default="",
        help_text="Human-readable description of the action performed.",
    )

    # ── Actor Fields (Task 75) ───────────────────────────────

    actor = models.ForeignKey(
        "platform.PlatformUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        help_text=(
            "The platform user who performed the action. "
            "Null if the user has been deleted or the action "
            "was performed by the system."
        ),
    )

    actor_email = models.CharField(
        max_length=ACTOR_EMAIL_MAX_LENGTH,
        blank=True,
        default="",
        help_text=(
            "Denormalized email of the actor at the time of the "
            "action. Preserved even if the user account is deleted."
        ),
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=(
            "IP address of the client that initiated the action. "
            "Supports both IPv4 and IPv6 addresses."
        ),
    )

    # ── Metadata Fields (Task 76) ────────────────────────────

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Structured metadata providing additional context for "
            "the action. Examples: changed field values, request "
            "parameters, error details, previous state snapshots."
        ),
    )

    user_agent = models.CharField(
        max_length=USER_AGENT_MAX_LENGTH,
        blank=True,
        default="",
        help_text="Browser or client user agent string.",
    )

    # ── Meta ─────────────────────────────────────────────────

    class Meta:
        db_table = "platform_auditlog"
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["action"],
                name="idx_auditlog_action",
            ),
            models.Index(
                fields=["resource_type"],
                name="idx_auditlog_resource_type",
            ),
            models.Index(
                fields=["resource_type", "resource_id"],
                name="idx_auditlog_resource",
            ),
            models.Index(
                fields=["actor"],
                name="idx_auditlog_actor",
            ),
            models.Index(
                fields=["-created_on"],
                name="idx_auditlog_created",
            ),
            models.Index(
                fields=["action", "-created_on"],
                name="idx_auditlog_action_created",
            ),
        ]

    # ── String Representation ────────────────────────────────

    def __str__(self):
        actor_display = self.actor_email or "system"
        return (
            f"[{self.created_on:%Y-%m-%d %H:%M}] "
            f"{actor_display} — {self.action} "
            f"{self.resource_type}"
        )

    # ── Properties ───────────────────────────────────────────

    @property
    def action_category(self):
        """Return the category grouping for this action."""
        crud_actions = {ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE}
        auth_actions = {ACTION_LOGIN, ACTION_LOGOUT, ACTION_LOGIN_FAILED}
        lifecycle_actions = {ACTION_ACTIVATE, ACTION_DEACTIVATE}
        data_actions = {ACTION_IMPORT, ACTION_EXPORT}

        if self.action in crud_actions:
            return "CRUD"
        if self.action in auth_actions:
            return "Authentication"
        if self.action in lifecycle_actions:
            return "Lifecycle"
        if self.action in data_actions:
            return "Data"
        if self.action == ACTION_CONFIG_CHANGE:
            return "Configuration"
        return "Unknown"

    @property
    def has_metadata(self):
        """Return True if this entry has non-empty metadata."""
        return bool(self.metadata)
