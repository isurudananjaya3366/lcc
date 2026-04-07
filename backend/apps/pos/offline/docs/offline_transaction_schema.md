# Offline Transaction Schema

> POS Offline Mode – Transaction Payload Reference

## Overview

This document defines the JSON structure of an offline transaction
payload stored in `OfflineTransaction.payload`. The schema covers the
transaction header, line items, payments, optional customer data,
and metadata used for validation and integrity verification.

---

## Top-Level Structure

```json
{
  "header": { ... },
  "line_items": [ ... ],
  "payments": [ ... ],
  "customer": { ... }
}
```

| Key          | Type   | Required  | Description                            |
| ------------ | ------ | --------- | -------------------------------------- |
| `header`     | object | Yes       | Transaction header with totals and IDs |
| `line_items` | array  | Yes (≥ 1) | Products sold in this transaction      |
| `payments`   | array  | Yes (≥ 1) | Payment tenders applied                |
| `customer`   | object | No        | Customer info (null for walk-ins)      |

---

## Header Object

| Field               | Type           | Required | Description                             |
| ------------------- | -------------- | -------- | --------------------------------------- |
| `offline_id`        | UUID string    | Yes      | Client-generated unique ID              |
| `transaction_type`  | string         | Yes      | `sale` / `refund` / `exchange` / `void` |
| `offline_timestamp` | ISO 8601       | Yes      | When transaction was created offline    |
| `terminal_id`       | string         | Yes      | Terminal code or UUID                   |
| `employee_id`       | string         | Yes      | Employee who processed the transaction  |
| `customer_id`       | string         | No       | Server customer UUID (null = walk-in)   |
| `subtotal`          | decimal string | Yes      | Sum of line totals before tax           |
| `tax_total`         | decimal string | Yes      | Total tax amount                        |
| `discount_total`    | decimal string | Yes      | Total discounts applied                 |
| `grand_total`       | decimal string | Yes      | Final amount payable                    |
| `notes`             | string         | No       | Cashier notes                           |

---

## Line Item Object

| Field             | Type           | Required | Description                       |
| ----------------- | -------------- | -------- | --------------------------------- |
| `line_id`         | string         | Yes      | Client-generated line ID          |
| `product_id`      | string         | Yes      | Server product UUID               |
| `variant_id`      | string         | No       | Server variant UUID (null if N/A) |
| `sku`             | string         | Yes      | Product SKU                       |
| `product_name`    | string         | Yes      | Display name (cached)             |
| `quantity`        | decimal string | Yes      | Quantity sold                     |
| `unit_price`      | decimal string | Yes      | Unit price at time of sale        |
| `discount_amount` | decimal string | Yes      | Line discount                     |
| `tax_rate`        | decimal string | Yes      | Applicable tax rate (0.12 = 12 %) |
| `tax_amount`      | decimal string | Yes      | Calculated tax for line           |
| `line_total`      | decimal string | Yes      | Final line amount incl. tax       |
| `notes`           | string         | No       | Line-level notes                  |

---

## Payment Object

| Field              | Type           | Required | Description                             |
| ------------------ | -------------- | -------- | --------------------------------------- |
| `payment_id`       | string         | Yes      | Client-generated payment ID             |
| `payment_method`   | string         | Yes      | `cash` / `card` / `mobile_frimi` / etc. |
| `amount`           | decimal string | Yes      | Amount tendered                         |
| `reference_number` | string         | No       | Card auth, mobile ref, etc.             |
| `timestamp`        | ISO 8601       | Yes      | When payment was captured               |
| `change_amount`    | decimal string | No       | Change returned (cash only)             |
| `status`           | string         | Yes      | `completed` / `pending`                 |

---

## Customer Object (Optional)

| Field            | Type   | Required | Description                 |
| ---------------- | ------ | -------- | --------------------------- |
| `id`             | string | Yes      | Server customer UUID        |
| `name`           | string | Yes      | Customer display name       |
| `phone`          | string | No       | Phone number                |
| `email`          | string | No       | Email address               |
| `loyalty_number` | string | No       | Loyalty programme reference |

---

## Validation Rules

1. `header` key must exist and contain all required fields.
2. `line_items` must be a non-empty array (≥ 1 item).
3. `payments` must be a non-empty array (≥ 1 payment).
4. Sum of `payments[].amount` must equal `header.grand_total`.
5. Sum of `line_items[].line_total` must match calculated totals.
6. All decimal values are strings with 2 decimal places.
7. All UUIDs must be valid UUID v4 format.
8. `offline_timestamp` and `payments[].timestamp` must be valid ISO 8601.

---

## Integrity Verification

The `OfflineTransaction.transaction_hash` field stores a SHA-256 hex
digest of the normalised `payload` JSON (keys sorted, no extra
whitespace). Before processing, the server recalculates the hash and
compares; a mismatch flags the transaction for manual review.

---

## Size Guidelines

| Transaction Size | Line Items | Payments | Approx. Payload |
| ---------------- | ---------- | -------- | --------------- |
| Small            | 1–5        | 1        | 1–3 KB          |
| Medium           | 5–20       | 1–2      | 3–8 KB          |
| Large            | 20–50      | 1–3      | 8–20 KB         |
| Bulk             | 50+        | 1–5      | 20–50 KB        |

Payloads exceeding 50 KB should be compressed (`payload_compressed=True`).
