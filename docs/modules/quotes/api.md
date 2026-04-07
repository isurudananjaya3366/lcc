# Quote API Reference

## Authenticated Endpoints

All authenticated endpoints require a valid JWT token.

### Quotes CRUD

| Method | Endpoint                      | Description                         |
| ------ | ----------------------------- | ----------------------------------- |
| GET    | `/api/v1/quotes/quotes/`      | List quotes (paginated, filterable) |
| POST   | `/api/v1/quotes/quotes/`      | Create a new draft quote            |
| GET    | `/api/v1/quotes/quotes/{id}/` | Retrieve quote detail               |
| PATCH  | `/api/v1/quotes/quotes/{id}/` | Update a draft quote                |
| DELETE | `/api/v1/quotes/quotes/{id}/` | Delete a draft quote                |

### Status Actions

| Method | Endpoint                                       | Description                     |
| ------ | ---------------------------------------------- | ------------------------------- |
| POST   | `/api/v1/quotes/quotes/{id}/send/`             | Send quote to customer          |
| POST   | `/api/v1/quotes/quotes/{id}/accept/`           | Accept a sent quote             |
| POST   | `/api/v1/quotes/quotes/{id}/reject/`           | Reject a sent quote             |
| POST   | `/api/v1/quotes/quotes/{id}/duplicate/`        | Duplicate a quote               |
| POST   | `/api/v1/quotes/quotes/{id}/create_revision/`  | Create a new revision           |
| POST   | `/api/v1/quotes/quotes/{id}/convert_to_order/` | Convert accepted quote to order |

### PDF & Email

| Method | Endpoint                                   | Description             |
| ------ | ------------------------------------------ | ----------------------- |
| POST   | `/api/v1/quotes/quotes/{id}/generate_pdf/` | Generate/regenerate PDF |
| GET    | `/api/v1/quotes/quotes/{id}/download_pdf/` | Download the PDF file   |
| POST   | `/api/v1/quotes/quotes/{id}/send_email/`   | Send quote via email    |

### Line Items & History

| Method   | Endpoint                                        | Description           |
| -------- | ----------------------------------------------- | --------------------- |
| GET/POST | `/api/v1/quotes/quotes/{id}/line_items/`        | List/add line items   |
| GET      | `/api/v1/quotes/quotes/{id}/history/`           | View audit history    |
| GET      | `/api/v1/quotes/quotes/{id}/available_actions/` | Get available actions |

### Filtering & Search

**Filter parameters** (via django-filter):

- `status` — Filter by status (draft, sent, accepted, etc.)
- `currency` — Filter by currency (LKR, USD)
- `created_on_after` / `created_on_before` — Date range
- `total_min` / `total_max` — Amount range
- `customer` — Filter by customer ID

**Search fields** (via `?search=`):

- `quote_number`, `title`, `guest_name`, `guest_email`
- `customer__first_name`, `customer__last_name`, `customer__business_name`

---

## Public Endpoints (No Authentication)

| Method | Endpoint                                | Description                        |
| ------ | --------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/quotes/public/{token}/`        | View quote (increments view count) |
| GET    | `/api/v1/quotes/public/{token}/pdf/`    | Download PDF                       |
| POST   | `/api/v1/quotes/public/{token}/accept/` | Accept the quote                   |
| POST   | `/api/v1/quotes/public/{token}/reject/` | Reject (reason required)           |

**Public endpoint notes:**

- `token` is a UUID generated when the quote is sent
- Expired quotes cannot be accepted or rejected via public endpoints
- View count and last_viewed_at are tracked automatically
- Rejection requires a `reason` field in the request body
