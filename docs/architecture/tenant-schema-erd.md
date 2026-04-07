# Tenant Schema Entity Relationship Diagram

> **Phase:** 02 — Database Architecture & Multi-Tenancy  
> **SubPhase:** 05 — Tenant Schema Template  
> **Document:** Group G Task 88 — Model Relationships  
> **Last updated:** 2026-02-21

---

## Overview

Every business tenant in LankaCommerce Cloud receives a dedicated PostgreSQL schema
(named `tenant_<slug>`). All models listed here live exclusively within that schema —
they are never stored in the public (shared) schema. The public schema holds the
`tenants`, `platform`, and other SHARED_APPS data.

---

## Entity Summary

| App        | Model          | Base Mixins                 | Purpose                                     |
| ---------- | -------------- | --------------------------- | ------------------------------------------- |
| products   | Category       | UUID, Timestamp             | Product category tree (self-referential)    |
| products   | Product        | UUID, Timestamp             | Core product catalog entry                  |
| products   | ProductImage   | UUID, Timestamp             | Product photo attachments                   |
| products   | ProductVariant | UUID, Timestamp             | Size/colour/attribute variants of a product |
| inventory  | StockLocation  | UUID, Timestamp             | Warehouse, store, or virtual location       |
| inventory  | Stock          | UUID, Timestamp             | Quantity on hand per product per location   |
| inventory  | StockMovement  | UUID, Timestamp             | Audit trail for every stock quantity change |
| customers  | Customer       | UUID, Timestamp, SoftDelete | Customer CRM record                         |
| vendors    | Supplier       | UUID, Timestamp, SoftDelete | Supplier / vendor record                    |
| orders     | Order          | UUID, Timestamp, SoftDelete | Customer purchase order header              |
| orders     | OrderItem      | UUID, Timestamp             | Line items belonging to an Order            |
| sales      | Invoice        | UUID, Timestamp, SoftDelete | Invoice issued to a customer                |
| sales      | Payment        | UUID, Timestamp             | Payment received against an Invoice         |
| hr         | Employee       | UUID, Timestamp, SoftDelete | Staff member linked to a PlatformUser       |
| accounting | Account        | UUID, Timestamp             | Chart-of-accounts entry                     |
| accounting | JournalEntry   | UUID, Timestamp             | Double-entry accounting transaction         |
| accounting | TenantAuditLog | UUID, Timestamp             | Tenant-level action audit trail             |

---

## Relationships

### Product Domain

**Category → Category** (self-referential)

- A Category may have one optional parent Category (nullable FK to self).
- The root categories have parent = null.
- Depth is unconstrained; the application enforces reasonable limits.

**Product → Category**

- Many Products belong to one Category (nullable FK).
- on_delete = SET_NULL — deleting a Category does not delete its Products.

**ProductImage → Product**

- Many ProductImages belong to one Product (FK, CASCADE).
- Deleting a Product cascades to all its images.
- The `is_primary` flag marks the default display image.

**ProductVariant → Product**

- Many ProductVariants belong to one Product (FK, CASCADE).
- Each variant overrides the product's default selling/cost price.
- Deleting a Product cascades to all its variants.

---

### Inventory Domain

**StockLocation** (independent root entity)

- Represents a physical warehouse, retail store, transit area, or virtual location.
- No foreign keys to other tenant models.

**Stock → Product + StockLocation**

- One Stock record per (Product, StockLocation) pair — enforced by UniqueConstraint.
- on_delete for both FKs = PROTECT — neither a Product nor a Location can be deleted
  while a Stock record references it.
- Stores the current quantity on hand (Decimal 12,3) and a reorder_level threshold.

**StockMovement → Product + StockLocation + PlatformUser**

- Records every individual change to stock quantity (in, out, transfer, adjustment, return).
- product FK (PROTECT), location FK (PROTECT), destination_location FK (nullable PROTECT).
- performed_by FK to AUTH_USER_MODEL (SET_NULL) — preserves the movement record
  even if the user is deleted.

---

### Customer Domain

**Customer** (independent root entity with soft delete)

- Stores billing and shipping address sets (6 fields each).
- customer_type: individual, business, wholesale, vip.
- credit_limit and current_balance tracked in LKR (Decimal 10,2).
- SoftDeleteMixin: records are never physically removed.

---

### Vendor Domain

**Supplier** (independent root entity with soft delete)

- Single address set (6 fields).
- payment_terms: immediate, net_15, net_30, net_60, cod.
- tax_id and vat_number for Sri Lanka tax compliance.
- SoftDeleteMixin: records are never physically removed.

---

### Order Domain

**Order → Customer + PlatformUser**

- Many Orders belong to one Customer (FK, PROTECT — cannot delete a Customer with orders).
- created_by FK to AUTH_USER_MODEL (SET_NULL).
- status workflow: pending → confirmed → processing → shipped → delivered / cancelled / returned.
- Financial totals (subtotal, tax_amount, discount_amount, total_amount) in LKR.
- SoftDeleteMixin: orders are never physically removed.

**OrderItem → Order + Product**

