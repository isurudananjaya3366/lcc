# Invoice Module — API Reference

Base URL: `/api/v1/invoices/`

## Endpoints

### List Invoices

```
GET /api/v1/invoices/
```

**Query Parameters:**

| Parameter         | Type    | Description                                              |
| ----------------- | ------- | -------------------------------------------------------- |
| `status`          | string  | Filter by status (DRAFT, ISSUED, SENT, PAID, etc.)       |
| `type`            | string  | Filter by type (STANDARD, SVAT, CREDIT_NOTE, DEBIT_NOTE) |
| `tax_scheme`      | string  | Filter by tax scheme (VAT, SVAT, NONE, EXEMPT)           |
| `customer`        | UUID    | Filter by customer ID                                    |
| `order`           | UUID    | Filter by order ID                                       |
| `issue_date_from` | date    | Issue date range start                                   |
| `issue_date_to`   | date    | Issue date range end                                     |
| `due_date_from`   | date    | Due date range start                                     |
| `due_date_to`     | date    | Due date range end                                       |
| `total_min`       | decimal | Minimum total amount                                     |
| `total_max`       | decimal | Maximum total amount                                     |
| `is_overdue`      | boolean | Filter overdue invoices                                  |
| `search`          | string  | Search invoice number, customer name, email              |

**Response:** Paginated list using `InvoiceListSerializer`.

### Create Invoice

```
POST /api/v1/invoices/
```

**Request Body:**

```json
{
  "type": "STANDARD",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "business_name": "My Business",
  "currency": "LKR",
  "tax_scheme": "VAT",
  "line_items": [
    {
      "description": "Product A",
      "quantity": "2.00",
      "unit_price": "1000.00",
      "tax_rate": "12.00",
      "is_taxable": true
    }
  ]
}
```

### Retrieve Invoice

```
GET /api/v1/invoices/{id}/
```

### Update Invoice

```
PUT/PATCH /api/v1/invoices/{id}/
```

Only DRAFT invoices can be updated.

### Delete Invoice

```
DELETE /api/v1/invoices/{id}/
```

Soft-deletes the invoice.

---

## Custom Actions

### Issue Invoice

```
POST /api/v1/invoices/{id}/issue/
```

Transitions DRAFT → ISSUED. Generates invoice number and sets due date.

### Send Invoice

```
POST /api/v1/invoices/{id}/send/
```

Transitions ISSUED → SENT. Triggers email with PDF attachment.

### Mark Paid

```
POST /api/v1/invoices/{id}/mark-paid/
```

Records payment. Accepts optional `amount` for partial payments.

```json
{ "amount": "5000.00" }
```

### Cancel Invoice

```
POST /api/v1/invoices/{id}/cancel/
```

Cancels a DRAFT invoice. Accepts optional `reason`.

### Void Invoice

```
POST /api/v1/invoices/{id}/void/
```

Voids an ISSUED/SENT invoice. Accepts optional `reason`.

### Duplicate Invoice

```
POST /api/v1/invoices/{id}/duplicate/
```

Creates a new DRAFT copy of the invoice with all line items.

### Download PDF

```
GET /api/v1/invoices/{id}/pdf/
```

Returns the generated PDF file.

### HTML Preview

```
GET /api/v1/invoices/{id}/preview/
```

Returns rendered HTML for browser preview.

### Invoice History

```
GET /api/v1/invoices/{id}/history/
```

Returns audit trail for the invoice.

---

## Reports

### Aging Report

```
GET /api/v1/invoices/reports/aging/
```

**Response:**

```json
{
  "current": "50000.00",
  "30_days": "25000.00",
  "60_days": "10000.00",
  "90_days": "5000.00",
  "90_plus": "2000.00",
  "total": "92000.00"
}
```

---

## Error Responses

| Status | Description                                 |
| ------ | ------------------------------------------- |
| 400    | Invalid transition, business rule violation |
| 401    | Not authenticated                           |
| 404    | Invoice not found                           |
| 500    | Server error                                |

Error format:

```json
{ "detail": "Cannot transition from DRAFT to PAID. Allowed: ['ISSUED', 'CANCELLED']" }
```
