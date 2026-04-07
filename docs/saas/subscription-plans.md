# Subscription Plans

LankaCommerce Cloud uses a tiered subscription model to provide different
service levels for tenants. All pricing is denominated in Sri Lankan Rupees
(LKR, ₨) as the platform targets the Sri Lankan market.

## Plan Tiers

The platform offers four subscription tiers, each designed for a different
business size and need level.

### Free Plan

Entry-level tier for small businesses exploring the platform. No payment
required. Includes basic POS, inventory, and reporting features.

| Resource             | Limit  |
| -------------------- | ------ |
| Users                | 2      |
| Products             | 100    |
| Locations            | 1      |
| Storage              | 256 MB |
| Monthly transactions | 500    |

Features: basic_pos, basic_inventory, basic_reports

### Starter Plan

For growing businesses that need essential commerce features. Includes
customer management and email support.

| Resource             | Limit |
| -------------------- | ----- |
| Users                | 5     |
| Products             | 1,000 |
| Locations            | 2     |
| Storage              | 1 GB  |
| Monthly transactions | 5,000 |

Pricing:

| Cycle   | Price (LKR) | Savings   |
| ------- | ----------- | --------- |
| Monthly | ₨2,999/mo   | —         |
| Annual  | ₨29,990/yr  | ₨5,998/yr |

Features: basic_pos, basic_inventory, basic_reports,
customer_management, email_support

### Pro Plan

For established businesses needing advanced features. Includes multi-location
support, advanced analytics, API access, and priority support.

| Resource             | Limit  |
| -------------------- | ------ |
| Users                | 20     |
| Products             | 10,000 |
| Locations            | 5      |
| Storage              | 5 GB   |
| Monthly transactions | 25,000 |

Pricing:

| Cycle   | Price (LKR) | Savings    |
| ------- | ----------- | ---------- |
| Monthly | ₨9,999/mo   | —          |
| Annual  | ₨99,990/yr  | ₨19,998/yr |

Features: basic_pos, basic_inventory, basic_reports,
customer_management, email_support, advanced_reports,
multi_location, api_access, priority_support

### Enterprise Plan

Unlimited access for large businesses and retail chains. Includes all
features, unlimited resources, dedicated support, white-label options,
and custom integrations. Default billing cycle is annual.

| Resource             | Limit     |
| -------------------- | --------- |
| Users                | Unlimited |
| Products             | Unlimited |
| Locations            | Unlimited |
| Storage              | Unlimited |
| Monthly transactions | Unlimited |

Pricing:

| Cycle   | Price (LKR) | Savings    |
| ------- | ----------- | ---------- |
| Monthly | ₨29,999/mo  | —          |
| Annual  | ₨299,990/yr | ₨59,998/yr |

Features: All features from lower tiers plus multi_currency,
custom_integrations, dedicated_support, white_label, sla_guarantee

## Pricing Structure

All prices are in Sri Lankan Rupees (LKR, ₨). Decimal precision is
maintained using Python Decimal fields with 2 decimal places.

Annual plans offer approximately 16-17% discount compared to monthly
billing. The annual_discount_percent property on SubscriptionPlan
calculates this automatically.

## Resource Limits

Resource limits control what tenants can use within their subscription:

- **max_users**: Maximum number of user accounts per tenant
- **max_products**: Maximum number of product records
- **max_locations**: Maximum number of store/warehouse locations
- **storage_limit_mb**: Maximum file storage in megabytes
- **max_monthly_transactions**: Maximum sales transactions per month

### Unlimited Values

A value of -1 (the UNLIMITED constant) means no limit is enforced.
Application code checks: if the limit equals UNLIMITED, skip enforcement.

## Feature Keys

Plans reference features through a JSON list of feature key strings.
This provides a lightweight linkage between plans and features without
requiring a separate join table.

When the FeatureFlag model is created (Group-D), plans will reference
flags by key for more granular control. Until then, feature_keys
provides the association.

Feature access enforcement: check whether a feature key exists in the
active plan's feature_keys list before granting access.

## Billing Cycles

Each plan has a default billing cycle (monthly or annual) that is
pre-selected when a tenant subscribes. Tenants can choose either cycle
regardless of the default.

Free plans do not have a trial period. Paid plans offer a configurable
trial period (default 14 days, Enterprise offers 30 days).

## Status and Visibility

Plans have three status flags that control their lifecycle:

- **is_active** (from StatusMixin): Whether the plan is currently operational
- **is_public**: Whether the plan appears on the public pricing page
- **is_archived**: Whether the plan is hidden from new subscriptions

A plan is selectable by new tenants only when all three conditions are met:
active, public, and not archived.

## Fixture Data

Default plans are stored in a JSON fixture file at
backend/apps/platform/fixtures/subscription_plans.json.

The fixture will be loaded after migrations are applied for the platform
app. To load the fixture manually, use the management command from the
project root.

## Related Documentation

- [Database Naming Conventions](../database/naming-conventions.md)
- [Public Schema ERD](../database/public-schema-erd.md)
- [Multi-Tenancy Overview](../multi-tenancy/database-routing.md)
