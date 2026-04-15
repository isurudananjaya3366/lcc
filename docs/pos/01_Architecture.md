# POS Architecture

## System Design

The POS module is a full-screen Next.js App Router interface at `app/(pos)/pos/page.tsx`, using a dedicated layout that hides the main navigation for an immersive point-of-sale experience.

### Technology Stack

- **Framework:** Next.js 14 (App Router)
- **State Management:** Zustand (cart store) + React Context (POS session)
- **UI Components:** shadcn/ui (Dialog, Button, Switch, DropdownMenu)
- **Styling:** Tailwind CSS with dark mode support
- **Icons:** Lucide React
- **Currency:** Sri Lankan Rupee (LKR / ₨)

## Component Hierarchy

```
app/(pos)/pos/page.tsx          ← Entry point
├── POSProvider                 ← Context: modals, shift, customer, held sales
│   ├── ProductPanel            ← Left panel (product search & selection)
│   │   ├── ProductSearch       ← Search input with barcode support
│   │   ├── SearchResults       ← Filtered product list
│   │   └── QuickButtons        ← Frequently used product shortcuts
│   ├── CartPanel               ← Right panel (cart & actions)
│   │   ├── CartContainer       ← Cart items + totals
│   │   │   ├── CartItemsList
│   │   │   │   └── CartItem    ← Individual line item
│   │   │   └── CartTotals      ← Subtotal, discount, tax, grand total
│   │   └── CartActionButtons   ← Pay + Hold buttons
│   ├── PaymentModal            ← Payment processing dialog
│   ├── ReceiptModal            ← Post-sale receipt display
│   ├── ShiftOpenModal          ← Shift opening (required to start POS)
│   └── ShiftCloseModal         ← End-of-shift cash reconciliation
```

## State Management

### Zustand Cart Store (`stores/pos/cart.ts`)

Persistent store with Immer for immutable updates:

- **Items:** `POSCartItem[]` — products with quantity, price, discounts
- **Discount:** `POSDiscount | null` — cart-level discount
- **Customer:** `POSCustomer | null` — attached customer
- **Computed:** `getSubtotal()`, `getGrandTotal()`, `getItemCount()`, `getDiscountTotal()`

### React Context (`context/POSContext.tsx`)

Session-level state via `useReducer`:

- **Modal management:** `openModal(type)`, `closeModal()`, `activeModal`
- **Shift tracking:** `currentShift`, `setShift()`
- **Held sales:** `heldSales[]`, `holdSale()`, `retrieveHold()`

## Data Flow

```
User Action → Component Handler → Store Action → State Update → React Re-render
                                  ↓
                              API Service (services/pos.ts) → Backend REST API
```

### Tax Calculation Pipeline

```
subtotal → calculateCartTotals(subtotal, discountTotal) → {
  subtotal, discountAmount, taxableAmount,
  taxAmount (15% VAT), taxRate, taxName, grandTotal
}
```

Located in `lib/pos/calculateTax.ts` with configurable `TaxConfig`.

## File Structure

```
frontend/
├── app/(pos)/pos/
│   ├── layout.tsx              ← Full-screen POS layout
│   └── page.tsx                ← Main POS page
├── components/modules/pos/
│   ├── context/                ← POSContext provider
│   ├── hooks/                  ← useBarcodeScanner, usePOSKeyboardShortcuts
│   ├── ProductPanel/           ← Product search & selection
│   ├── CartPanel/              ← Cart wrapper
│   ├── Cart/                   ← Cart components (items, totals, discount)
│   ├── Payment/                ← Payment processing
│   ├── Receipt/                ← Post-sale receipt
│   ├── Shift/                  ← Shift open/close management
│   ├── Hold/                   ← Hold/retrieve sales
│   ├── types.ts                ← TypeScript interfaces
│   └── index.ts                ← Barrel exports
├── services/pos.ts             ← API service layer
├── stores/pos/cart.ts          ← Zustand cart store
└── lib/pos/
    ├── calculateTax.ts         ← Tax calculation utilities
    └── totalCalculator.ts      ← Price/discount/change helpers
```
