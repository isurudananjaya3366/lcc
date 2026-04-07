# Order Management Module

## Overview

The Order Management module provides a complete order lifecycle for the POS/ERP system — from creation through fulfillment, delivery, returns, and cancellations. It supports multiple order sources, complex fulfillment workflows, comprehensive return processing, and full audit history.

## Architecture

```
apps/orders/
├── models/
│   ├── order.py                # Core Order model
│   ├── line_item.py            # OrderLineItem with pricing
│   ├── fulfillment.py          # Fulfillment (shipping/delivery)
│   ├── fulfillment_item.py     # FulfillmentLineItem
│   ├── order_return.py         # OrderReturn (RMA)
│   ├── return_line_item.py     # ReturnLineItem
│   ├── history.py              # OrderHistory audit trail
│   └── settings.py             # OrderSettings (per-tenant)
├── services/
│   ├── order_service.py              # Order creation & management
│   ├── fulfillment_service.py        # Fulfillment workflow
│   ├── return_service.py             # Return processing
│   ├── cancellation_service.py       # Cancellation logic
│   ├── calculation_service.py        # Financial calculations
│   ├── history_service.py            # Event logging
│   └── order_number_generator.py     # Sequential numbering
├── views/
│   ├── order.py          # OrderViewSet (CRUD + actions)
│   ├── fulfillment.py    # FulfillmentViewSet (pick/pack/ship)
│   └── order_return.py   # ReturnViewSet (RMA CRUD)
├── serializers/
│   ├── order.py          # Order list/detail/create serializers
│   ├── line_item.py      # LineItem serializer
│   ├── fulfillment.py    # Fulfillment serializer
│   └── order_return.py   # Return serializer
├── signals/
│   └── order_signals.py  # Auto-history & recalculation signals
├── tasks/
│   └── order_tasks.py    # Celery async tasks
├── managers/
│   └── order_manager.py  # Custom QuerySet/Manager
├── filters.py            # django-filter FilterSet
├── constants.py          # Status, source, transition enums
└── urls.py               # URL routing
```

## Key Features

- **Multi-Source Creation**: Manual, Quote Conversion, POS, Webstore, Bulk Import
- **Status Lifecycle**: Pending → Confirmed → Processing → Shipped → Delivered → Completed
- **Fulfillment Workflow**: Pick → Pack → Ship → Deliver with warehouse integration
- **Return Processing**: Full RMA workflow with approve/reject/receive/refund
- **Cancellation Logic**: Configurable cancellation with stock reversal
- **Financial Calculations**: Line-item pricing, discounts (% / fixed), tax, shipping
- **Audit History**: Full change tracking with old/new values
- **Multi-Tenant**: Per-tenant settings and data isolation via django-tenants

## Models

### Entity Relationships

```
Order
├── OrderLineItem (1:N)     — Items in the order
├── Fulfillment (1:N)       — Shipments
│   └── FulfillmentLineItem — Items per shipment
├── OrderReturn (1:N)       — Return requests
│   └── ReturnLineItem      — Items being returned
├── OrderHistory (1:N)      — Audit trail
└── OrderSettings (1:1 Tenant) — Tenant config
```

### Order

Core entity with 30+ fields covering customer info, financial totals, status, metadata.

| Field            | Type          | Description                                       |
| ---------------- | ------------- | ------------------------------------------------- |
| id               | UUID          | Primary key                                       |
| order_number     | CharField     | Auto-generated (e.g., ORD-2026-00001)             |
| status           | CharField     | Current lifecycle status                          |
| source           | CharField     | Origin channel (pos/webstore/quote/manual/import) |
| priority         | CharField     | Order priority level                              |
| customer         | FK(Customer)  | Linked customer (optional)                        |
| customer_name    | CharField     | Guest/override customer name                      |
| customer_email   | EmailField    | Customer email                                    |
| customer_phone   | CharField     | Customer phone                                    |
| currency         | CharField     | LKR or USD                                        |
| subtotal         | Decimal(12,2) | Sum of line items before discount                 |
| discount_type    | CharField     | percentage or fixed                               |
| discount_value   | Decimal(12,2) | Discount amount/percentage                        |
| discount_amount  | Decimal(12,2) | Calculated discount total                         |
| tax_amount       | Decimal(12,2) | Total tax                                         |
| shipping_amount  | Decimal(12,2) | Shipping cost                                     |
| grand_total      | Decimal(12,2) | Final total                                       |
| amount_paid      | Decimal(12,2) | Amount paid so far                                |
| balance_due      | Decimal(12,2) | Remaining balance                                 |
| payment_status   | CharField     | unpaid/partial/paid/refunded                      |
| shipping_method  | CharField     | Shipping method                                   |
| billing_address  | JSONField     | Billing address                                   |
| shipping_address | JSONField     | Shipping address                                  |
| notes            | TextField     | Customer-visible notes                            |
| internal_notes   | TextField     | Staff-only notes                                  |
| tags             | JSONField     | Flexible tagging                                  |
| is_locked        | BooleanField  | Lock for editing                                  |
| is_deleted       | BooleanField  | Soft-delete flag                                  |

