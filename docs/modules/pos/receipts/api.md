# Receipt API Reference

> Back to [Receipt Module](index.md)

All endpoints are prefixed with `/api/v1/pos/`. Authentication is required.

---

## Receipts

| Method | Path                        | Description                            |
| ------ | --------------------------- | -------------------------------------- |
| GET    | `/receipts/`                | List receipts                          |
| GET    | `/receipts/{id}/`           | Retrieve receipt detail                |
| POST   | `/receipts/generate/`       | Generate receipt from a completed cart |
| POST   | `/receipts/{id}/print/`     | Send receipt to thermal printer        |
| POST   | `/receipts/{id}/email/`     | Email receipt to customer              |
| GET    | `/receipts/{id}/pdf/`       | Download receipt as PDF                |
| POST   | `/receipts/{id}/duplicate/` | Create a duplicate receipt             |
| GET    | `/receipts/search/`         | Search receipts with filters           |
| GET    | `/receipts/export/`         | Export receipts as CSV or JSON         |

### Filters (query params on list)

- `search` — receipt number (partial match)
- `ordering` — default `-generated_at`

---

### Generate Receipt

**POST** `/api/v1/pos/receipts/generate/`

Create a receipt from a completed cart.

**Request Body**

```json
{
  "cart": "a1b2c3d4-...",
  "receipt_type": "SALE",
  "template": "t1u2v3w4-...",
  "auto_print": false
}
```

| Field          | Type   | Required | Description                             |
| -------------- | ------ | -------- | --------------------------------------- |
| `cart`         | UUID   | Yes      | Completed cart ID                       |
| `receipt_type` | string | Yes      | `SALE`, `REFUND`, `VOID`                |
| `template`     | UUID   | No       | Template ID; uses default if omitted    |
| `auto_print`   | bool   | No       | Trigger immediate print (default false) |

**Response** `201 Created`

```json
{
  "id": "uuid",
  "receipt_number": "REC-20250101-00001",
  "receipt_type": "SALE",
  "generated_at": "2025-01-01T10:00:00Z",
  "receipt_data": { "..." }
}
```

---

### Print Receipt

**POST** `/api/v1/pos/receipts/{id}/print/`

**Request Body**

```json
{
  "printer_ip": "192.168.1.100",
  "port": 9100,
  "paper_width": "80mm",
  "copies": 1,
  "open_drawer": true
}
```

| Field         | Type   | Required | Description                       |
| ------------- | ------ | -------- | --------------------------------- |
| `printer_ip`  | string | Yes      | Printer IP address                |
| `port`        | int    | No       | TCP port (default 9100)           |
| `paper_width` | string | No       | `80mm` or `58mm` (default `80mm`) |
| `copies`      | int    | No       | Number of copies (default 1)      |
| `open_drawer` | bool   | No       | Open cash drawer after print      |

**Response** `200 OK`

```json
{
  "status": "printed",
  "copies": 1,
  "receipt_number": "REC-20250101-00001"
}
```

---

### Email Receipt

**POST** `/api/v1/pos/receipts/{id}/email/`

**Request Body**

```json
{
  "email": "customer@example.com",
  "subject": "Your Receipt",
  "message": "Thank you for your purchase!",
  "attach_pdf": true,
  "cc": ["manager@example.com"]
}
```

| Field        | Type   | Required | Description               |
| ------------ | ------ | -------- | ------------------------- |
| `email`      | string | Yes      | Recipient email           |
| `subject`    | string | No       | Custom subject line       |
| `message`    | string | No       | Custom body message       |
| `attach_pdf` | bool   | No       | Attach PDF (default true) |
| `cc`         | list   | No       | CC addresses              |

**Response** `200 OK`

```json
{
  "status": "sent",
  "email": "customer@example.com",
  "receipt_number": "REC-20250101-00001"
}
```

---

### Download PDF

**GET** `/api/v1/pos/receipts/{id}/pdf/`

Returns the receipt as a PDF file download.

**Response** `200 OK` — `Content-Type: application/pdf`

---

### Duplicate Receipt

**POST** `/api/v1/pos/receipts/{id}/duplicate/`

**Request Body**

```json
{
  "reason": "Customer requested reprint"
}
```

**Response** `201 Created`

```json
{
  "id": "uuid",
  "receipt_number": "REC-20250101-00002",
  "receipt_type": "DUPLICATE",
  "original_receipt": "uuid-of-original"
}
```

---

### Search Receipts

**GET** `/api/v1/pos/receipts/search/`

| Param          | Type    | Description                  |
| -------------- | ------- | ---------------------------- |
| `query`        | string  | Partial receipt number match |
| `receipt_type` | string  | Filter by type               |
| `date_from`    | date    | Start date (YYYY-MM-DD)      |
| `date_to`      | date    | End date (YYYY-MM-DD)        |
| `cart`         | UUID    | Filter by cart ID            |
| `min_total`    | decimal | Minimum grand total          |
| `max_total`    | decimal | Maximum grand total          |

