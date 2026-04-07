# POS Module Integrations

## Inventory Module

The POS terminal is linked to a warehouse via `POSTerminal.warehouse`.

- **Stock lookups** — `ProductSearchService` queries products filtered by
  `is_pos_visible=True` and `status=ACTIVE`. Stock availability can be
  checked against the terminal's warehouse.
- **Stock deductions** — future enhancement to decrement stock on
  transaction completion.
- **Negative inventory** — controlled per terminal via
  `allow_negative_inventory`. When `False`, sales of zero-stock items
  are blocked at the cart validation step.

## Products Module

| Integration Point | Detail                                                       |
| ----------------- | ------------------------------------------------------------ |
| `Product` model   | Referenced by `POSCartItem.product` and search service       |
| `ProductVariant`  | Optional variant reference with separate barcode/SKU         |
| `TaxClass`        | Tax rate pulled into cart items via `set_tax_from_product()` |
| `Category` (MPTT) | Used for category-filtered search                            |
| `is_pos_visible`  | Boolean flag on Product controlling POS visibility           |

## Customers Module

- `POSCart.customer` — optional FK to `Customer`.
- Used for:
  - Customer-linked sales and purchase history
  - Store credit payments (`process_store_credit` requires a customer)
  - Loyalty programmes (future)

## Accounting Module

Future integration points:

- **Journal entries** — auto-create accounting entries on transaction
  completion (cash, receivables, revenue).
- **Payment reconciliation** — map POS payments to bank deposits.
- **Tax reporting** — aggregate tax collected per session/period.

## Payment Gateways

Currently, payments are recorded locally. External gateway integration:

```
┌──────────┐     ┌──────────────────┐     ┌─────────────┐
│ POS View │────▶│ PaymentService   │────▶│ Gateway API │
│          │◀────│                  │◀────│ (future)    │
└──────────┘     └──────────────────┘     └─────────────┘
```

Planned integrations:

| Gateway         | Method Constant | Status               |
| --------------- | --------------- | -------------------- |
| Visa/Mastercard | `card`          | Local recording only |
| FriMi           | `mobile_frimi`  | Local recording only |
| Genie           | `mobile_genie`  | Local recording only |

Gateway adapters should be implemented as strategy classes injected
into `PaymentService`.

## Webhooks & Events

Currently none. Planned:

- `pos.transaction.completed` — notify external systems on sale
- `pos.session.closed` — trigger end-of-day reports
- `pos.stock.low` — alert when terminal warehouse stock is low

## Multi-Tenant

All POS data is tenant-scoped. The `django-tenants` middleware sets the
schema before any request, so queries automatically return only the
current tenant's data.

Terminal, session, cart, payment, and search models are all in the
tenant schema (not the public schema).
