# POS API Integration

## Base URL

```
/api/v1/pos/
```

## Service Layer

All API calls are centralized in `services/pos.ts` via the `posService` object.

## Endpoints

### Products

| Method | Endpoint                   | Service Method          | Description                         |
| ------ | -------------------------- | ----------------------- | ----------------------------------- |
| GET    | `/products/`               | `searchProducts(query)` | Search products by name/SKU/barcode |
| GET    | `/products/quick-buttons/` | `getQuickButtons()`     | Get configured quick-add products   |

### Sessions (Shifts)

| Method | Endpoint               | Service Method                         | Description                   |
| ------ | ---------------------- | -------------------------------------- | ----------------------------- |
| POST   | `/sessions/open/`      | `openSession(terminalId, openingCash)` | Open a new POS session        |
| POST   | `/sessions/:id/close/` | `closeSession(sessionId, data)`        | Close session with cash count |
| GET    | `/sessions/active/`    | `getActiveSession()`                   | Get current active session    |

### Payments

| Method | Endpoint              | Service Method            | Description                |
| ------ | --------------------- | ------------------------- | -------------------------- |
| POST   | `/payments/complete/` | `completePayment(cartId)` | Complete sale with payment |

### Customers

| Method | Endpoint      | Service Method           | Description                    |
| ------ | ------------- | ------------------------ | ------------------------------ |
| GET    | `/customers/` | `searchCustomers(query)` | Search customers by name/phone |

### Receipts

| Method | Endpoint               | Service Method                   | Description               |
| ------ | ---------------------- | -------------------------------- | ------------------------- |
| POST   | `/receipts/:id/email/` | `emailReceipt(receiptId, email)` | Email receipt to customer |

## Request/Response Format

All requests use JSON. Standard response wrapper:

```typescript
interface APIResponse<T> {
  data: T;
  status: number;
  message?: string;
}
```

## Error Handling

The `api` utility handles common errors:

- **401**: Redirect to login
- **403**: Permission denied
- **404**: Resource not found
- **500**: Server error with retry option

Components show user-friendly error messages via inline `<p className="text-red-500">` elements.

## Authentication

All POS API calls include the session JWT token via cookies. The `api` utility handles authentication headers automatically.

## Offline Considerations

- Cart state persisted in localStorage (Zustand persist middleware)
- Held sales stored in React context + localStorage
- API failures show retry options in UI
- Search degrades gracefully (empty results on network error)