---

### Export Receipts

**GET** `/api/v1/pos/receipts/export/`

| Param          | Type   | Description                |
| -------------- | ------ | -------------------------- |
| `format`       | string | `csv` or `json` (required) |
| `date_from`    | date   | Start date filter          |
| `date_to`      | date   | End date filter            |
| `receipt_type` | string | Filter by type             |

Maximum 5 000 records per export.

**Response** — `text/csv` or `application/json` file download.

---

## Receipt Templates

| Method | Path                                   | Description                   |
| ------ | -------------------------------------- | ----------------------------- |
| GET    | `/receipt-templates/`                  | List templates                |
| POST   | `/receipt-templates/`                  | Create template               |
| GET    | `/receipt-templates/{id}/`             | Retrieve template             |
| PUT    | `/receipt-templates/{id}/`             | Update template               |
| PATCH  | `/receipt-templates/{id}/`             | Partial update                |
| DELETE | `/receipt-templates/{id}/`             | Soft delete (non-system only) |
| POST   | `/receipt-templates/{id}/set_default/` | Set as tenant default         |
| POST   | `/receipt-templates/{id}/clone/`       | Clone template                |
| POST   | `/receipt-templates/{id}/preview/`     | Preview rendered HTML         |
| GET    | `/receipt-templates/{id}/usage/`       | Usage statistics              |

### Create Template

**POST** `/api/v1/pos/receipt-templates/`

```json
{
  "name": "New Template",
  "paper_size": "80mm",
  "header_business_name": "My Store",
  "is_default": false
}
```

### Clone Template

**POST** `/api/v1/pos/receipt-templates/{id}/clone/`

```json
{
  "new_name": "Copy of Standard"
}
```

### Usage Stats

**GET** `/api/v1/pos/receipt-templates/{id}/usage/`

```json
{
  "total_receipts": 142,
  "recent_receipts": ["REC-20250101-00001", "..."],
  "child_templates": 3
}
```

---

## Error Codes

| Code                        | HTTP | Description                                            |
| --------------------------- | ---- | ------------------------------------------------------ |
| `cart_not_found`            | 404  | Cart UUID does not exist                               |
| `cart_validation_error`     | 400  | Cart is not in "completed" status                      |
| `template_not_found`        | 404  | Template UUID does not exist and no default configured |
| `receipt_generation_error`  | 500  | Builder or number generator failure                    |
| `printer_connection_error`  | 502  | Cannot connect to thermal printer                      |
| `email_send_failed`         | 502  | SMTP delivery failure                                  |
| `duplicate_not_allowed`     | 400  | Cannot duplicate a VOID or DUPLICATE receipt           |
| `export_limit_exceeded`     | 400  | Export exceeds 5 000 record limit                      |
| `system_template_protected` | 403  | Cannot delete a system template                        |

### Error Response Format

```json
{
  "detail": "Cart is not in completed status.",
  "code": "cart_validation_error"
}
```

---

## Integration Guide

### Generate a receipt after sale

```python
import requests

# After cart is completed
resp = requests.post(
    "https://api.example.com/api/v1/pos/receipts/generate/",
    headers={"Authorization": "Bearer <token>"},
    json={"cart": str(cart.pk), "receipt_type": "SALE"},
)
receipt = resp.json()
```

### Handle print failures

```python
resp = requests.post(
    f"https://api.example.com/api/v1/pos/receipts/{receipt_id}/print/",
    headers={"Authorization": "Bearer <token>"},
    json={"printer_ip": "192.168.1.100"},
)
if resp.status_code == 502:
    # Printer unreachable — queue for retry or offer email
    pass
```

### JavaScript (fetch)

```javascript
const resp = await fetch("/api/v1/pos/receipts/generate/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    cart: cartId,
    receipt_type: "SALE",
  }),
});
const receipt = await resp.json();
```

---

## Configuration Reference

### Environment Variables

| Variable                | Description            | Default      |
| ----------------------- | ---------------------- | ------------ |
| `RECEIPT_PDF_ENGINE`    | `weasyprint` or `html` | `weasyprint` |
| `RECEIPT_DEFAULT_PAPER` | Default paper size     | `80mm`       |
| `RECEIPT_MAX_EXPORT`    | Max export records     | `5000`       |

### Django Settings

```python
# config/settings/base.py
RECEIPT_NUMBER_PREFIX = "REC"
RECEIPT_NUMBER_DATE_FORMAT = "%Y%m%d"
RECEIPT_NUMBER_PAD = 5  # digits for sequence
```
