# Inventory Module Architecture

## Design Principles

1. **Service layer pattern** — All business logic lives in services, not in models or views. Views are thin dispatchers.
2. **Immutable audit trail** — Every stock change creates a `StockMovement`. Movements are never deleted or modified (except marking `is_reversed`).
3. **Pessimistic locking** — `SELECT … FOR UPDATE` on `StockLevel` rows prevents race conditions.
4. **Structured results** — All service methods return `OperationResult`, never raise on business errors (only on programming errors).

## Module Structure

```
apps/inventory/stock/
├── __init__.py
├── constants.py           # All enums, thresholds, choices
├── exceptions.py          # StockOperationError
├── results.py             # OperationResult dataclass
├── models/
│   ├── __init__.py
│   ├── stock_level.py     # StockLevel + StockLevelManager
│   ├── stock_movement.py  # StockMovement + StockMovementManager
│   ├── stock_take.py      # StockTake + StockTakeManager
│   └── stock_take_item.py # StockTakeItem + StockTakeItemManager
├── services/
│   ├── __init__.py
│   ├── stock_service.py       # StockIn/Out/Transfer/Reserve/Release/Commit
│   ├── adjustment_service.py  # AdjustUp/AdjustDown with auth thresholds
│   ├── stock_take_service.py  # Full stock-take lifecycle
│   ├── batch_operations.py    # Bulk stock operations
│   └── costing.py             # Weighted-average cost calculations
└── api/
    ├── __init__.py
    ├── urls.py            # DefaultRouter registration
    ├── views.py           # 4 ViewSets
    └── serializers.py     # Read/write serializers
```

## Data Flow

### Stock-In Operation

```
API Request → StockOperationViewSet.stock_in()
  → StockInSerializer validates payload
  → _resolve_objects() fetches Product, Warehouse, etc.
  → StockService(user).stock_in(...)
    → @transaction.atomic
    → StockLevel.objects.select_for_update().get_or_create(...)
    → level.quantity += quantity
    → level.save()
    → StockMovement.objects.create(type="in", ...)
    → return OperationResult.ok("stock_in", data={...})
  → Response(result.to_dict(), 201)
```

### Transfer Operation

```
StockService.transfer(product, qty, from_wh, to_wh)
  → @transaction.atomic
  → source_level = select_for_update().get(product, from_wh)
  → validate available_quantity >= qty
  → source_level.quantity -= qty → save
  → dest_level = get_or_create(product, to_wh)
  → dest_level.quantity += qty → save
  → create StockMovement(type="transfer", from=from_wh, to=to_wh)
  → return OperationResult.ok(...)
```

### Stock Take Lifecycle

```
create_stock_take() → StockTake(status="draft")
     ↓
start_stock_take() → status="counting"
  → For each StockLevel in warehouse:
      create StockTakeItem(expected_quantity=level.quantity)
     ↓
record_count() → StockTakeItem.counted_quantity = X
  → calculate_variance() auto-computed on save
     ↓
submit_for_review() → status="review"
     ↓
approve_stock_take() → approval_status="approved"
     ↓
complete_stock_take() → status="completed"
  → For each item with variance:
      AdjustmentService.adjust_up/down() to reconcile
```

## Concurrency Strategy

### Problem

Multiple users or processes updating the same `StockLevel` row simultaneously:

- User A reads quantity = 100
- User B reads quantity = 100
- User A writes quantity = 90 (sold 10)
- User B writes quantity = 95 (sold 5)
- **Result:** quantity = 95, but should be 85

### Solution

All service methods that modify `StockLevel` use:

```python
@transaction.atomic
def stock_out(self, ...):
    level = StockLevel.objects.select_for_update().get(...)
    # Row is now locked — other transactions wait here
    level.quantity -= quantity
    level.save()
```

`select_for_update()` acquires a PostgreSQL row-level lock. Concurrent transactions block until the lock is released (at commit/rollback).

### Trade-offs

- **Correctness:** Prevents all lost-update and negative-stock bugs.
- **Throughput:** Serialises writes to the same row. Acceptable for POS workloads.
- **Deadlock risk:** Minimal — each operation locks only one `StockLevel` row (two for transfers, always in consistent order).

## Multi-Tenancy

The module uses `django-tenants`. All queries run within a tenant schema context. `StockLevel`, `StockMovement`, `StockTake`, and `StockTakeItem` are tenant-specific tables.

## Constants & Thresholds

Defined in `constants.py`:

| Constant                             | Value | Purpose                                   |
| ------------------------------------ | ----- | ----------------------------------------- |
| `VARIANCE_THRESHOLD_MINOR`           | 2%    | Minor variance classification             |
| `VARIANCE_THRESHOLD_MODERATE`        | 5%    | Moderate variance                         |
| `VARIANCE_THRESHOLD_SIGNIFICANT`     | 10%   | Significant variance                      |
| `DEFAULT_REORDER_POINT`              | 10    | Default reorder alert threshold           |
| `ADJUSTMENT_AUTHORIZATION_THRESHOLD` | 100   | Adjustments above this need authorisation |
