# Order Module — Models Reference

## Order

The core order model representing a customer purchase.

| Field                              | Type                | Description                                   |
| ---------------------------------- | ------------------- | --------------------------------------------- |
| `id`                               | UUID                | Primary key                                   |
| `order_number`                     | CharField(50)       | Auto-generated (ORD-YYYYMMDD-NNNN)            |
| `status`                           | CharField(30)       | Order lifecycle status                        |
| `source`                           | CharField(20)       | Channel: pos, webstore, quote, manual, import |
| `priority`                         | CharField(20)       | normal, high, urgent, low                     |
| `customer`                         | FK → Customer       | Optional customer reference                   |
| `customer_name/email/phone`        | CharField           | Denormalized customer info                    |
| `billing_address/shipping_address` | JSONField           | Address data                                  |
| `subtotal`                         | Decimal(12,2)       | Sum of line items before discounts            |
| `discount_type/value/amount`       | Various             | Order-level discount                          |
| `tax_amount`                       | Decimal(12,2)       | Calculated tax                                |
| `shipping_amount`                  | Decimal(12,2)       | Shipping charges                              |
| `total_amount`                     | Decimal(12,2)       | Grand total                                   |
| `payment_status`                   | CharField(20)       | unpaid, partial, paid, refunded               |
| `amount_paid/balance_due`          | Decimal(12,2)       | Payment tracking                              |
| `is_draft/is_locked`               | Boolean             | Draft and lock flags                          |
| `notes/internal_notes`             | TextField           | Customer/staff notes                          |
| `tags`                             | JSONField           | Flexible tagging                              |
| `created_by/assigned_to`           | FK → User           | Users                                         |
| `cancellation_reason/notes`        | TextField           | Cancellation details                          |
| `lock_reason/lock_notes`           | CharField/TextField | Lock details                                  |

### Key Properties

- `is_editable` — True if status in PENDING/CONFIRMED and not locked
- `can_cancel` — True if in a cancellable state
- `is_overdue` — True if past expected delivery date
- `is_fully_paid` — True if balance_due ≤ 0
- `profit_margin` — Calculated margin percentage

---

## OrderLineItem

Individual items within an order.

| Field                                   | Type          | Description                       |
| --------------------------------------- | ------------- | --------------------------------- |
| `order`                                 | FK → Order    | Parent order                      |
| `product/variant`                       | FK            | Product references                |
| `item_name/item_sku`                    | CharField     | Denormalized (historical)         |
| `quantity_ordered`                      | Decimal(12,3) | Ordered quantity                  |
| `quantity_fulfilled/returned/cancelled` | Decimal(12,3) | Lifecycle quantities              |
| `unit_price/total_price`                | Decimal(12,2) | Pricing                           |
| `discount_type/value/amount`            | Various       | Line-item discount                |
| `tax_rate/tax_amount`                   | Decimal       | Tax                               |
| `position`                              | Integer       | Display order                     |
| `status`                                | CharField(20) | pending, confirmed, shipped, etc. |

### Key Properties

- `is_fully_fulfilled` — All ordered quantity fulfilled
- `quantity_remaining` — Outstanding quantity
- `product_display` — Formatted product name with variant

---

## Fulfillment

Shipment tracking for order items.

| Field                                 | Type           | Description           |
| ------------------------------------- | -------------- | --------------------- |
| `order`                               | FK → Order     | Parent order          |
| `fulfillment_number`                  | CharField(50)  | FUL-{ORDER}-{SEQ}     |
| `status`                              | CharField(20)  | Fulfillment lifecycle |
| `warehouse`                           | FK → Warehouse | Source warehouse      |
| `carrier/carrier_service`             | CharField      | Shipping carrier      |
| `tracking_number/tracking_url`        | CharField/URL  | Tracking info         |
| `shipped_at/delivered_at`             | DateTime       | Milestones            |
| `weight/dimensions/volumetric_weight` | Various        | Package data          |
| `number_of_packages`                  | Integer        | Package count         |
| `is_international`                    | Boolean        | International flag    |
| `customs_value/description`           | Various        | Customs data          |

### Key Methods

- `generate_tracking_url()` — Auto-build URL from carrier+tracking
- `calculate_volumetric_weight()` — From dimensions
- `get_total_quantity()` — Sum of line item quantities
- `get_fulfillment_percentage()` — % of order fulfilled
- `can_cancel()` — Whether cancellation is allowed

---

## OrderReturn

Return/RMA tracking.

| Field                          | Type           | Description            |
| ------------------------------ | -------------- | ---------------------- |
| `order`                        | FK → Order     | Original order         |
| `return_number`                | CharField(50)  | RET-{YEAR}-{SEQ}       |
| `status`                       | CharField(20)  | Return lifecycle       |
| `reason`                       | CharField(30)  | Return reason category |
| `refund_amount/restocking_fee` | Decimal(12,2)  | Financial              |
| `refund_method`                | CharField(30)  | Refund channel         |
| `refund_reference`             | CharField(100) | Gateway reference      |
| `return_shipping_cost`         | Decimal(12,2)  | Return shipping        |

### Key Methods

- `calculate_refund_amount()` — Net refund calculation
- `is_refund_eligible()` — Status check
- `is_approved()` / `is_completed()` / `can_receive()` — Status helpers

---

## OrderHistory

Audit trail for all order changes.

| Field                   | Type          | Description                |
| ----------------------- | ------------- | -------------------------- |
| `order`                 | FK → Order    | Related order              |
| `event_type`            | CharField(50) | Event category             |
| `actor`                 | FK → User     | Who performed the action   |
| `actor_role/source`     | CharField     | Context                    |
| `old_values/new_values` | JSONField     | Before/after snapshots     |
| `description`           | TextField     | Human-readable description |

---

## OrderSettings

Per-tenant order configuration.

| Field                      | Type          | Description               |
| -------------------------- | ------------- | ------------------------- |
| `order_prefix`             | CharField(10) | Order number prefix       |
| `default_currency`         | CharField(3)  | Default currency          |
| `auto_confirm_paid_orders` | Boolean       | Auto-confirm when paid    |
| `allow_guest_checkout`     | Boolean       | Guest orders allowed      |
| `default_tax_rate`         | Decimal(5,2)  | Default tax %             |
| `return_window_days`       | Integer       | Return eligibility window |
| `low_stock_threshold`      | Integer       | Stock warning level       |
| `max_discount_percent`     | Decimal(5,2)  | Max allowed discount      |
