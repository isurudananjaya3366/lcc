# Data Freshness Requirements

> POS Offline Mode – Staleness & Refresh Policy Reference

## Overview

This document defines how fresh (recent) cached data must be for each
entity type when a POS terminal is operating offline. It establishes
acceptable staleness levels, handling strategies, business-impact
assessments, and refresh trigger mechanisms.

**Staleness** = `now − cache_timestamp`. If staleness exceeds the
entity's maximum allowed TTL the appropriate handling strategy is
applied.

---

## Freshness Categories

| Category             | Staleness Threshold | TTL    | Description                 |
| -------------------- | ------------------- | ------ | --------------------------- |
| **Real-time**        | < 5 minutes         | 5 min  | Mission-critical config     |
| **Near Real-time**   | 5 – 30 minutes      | 30 min | Financial data              |
| **Fresh**            | 30 min – 4 hours    | 4 hr   | Core master data            |
| **Acceptable**       | 4 – 24 hours        | 24 hr  | Reference / supporting data |
| **Stale-acceptable** | > 24 hours          | 7 days | Static / historical data    |

---

## Critical Entities (Strategy: BLOCK)

Operations **must not proceed** if these entities are stale beyond the
stated threshold.

| Entity          | Max Staleness | Refresh Trigger | Business Impact                      |
| --------------- | ------------- | --------------- | ------------------------------------ |
| Tax Rates       | 5 min         | Auto + Manual   | Compliance violations, incorrect tax |
| POS Settings    | 5 min         | Auto + On-login | Operational errors                   |
| Payment Methods | 15 min        | Auto            | Payment processing failures          |

---

## High-Priority Entities (Strategy: WARN)

A warning is shown to the cashier but the operation is **allowed to
continue** if confirmed.

| Entity           | Max Staleness | Refresh Trigger | Business Impact             |
| ---------------- | ------------- | --------------- | --------------------------- |
| Product Prices   | 30 min        | Auto + Manual   | Incorrect charges           |
| Products         | 4 hr          | Auto            | Outdated product info       |
| Product Variants | 4 hr          | Auto            | Incorrect variant selection |
| Discount Rules   | 2 hr          | Auto + Manual   | Incorrect discounts         |

---

## Normal-Priority Entities (Strategy: ALLOW)

Stale data is used silently; a background refresh is scheduled.

| Entity        | Max Staleness | Refresh Trigger  | Business Impact              |
| ------------- | ------------- | ---------------- | ---------------------------- |
| Customers     | 4 hr          | Auto + On-search | Outdated customer info       |
| Employees     | 4 hr          | Auto + On-login  | Outdated employee list       |
| Terminals     | 1 hr          | Auto             | Minor terminal mismatch      |
| Quick Buttons | 4 hr          | Auto             | Stale quick-access shortcuts |
| Categories    | 24 hr         | Auto (daily)     | Minor categorisation issues  |

---

## Low-Priority Entities (Strategy: ALLOW)

| Entity           | Max Staleness | Refresh Trigger | Business Impact     |
| ---------------- | ------------- | --------------- | ------------------- |
| Units of Measure | 7 days        | Manual          | Minimal             |
| Warehouses       | 24 hr         | Auto (daily)    | Minor info mismatch |
| Product Images   | 30 days       | On-demand       | Visual only         |
| Historical Data  | N/A           | Manual          | Reference only      |

---

## Staleness Detection

```
1. Access cached entity
2. Read cache_timestamp from local store
3. Calculate age = now − cache_timestamp
4. Compare age against entity's max staleness
5. If age ≤ threshold → data is FRESH → use directly
6. If age > threshold → data is STALE → apply handling strategy
```

---

## Handling Strategies

### BLOCK

- Prevent the operation from proceeding.
- Display error: _"Cannot process sale — tax rates are outdated. Refreshing…"_
- Force an immediate foreground refresh.
- Log the blocked attempt for monitoring.

### WARN

- Display warning: _"Product prices may be outdated (2 hours old). Refresh now or continue?"_
- Allow the user to confirm or trigger a manual refresh.
- Log the warning and user decision.

### ALLOW

- Use cached data without user interruption.
- Queue a background refresh for the entity.
- Log staleness for monitoring dashboards.

### FALLBACK

- Attempt to use an alternative data source (e.g. default tax rate).
- Fall back to last-known-good value if alternative is unavailable.
- Log fallback usage for auditing.

---

## Refresh Triggers

| Trigger          | Description                         | Entities Affected              |
| ---------------- | ----------------------------------- | ------------------------------ |
| **Automatic**    | Background check at TTL expiry      | All cached entities            |
| **Manual**       | User presses "Sync Now"             | All cached entities            |
| **On-Login**     | Refresh when user authenticates     | Settings, employees, terminals |
| **On-Search**    | Refresh when entity is looked up    | Customers                      |
| **On-Demand**    | Fetch when accessed and found stale | Product images, historical     |
| **Event-Driven** | Server push via WebSocket           | Tax rates, prices, settings    |

---

## Business Impact Summary

| Impact Level | Examples                            | Required Response                  |
| ------------ | ----------------------------------- | ---------------------------------- |
| **Critical** | Wrong tax, disabled payment method  | Block operation, force refresh     |
| **High**     | Outdated price, wrong discount      | Warn user, allow with confirmation |
| **Medium**   | Old customer info, stale categories | Silent background refresh          |
| **Low**      | Historical data, images             | Scheduled or on-demand refresh     |

---

## Monitoring Recommendations

### Metrics to Track

- Average staleness per entity type per terminal.
- Percentage of sales processed with stale data.
- Refresh success / failure rates.
- Time since last successful refresh per terminal.
- Count of BLOCK and WARN events per day.

### Alert Conditions

- Tax rates stale for > 10 minutes.
- Prices not refreshed in > 1 hour.
- Three or more consecutive refresh failures.
- Any terminal with > 50 % stale-data warnings in a shift.

### Reporting

- Daily freshness summary per terminal.
- Entity-wise refresh success dashboard.
- Trend analysis on staleness-related blocks and warnings.
