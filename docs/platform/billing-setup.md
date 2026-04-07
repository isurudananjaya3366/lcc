# Billing Setup

LankaCommerce Cloud tracks tenant subscription billing through
the BillingRecord model. Each billing record represents a single
billing event for a tenant, including the subscription amount,
payment status, billing period, and Sri Lanka-specific business
registration details for tax compliance.

## Overview

Billing records are created at the start of each billing cycle
and progress through a defined status lifecycle. All amounts are
denominated in Sri Lankan Rupees (LKR, ₨) to serve the local
market. Records reside in the public schema and are shared across
all tenants.

Financial records use all four platform mixins to provide maximum
data protection. Billing records are never physically deleted —
the soft delete mechanism preserves the complete billing audit
trail for compliance and reporting.

## Model

The BillingRecord model resides in the platform app and uses the
following mixins:

- UUIDMixin for UUID v4 primary keys
- TimestampMixin for created_on and updated_on audit fields
- StatusMixin for is_active and deactivated_on lifecycle flags
- SoftDeleteMixin for is_deleted and deleted_on soft deletion

Each billing record has a foreign key to the Tenant model
(CASCADE on delete) and an optional foreign key to the
SubscriptionPlan model (SET_NULL on delete, preserving the
billing record if a plan is removed).

## Billing Fields

### Amount

The amount field stores the base billing amount as a Decimal with
12 digits of precision and 2 decimal places. A minimum value
validator ensures amounts cannot be negative. The default value is
zero.

### Tax Amount

The tax_amount field stores the tax portion applied to the billing
record, following the same decimal precision as the amount field.

### Total Amount

The total_amount field stores the sum of amount and tax_amount.
This denormalized field avoids recalculation in queries and
reports.

### Currency

The currency field stores the ISO 4217 currency code, defaulting
to LKR (Sri Lankan Rupee). The field is a 3-character string to
accommodate any ISO currency code if multi-currency support is
enabled in future phases.

### Invoice Number

The invoice_number field is a unique identifier for each billing
record. The recommended format is INV-YYYYMM-NNNNN where YYYYMM
is the billing period and NNNNN is a sequential number. The field
is indexed for fast lookups.

### Notes

An optional free-text field for recording comments, adjustments,
or special instructions related to the billing record. Maximum
length is 1000 characters.

## Business Registration Number

Sri Lanka Business Registration Number (BRN) fields support tax
compliance and invoice generation for local businesses.

### BRN Field

The business_registration_number field accepts Sri Lanka BRN
formats including:

- PV followed by 5 or more digits (private companies)
- PB followed by 5 or more digits (public companies)
- GA followed by 5 or more digits (government agencies)
- Numeric-only registrations (5 or more digits)

The field uses a regex validator to enforce these formats.

### BRN Validated

A boolean flag indicating whether the business registration
number has been validated against external registries or manual
verification.

### BRN Validated On

A timestamp recording when the BRN was last validated. This field
is read-only in the admin interface to prevent manual modification
of the validation timestamp.

## Billing Cycle Rules

### Billing Cycle

The billing_cycle field specifies whether the record covers a
monthly or annual period. This mirrors the billing cycle choices
defined in the SubscriptionPlan model to maintain consistency.

### Period Start and Period End

The period_start and period_end date fields define the inclusive
date range for the billing period. Monthly cycles typically span
one calendar month, while annual cycles span one year from the
start date.

### Due Date

The due_date field specifies the payment deadline. When the
current date passes the due date and the billing status is still
pending, the record should transition to overdue status.

### Billing Status

The billing_status field tracks the payment lifecycle with five
possible values:

Pending — the billing record has been created and payment has not
yet been received. This is the initial status for all new records.

Paid — payment has been received and the paid_on timestamp is set.
This is a terminal state unless a refund is issued.

Overdue — the due date has passed without payment. Records
transition from pending to overdue automatically or through
a scheduled task.

Cancelled — the billing record has been voided, typically due to
a subscription change, downgrade, or administrative action.

Refunded — payment was previously received but has been returned
to the tenant. Records transition from paid to refunded.

### Paid On

A timestamp recording when payment was received. This field is
read-only in the admin interface and is set programmatically when
the billing status changes to paid.

## Status Transitions

The billing status follows a defined set of valid transitions:

- pending to paid (payment received)
- pending to overdue (past due date)
- pending to cancelled (subscription change)
- overdue to paid (late payment received)
- paid to refunded (refund issued)

These transitions are documented for reference. Enforcement of
valid transitions will be implemented in the service layer during
Phase 3.

## Indexes

The BillingRecord model includes six database indexes optimized
for common query patterns:

- idx_billing_tenant_period — tenant + period_start for tenant
  billing history queries
- idx_billing_status — billing_status for status-based filtering
- idx_billing_invoice — invoice_number for invoice lookups
- idx_billing_tenant_status — tenant + billing_status for
  per-tenant status queries
- idx_billing_due_status — due_date + billing_status for overdue
  detection queries
- idx_billing_created — created_on for chronological ordering

## Admin Interface

Billing records are managed through the Django admin using
FullPlatformModelAdmin, which provides both status lifecycle and
soft delete management capabilities.

The admin interface provides:

- List view showing invoice number, tenant, plan, total amount
  with currency symbol, billing status, cycle, period start,
  due date, paid timestamp, and creation date
- Filtering by billing status, billing cycle, active state,
  deleted state, BRN validation status, and creation date
- Searching by invoice number, business registration number,
  and notes
- Date hierarchy based on period start date
- Optimized queries with select_related for tenant and
  subscription plan relationships

The admin organizes fields into logical fieldsets:

- Invoice Details — ID, invoice number, tenant, subscription plan
- Billing Amounts — amount, tax, total, and currency
- Billing Cycle — cycle type, period start, period end, due date
- Payment Status — billing status and paid timestamp
- Business Registration — BRN, validation flag, validation date
- Notes — collapsible section for optional comments
- Status and Lifecycle — collapsible section for active and
  deleted flags
- Timestamps — collapsible section for created and updated dates

## Currency

All billing amounts use Sri Lankan Rupees (LKR) by default. The
currency symbol ₨ is used in display formatting throughout the
admin interface and reports.

The currency field supports ISO 4217 codes to accommodate future
multi-currency requirements. The billing.multi_currency feature
flag controls whether tenants can use currencies other than LKR.

## Retention

Billing records are retained indefinitely using soft deletion.
Financial records are never physically removed from the database
to maintain a complete billing history for compliance, auditing,
and reporting purposes.

## Integration

Billing record creation and status management will be integrated
into the subscription service layer during Phase 3. The
integration pattern involves:

- Creating billing records when a subscription period begins
- Updating billing status when payments are processed
- Automatically detecting overdue records past their due dates
- Generating invoice numbers using a consistent format

## Related Documentation

- [Subscription Plans](../saas/subscription-plans.md)
- [Feature Flags](../saas/feature-flags.md)
- [Audit Logging](audit-logging.md)
- [User Hierarchy](../users/user-hierarchy.md)
