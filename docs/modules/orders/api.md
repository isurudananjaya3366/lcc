# Order Module — API Reference

## Base URL

All order endpoints are prefixed with `/api/` and registered via DRF's `DefaultRouter`.

## Authentication

All endpoints require `IsAuthenticated`. Include `Authorization: Token <token>` header.

---

## Orders

### List Orders

```
GET /api/orders/
```

**Query Parameters (Filters):**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string (repeatable) | Filter by status (supports multiple: `?status=pending&status=confirmed`) |
| `source` | string | Filter by source channel |
| `payment_status` | string | Filter by payment status |
| `customer` | UUID | Filter by customer ID |
| `created_from` / `created_to` | date | Date range filter |
| `total_min` / `total_max` | number | Total amount range |
| `is_draft` | boolean | Draft filter |
| `is_locked` | boolean | Lock filter |
| `search` | string | Search order_number, customer name/email, notes, item names |
| `ordering` | string | Sort by: `created_on`, `total_amount`, `order_number`, `status` |

**Response:** Paginated list using `OrderListSerializer`

### Create Order

```
POST /api/orders/
Content-Type: application/json

{
  "source": "manual",
  "customer": "uuid-of-customer",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "currency": "LKR",
  "notes": "Rush order"
}
```

### Retrieve Order

```
GET /api/orders/{id}/
```

Returns full `OrderSerializer` with nested line items and computed fields.

### Update Order

```
PATCH /api/orders/{id}/
```

Only allowed on editable orders (PENDING/CONFIRMED, not locked).

### Delete Order (Draft Only)

```
DELETE /api/orders/{id}/
```

Returns 400 if order is not a draft.

---

## Order Actions

### Confirm Order

```
POST /api/orders/{id}/confirm/
```

### Start Processing

```
POST /api/orders/{id}/process/
```

### Ship Order

```
POST /api/orders/{id}/ship/
Content-Type: application/json

{
  "tracking_number": "TRK123456",
  "carrier": "dhl"
}
```

### Confirm Delivery

```
POST /api/orders/{id}/deliver/
```

### Complete Order

```
POST /api/orders/{id}/complete/
```

### Cancel Order

```
POST /api/orders/{id}/cancel/
Content-Type: application/json

{
  "reason": "Customer requested cancellation"
}
```

### Duplicate Order

```
POST /api/orders/{id}/duplicate/
```

Creates a new PENDING order with the same line items.

### View History

```
GET /api/orders/{id}/history/
```

Returns chronological list of order events.

### Available Actions

```
GET /api/orders/{id}/available_actions/
```

Returns list of valid status transitions for the current state.

---

## Fulfillments

### List Fulfillments

```
GET /api/fulfillments/
```

### Pick Items

```
POST /api/fulfillments/{id}/pick_items/
Content-Type: application/json

{
  "picked_items": [
    {"fulfillment_line_item_id": "uuid", "bin_location": "A-1-3"}
  ]
}
```

### Pack Fulfillment

```
POST /api/fulfillments/{id}/pack_items/
Content-Type: application/json

{
  "weight": 2.5,
  "dimensions": {"length": 30, "width": 20, "height": 15}
}
```

### Ship Fulfillment

```
POST /api/fulfillments/{id}/ship_fulfillment/
Content-Type: application/json

{
  "carrier": "dhl",
  "tracking_number": "TRK789"
}
```

### Confirm Delivery

```
POST /api/fulfillments/{id}/deliver_fulfillment/
Content-Type: application/json

{
  "recipient": "Jane Doe",
  "signature": "base64-sig-data"
}
```

### Fulfillment Progress

```
GET /api/fulfillments/{id}/progress/
```

---

## Returns

### Create Return Request

```
POST /api/returns/
Content-Type: application/json

{
  "order": "uuid-of-order",
  "reason": "defective",
  "reason_detail": "Screen has dead pixels",
  "items": [
    {"order_line_item_id": "uuid", "quantity": 1}
  ]
}
```

### Approve Return

```
POST /api/returns/{id}/approve_return/
Content-Type: application/json

{
  "notes": "Approved per return policy"
}
```

### Reject Return

```
POST /api/returns/{id}/reject_return/
Content-Type: application/json

{
  "reason": "Outside return window"
}
```

### Receive Return

```
POST /api/returns/{id}/receive_return/
Content-Type: application/json

{
  "inspections": [
    {
      "return_line_item_id": "uuid",
      "condition": "opened",
      "notes": "Original packaging missing"
    }
  ]
}
```

### Process Refund

```
POST /api/returns/{id}/process_refund/
Content-Type: application/json

{
  "refund_method": "original_method"
}
```
