# Audit Logging

LankaCommerce Cloud maintains an immutable audit trail of all
significant platform administrative actions. The audit log records
who did what, when, and from where, providing accountability and
compliance support.

## Overview

Every significant action performed by platform staff is recorded
in the AuditLog model. Audit entries are append-only and cannot be
modified or deleted through the application. The Django admin
interface provides a read-only view for reviewing audit entries.

Audit logs reside in the public schema and are shared across all
tenants. They capture platform-level actions such as managing
subscription plans, toggling feature flags, modifying platform
settings, and user authentication events.

## Model

The AuditLog model resides in the platform app and uses the
following mixins:

- UUIDMixin for UUID v4 primary keys
- TimestampMixin for created_on and updated_on audit fields

Audit logs do not use StatusMixin (entries are always active) or
SoftDeleteMixin (entries are never deleted). The model is designed
to be immutable once created.

## Event Fields

### Action

Each audit entry records an action type categorized into five groups:

CRUD actions: create, update, delete — standard data manipulation
operations performed on platform resources.

Authentication actions: login, logout, login_failed — user
authentication events tracked for security monitoring.

Lifecycle actions: activate, deactivate — status changes on
platform resources such as toggling a subscription plan or
feature flag.

Data actions: import_data, export_data — bulk data operations
performed through the platform admin.

Configuration actions: config_change — modifications to platform
settings or system configuration.

### Resource Type

The resource_type field identifies the model or subsystem that was
acted upon. Common values include subscription_plan, feature_flag,
tenant, platform_user, platform_setting, and tenant_feature_override.

### Resource ID

The resource_id field stores the primary key of the affected object
as a string. This accommodates both UUID and integer primary keys
across different models.

### Description

An optional human-readable description of the action performed.
This provides additional context beyond the action and resource
type fields.

## Actor Fields

### Actor

The actor field is a foreign key to the PlatformUser model. It
identifies the platform user who performed the action. The field
uses SET_NULL on delete to preserve the audit entry even if the
user account is removed.

### Actor Email

The actor_email field stores a denormalized copy of the actor's
email address at the time of the action. This ensures the email
is preserved in the audit trail even if the user account is
deleted or the email is changed.

### IP Address

The ip_address field records the client IP address using a
GenericIPAddressField that supports both IPv4 and IPv6 addresses.
This helps identify the source of administrative actions.

## Metadata Fields

### Metadata

The metadata field is a JSONField that stores structured context
data for the audit event. Examples of metadata include:

- Changed field values (before and after)
- Request parameters
- Error details for failed actions
- Previous state snapshots
- Affected tenant information

### User Agent

The user_agent field records the browser or client user agent
string, providing additional context about the client environment.

## Admin Interface

Audit logs are managed through a read-only admin interface using
ReadOnlyPlatformAdmin. The admin interface:

- Prevents adding, editing, or deleting audit entries
- Displays entries in reverse chronological order
- Provides filtering by action type, resource type, and date
- Supports searching by actor email, resource type, resource ID,
  description, and IP address
- Uses date hierarchy for quick date-based navigation
- Shows 50 entries per page for efficient browsing

Access to audit logs should be restricted to platform users with
the can_view_audit_logs permission. Super admins, platform admins,
and support staff have this permission by default. Viewers do not
have audit log access.

## Retention

Audit log entries are retained indefinitely. There is no automatic
purging or archival of audit records. Future phases may implement
export functionality for long-term archival or compliance reporting.

## Integration

Audit logging will be integrated into platform operations during
Phase 3 when service layers are implemented. The integration
pattern involves creating audit entries within service methods
that perform significant actions.

## Related Documentation

- [User Hierarchy](../users/user-hierarchy.md)
- [Role Permissions](../users/role-permissions.md)
- [Feature Flags](../saas/feature-flags.md)
- [Subscription Plans](../saas/subscription-plans.md)
