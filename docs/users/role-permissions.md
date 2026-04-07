# Platform Role Permissions

Defines the permission mapping for each platform role in the
LankaCommerce Cloud SaaS platform.

## Design Principles

All platform roles follow the principle of least privilege. Each
role grants only the permissions necessary for its intended
responsibilities. Permissions are enforced through the role field
on the PlatformUser model combined with Django's built-in
permission system via PermissionsMixin.

## Role Definitions

### Super Admin

The highest-privilege platform role with full unrestricted access.

Responsibilities:

- Manage all platform user accounts (create, update, deactivate)
- Create and configure tenants
- Manage subscription plans and pricing
- Configure platform-wide settings and feature toggles
- Access billing records and payment management
- View complete audit trail

Enforcement: The super_admin role is paired with is_superuser=True,
which bypasses Django's permission checks entirely. The
create_superuser manager method automatically assigns this role.

### Platform Admin

Mid-level administrative role for day-to-day platform operations.

Responsibilities:

- Create and manage tenant accounts
- Configure subscription plans (create, update, archive)
- Update platform settings (non-critical configuration)
- View platform user list (read-only, cannot modify admins)
- View audit logs for operational oversight

Restrictions:

- Cannot create or modify platform user accounts
- Cannot access billing or payment records
- Cannot change critical system settings

### Support

Troubleshooting and customer support role with limited access.

Responsibilities:

- View tenant details for troubleshooting
- View platform user information (read-only)
- View subscription plan details (read-only)
- Update tenant status (activate or suspend accounts)
- View audit logs for investigation

Restrictions:

- Cannot create or modify any resources except tenant status
- Cannot access billing, payment, or pricing data
- Cannot view or change platform settings

### Viewer

Read-only observer role for stakeholders and reporting.

Responsibilities:

- View platform dashboard summaries
- View subscription plan overviews
- View tenant summaries and counts

Restrictions:

- Cannot modify any platform resources
- Cannot access detailed user or tenant records
- Cannot view audit logs or billing data

## Permission Matrix

| Resource           | Super Admin | Platform Admin | Support     | Viewer |
| ------------------ | ----------- | -------------- | ----------- | ------ |
| Platform Users     | Full CRUD   | View           | View        | None   |
| Tenants            | Full CRUD   | Full CRUD      | Status only | View   |
| Subscription Plans | Full CRUD   | Full CRUD      | View        | View   |
| Platform Settings  | Full CRUD   | Read/Update    | None        | None   |
| Billing Records    | Full CRUD   | None           | None        | None   |
| Audit Logs         | Read        | Read           | Read        | None   |
| Feature Toggles    | Full CRUD   | None           | None        | None   |
| System Config      | Full CRUD   | None           | None        | None   |

Permission levels:

- Full CRUD: Create, read, update, delete
- Read/Update: Read and modify existing records
- Status only: Read and update status field
- View: Read-only access
- Read: Read-only access (used for logs)
- None: No access

## Role Assignment

Platform roles are assigned through the role field on PlatformUser.
The default role for new users is Viewer, ensuring least-privilege
by default.

Super admins created via the createsuperuser management command
automatically receive the super_admin role. Platform admin, support,
and viewer accounts are created using the create_platform_admin
management command, which provides an interactive workflow for
setting email, password, role, and optional name fields.

## Role Enforcement

Role-based access is enforced at multiple levels:

**Model level**: The PlatformUser model provides convenience
properties (is_super_admin, is_platform_admin, is_support,
is_viewer) and permission-check properties (can_manage_tenants,
can_manage_users, can_manage_billing, can_view_audit_logs) for
use in views and API endpoints.

**Admin level**: The PlatformUserAdmin configuration restricts
which fields are visible and editable based on the requesting
user's permissions.

**Django permissions**: The PermissionsMixin provides standard
Django group and user_permissions M2M fields for fine-grained
permission control when needed beyond role-based checks.

## Related Documentation

- [User Hierarchy](user-hierarchy.md)
- [Subscription Plans](../saas/subscription-plans.md)
