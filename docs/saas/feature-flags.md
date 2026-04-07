# Feature Flags

LankaCommerce Cloud uses a feature flag system to control feature
availability across the platform without requiring code deployments.

## Overview

Feature flags provide a mechanism to toggle functionality on or off
at the platform level. They support gradual rollout through
percentage-based enablement and can be managed entirely through
the Django admin interface.

Feature flags exist in the public schema and apply globally across
all tenants. Tenant-specific overrides allow individual tenants to
opt in or out of specific features, superseding the global flag state.

## Model

The FeatureFlag model resides in the platform app and uses the
following mixins:

- UUIDMixin for UUID v4 primary keys
- TimestampMixin for created_on and updated_on audit fields
- StatusMixin for is_active and deactivated_on lifecycle management

Feature flags do not use SoftDeleteMixin because flag history should
be preserved and flags are deactivated rather than deleted.

## Fields

### Identity

**key**: Unique identifier for the flag using lowercase snake_case
with a module prefix. Examples: webstore.live_chat,
inventory.barcode_scanner, billing.multi_currency,
reports.advanced_analytics. Maximum 100 characters.

**name**: Human-readable display name for the feature flag.
Maximum 200 characters.

**description**: Optional description of what the feature flag
controls and its expected behavior. Maximum 500 characters.

### Rollout

**rollout_percentage**: Integer from 0 to 100 that determines what
percentage of tenants receive the feature:

- 0 means the feature is disabled for all tenants
- 100 means the feature is enabled for all tenants
- Values between 0 and 100 enable gradual rollout

The default value is 0, ensuring new flags do not affect tenants
until explicitly enabled.

### Status

**is_active**: Boolean flag from StatusMixin that controls whether
the feature flag is globally active. When set to False, the feature
is disabled regardless of rollout percentage.

**deactivated_on**: Timestamp from StatusMixin recording when the
flag was last deactivated.

**is_public**: Boolean flag controlling whether the flag is visible
to tenant administrators. Non-public flags are managed only by
platform admins and are invisible in tenant-facing interfaces.

## Key Naming Convention

Feature flag keys follow a consistent naming format:

- Use lowercase letters and underscores only
- Prefix with the module or domain name
- Separate the module prefix with a dot
- Keep keys descriptive but concise

Examples:

- webstore.live_chat
- webstore.product_reviews
- inventory.barcode_scanner
- inventory.multi_warehouse
- billing.multi_currency
- billing.auto_invoicing
- reports.advanced_analytics
- reports.custom_dashboards

## Rollout Strategy

Gradual rollout allows features to be tested with a subset of
tenants before full deployment:

1. Create the flag with rollout_percentage at 0 (disabled)
2. Set is_active to True to enable the flag mechanism
3. Increase rollout_percentage to 10-25 for initial testing
4. Monitor for issues and collect feedback
5. Gradually increase to 50, 75, and finally 100
6. Once stable at 100, the flag can be retired

## Admin Interface

Feature flags are managed through the FeatureFlagAdmin in the
Django admin. The admin interface provides:

- List view with key, name, status, rollout, and visibility
- Inline editing of is_active, rollout_percentage, and is_public
- Search by key, name, and description
- Filtering by active status, visibility, and rollout percentage

The FeatureFlagAdmin extends StatusModelAdmin, which provides the
standard is_active filter and deactivated_on as a read-only field.
Flags are managed at the platform level and only accessible by
staff users with appropriate permissions.

Admin usage guidelines:

- Use the list view to quickly toggle flags on or off via inline
  editing without opening the detail page
- Use the rollout_percentage column to adjust rollout directly
  from the list view for gradual feature deployment
- Use the is_public toggle to control whether tenant admins can
  see the flag in their own admin interfaces
- Use the search bar to find flags by key, name, or description
- Use the is_active filter to view only active or inactive flags

Tenant overrides are managed through a separate
TenantFeatureOverrideAdmin with:

- List view showing flag, tenant, enabled state, and reason
- Search by flag key, flag name, tenant name, and reason
- Filtering by enabled state and feature flag
- Related object selection for tenant and feature flag
- Optimized queries via list_select_related for tenant and flag

Override admin usage guidelines:

- Always provide a reason when creating an override to maintain
  an audit trail of why the override was applied
- Use the is_enabled filter to quickly view all force-enabled
  or force-disabled overrides across tenants
- Use the feature_flag filter to see all tenant overrides for a
  specific flag

## Tenant Feature Overrides

