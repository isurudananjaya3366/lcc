# Cacheable Entities

> POS Offline Mode – Entity Caching Reference

## Overview

This document lists all entities that should be cached locally on POS
terminals for offline operation, organised by sync priority. Each entry
specifies the recommended TTL, sync frequency, approximate size per
record, sync direction, and filtering criteria.

---

## Priority 1 – Critical (Real-time, TTL ≤ 5 min)

| Entity                | TTL   | Sync Freq   | Size/Record | Direction | Filter          |
| --------------------- | ----- | ----------- | ----------- | --------- | --------------- |
| Tax Rates             | 5 min | Every 5 min | ~200 B      | Pull      | Active only     |
| POS Settings          | 5 min | Every 5 min | ~1 KB       | Pull      | Current tenant  |
| Payment Method Config | 5 min | Every 5 min | ~500 B      | Pull      | Enabled methods |

**Staleness handling:** BLOCK – terminal must not process sales with
outdated tax rates or disabled payment methods.

---

## Priority 2 – High (Near Real-time, TTL ≤ 30 min)

| Entity           | TTL    | Sync Freq    | Size/Record | Direction | Filter                     |
| ---------------- | ------ | ------------ | ----------- | --------- | -------------------------- |
| Product Prices   | 30 min | Every 30 min | ~150 B      | Pull      | Active price lists         |
| Products         | 60 min | Every 60 min | ~2 KB       | Pull      | is_active, saleable        |
| Product Variants | 60 min | Every 60 min | ~800 B      | Pull      | Active parent              |
| Discount Rules   | 30 min | Every 30 min | ~500 B      | Pull      | Active, current date range |

**Staleness handling:** WARN – show warning to cashier but allow sale.

---

## Priority 3 – Normal (Fresh, TTL ≤ 4 hours)

| Entity        | TTL  | Sync Freq  | Size/Record | Direction     | Filter           |
| ------------- | ---- | ---------- | ----------- | ------------- | ---------------- |
| Customers     | 4 hr | Every 2 hr | ~1 KB       | Bidirectional | Frequent/recent  |
| Employees     | 4 hr | Every 4 hr | ~500 B      | Pull          | Active, POS role |
| Terminals     | 1 hr | Every 1 hr | ~1 KB       | Pull          | Same warehouse   |
| Quick Buttons | 4 hr | Every 4 hr | ~300 B      | Pull          | Active groups    |

**Staleness handling:** ALLOW – use cached data silently, queue refresh.

---

## Priority 4 – Low (Acceptable, TTL ≤ 24 hours)

| Entity           | TTL    | Sync Freq | Size/Record | Direction | Filter      |
| ---------------- | ------ | --------- | ----------- | --------- | ----------- |
| Categories       | 24 hr  | Daily     | ~200 B      | Pull      | Active tree |
| Units of Measure | 7 days | Weekly    | ~100 B      | Pull      | All         |
| Warehouses       | 24 hr  | Daily     | ~500 B      | Pull      | Active      |

**Staleness handling:** ALLOW – minimal business impact.

---

## Priority 5 – Deferred (On-demand, TTL > 24 hours)

| Entity             | TTL     | Sync Freq | Size/Record | Direction | Filter         |
| ------------------ | ------- | --------- | ----------- | --------- | -------------- |
| Product Images     | 30 days | On-demand | ~50 KB      | Pull      | Thumbnail only |
| Historical Reports | N/A     | Manual    | Variable    | Pull      | None           |

**Staleness handling:** ALLOW – fetched only when explicitly requested.

---

## Sync Dependency Order

Entities must be synced in dependency order to satisfy foreign-key
relationships on the client:

```
1. Tax Rates, POS Settings, Payment Methods   (no deps)
2. Categories                                  (self-referential MPTT)
3. Products                                    (→ Category)
4. Product Variants                            (→ Product)
5. Product Prices / Discount Rules             (→ Variant / Product)
6. Customers                                   (no deps)
7. Employees, Terminals                        (no deps)
8. Quick Buttons                               (→ Product / Category)
```

---

## Size Estimates (Typical Retail Store)

| Entity         | Record Count | Per Record | Total      |
| -------------- | ------------ | ---------- | ---------- |
| Products       | 5,000        | 2 KB       | 10 MB      |
| Variants       | 15,000       | 800 B      | 12 MB      |
| Prices         | 15,000       | 150 B      | 2.3 MB     |
| Customers      | 3,000        | 1 KB       | 3 MB       |
| Categories     | 200          | 200 B      | 40 KB      |
| Tax Rates      | 10           | 200 B      | 2 KB       |
| Discount Rules | 50           | 500 B      | 25 KB      |
| **Total**      |              |            | **~28 MB** |

Large stores (50k+ products) should enable `low_bandwidth_mode` in
`OfflineSyncConfig` and use incremental sync.

---

## Filtering Criteria

- **Products**: `is_active=True`, `is_deleted=False`, available in the
  terminal's warehouse.
- **Customers**: last purchase within 90 days OR loyalty member.
- **Employees**: `is_active=True`, assigned POS role for current
  warehouse.
- **Discount Rules**: `is_active=True`, within valid date range.
- **Prices**: current price list for terminal's warehouse.
