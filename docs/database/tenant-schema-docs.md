# Tenant Schema Documentation

> **Phase:** 02 — Database Architecture & Multi-Tenancy  
> **SubPhase:** 05 — Tenant Schema Template  
> **Group:** G — Configuration & Verification  
> **Task:** 93 — Schema Documentation  
> **Last updated:** 2026-02-21

---

## Overview

Each business tenant in LankaCommerce Cloud receives its own isolated PostgreSQL schema
(named `tenant_<slug>`). All 11 LankaCommerce business-module apps are registered in
`TENANT_APPS` and their tables exist only within each tenant's schema.

The public schema contains only SHARED_APPS tables (platform, tenants, auth, admin, etc.)
and is never polluted with tenant business data.

---

## Tenant Schema Tables

When a new tenant is created (Tenant.save() with auto_create_schema=True), all TENANT_APPS
migrations are applied to the new schema. The resulting tables are:

### products app

| Table                   | Description                                        |
| ----------------------- | -------------------------------------------------- |
| products_category       | Product category tree (self-referential parent FK) |
| products_product        | Core product catalog — SKU, pricing, tax, status   |
| products_productimage   | Product photo attachments (is_primary flag)        |
| products_productvariant | Product variants — size, colour, attributes        |

### inventory app

| Table                   | Description                                          |
| ----------------------- | ---------------------------------------------------- |
| inventory_stocklocation | Warehouses, stores, transit areas, virtual locations |
| inventory_stock         | Quantity on hand per product per location            |
| inventory_stockmovement | Audit trail for every stock quantity change          |

### vendors app

| Table            | Description                 |
| ---------------- | --------------------------- |
| vendors_supplier | Supplier and vendor records |

### customers app

| Table              | Description                                              |
| ------------------ | -------------------------------------------------------- |
| customers_customer | Customer CRM records with billing and shipping addresses |

### orders app

| Table            | Description                     |
| ---------------- | ------------------------------- |
| orders_order     | Customer purchase order headers |
| orders_orderitem | Line items within each order    |

### sales app

| Table         | Description                        |
| ------------- | ---------------------------------- |
| sales_invoice | Invoices issued to customers       |
| sales_payment | Payments received against invoices |

### hr app

| Table       | Description                                   |
| ----------- | --------------------------------------------- |
| hr_employee | Staff members linked to PlatformUser accounts |

### accounting app

| Table                     | Description                          |
| ------------------------- | ------------------------------------ |
| accounting_account        | Chart of accounts entries            |
| accounting_journalentry   | Double-entry accounting transactions |
| accounting_tenantauditlog | Tenant-level action audit trail      |

---

## Key Constraints and Indexes

Every model uses a UUID v4 primary key (from UUIDMixin). Key indexes include:

- products_category: idx_category_active_sort, idx_category_parent
- products_product: idx_product_status_created, idx_product_category_status, idx_product_sku
- products_productvariant: idx_variant_product_attr, idx_variant_sku, uq_variant_product_attr_value
- inventory_stock: uq_stock_product_location (unique per product+location)
- orders_order: idx_order_status_date, idx_order_customer_status, idx_order_date_desc
- accounting_tenantauditlog: idx_audit_action_time, idx_audit_actor_time, idx_audit_model_object

---

## Migration State

All 8 initial migrations are applied and verified:

| Migration               | App        | Status  |
| ----------------------- | ---------- | ------- |
| products 0001_initial   | products   | Applied |
| inventory 0001_initial  | inventory  | Applied |
| vendors 0001_initial    | vendors    | Applied |
| sales 0001_initial      | sales      | Applied |
| customers 0001_initial  | customers  | Applied |
| orders 0001_initial     | orders     | Applied |
| hr 0001_initial         | hr         | Applied |
| accounting 0001_initial | accounting | Applied |

---

## Signal-Driven Auto-Creation

When records are created, the following auto-creation signals fire (defined in
`apps/core/signals.py`, connected via `CoreConfig.ready()`):

- Tenant created → TenantSettings auto-created (public schema)
- Product created → Stock entry (qty=0) auto-created at every StockLocation
- StockLocation created → Stock entry (qty=0) auto-created for every Product

---

## Related Documentation

- Full ERD and relationship details: [docs/architecture/tenant-schema-erd.md](../architecture/tenant-schema-erd.md)
- Multi-tenancy architecture: [docs/multi-tenancy/](../multi-tenancy/)
- Database naming conventions: [docs/database/](./README.md)
