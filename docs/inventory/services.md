# Inventory Services

## StockService

Core service for stock-in, stock-out, transfer, and reservation operations.

**Location:** `apps/inventory/stock/services/stock_service.py`

### Constructor

```python
StockService(user, notes="")
```

- `user` — `PlatformUser` performing the operation (required for audit trail).
- `notes` — Optional free-text notes attached to movements.

### Methods

#### `stock_in(product, quantity, warehouse, variant=None, location=None, cost_per_unit=None, reason="purchase", reference_type="", reference_id="")`

Receive stock into a warehouse. Creates or updates the `StockLevel` row and records a `StockMovement(type="in")`.

**Returns:** `OperationResult` with `data={"stock_level": ..., "movement": ...}`

#### `stock_out(product, quantity, warehouse, variant=None, location=None, reason="sale", reference_type="", reference_id="")`

Dispatch stock from a warehouse. Validates available quantity before deducting. Raises `StockOperationError` if insufficient.

**Returns:** `OperationResult`

#### `transfer(product, quantity, from_warehouse, to_warehouse, variant=None, from_location=None, to_location=None)`

Move stock between warehouses (or locations within the same warehouse). Creates two movements: one `out` from source, one `in` to destination. Both wrapped in a single transaction.

**Returns:** `OperationResult`

#### `reserve_stock(product, quantity, warehouse, variant=None, location=None, reference_type="", reference_id="")`

Reserve stock for a pending order. Increases `reserved_quantity` on the `StockLevel`. Does not decrease `quantity` — the stock is still physically present.

**Returns:** `OperationResult`

#### `release_stock(product, quantity, warehouse, variant=None, location=None)`

Release previously reserved stock (e.g., cancelled order). Decreases `reserved_quantity`.

**Returns:** `OperationResult`

#### `commit_reserved(product, quantity, warehouse, variant=None, location=None, reason="sale", reference_type="", reference_id="")`

Convert a reservation into an actual stock-out. Decreases both `quantity` and `reserved_quantity`.

**Returns:** `OperationResult`

#### `check_availability(product, warehouse, variant=None, location=None)`

Read-only check. Returns the current `StockLevel` data without locking.

**Returns:** `OperationResult` with availability data.

#### `validate_availability_or_raise(product, quantity, warehouse, variant=None, location=None)`

Raises `StockOperationError` if the requested quantity exceeds available stock.

---

## StockAdjustmentService

Manual stock adjustments with authorization thresholds.

**Location:** `apps/inventory/stock/services/adjustment_service.py`

### Constructor

```python
StockAdjustmentService(user, notes="")
```

### Methods

#### `requires_authorization(quantity, cost_per_unit=None)`

Returns `True` if the adjustment value exceeds `ADJUSTMENT_AUTHORIZATION_THRESHOLD` (100 units by default).

#### `adjust_up(product, quantity, warehouse, reason, variant=None, location=None, cost_per_unit=None, reference_id="", notes="")`

Increase stock level. Creates a `StockMovement(type="adjustment", reason=reason)`.

#### `adjust_down(product, quantity, warehouse, reason, variant=None, location=None, reference_id="", notes="")`

Decrease stock level. Validates that sufficient stock exists before adjusting.

---

## StockTakeService

Full stock-take lifecycle management.

**Location:** `apps/inventory/stock/services/stock_take_service.py`

### Constructor

```python
StockTakeService(user)
```

### Lifecycle Methods

| Method                                                            | Transition               | Description                                                      |
| ----------------------------------------------------------------- | ------------------------ | ---------------------------------------------------------------- |
| `create_stock_take(warehouse, name, scope, ...)`                  | → `draft`                | Creates a new stock take record.                                 |
| `start_stock_take(stock_take_id)`                                 | `draft` → `counting`     | Populates `StockTakeItem` rows from current `StockLevel` data.   |
| `record_count(stock_take_item_id, counted_quantity, user, notes)` | —                        | Records a physical count for one item. Auto-calculates variance. |
| `record_counts_bulk(counts_list, user)`                           | —                        | Records multiple counts in one transaction.                      |
| `submit_for_review(stock_take_id)`                                | `counting` → `review`    | Submits the count for supervisor review.                         |
| `approve_stock_take(stock_take_id, approver, notes)`              | `review` → `approved`    | Approves the stock take.                                         |
| `reject_stock_take(stock_take_id, approver, reason)`              | `review` → `counting`    | Rejects back to counting with a reason.                          |
| `complete_stock_take(stock_take_id, user, force)`                 | `approved` → `completed` | Finalises and optionally creates adjustment movements.           |
| `cancel_stock_take(stock_take_id)`                                | `*` → `cancelled`        | Cancels the stock take (except completed).                       |
| `get_report_data(stock_take_id)`                                  | —                        | Returns variance report data.                                    |

### Blind Counts

When `is_blind_count=True`, the API hides `expected_quantity` from the counting interface. Counters only see product name, SKU, and location. Variances are revealed during review.

---

## OperationResult

Structured result object returned by all service methods.

**Location:** `apps/inventory/stock/results.py`

```python
@dataclass
class OperationResult:
    success: bool
    operation_type: str
    timestamp: datetime
    data: dict | None
    errors: list[str]
    warnings: list[str]
    message: str
```

### Class Methods

- `OperationResult.ok(operation_type, data=None, warnings=None, message="")` — Success result.
- `OperationResult.fail(operation_type, errors)` — Failure result.

### Instance Methods

- `to_dict()` — Serializable dictionary for API responses.

---

## Concurrency Model

All write operations use:

1. `@transaction.atomic` — ensures all-or-nothing updates.
2. `select_for_update()` — acquires row-level locks on `StockLevel` before reading/writing.

This prevents:

- **Lost updates:** Two concurrent stock-outs reading the same quantity.
- **Negative stock:** Over-selling via race conditions.
- **Partial transfers:** Source debited but destination not credited.
