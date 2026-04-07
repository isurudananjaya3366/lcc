# Inventory API Reference

Base URL: `/api/v1/stock/`

All endpoints require authentication (`IsAuthenticated`).

---

## Stock Levels

### `GET /stock-levels/`

List all stock levels. Supports filtering, search, and ordering.

**Query Parameters:**

| Param       | Type   | Description                    |
| ----------- | ------ | ------------------------------ |
| `product`   | UUID   | Filter by product ID           |
| `warehouse` | UUID   | Filter by warehouse ID         |
| `search`    | string | Search product name / SKU      |
| `ordering`  | string | Sort field (e.g., `-quantity`) |

**Response:** Paginated list of stock level objects.

### `GET /stock-levels/{id}/`

Retrieve a single stock level with full detail (includes `projected_quantity`, `stock_value`).

### `GET /stock-levels/low-stock/`

Returns stock levels where `quantity <= reorder_point` and `quantity > 0`.

### `GET /stock-levels/out-of-stock/`

Returns stock levels where `quantity = 0`.

### `POST /stock-levels/check-availability/`

Check availability for multiple products at once.

**Request Body:**

```json
{
  "product_ids": ["uuid1", "uuid2"],
  "warehouse_ids": ["uuid1"] // optional
}
```

**Response:** Availability data per product.

---

## Stock Movements

### `GET /stock-movements/`

List all stock movements (read-only). Supports filtering and search.

### `GET /stock-movements/{id}/`

Retrieve a single movement record.

### `GET /stock-movements/for-product/?product_id={uuid}`

Filter movements for a specific product. **Required** query parameter: `product_id`.

### `GET /stock-movements/summary/?days={n}&warehouse_id={uuid}`

Aggregated movement summary. Optional filters: `days` (default 30), `warehouse_id`.

---

## Stock Operations

Write-only endpoints for stock mutations. Each creates a `StockMovement` and updates `StockLevel`.

### `POST /stock-operations/stock-in/`

Receive stock into a warehouse.

```json
{
  "product_id": "uuid",
  "warehouse_id": "uuid",
  "quantity": "10.000",
  "cost_per_unit": "500.000",
  "variant_id": null,
  "location_id": null,
  "reason": "purchase",
  "reference_type": "",
  "reference_id": "",
  "notes": ""
}
```

**Response:** `201 Created` with `OperationResult`.

### `POST /stock-operations/stock-out/`

Dispatch stock from a warehouse.

```json
{
  "product_id": "uuid",
  "warehouse_id": "uuid",
  "quantity": "5.000",
  "reason": "sale",
  "variant_id": null,
  "location_id": null,
  "reference_type": "",
  "reference_id": "",
  "notes": ""
}
```

**Response:** `200 OK` with `OperationResult`. Returns `400` if insufficient stock.

### `POST /stock-operations/transfer/`

Transfer stock between warehouses.

```json
{
  "product_id": "uuid",
  "from_warehouse_id": "uuid",
  "to_warehouse_id": "uuid",
  "quantity": "5.000",
  "variant_id": null,
  "from_location_id": null,
  "to_location_id": null,
  "notes": ""
}
```

**Validation:** Source and destination must differ (or locations must differ within same warehouse).

### `POST /stock-operations/adjust/`

Manual stock adjustment (up or down).

```json
{
  "product_id": "uuid",
  "warehouse_id": "uuid",
  "quantity": "10.000",
  "direction": "up",
  "reason": "found",
  "cost_per_unit": null,
  "variant_id": null,
  "location_id": null,
  "reference_id": "",
  "notes": ""
}
```

---

## Stock Takes

Full CRUD plus lifecycle actions.

### `GET /stock-takes/`

List all stock takes. Filterable by `warehouse`, `status`, `scope`, `approval_status`.

### `POST /stock-takes/`

Create a new stock take.

```json
{
  "warehouse_id": "uuid",
  "name": "Annual Count 2025",
  "scope": "full",
  "is_blind_count": false,
  "scheduled_date": "2025-03-15",
  "description": ""
}
```

### `GET /stock-takes/{id}/`

Retrieve stock take with nested items.

### `DELETE /stock-takes/{id}/`

Delete a stock take. Only allowed when `status = "draft"`.

### Lifecycle Actions

| Endpoint                        | Method | Description                       |
| ------------------------------- | ------ | --------------------------------- |
| `/stock-takes/{id}/start/`      | POST   | Start counting (draft → counting) |
| `/stock-takes/{id}/count/`      | POST   | Record single item count          |
| `/stock-takes/{id}/bulk-count/` | POST   | Record multiple counts            |
| `/stock-takes/{id}/submit/`     | POST   | Submit for review                 |
| `/stock-takes/{id}/approve/`    | POST   | Approve stock take                |
| `/stock-takes/{id}/complete/`   | POST   | Complete and create adjustments   |
| `/stock-takes/{id}/cancel/`     | POST   | Cancel stock take                 |

### Read Actions

| Endpoint                       | Method | Description                      |
| ------------------------------ | ------ | -------------------------------- |
| `/stock-takes/{id}/items/`     | GET    | List all items in the stock take |
| `/stock-takes/{id}/variances/` | GET    | Items with non-zero variance     |
| `/stock-takes/{id}/report/`    | GET    | Variance report data             |

### Count Payload

```json
// Single count
{
  "item_id": "uuid",
  "counted_quantity": "98.000",
  "notes": ""
}

// Bulk count
{
  "counts": [
    {"item_id": "uuid", "counted_quantity": "98.000", "notes": ""},
    {"item_id": "uuid", "counted_quantity": "50.000", "notes": "shelf B"}
  ]
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error description"
}
```

Common HTTP status codes:

| Code  | Meaning                                     |
| ----- | ------------------------------------------- |
| `200` | Success                                     |
| `201` | Created                                     |
| `204` | Deleted                                     |
| `400` | Validation error or business rule violation |
| `401` | Not authenticated                           |
| `404` | Resource not found                          |
