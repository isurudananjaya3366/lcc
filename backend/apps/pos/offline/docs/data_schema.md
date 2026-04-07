# Offline Data Schema

> POS Offline Mode – Data Architecture Reference

## Overview

This document defines the data schema for POS offline mode, covering all entity
categories stored locally, their relationships, storage strategy, version
tracking, and security considerations.

---

## Entity Categories

### 1. Critical Entities (Must be cached for operation)

| Entity          | Table             | Sync Direction | Priority |
| --------------- | ----------------- | -------------- | -------- |
| Tax Rates       | `tax_rates`       | Pull           | Critical |
| POS Settings    | `pos_settings`    | Pull           | Critical |
| Product Prices  | `product_prices`  | Pull           | High     |
| Payment Methods | `payment_methods` | Pull           | High     |

### 2. Master Data (Core business entities)

| Entity           | Table              | Sync Direction | Priority |
| ---------------- | ------------------ | -------------- | -------- |
| Products         | `products`         | Pull           | High     |
| Product Variants | `product_variants` | Pull           | High     |
| Categories       | `categories`       | Pull           | Normal   |
| Discount Rules   | `discount_rules`   | Pull           | High     |
| Units of Measure | `units_of_measure` | Pull           | Low      |

### 3. Reference Data (Supporting entities)

| Entity    | Table           | Sync Direction | Priority |
| --------- | --------------- | -------------- | -------- |
| Customers | `customers`     | Bidirectional  | Normal   |
| Employees | `employees`     | Pull           | Normal   |
| Terminals | `pos_terminals` | Pull           | Normal   |

### 4. Transaction Data (Generated offline)

| Entity               | Table                  | Sync Direction | Priority |
| -------------------- | ---------------------- | -------------- | -------- |
| Offline Transactions | `offline_transactions` | Push           | Critical |
| Offline Payments     | (embedded in payload)  | Push           | Critical |
| Cart Data            | (embedded in payload)  | Push           | High     |

---

## Relationships

```
Tenant (schema isolation)
 ├── POSTerminal
 │    ├── POSSession
 │    │    └── POSCart → POSCartItem → Product/ProductVariant
 │    └── OfflineTransaction (queued for sync)
 │         └── payload (header, line_items, payments, customer)
 │
 ├── OfflineSyncConfig (per-tenant settings)
 │    └── SyncLog (per-sync operation)
 │
 ├── Products → ProductVariant → Prices
 ├── Categories (hierarchical via MPTT)
 ├── Customers
 └── Tax Rates / Discount Rules
```

---

## Storage Strategy

### Server-Side (PostgreSQL)

- All models live in tenant-specific schemas (django-tenants).
- `OfflineSyncConfig`: one active config per tenant.
- `SyncLog`: append-only log of every sync operation.
- `OfflineTransaction`: queue table for incoming offline data.

### Client-Side (IndexedDB via Dexie.js)

- Products, variants, prices cached with TTL-based expiry.
- Customer data cached with shorter TTL (privacy).
- Transaction payloads stored until confirmed synced.
- Sync metadata stored for conflict detection.

### Storage Limits

| Store        | Recommended Limit | Notes                              |
| ------------ | ----------------- | ---------------------------------- |
| Products     | 50,000 records    | Full catalog                       |
| Prices       | 100,000 records   | All variant prices                 |
| Customers    | 10,000 records    | Recent/frequent                    |
| Transactions | 1,000 pending     | Configurable via OfflineSyncConfig |
| Total Local  | ~200 MB           | Browser IndexedDB quota            |

---

## Version Tracking

Each cached entity tracks:

| Field            | Purpose                                 |
| ---------------- | --------------------------------------- |
| `entity_id`      | Server UUID of the record               |
| `entity_type`    | Model name (e.g. `product`, `customer`) |
| `local_version`  | Client-side version counter             |
| `server_version` | Last known server version               |
| `last_synced_at` | Timestamp of last sync                  |
| `checksum`       | SHA-256 hash for integrity              |

Version mismatch between `local_version` and `server_version` triggers
conflict resolution per the tenant's `OfflineSyncConfig` strategy.

---

## Security Considerations

1. **Encryption at rest** – sensitive fields (customer PII, payment refs)
   should be encrypted in IndexedDB using the Web Crypto API.
2. **Token-scoped access** – offline cache is scoped to the authenticated
   session; clearing session clears cache.
3. **Payload integrity** – every `OfflineTransaction` stores a SHA-256
   `transaction_hash`; server verifies before processing.
4. **Audit trail** – `SyncLog` records who initiated each sync and all
   errors encountered.
5. **Data minimisation** – only cache entities required for offline
   operation; purge stale data per TTL.
