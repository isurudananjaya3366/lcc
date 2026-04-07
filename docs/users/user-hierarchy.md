# User Hierarchy

LankaCommerce Cloud uses a two-tier user architecture to separate
platform operations from tenant business operations.

## Platform Users

Platform users exist in the public schema and manage the SaaS platform
itself. They are defined by the PlatformUser model in the platform app
and serve as the AUTH_USER_MODEL for Django authentication.

### Characteristics

- Email-based authentication (no username field)
- UUID v4 primary keys
- Public schema only — not visible within tenant schemas
- Phone numbers in +94 (Sri Lanka) format
- Created via PlatformUserManager

### Authentication Configuration

Platform authentication uses a custom EmailBackend that authenticates
users by email address and password. The backend is configured in
AUTHENTICATION_BACKENDS and works with Django's standard authenticate()
function, the admin login form, and LoginRequiredMixin.

Key settings:

- AUTH_USER_MODEL is set to platform.PlatformUser
- AUTHENTICATION_BACKENDS uses apps.platform.backends.EmailBackend
- Email lookup is case-insensitive for user convenience
- Inactive users (is_active=False) are rejected at the backend level
- Four password validators enforce minimum length (8 characters),
  common password rejection, numeric-only rejection, and attribute
  similarity checking

### Access Levels

Platform users have two access flags that control their privileges:

**is_staff**: Grants access to the Django admin interface. Staff users
can view and manage platform resources like subscription plans,
platform settings, and tenant records.

**is_superuser**: Grants all permissions without explicit assignment.
Superusers have unrestricted access to all platform operations
including user management, billing, and system configuration.

### Platform Roles

Each platform user is assigned a role that determines their access
scope. Roles follow the principle of least privilege — each role
grants only the permissions required for its responsibilities.

**Super Admin**: Full unrestricted access to all platform operations.
Can manage users, tenants, billing, subscription plans, platform
settings, and system configuration. Automatically assigned when
creating superusers via the createsuperuser command.

**Platform Admin**: Can manage tenants, subscription plans, and
platform settings. Can view platform users but cannot create or
modify admin accounts. Has access to audit logs for operational
oversight.

**Support**: Read-only access to tenants, users, and subscription
data for troubleshooting purposes. Can update tenant status
(activate or suspend) but cannot modify other platform resources.
Has read-only access to audit logs.

**Viewer**: Read-only access to platform dashboards and report
summaries. Cannot modify any platform resources. Suitable for
stakeholders who need visibility without operational access.

### Role Hierarchy

The role hierarchy follows a strict top-down privilege model:

| Role           | Users | Tenants | Plans | Settings | Billing | Audit |
| -------------- | ----- | ------- | ----- | -------- | ------- | ----- |
| Super Admin    | Full  | Full    | Full  | Full     | Full    | Read  |
| Platform Admin | View  | Full    | Full  | Write    | No      | Read  |
| Support        | View  | Status  | View  | No       | No      | Read  |
| Viewer         | No    | View    | View  | No       | No      | No    |

Permission levels: Full (create, read, update, delete), Write
(read, update), Status (read, update status only), View (read-only),
No (no access).

### Creation

Platform superusers are created using the createsuperuser management
command. The createsuperuser command automatically assigns the
super_admin role and sets both is_staff and is_superuser to True.

Platform admin, support, and viewer accounts are created using the
create_platform_admin management command. This command provides an
interactive workflow that prompts for email, password, role, and
optional name fields. It sets is_staff to True so the created user
can access the Django admin interface.

### Management Commands

**createsuperuser**: Django's built-in command for creating superuser
accounts. Automatically assigns the super_admin role. Use this for
bootstrapping the first platform administrator.

**create_platform_admin**: Custom command for creating non-superuser
platform staff. Supports three roles: platform_admin (default),
support, and viewer. The command validates email uniqueness, enforces
password validators, and confirms the password before creating the
account.

Required inputs for create_platform_admin:

- Email address (unique, used as login identifier)
- Password (minimum 8 characters, validated against all configured
  password validators)
- Role (platform_admin, support, or viewer)
- First name and last name (optional)

The command can also accept arguments non-interactively using the
email and role flags, though password must be set interactively
for security.

## Tenant Users (Planned)

Tenant users will be defined in the users app and scoped to individual
tenant schemas. They represent business users who operate within a
specific tenant — cashiers, managers, accountants, and store owners.

Tenant users are distinct from platform users:

- They belong to a specific tenant and cannot access other tenants
- They have tenant-level roles and permissions
- They interact with the POS, inventory, and reporting modules
- They are managed by tenant administrators, not platform admins

## Separation of Concerns

The two-tier model ensures clear boundaries:

| Aspect         | Platform User   | Tenant User        |
| -------------- | --------------- | ------------------ |
| Schema         | Public          | Tenant-specific    |
| App            | apps.platform   | apps.users         |
| Authentication | AUTH_USER_MODEL | Tenant-scoped auth |
| Admin Access   | Django admin    | Tenant admin panel |
| Scope          | All tenants     | Single tenant      |
| Phone Format   | +94             | +94                |
| Primary Key    | UUID v4         | UUID v4            |

## Related Documentation

- [Role Permissions](role-permissions.md)
- [Subscription Plans](../saas/subscription-plans.md)
- [App Classification](../database/app-classification.md)
- [Database Routing](../multi-tenancy/database-routing.md)
