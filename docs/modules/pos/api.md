# POS API Reference

All endpoints are prefixed with `/api/v1/pos/`. Authentication is required
for every endpoint (`IsAuthenticated`).

---

## Terminals

| Method | Path                                | Description                                           |
| ------ | ----------------------------------- | ----------------------------------------------------- |
| GET    | `/terminals/`                       | List terminals (filterable by status, location, code) |
| POST   | `/terminals/`                       | Create terminal                                       |
| GET    | `/terminals/{id}/`                  | Terminal detail                                       |
| PUT    | `/terminals/{id}/`                  | Full update                                           |
| PATCH  | `/terminals/{id}/`                  | Partial update                                        |
| DELETE | `/terminals/{id}/`                  | Soft-delete                                           |
| POST   | `/terminals/{id}/activate/`         | Set status → active                                   |
| POST   | `/terminals/{id}/deactivate/`       | Set status → inactive (409 if open session)           |
| POST   | `/terminals/{id}/maintenance_mode/` | Set status → maintenance (409 if open session)        |
| GET    | `/terminals/available/`             | Active terminals without an open session              |

### Filters (query params)

- `status` — exact match
- `location` — case-insensitive contains
- `code` — case-insensitive exact
- `is_active` — boolean
- `has_open_session` — boolean (custom filter)

---

## Sessions

| Method | Path                            | Description                               |
| ------ | ------------------------------- | ----------------------------------------- |
| GET    | `/sessions/`                    | List sessions (filtered)                  |
| GET    | `/sessions/{id}/`               | Session detail with stats                 |
| POST   | `/sessions/open_session/`       | Open a new session                        |
| POST   | `/sessions/{id}/close_session/` | Close & reconcile session                 |
| GET    | `/sessions/current/`            | Current user's or terminal's open session |
| GET    | `/sessions/{id}/summary/`       | Detailed summary with payment breakdown   |
| GET    | `/sessions/my_sessions/`        | Current user's session history            |

### Open Session — Request Body

```json
{
  "terminal": "<uuid>",
  "opening_cash_amount": "10000.00"
}
```

### Close Session — Request Body

```json
{
  "actual_cash_amount": "12500.00"
}
```

### Filters

- `status` — exact
- `terminal` — UUID
- `operator` — UUID (user)
- `opened_after` / `opened_before` — datetime

---

## Cart

| Method | Path                                        | Description                       |
| ------ | ------------------------------------------- | --------------------------------- |
| GET    | `/cart/`                                    | List carts                        |
| GET    | `/cart/{id}/`                               | Cart detail with items & payments |
| POST   | `/cart/{id}/add_item/`                      | Add product to cart               |
| PATCH  | `/cart/{id}/update_quantity/{item_id}/`     | Update line quantity              |
| DELETE | `/cart/{id}/remove_item/{item_id}/`         | Remove line from cart             |
| POST   | `/cart/{id}/apply_discount/`                | Apply cart-level discount         |
| POST   | `/cart/{id}/apply_line_discount/{item_id}/` | Apply line discount               |
| POST   | `/cart/{id}/hold/`                          | Hold cart                         |
| POST   | `/cart/{id}/recall/`                        | Recall held cart                  |
| POST   | `/cart/{id}/void/`                          | Void cart                         |
| GET    | `/cart/active/`                             | Active carts for current user     |
| GET    | `/cart/held/`                               | Held carts for current user       |

### Add Item — Request Body

```json
{
  "product": "<uuid>",
  "quantity": 2,
  "variant": "<uuid | null>"
}
```

### Cart Discount — Request Body

```json
{
  "discount_type": "percent",
  "discount_value": "10.00",
  "reason": "Loyalty discount"
}
```

---

## Search

| Method | Path                     | Description             |
| ------ | ------------------------ | ----------------------- |
| POST   | `/search/`               | Combined product search |
| POST   | `/search/barcode/`       | Barcode lookup          |
| GET    | `/search/quick-buttons/` | Quick-button groups     |
| GET    | `/search/history/`       | Recent search history   |

### Product Search — Request Body

```json
{
  "query": "Coca Cola",
  "category": "<uuid | null>",
  "limit": 20
}
```

### Barcode Scan — Request Body

```json
{
  "barcode": "8901234567890"
}
```

---

## Payment

| Method | Path                             | Description                       |
| ------ | -------------------------------- | --------------------------------- |
| POST   | `/payment/process/`              | Process single payment            |
| POST   | `/payment/split/`                | Split payment (2+ methods)        |
| POST   | `/payment/complete/`             | Explicitly complete a transaction |
| GET    | `/payment/history/?session={id}` | Payment history for session       |
| POST   | `/payment/{id}/refund/`          | Refund a completed payment        |
| GET    | `/payment/{id}/status/`          | Check payment status              |

### Process Payment — Request Body

```json
{
  "cart": "<uuid>",
  "payment_method": "cash",
  "amount": "500.00",
  "tendered_amount": "1000.00",
  "reference_number": "",
  "authorization_code": ""
}
```

### Split Payment — Request Body

```json
{
  "cart": "<uuid>",
  "payments": [
    { "payment_method": "cash", "amount": "300.00", "tendered_amount": "300.00" },
    { "payment_method": "card", "amount": "200.00", "authorization_code": "AUTH-1" }
  ]
}
```

### Refund — Request Body

```json
{
  "refund_amount": "150.00",
  "reason": "Product damaged"
}
```

---

## Common Response Patterns

### Success (200 / 201)

Standard DRF serializer output. List endpoints use `StandardPagination`
(page-based, `PAGE_SIZE=20`).

### Error Responses

| Status | Meaning                                                  |
| ------ | -------------------------------------------------------- |
| 400    | Validation error or bad request                          |
| 401    | Authentication required                                  |
| 404    | Resource not found                                       |
| 409    | Conflict (e.g., deactivating terminal with open session) |
