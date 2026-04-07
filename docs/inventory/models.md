# Inventory Models

## StockLevel

Tracks the current stock position for a specific product (or variant) at a warehouse/location.

**Location:** `apps/inventory/stock/models/stock_level.py`

### Fields

| Field               | Type                 | Description                                      |
| ------------------- | -------------------- | ------------------------------------------------ |
| `product`           | FK → Product         | Required. The product being tracked.             |
| `variant`           | FK → ProductVariant  | Optional. Specific variant (size, colour, etc.). |
| `warehouse`         | FK → Warehouse       | Required. Physical warehouse.                    |
| `location`          | FK → StorageLocation | Optional. Bin/shelf within warehouse.            |
| `quantity`          | Decimal(15,3)        | Total physical quantity on hand.                 |
| `reserved_quantity` | Decimal(15,3)        | Quantity reserved for pending orders.            |
| `incoming_quantity` | Decimal(15,3)        | Quantity expected from purchase orders.          |
| `reorder_point`     | Decimal(15,3)        | Threshold that triggers reorder alerts.          |
| `cost_per_unit`     | Decimal(15,3)        | Current weighted-average cost.                   |
| `last_stock_update` | DateTime             | Timestamp of the most recent change.             |

### Computed Properties

| Property             | Formula                                                            |
| -------------------- | ------------------------------------------------------------------ |
| `available_quantity` | `quantity - reserved_quantity`                                     |
| `projected_quantity` | `available_quantity + incoming_quantity`                           |
| `stock_value`        | `quantity × cost_per_unit`                                         |
| `stock_status`       | One of: `out_of_stock`, `critical`, `low`, `adequate`, `overstock` |

### Constraints

- **Unique together:** `(product, variant, warehouse, location)` — one row per combination.
- **Non-negative:** `quantity >= 0`, `reserved_quantity >= 0`.

### Manager: `StockLevelManager`

Key queryset methods:

- `for_product(product, variant=None)` — filter by product/variant
- `for_warehouse(warehouse)` — filter by warehouse
- `low_stock()` — quantity ≤ reorder_point (non-zero)
- `out_of_stock()` — quantity = 0
- `in_stock()` — quantity > 0
- `get_or_create_level(product, warehouse, variant=None, location=None)` — upsert

---

## StockMovement

Immutable audit record of every stock quantity change.

**Location:** `apps/inventory/stock/models/stock_movement.py`

### Fields

| Field              | Type                 | Description                                                                                               |
| ------------------ | -------------------- | --------------------------------------------------------------------------------------------------------- |
| `product`          | FK → Product         | Product affected.                                                                                         |
| `variant`          | FK → ProductVariant  | Optional variant.                                                                                         |
| `movement_type`    | Choice               | `in`, `out`, `transfer`, `adjustment`, `return`, `reservation`, `release`                                 |
| `quantity`         | Decimal(15,3)        | Amount moved (always positive).                                                                           |
| `reason`           | Choice               | `purchase`, `sale`, `transfer`, `adjustment`, `return`, `damaged`, `expired`, `found`, `initial`, `other` |
| `from_warehouse`   | FK → Warehouse       | Source warehouse (for out/transfer).                                                                      |
| `to_warehouse`     | FK → Warehouse       | Destination warehouse (for in/transfer).                                                                  |
| `from_location`    | FK → StorageLocation | Source bin (optional).                                                                                    |
| `to_location`      | FK → StorageLocation | Destination bin (optional).                                                                               |
| `cost_per_unit`    | Decimal(15,3)        | Cost at time of movement.                                                                                 |
| `reference_type`   | CharField            | E.g., `purchase_order`, `sales_order`.                                                                    |
| `reference_id`     | CharField            | UUID or code of the source document.                                                                      |
| `reference_number` | CharField            | Human-readable reference.                                                                                 |
| `notes`            | TextField            | Free-text notes.                                                                                          |
| `is_reversed`      | Boolean              | True if this movement has been reversed.                                                                  |
| `reversed_by`      | FK → self            | Points to the reversal movement.                                                                          |
| `movement_date`    | DateTime             | When the movement occurred.                                                                               |
| `created_by`       | FK → PlatformUser    | Who initiated the movement.                                                                               |

### Validation (`clean()`)

