# Backend Models

> Database model conventions, base classes, and domain model reference for LankaCommerce Cloud.

**Navigation:** [Docs Index](../index.md) · [Backend README](../../backend/README.md) · [Apps](apps.md) · [API](api.md)

---

## Overview

LankaCommerce Cloud uses Django's ORM with PostgreSQL as the primary database. Models follow a consistent set of conventions for naming, field types, and inheritance patterns. Shared base classes and mixins are defined in `apps/core/models.py` and inherited by domain models across all apps.

---

## Base Models and Mixins

All models inherit from shared base classes defined in `apps/core/`. These provide consistent behavior across the entire codebase.

### BaseModel

The foundation for all domain models. Provides:

- **UUID primary key** — Uses `uuid4` instead of auto-incrementing integers for security and distributed system compatibility
- **Timestamps** — Automatic `created_at` and `updated_at` fields
- **Ordering** — Default ordering by creation date (newest first)

All domain models should extend `BaseModel` unless there is a specific reason not to.

### TimeStampedMixin

A lighter alternative to `BaseModel` when UUID primary keys are not needed.

- `created_at` — Set automatically when the record is first created
- `updated_at` — Updated automatically on every save

### SoftDeleteMixin

Enables logical deletion instead of physical removal from the database.

- `is_deleted` — Boolean flag indicating soft-deleted status
- `deleted_at` — Timestamp of when the record was soft-deleted
- Custom manager filters out deleted records by default
- Provides `soft_delete()` and `restore()` methods

### TenantAwareMixin

Scopes models to a specific tenant for multi-tenant isolation.

- Foreign key to the Tenant model
- Ensures queries are automatically filtered by the current tenant context
- Works in conjunction with django-tenants schema isolation

---

## Model Conventions

### Naming

| Convention                                         | Example                                    |
| -------------------------------------------------- | ------------------------------------------ |
| Model names are singular PascalCase                | `Product`, `SalesOrder`, `CustomerProfile` |
| Table names use app label prefix (auto)            | `products_product`, `sales_salesorder`     |
| Field names use snake_case                         | `created_at`, `unit_price`, `is_active`    |
| Foreign key fields end with the related model name | `customer`, `created_by`, `tenant`         |
| Boolean fields start with `is_` or `has_`          | `is_active`, `has_discount`, `is_deleted`  |

### Common Field Patterns

| Field                | Type                 | Usage                        |
| -------------------- | -------------------- | ---------------------------- |
| `id`                 | UUIDField            | Primary key (from BaseModel) |
| `created_at`         | DateTimeField        | Auto-set on creation         |
| `updated_at`         | DateTimeField        | Auto-set on every save       |
| `is_active`          | BooleanField         | Soft-enable/disable toggle   |
| `name` / `title`     | CharField            | Human-readable identifier    |
| `description`        | TextField            | Optional long-form text      |
| `slug`               | SlugField            | URL-safe identifier          |
| `order` / `position` | PositiveIntegerField | Display ordering             |

### Money and Currency

All monetary values use `DecimalField` with:

- `max_digits=12` — Supports values up to 9,999,999,999.99
- `decimal_places=2` — Standard two decimal places for LKR
- Default currency is **LKR** (Sri Lankan Rupee)

### Relationships

| Pattern             | When to Use                                     |
| ------------------- | ----------------------------------------------- |
| `ForeignKey`        | Many-to-one (e.g., Product → Category)          |
| `ManyToManyField`   | Many-to-many (e.g., Product ↔ Tag)              |
| `OneToOneField`     | One-to-one extension (e.g., User → UserProfile) |
| `GenericForeignKey` | Polymorphic relations (use sparingly)           |

Always set `on_delete` explicitly:

- `CASCADE` — Delete child when parent is deleted (orders → order items)
- `PROTECT` — Prevent deletion if references exist (category with products)
- `SET_NULL` — Nullify reference on deletion (optional relations)

---

## Domain Models by App