### OrderLineItem

Individual items in an order with pricing, quantity, and fulfillment tracking.

### Fulfillment

Represents a shipment within an order. Tracks carrier, tracking info, weight, dimensions, and workflow timestamps.

### OrderReturn

Return/RMA request with reason codes, condition tracking, and refund processing.

### OrderHistory

Audit trail recording all order events with old/new values and user attribution.

### OrderSettings

Per-tenant configuration for order numbering, policies, and defaults.

## Order Lifecycle

```
PENDING ──→ CONFIRMED ──→ PROCESSING ──→ SHIPPED ──→ DELIVERED ──→ COMPLETED
  │             │              │                          │            │
  └──→ CANCELLED ←─────────────┘                          └──→ RETURNED ←──┘
```

### Status Descriptions

| Status     | Description                     | Available Actions            |
| ---------- | ------------------------------- | ---------------------------- |
| pending    | Draft order, not yet confirmed  | Edit, Confirm, Cancel        |
| confirmed  | Order confirmed, stock reserved | Process, Cancel              |
| processing | Fulfillment in progress         | Ship, Cancel (with approval) |
| shipped    | Package dispatched              | Mark Delivered               |
| delivered  | Customer received order         | Complete, Return             |
| completed  | Order fully completed           | Return                       |
| cancelled  | Order cancelled                 | —                            |
| returned   | Order returned                  | —                            |

### Allowed Transitions

```python
ALLOWED_TRANSITIONS = {
    "pending":               ["confirmed", "cancelled"],
    "confirmed":             ["processing", "cancelled"],
    "processing":            ["shipped", "partially_fulfilled", "cancelled"],
    "partially_fulfilled":   ["shipped", "cancelled"],
    "shipped":               ["delivered"],
    "delivered":             ["completed", "returned"],
    "completed":             ["returned"],
    "cancelled":             [],
    "returned":              [],
}
```

## Fulfillment Workflow

```
1. Order Confirmed
   ↓
2. Create Fulfillment
   ↓
3. Pick Items (scan & locate in warehouse)
   ↓
4. Pack Items (weigh & dimension)
   ↓
5. Ship (generate tracking, notify customer)
   ↓
6. Deliver (confirm receipt)
```

### Fulfillment Statuses

| Status     | Description                  |
| ---------- | ---------------------------- |
| PENDING    | Created, awaiting processing |
| CONFIRMED  | Confirmed for fulfillment    |
| PROCESSING | Being prepared               |
| PICKING    | Items being picked           |
| PICKED     | All items picked             |
| PACKING    | Items being packed           |
| PACKED     | Ready to ship                |
| SHIPPED    | Dispatched with tracking     |
| DELIVERED  | Customer received            |
| FAILED     | Fulfillment failed           |
| CANCELLED  | Cancelled                    |

### Partial Fulfillment

Orders can be fulfilled in multiple shipments when:

- Stock not available for all items
- Items in different warehouses
- Large orders split for efficiency

## Return Workflow

```
1. Customer Requests Return (PENDING)
   ↓
2. Staff Reviews (APPROVED / REJECTED)
   ↓
3. Customer Ships Items (RECEIVED)
   ↓
4. Staff Inspects (INSPECTED)
   ↓
5. Stock Restored / Refund Processed (REFUNDED / COMPLETED)
```

### Return Reasons

- `DEFECTIVE` — Product defective or damaged
- `WRONG_ITEM` — Wrong item received
- `CHANGED_MIND` — Customer changed mind
- `NOT_AS_DESCRIBED` — Product not as advertised
- `BETTER_PRICE` — Found better price elsewhere
- `DUPLICATE` — Duplicate order
- `OTHER` — Other reason (with notes)

## API Reference

Base URL: `/api/v1/`

### Order Endpoints

| Method | Endpoint                        | Description                         |
| ------ | ------------------------------- | ----------------------------------- |
| GET    | /orders/                        | List orders (paginated, filterable) |
| POST   | /orders/                        | Create new order                    |
| GET    | /orders/{id}/                   | Retrieve order detail               |
| PUT    | /orders/{id}/                   | Update order                        |
| PATCH  | /orders/{id}/                   | Partial update                      |
| POST   | /orders/{id}/confirm/           | Confirm order                       |
| POST   | /orders/{id}/process/           | Start processing                    |
| POST   | /orders/{id}/ship/              | Mark as shipped                     |
| POST   | /orders/{id}/deliver/           | Confirm delivery                    |
| POST   | /orders/{id}/complete/          | Complete order                      |
| POST   | /orders/{id}/cancel/            | Cancel order                        |
| POST   | /orders/{id}/duplicate/         | Duplicate order                     |
| GET    | /orders/{id}/line_items/        | List line items                     |
| GET    | /orders/{id}/history/           | Order history                       |
| GET    | /orders/{id}/available_actions/ | Available status transitions        |

### Fulfillment Endpoints

