# Sales Module

## Overview

The Sales module provides a comprehensive UI for managing the entire sales lifecycle in LankaCommerce Cloud POS: from quoting to ordering, invoicing, payment collection, and fulfilment.

## Features

| Feature | Directory | Description |
|---------|-----------|-------------|
| **Orders** | `Orders/` | List, create, view, and manage sales orders with status tracking, timeline, and notes |
| **Invoices** | `Invoices/` | Invoice listing, PDF preview/download, email sending, payment history |
| **Quotes** | `Quotes/` | Create and send quotations, convert accepted quotes to orders |
| **Payments** | `Payments/` | Record payments against orders with multiple methods (cash, card, bank, cheque, online) |
| **Shipping** | `Shipping/` | Select carriers, enter tracking numbers, print shipping labels, mark as shipped |

## Tech Stack

- **React 18** with Next.js App Router
- **TanStack Table v8** — sortable, paginated data tables
- **TanStack Query 5** — server-state caching and mutations
- **React Hook Form + Zod** — form management and validation
- **shadcn/ui** — UI component primitives
- **Tailwind CSS** — utility-first styling with dark mode
- **Lucide React** — iconography

## Component Reference

### Orders

| Component | Props | Description |
|-----------|-------|-------------|
| `OrdersList` | — | Full orders page with filters, summary cards, and table |
| `OrderDetail` | `orderId: string` | Order detail view with timeline, notes, status updates |
| `NewOrderForm` | — | Order creation form with line items |
| `OrderStatusBadge` | `status, size?` | Coloured badge for 9 order statuses |

### Invoices

| Component | Props | Description |
|-----------|-------|-------------|
| `InvoicesList` | — | Invoice listing with filters and summary |
| `InvoiceDetail` | `invoiceId: string` | Detail view with PDF preview and payment history |
| `SendInvoiceModal` | `isOpen, onClose, invoice` | Email invoice dialog with RHF + Zod |
| `InvoiceStatusBadge` | `status, size?` | Badge for 7 invoice statuses |

### Quotes

| Component | Props | Description |
|-----------|-------|-------------|
| `QuotesList` | — | Quote listing with filters and status |
| `QuoteDetail` | `quoteId: string` | Detail view with items, pricing, conversion |
| `NewQuoteForm` | — | Quote creation with line items |
| `ConversionModal` | `isOpen, onClose, quote, ...` | Convert quote to order dialog |
| `QuoteStatusBadge` | `status, size?` | Badge for 6 quote statuses |

### Payments

| Component | Props | Description |
|-----------|-------|-------------|
| `RecordPaymentModal` | `isOpen, orderId, orderTotal, ...` | Full payment recording dialog |
| `PaymentMethodSelect` | `value, onChange` | Dropdown with 6 payment methods |
| `AmountInput` | `value, onChange, amountDue` | Currency input with quick-fill buttons |

### Shipping

| Component | Props | Description |
|-----------|-------|-------------|
| `ShippingLabelModal` | `isOpen, orderNumber, ...` | Carrier + tracking + label dialog |
| `CarrierSelection` | `value, onChange` | Dropdown with 6 carriers |
| `TrackingInput` | `value, onChange, carrier?` | Auto-format tracking with carrier links |

## Usage

```tsx
import {
  OrdersList,
  RecordPaymentModal,
  ShippingLabelModal,
} from '@/components/modules/sales';
```

## API Integration

Services are in `services/api/`:

| Service | Endpoints |
|---------|-----------|
| `salesService` | Orders CRUD, payments, shipments, notes, discounts |
| `invoiceService` | Invoices CRUD, send, record payment, download PDF |
| `quoteService` | Quotes CRUD, send, convert to order |

Hooks are in `hooks/`:

| Hook | Location |
|------|----------|
| `useOrders`, `useOrder` | `hooks/queries/useOrders.ts` |
| `useInvoices`, `useInvoiceDetails` | `hooks/queries/useInvoices.ts` |
| `useQuotes`, `useQuoteDetails` | `hooks/queries/useQuotes.ts` |
| `useRecordPayment` | `hooks/sales/usePayment.ts` |
| `useCreateShipment`, `useMarkDelivered` | `hooks/sales/useShipping.ts` |
| `useQuoteConversion` | `hooks/sales/useQuoteConversion.ts` |

## Currency

All monetary values use Sri Lankan Rupee (LKR):

```ts
`₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`
```
