# POS Components Reference

## Product Panel

### ProductSearch

**File:** `components/modules/pos/ProductPanel/ProductSearch.tsx`

| Prop | Type | Description                                                             |
| ---- | ---- | ----------------------------------------------------------------------- |
| —    | —    | Self-contained; uses debounced search via `posService.searchProducts()` |

**Features:** Text search, barcode icon indicator, keyboard Escape to clear, auto-focus on F2.

### SearchResults

**File:** `components/modules/pos/ProductPanel/SearchResults.tsx`

| Prop      | Type                | Description                 |
| --------- | ------------------- | --------------------------- |
| results   | `POSProduct[]`      | Products matching search    |
| onSelect  | `(product) => void` | Add to cart callback        |
| isLoading | `boolean`           | Show skeleton during search |

**Features:** Shows max 10 results, keyboard arrow navigation, Enter to select, "Showing X of Y" footer.

### QuickButtons

**File:** `components/modules/pos/ProductPanel/QuickButtons.tsx`

| Prop     | Type               | Description                   |
| -------- | ------------------ | ----------------------------- |
| buttons  | `QuickButton[]`    | Configured quick-add products |
| onSelect | `(button) => void` | Add to cart callback          |

**Features:** Section header, variant support (`hasVariants → openModal`), grid layout.

---

## Cart Components

### CartContainer

Wraps `CartItemsList` + `CartTotals`. Shows `EmptyCart` when no items.

### CartItem

| Prop | Type          | Description         |
| ---- | ------------- | ------------------- |
| item | `POSCartItem` | Cart line item data |

**Sub-components:** `ItemName` (with tooltip), `QuantityControls`/`QuantityInput`, `ItemPrice`, `RemoveItemButton`, `ItemOptionsMenu`, `ItemDiscount`.

### CartTotals

Aggregates: `SubtotalDisplay`, `DiscountSection`, `TaxDisplay`, `GrandTotalDisplay`, `ItemsCountDisplay`.

### DiscountModal

| Prop            | Type                              | Description               |
| --------------- | --------------------------------- | ------------------------- |
| open            | `boolean`                         | Dialog visibility         |
| onClose         | `() => void`                      | Close handler             |
| onApply         | `(discount: POSDiscount) => void` | Apply discount            |
| onClear         | `() => void`                      | Clear existing discount   |
| currentDiscount | `POSDiscount \| null`             | Current discount state    |
| subtotal        | `number`                          | Cart subtotal for preview |

**Features:** Type toggle (% / fixed ₨), value input, reason dropdown with "Other" free-text, live preview, clear button, state reset on open.

### CartActionButtons

| Prop       | Type         | Description                |
| ---------- | ------------ | -------------------------- |
| cartEmpty  | `boolean`    | Disable buttons when empty |
| grandTotal | `number`     | Display on Pay button      |
| onPay      | `() => void` | Open payment modal         |
| onHold     | `() => void` | Hold current sale          |

### PendingAmountDisplay

| Prop       | Type     | Description |
| ---------- | -------- | ----------- |
| grandTotal | `number` | Total due   |
| paidAmount | `number` | Total paid  |

**States:** "Balance Due" (red), "Paid in Full ✓" (green), "Change Due" (blue).

---

## Payment Components

### PaymentModal

Full payment flow with: `PaymentAmount`, `PaymentMethodsGrid`, method-specific inputs (`CashPayment`, `CardPayment`, `BankPayment`), `SplitPaymentToggle`/`SplitPaymentInterface`, `CustomerSelect`, `CompleteSale`.

### CashPayment

`Numpad` + `QuickAmounts` + `ChangeCalculator`. Quick amounts include exact amount and round-up options.

### CardPayment

Card type select, last 4 digits input, approval code. Validates 4-digit requirement.

### BankPayment

Transfer reference input, bank name field.

---

## Receipt Components

### ReceiptModal

Post-sale modal with `ReceiptContent` display and action buttons.

### ReceiptContent

Formatted receipt with: store header, transaction details, itemized list, totals, payment info, footer.

### PrintReceiptButton

Triggers `window.print()`. Keyboard shortcut: P.

### EmailReceiptButton

Opens email dialog with validation (regex-based), loading states, error handling.

### NewSaleButton

Resets cart and starts fresh. Auto-focuses after 2 seconds. Keyboard shortcut: N.

---

## Shift Components

### ShiftOpenModal

Non-dismissible modal for shift start. `OpeningCashInput` with quick amounts (5K/10K/20K/50K LKR).

### ShiftCloseModal

End-of-shift: `ShiftSummaryDisplay` → `CashCountInput` → `ShiftVarianceDisplay` → notes → close.

### ShiftSummaryDisplay

Displays shift number, transactions, duration, opening cash, sales, expected cash.

### CashCountInput

11 Sri Lankan denominations with quantity inputs, +/- buttons, keyboard navigation (Tab/Enter/Arrow), running total, Clear All.

### ShiftVarianceDisplay

5-tier color-coded variance: Perfect Match (green ✓), Acceptable (green ✓), Minor (yellow ⚠️), Investigate (orange ⚠️), Major (red 🚨). Includes breakdown and recommendations.

---

## Hold Components

### HoldSaleButton

Hold current cart with optional reason. Max 10 held sales. Shows F4 shortcut hint.

### RetrieveHoldButton

Lists held sales with time, reason, item count. Retrieve with Play button. Shows F5 shortcut. Badge count indicator.
