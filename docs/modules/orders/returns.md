# Order Module — Returns & Cancellations

## Returns Workflow

### Status Flow

```
REQUESTED → APPROVED → RECEIVED → INSPECTED → REFUNDED
         ↓
      REJECTED → CANCELLED
```

### Step 1: Create Return Request (Task 74)

**Service:** `ReturnService.create_return_request()`

- Customer or staff initiates return with reason and item list
- Validates return eligibility (status, return window, policy)
- Creates `OrderReturn` with `REQUESTED` status
- Creates `ReturnLineItem` entries with quantities
- Logs return request event

### Step 2: Approve/Reject Return (Task 75)

**Service:** `ReturnService.approve_return()` / `reject_return()`

**Approval:**

- Sets status to `APPROVED`, records approver and timestamp
- Calculates estimated refund amount
- Logs approval event

**Rejection:**

- Sets status to `REJECTED` with reason
- Logs rejection event

### Step 3: Receive Return Items (Task 76)

**Service:** `ReturnService.receive_return()`

- Inspects each item: condition (UNOPENED / OPENED / DAMAGED)
- Adjusts refund based on condition:
  - UNOPENED → 100% refund
  - OPENED → 80% refund + restocking fee
  - DAMAGED → 50% refund
- Marks items as inspected
- Triggers stock restoration
- Sets status to `RECEIVED`

### Step 4: Stock Restoration (Task 77)

**Service:** `ReturnService._restore_stock()`

- UNOPENED items → restored to sellable inventory
- OPENED items → logged for open-box handling
- DAMAGED items → logged as write-off
- Each item tracked with `stock_restored` and `stock_restored_at`

### Step 5: Process Refund (Task 77)

**Service:** `ReturnService.process_refund()`

- Validates return is in RECEIVED status
- Sets refund method (original_method, store_credit, cash, bank_transfer)
- Records `refunded_at` timestamp and `refund_reference`
- Sets status to `REFUNDED`
- Checks if entire order is returned

## Return Financial Fields

- `refund_amount` — Calculated net refund
- `restocking_fee` — Fee for opened/used items
- `refund_shipping` — Whether shipping is refunded
- `return_shipping_cost` — Cost of return shipping
- `refund_reference` — Payment gateway reference

---

## Cancellation Workflow

### Full Order Cancellation (Task 78)

**Service:** `CancellationService.cancel_order()`

1. Validates cancellation is allowed (status check, fulfillment check)
2. Cancels all active fulfillments
3. Releases reserved stock
4. Handles payment (void or refund)
5. Cancels all non-terminal line items
6. Transitions order to `CANCELLED`
7. Records `cancelled_at`, `cancelled_by`, `cancellation_reason`

### Cancellation Validation (Task 79)

**Service:** `CancellationService._validate_cancellation()`

- CANCELLED/RETURNED orders → always blocked
- SHIPPED/DELIVERED/COMPLETED → must use return process
- PROCESSING with active fulfillments (picked/packed/shipped) → blocked
- PROCESSING without active fulfillments → allowed (may require approval)

### Partial Cancellation (Task 80)

**Service:** `CancellationService.cancel_line_items()`

- Validates each item: checks fulfillment status, available quantity
- Updates `quantity_cancelled` per item
- Sets item status to CANCELLED if fully cancelled
- Recalculates order totals
- If ALL items cancelled → auto-cancels entire order
- Logs partial cancellation event

## Cancellable States

Orders can be cancelled from: `PENDING`, `CONFIRMED`, `PROCESSING`

Orders in `SHIPPED`, `DELIVERED`, `COMPLETED` must use the return workflow instead.