The TenantFeatureOverride model allows tenant-specific feature flag
states that supersede global defaults. Each override links a single
tenant to a single feature flag with an explicit enabled or disabled
value.

### Override Model

The TenantFeatureOverride resides in the platform app alongside
the FeatureFlag model and uses:

- UUIDMixin for UUID v4 primary keys
- TimestampMixin for created_on and updated_on audit fields

Overrides do not use StatusMixin or SoftDeleteMixin. An override is
either present or deleted — there is no deactivated state.

### Fields

**tenant**: Foreign key to the Tenant model. Cascading delete
ensures overrides are removed when a tenant is deleted.

**feature_flag**: Foreign key to the FeatureFlag model. Cascading
delete ensures overrides are removed when a flag is deleted.

**is_enabled**: Boolean value that supersedes the global flag state.
True means the feature is force-enabled for the tenant. False means
the feature is force-disabled.

**reason**: Optional text field (up to 500 characters) explaining
why the override was created. Useful for audit trails.

### Uniqueness

Each tenant may have at most one override per feature flag, enforced
by a unique_together constraint on tenant and feature_flag.

### Override Types

Force-enable (is_enabled=True): The tenant gets the feature
regardless of the global rollout percentage or flag active state.
Use cases include beta testing, enterprise agreements, and early
access programs.

Force-disable (is_enabled=False): The tenant is excluded from the
feature even if the global flag is fully rolled out. Use cases
include plan restrictions, regulatory compliance, and custom
contractual agreements.

## Resolution Order

When determining whether a feature is enabled for a given tenant,
the system follows this precedence order:

1. Check for a TenantFeatureOverride for the tenant and flag pair
2. If an override exists, use its is_enabled value (authoritative)
3. If no override exists, check the global FeatureFlag state
4. If the flag is active and rollout_percentage is greater than 0,
   the feature is enabled
5. If the flag does not exist or is inactive, the feature is disabled

Override interaction with rollout percentage:

- A force-enable override enables the feature even when the global
  rollout_percentage is 0 or the flag is inactive
- A force-disable override disables the feature even when the global
  rollout_percentage is 100 and the flag is active
- When no override exists, the rollout_percentage determines
  eligibility based on the global flag configuration

## Caching Strategy

Feature flag resolution results are cached per tenant for
performance, avoiding repeated database queries.

### Cache Scope

Each tenant has a separate cache entry containing a dictionary of
all resolved flag states. The cache key format is
feature_flags followed by the tenant identifier.

### Cache TTL

Cache entries expire after 3600 seconds (one hour), matching the
platform settings cache TTL for consistency.

### Cache Invalidation

Cache entries are invalidated when feature flag data changes:

- FeatureFlag save or delete: All tenant caches are invalidated
  because any tenant could be affected by a global flag change
- TenantFeatureOverride save or delete: Only the affected tenant's
  cache is invalidated, minimizing cache churn

### Helper Functions

The platform utilities module provides convenience functions:

- is_flag_enabled: Check whether a specific flag is enabled for a
  tenant (primary entry point for application code)
- get_tenant_flags: Return a dictionary of all resolved flag states
  for a tenant (cache-first, then DB with override resolution)
- invalidate_feature_cache: Invalidate cache for a specific tenant
  or all tenants (called on flag and override changes)

### High-Level Helpers

The utils/flags module provides a simplified API for feature flag
checks throughout the application:

- is_enabled: Primary entry point for flag checks. Accepts an
  optional tenant argument. With a tenant, resolves using the
  full override and caching pipeline. Without a tenant, checks
  the global flag state only.
- get_flag: Retrieve a FeatureFlag instance by its key. Returns
  None if the flag does not exist.
- require_feature: View decorator that returns a 404 response if
  the feature flag is not enabled for the current tenant. The
  tenant is resolved from the request object.

Services and views should use is_enabled from utils/flags as the
standard way to check feature flags. The require_feature decorator
is useful for gating entire views behind a feature flag.

### Middleware

The FeatureFlagMiddleware resolves all feature flag states for the
current tenant and attaches them to the request object as
request.feature_flags. This dictionary maps flag keys to boolean
states, making flag checks available throughout the request
lifecycle without additional database queries.

The middleware should be placed after AuthenticationMiddleware and
after any tenant resolution middleware. If no tenant is available
on the request, an empty dictionary is attached.

The middleware is located at apps.platform.middleware.feature_flags
and will be registered in the MIDDLEWARE setting during Phase 3
when tenant middleware is activated.

## Related Documentation

- [Subscription Plans](subscription-plans.md)
