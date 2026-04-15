# POS Workflows

## 1. Complete Sale Flow

```
Open Shift → Search Product → Add to Cart → (Apply Discounts) →
  Pay → Select Method → Enter Amount → Complete → Print/Email Receipt → New Sale
```

### Step Details

1. **Shift Open** (required): Cashier enters opening cash → API creates session
2. **Product Selection**: Search by name/SKU/barcode OR use Quick Buttons
3. **Cart Management**: Adjust quantities, apply item/cart discounts, remove items
4. **Payment**: Open payment modal → select method → enter amount → complete
5. **Receipt**: Auto-displays after completion → Print / Email / New Sale

## 2. Payment Flow

```
┌─ PaymentModal ─────────────────────────────────┐
│  PaymentAmount: Total due / Paid / Remaining    │
│  PaymentMethodsGrid: Cash | Card | Bank        │
│  ┌─ CashPayment ─────────────────────────┐     │
│  │  Numpad → QuickAmounts → ChangeCalc   │     │
│  └────────────────────────────────────────┘     │
│  ┌─ CardPayment ──────────────────────────┐    │
│  │  Card Type → Last 4 → Approval Code   │     │
│  └────────────────────────────────────────┘     │
│  SplitPaymentToggle → SplitPaymentInterface     │
│  CustomerSelect (optional)                      │
│  CompleteSale button                            │
└─────────────────────────────────────────────────┘
```

### Split Payment

1. Toggle "Split Payment" on
2. Enter first payment amount → method → Add
3. Enter remaining amount → different method → Add
4. Complete when fully paid

## 3. Shift Management

### Opening

1. POS shows non-dismissible ShiftOpenModal on load (if no active shift)
2. Enter opening cash amount (manual or quick buttons)
3. Optional notes
4. "Open Shift" → API creates POS session → POS becomes operational

### Closing

1. Click shift close or menu action
2. ShiftSummaryDisplay shows stats (transactions, sales, expected cash)
3. CashCountInput: count physical cash by denomination
4. ShiftVarianceDisplay: color-coded comparison with recommendations
5. Enter closing notes (recommended for variances)
6. "Close Shift" → API closes session → shift cleared

### Variance Categories

| Range (₨)  | Color     | Status            | Action              |
| ---------- | --------- | ----------------- | ------------------- |
| 0          | Green ✓   | Perfect Match     | No action           |
| 1–9.99     | Green ✓   | Acceptable        | No action           |
| 10–99.99   | Yellow ⚠️ | Minor Discrepancy | Document notes      |
| 100–499.99 | Orange ⚠️ | Investigate       | Review transactions |
| 500+       | Red 🚨    | Major Discrepancy | Manager review      |

## 4. Hold / Retrieve Sales

### Hold Sale

1. Cart has items → Click Hold (F4)
2. Enter optional reason in dialog
3. Cart serialized to context + localStorage
4. Current cart cleared
5. Max 10 held sales per shift

### Retrieve Sale

1. Click Retrieve (F5)
2. Browse held sales list (time, reason, item count)
3. Select and click Play icon to retrieve
4. Held sale restored to current cart
5. Hold removed from list

## 5. Barcode Scanning

1. User scans barcode (physical scanner acts as keyboard)
2. `useBarcodeScanner` detects rapid keystrokes (<50ms between chars)
3. On Enter: validates length (2-13 chars) and pattern (alphanumeric)
4. Calls `posService.searchProducts(barcode)` → adds first match to cart