### tenants

| Model          | Purpose                                                |
| -------------- | ------------------------------------------------------ |
| Tenant         | Multi-tenant account (TenantMixin from django-tenants) |
| Domain         | Tenant domain routing (DomainMixin)                    |
| TenantSettings | Per-tenant configuration and preferences               |
| TenantBilling  | Subscription and billing information                   |

### users

| Model           | Purpose                                                 |
| --------------- | ------------------------------------------------------- |
| CustomUser      | Email-based authentication with Sri Lankan phone format |
| UserProfile     | Extended user information and avatar                    |
| UserPreferences | UI and notification preferences                         |
| LoginHistory    | Authentication audit trail                              |

### products

| Model        | Purpose                             |
| ------------ | ----------------------------------- |
| Product      | Catalog item with name, price, SKU  |
| Category     | Hierarchical product categorization |
| ProductImage | Product media attachments           |
| PriceRule    | Discount and pricing logic          |

### inventory

| Model         | Purpose                                         |
| ------------- | ----------------------------------------------- |
| StockItem     | Current stock quantity per product per location |
| Warehouse     | Physical storage location                       |
| StockMovement | Transfer, adjustment, and receipt records       |
| ReorderRule   | Automatic reorder point triggers                |

### sales

| Model      | Purpose                           |
| ---------- | --------------------------------- |
| SalesOrder | Customer order header             |
| OrderItem  | Individual line items in an order |
| Payment    | Payment records and methods       |
| Receipt    | Generated receipt for printing    |

### customers

| Model         | Purpose                              |
| ------------- | ------------------------------------ |
| Customer      | Customer profile and contact details |
| CustomerGroup | Segmentation and grouping            |
| LoyaltyRecord | Points and rewards tracking          |

### vendors

| Model             | Purpose                              |
| ----------------- | ------------------------------------ |
| Vendor            | Supplier profile and contact details |
| PurchaseOrder     | Procurement order header             |
| PurchaseOrderItem | Individual procurement line items    |

### hr

| Model        | Purpose                          |
| ------------ | -------------------------------- |
| Employee     | Employee profile linked to user  |
| Attendance   | Check-in/check-out records       |
| LeaveRequest | Leave applications and approvals |
| PayrollEntry | Salary calculation records       |

### accounting

| Model        | Purpose                                     |
| ------------ | ------------------------------------------- |
| Account      | Chart of accounts entries                   |
| JournalEntry | Double-entry bookkeeping records            |
| Invoice      | Customer and vendor invoices                |
| TaxRate      | Tax configuration for Sri Lankan compliance |

### reports

| Model            | Purpose                              |
| ---------------- | ------------------------------------ |
| ReportDefinition | Saved report configuration           |
| ReportSchedule   | Automated report generation schedule |
| ExportJob        | Async export task tracking           |

### webstore

| Model           | Purpose                            |
| --------------- | ---------------------------------- |
| Cart            | Shopping cart per customer session |
| CartItem        | Individual items in a cart         |
| WebOrder        | Online order (extends SalesOrder)  |
| ShippingAddress | Customer delivery addresses        |

### integrations

| Model          | Purpose                                     |
| -------------- | ------------------------------------------- |
| PaymentGateway | Gateway configuration (PayHere, etc.)       |
| WebhookLog     | Incoming webhook audit trail                |
| CourierConfig  | Delivery service settings (Domex, Koombiyo) |

---

## Migration Strategy

- Each app manages its own migrations in `<app>/migrations/`
- Multi-tenant models use `migrate_schemas` instead of standard `migrate`
- See the [Database Migrations](../../backend/README.md#database-migrations) section in the Backend README for workflow details

---

## Related Documentation

- [Backend README](../../backend/README.md) — Setup and development guide
- [Apps Documentation](apps.md) — App responsibilities and structure
- [API Documentation](api.md) — API structure and conventions
- [Docs Index](../index.md) — Full documentation hub
