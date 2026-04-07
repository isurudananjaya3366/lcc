"""
Platform application models package.

Public schema models for platform-wide configuration, organized by domain:

Mixins (models/mixins.py):
    - UUIDMixin: UUID v4 primary key for all platform models
    - TimestampMixin: created_on / updated_on audit fields
    - StatusMixin: is_active / deactivated_on lifecycle flags
    - SoftDeleteMixin: is_deleted / deleted_on soft deletion

Models:
    - models/subscription.py: SubscriptionPlan
    - models/settings.py: PlatformSetting (singleton)
    - models/user.py: PlatformUser (AUTH_USER_MODEL)
    - models/managers.py: PlatformUserManager
    - models/features.py: FeatureFlag
    - models/overrides.py: TenantFeatureOverride
    - models/audit.py: AuditLog
    - models/billing.py: BillingRecord

All models reside exclusively in the public (shared) schema
and are accessible from all tenant contexts.
"""

from apps.platform.models.mixins import (
    SoftDeleteMixin,
    StatusMixin,
    TimestampMixin,
    UUIDMixin,
)
from apps.platform.models.audit import (
    ACTION_ACTIVATE,
    ACTION_CONFIG_CHANGE,
    ACTION_CREATE,
    ACTION_DEACTIVATE,
    ACTION_DELETE,
    ACTION_EXPORT,
    ACTION_IMPORT,
    ACTION_LOGIN,
    ACTION_LOGIN_FAILED,
    ACTION_LOGOUT,
    ACTION_UPDATE,
    AuditLog,
)
from apps.platform.models.billing import (
    BILLING_CYCLE_CHOICES,
    BILLING_STATUS_CHOICES,
    CURRENCY_CODE,
    CURRENCY_SYMBOL,
    CYCLE_ANNUAL,
    CYCLE_MONTHLY,
    STATUS_CANCELLED,
    STATUS_OVERDUE,
    STATUS_PAID,
    STATUS_PENDING,
    STATUS_REFUNDED,
    BillingRecord,
)
from apps.platform.models.features import FeatureFlag
from apps.platform.models.overrides import TenantFeatureOverride
from apps.platform.models.settings import PlatformSetting
from apps.platform.models.subscription import UNLIMITED, SubscriptionPlan
from apps.platform.models.user import (
    PLATFORM_ROLE_CHOICES,
    ROLE_PLATFORM_ADMIN,
    ROLE_SUPER_ADMIN,
    ROLE_SUPPORT,
    ROLE_VIEWER,
    PlatformUser,
)

__all__ = [
    "UUIDMixin",
    "TimestampMixin",
    "StatusMixin",
    "SoftDeleteMixin",
    "SubscriptionPlan",
    "UNLIMITED",
    "PlatformSetting",
    "FeatureFlag",
    "TenantFeatureOverride",
    "AuditLog",
    "ACTION_CREATE",
    "ACTION_UPDATE",
    "ACTION_DELETE",
    "ACTION_LOGIN",
    "ACTION_LOGOUT",
    "ACTION_LOGIN_FAILED",
    "ACTION_ACTIVATE",
    "ACTION_DEACTIVATE",
    "ACTION_IMPORT",
    "ACTION_EXPORT",
    "ACTION_CONFIG_CHANGE",
    "BillingRecord",
    "CURRENCY_CODE",
    "CURRENCY_SYMBOL",
    "STATUS_PENDING",
    "STATUS_PAID",
    "STATUS_OVERDUE",
    "STATUS_CANCELLED",
    "STATUS_REFUNDED",
    "BILLING_STATUS_CHOICES",
    "CYCLE_MONTHLY",
    "CYCLE_ANNUAL",
    "BILLING_CYCLE_CHOICES",
    "PlatformUser",
    "PLATFORM_ROLE_CHOICES",
    "ROLE_SUPER_ADMIN",
    "ROLE_PLATFORM_ADMIN",
    "ROLE_SUPPORT",
    "ROLE_VIEWER",
]