- Many OrderItems belong to one Order (FK, CASCADE — deleting an Order deletes its items).
- product FK (PROTECT — cannot delete a Product with order history).
- Stores unit_price at time of order (price snapshot, not live FK to price).
- Stores discount_amount, tax_amount, and line_total per item.

---

### Sales Domain

**Invoice → Order + Customer + PlatformUser**

- One Invoice per Order (OneToOne or FK depending on implementation).
- Links to Customer for billing address snapshot.
- issued_by FK to AUTH_USER_MODEL (SET_NULL).
- status workflow: draft → issued → paid → overdue → cancelled / voided.
- SoftDeleteMixin: invoices are never physically removed.

**Payment → Invoice + PlatformUser**

- Many Payments can be applied to one Invoice (FK, PROTECT).
- payment_method: cash, card, bank_transfer, cheque, mobile.
- received_by FK to AUTH_USER_MODEL (SET_NULL).
- Stores amount in LKR and payment_date.

---

### HR Domain

**Employee → PlatformUser**

- One Employee record per PlatformUser (OneToOneField or FK).
- role: admin, manager, cashier, warehouse, accountant.
- status: active, inactive, suspended.
- Contact fields (phone, email in +94 format).
- SoftDeleteMixin: records are never physically removed.

---

### Accounting Domain

**Account** (independent root entity)

- Represents one entry in the chart of accounts.
- account_code is unique per tenant.
- account_type: asset, liability, equity, revenue, expense.
- Supports parent_account (self-referential, nullable) for account hierarchies.

**JournalEntry → Account + PlatformUser**

- Records a double-entry accounting transaction.
- debit_account FK and credit_account FK both → Account (PROTECT).
- amount in LKR (Decimal 10,2).
- created_by FK to AUTH_USER_MODEL (SET_NULL).
- reference links to the source document (invoice number, order number, etc.).

**TenantAuditLog → PlatformUser**

- Append-only log of significant actions within the tenant schema.
- actor FK to AUTH_USER_MODEL (SET_NULL — preserves log if user deleted).
- action: create, update, delete, login, activate, deactivate, config_change, etc.
- Stores actor_email (denormalized) and ip_address for tamper-evident records.
- metadata JSONField for structured context (changed fields, previous values, etc.).

---

## Cross-Schema Boundaries

Tenant models reference the following public-schema models via string labels:

| Tenant FK                  | Public Target                           | on_delete         |
| -------------------------- | --------------------------------------- | ----------------- |
| Order.customer             | customers.Customer                      | PROTECT           |
| Order.created_by           | platform.PlatformUser (AUTH_USER_MODEL) | SET_NULL          |
| OrderItem.order            | orders.Order                            | CASCADE           |
| OrderItem.product          | products.Product                        | PROTECT           |
| StockMovement.performed_by | platform.PlatformUser                   | SET_NULL          |
| Invoice.created_by         | platform.PlatformUser                   | SET_NULL          |
| Payment.received_by        | platform.PlatformUser                   | SET_NULL          |
| Employee.user              | platform.PlatformUser                   | CASCADE / PROTECT |
| JournalEntry.created_by    | platform.PlatformUser                   | SET_NULL          |
| TenantAuditLog.actor       | platform.PlatformUser                   | SET_NULL          |

---

## Signal-Driven Auto-Creation

The following records are created automatically via Django post_save signals
defined in `apps/core/signals.py`:

| Trigger                            | Signal                         | Auto-Created Record                  |
| ---------------------------------- | ------------------------------ | ------------------------------------ |
| Tenant saved (created=True)        | auto_create_tenant_settings    | TenantSettings (in public schema)    |
| Product saved (created=True)       | auto_create_stock_for_product  | Stock at every StockLocation (qty=0) |
| StockLocation saved (created=True) | auto_create_stock_for_location | Stock for every Product (qty=0)      |

---

## Manager Helpers (apps/core/managers.py)

Custom QuerySet and Manager classes are provided for models using the
core mixins. They are importable from `apps.core.managers`.

**ActiveQuerySet / ActiveManager**

- Use on models with `StatusMixin` (is_active field).
- Default queryset filters `is_active=True`.
- Exposes `.active()` and `.inactive()` helper methods.

**SoftDeleteQuerySet / SoftDeleteManager**

- Use on models with `SoftDeleteMixin` (is_deleted field).
- Default queryset filters `is_deleted=False`.
- Exposes `.alive()` and `.dead()` helper methods.

**AliveQuerySet / AliveManager**

- Use on models with both `StatusMixin` and `SoftDeleteMixin`.
- Default queryset filters `is_active=True AND is_deleted=False`.
- Exposes `.active()`, `.inactive()`, `.alive()`, `.dead()`, `.active_alive()`.

---

## TENANT_APPS Registration

All tenant-schema models reside in apps listed under `TENANT_APPS` in
`config/settings/database.py`. The current registered apps are:

- django.contrib.contenttypes
- django.contrib.auth
- apps.products
- apps.inventory
- apps.vendors
- apps.sales
- apps.customers
- apps.orders
- apps.hr
- apps.accounting
- apps.reports
- apps.webstore
- apps.integrations

All 11 LankaCommerce business-module apps are registered. Each app's models
are migrated into every tenant schema when a new Tenant is created
(via `auto_create_schema = True` on the Tenant model).