- `in` movements must have `to_warehouse`.
- `out` movements must have `from_warehouse`.
- `transfer` movements must have both `from_warehouse` and `to_warehouse`.

### Methods

- `reverse()` — Creates a mirror movement that cancels this one. Marks original as `is_reversed`.
- `total_cost` — `quantity × cost_per_unit`.

---

## StockTake

Represents a physical inventory count event.

**Location:** `apps/inventory/stock/models/stock_take.py`

### Fields

| Field                  | Type              | Description                                                         |
| ---------------------- | ----------------- | ------------------------------------------------------------------- |
| `reference`            | CharField         | Auto-generated reference (e.g., `ST-20250101-0001`).                |
| `name`                 | CharField         | Human-readable name.                                                |
| `warehouse`            | FK → Warehouse    | Target warehouse.                                                   |
| `status`               | Choice            | `draft`, `counting`, `review`, `approved`, `completed`, `cancelled` |
| `scope`                | Choice            | `full`, `partial`, `cycle`                                          |
| `is_blind_count`       | Boolean           | If true, counters cannot see expected quantities.                   |
| `description`          | TextField         | Optional description.                                               |
| `scheduled_date`       | DateField         | When the count is planned.                                          |
| `started_at`           | DateTime          | When counting actually began.                                       |
| `completed_at`         | DateTime          | When the count was finalised.                                       |
| `cancelled_at`         | DateTime          | When cancelled (if applicable).                                     |
| `total_items`          | Integer           | Number of items to count.                                           |
| `counted_items`        | Integer           | Items counted so far.                                               |
| `items_with_variance`  | Integer           | Items where counted ≠ expected.                                     |
| `total_variance_value` | Decimal           | Monetary value of all variances.                                    |
| `approval_status`      | Choice            | `pending`, `approved`, `rejected`                                   |
| `created_by`           | FK → PlatformUser | Creator.                                                            |
| `completed_by`         | FK → PlatformUser | Who completed.                                                      |
| `approved_by`          | FK → PlatformUser | Who approved.                                                       |

### Status Transitions

```
draft → counting → review → approved → completed
  ↓        ↓         ↓
cancelled cancelled cancelled
```

### Aggregated Property

- `progress_percentage` — `(counted_items / total_items) × 100`

---

## StockTakeItem

Individual line item in a stock take.

**Location:** `apps/inventory/stock/models/stock_take_item.py`

### Fields

| Field                 | Type                 | Description                                       |
| --------------------- | -------------------- | ------------------------------------------------- |
| `stock_take`          | FK → StockTake       | Parent stock take.                                |
| `product`             | FK → Product         | Product being counted.                            |
| `variant`             | FK → ProductVariant  | Optional variant.                                 |
| `location`            | FK → StorageLocation | Optional bin location.                            |
| `expected_quantity`   | Decimal              | System quantity at start of count.                |
| `counted_quantity`    | Decimal              | Physically counted quantity (null until counted). |
| `system_quantity`     | Decimal              | Snapshot of system quantity.                      |
| `variance_quantity`   | Decimal              | `counted - expected` (auto-calculated on save).   |
| `variance_percentage` | Decimal              | `(variance / expected) × 100`.                    |
| `variance_value`      | Decimal              | `variance_quantity × cost_per_unit`.              |
| `cost_per_unit`       | Decimal              | Item cost at time of count.                       |
| `expected_value`      | Decimal              | `expected × cost`.                                |
| `counted_value`       | Decimal              | `counted × cost`.                                 |
| `status`              | Choice               | `pending`, `counted`, `recounted`, `verified`     |
| `count_sequence`      | Integer              | Order in which items should be counted.           |
| `is_locked`           | Boolean              | Cannot be modified once locked.                   |
| `requires_recount`    | Boolean              | Flagged for re-counting.                          |
| `notes`               | TextField            | Counter notes.                                    |
| `discrepancy_reason`  | TextField            | Explanation for variances.                        |
| `counted_by`          | FK → PlatformUser    | Who performed the count.                          |
| `counted_at`          | DateTime             | When counted.                                     |

### Methods

- `calculate_variance()` — Computes variance fields from expected/counted.
- `get_variance_classification()` — Returns `"exact"`, `"minor"` (≤2%), `"moderate"` (≤5%), `"significant"` (≤10%), or `"critical"` (>10%).