| Method | Endpoint                     | Description          |
| ------ | ---------------------------- | -------------------- |
| GET    | /fulfillments/               | List fulfillments    |
| GET    | /fulfillments/{id}/          | Retrieve fulfillment |
| POST   | /fulfillments/{id}/pick/     | Mark items picked    |
| POST   | /fulfillments/{id}/pack/     | Mark items packed    |
| POST   | /fulfillments/{id}/ship/     | Mark as shipped      |
| POST   | /fulfillments/{id}/deliver/  | Confirm delivery     |
| GET    | /fulfillments/{id}/progress/ | Fulfillment progress |

### Return Endpoints

| Method | Endpoint               | Description            |
| ------ | ---------------------- | ---------------------- |
| GET    | /returns/              | List returns           |
| POST   | /returns/              | Create return request  |
| GET    | /returns/{id}/         | Retrieve return detail |
| POST   | /returns/{id}/approve/ | Approve return         |
| POST   | /returns/{id}/reject/  | Reject return          |
| POST   | /returns/{id}/receive/ | Mark items received    |
| POST   | /returns/{id}/refund/  | Process refund         |

### Filtering & Search

Orders support filtering via query parameters:

| Parameter      | Type   | Description                                     |
| -------------- | ------ | ----------------------------------------------- |
| status         | string | Filter by order status                          |
| source         | string | Filter by order source                          |
| payment_status | string | Filter by payment status                        |
| customer       | UUID   | Filter by customer ID                           |
| search         | string | Search order number, customer name/email        |
| ordering       | string | Sort field (e.g., `-created_on`, `grand_total`) |

### Authentication

All endpoints require authentication via `IsAuthenticated` permission class. Include the auth token in the `Authorization` header.

## Services

### OrderService

Core business logic for order management.

| Method                                           | Description                               |
| ------------------------------------------------ | ----------------------------------------- |
| `create_order(data, items_data, user)`           | Create new order with optional line items |
| `create_from_quote(quote, user)`                 | Convert quote to order                    |
| `transition_status(order, new_status, user)`     | Change order status with validation       |
| `duplicate_order(order_id, user, modifications)` | Clone an existing order                   |

### FulfillmentService

Fulfillment workflow operations.

| Method                                             | Description                  |
| -------------------------------------------------- | ---------------------------- |
| `create_fulfillment(order, items, warehouse)`      | Create fulfillment for order |
| `pick_items(fulfillment, user)`                    | Mark items as picked         |
| `pack_items(fulfillment, user)`                    | Mark items as packed         |
| `ship_fulfillment(fulfillment, carrier, tracking)` | Ship with tracking info      |
| `deliver_fulfillment(fulfillment)`                 | Confirm delivery             |

### ReturnService

Return/RMA processing.

| Method                                    | Description           |
| ----------------------------------------- | --------------------- |
| `create_return(order, items, reason)`     | Create return request |
| `approve_return(return_obj, user)`        | Approve a return      |
| `reject_return(return_obj, user, reason)` | Reject a return       |
| `receive_return(return_obj, user)`        | Mark items received   |
| `process_refund(return_obj, user)`        | Process refund        |

### CancellationService

Order cancellation with stock reversal.

| Method                                  | Description                      |
| --------------------------------------- | -------------------------------- |
| `cancel_order(order, user, reason)`     | Cancel entire order              |
| `can_cancel(order)`                     | Check if cancellation is allowed |
| `cancel_line_items(order, items, user)` | Partial line item cancellation   |

### CalculationService

Financial calculations for orders.

| Method                              | Description                                 |
| ----------------------------------- | ------------------------------------------- |
| `calculate_line_item(item)`         | Calculate line item total with discount/tax |
| `calculate_order_totals(order)`     | Recalculate all order totals                |
| `calculate_shipping(order, method)` | Calculate shipping cost                     |

## Configuration

### OrderSettings (Per-Tenant)

Each tenant can configure order behavior via the `OrderSettings` model:

| Setting              | Default                        | Description                               |
| -------------------- | ------------------------------ | ----------------------------------------- |
| order_number_prefix  | "ORD"                          | Prefix for order numbers                  |
| order_number_format  | `{prefix}-{year}-{number:05d}` | Number format template                    |
| default_currency     | "LKR"                          | Default order currency                    |
| allow_guest_orders   | True                           | Allow orders without customer account     |
| require_confirmation | True                           | Orders start as pending (vs auto-confirm) |

### Environment Variables

No module-specific environment variables. Configuration is per-tenant via the admin panel.

## Testing

Tests are in `backend/tests/orders/` with 55+ tests covering:

- **Model tests**: CRUD, field validation, relationships, string representations
- **Service tests**: Order creation, status transitions, calculations, cancellation, returns
- **API tests**: All endpoints, authentication, filtering, status actions

Run tests:

```bash
docker compose exec -e DJANGO_SETTINGS_MODULE=config.settings.test_pg backend \
  python -m pytest tests/orders/ -v --tb=short
```

## Detailed Documentation

- [Model Reference](models.md) — Full field-level documentation for all models
- [API Reference](api.md) — Endpoint details with request/response examples
- [Fulfillment Workflow](fulfillment.md) — Step-by-step fulfillment guide
- [Returns & Cancellations](returns.md) — Return and cancellation workflows
