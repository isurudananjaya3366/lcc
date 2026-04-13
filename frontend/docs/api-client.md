# API Client Documentation

> **SubPhase:** SP04 — API Client Layer  
> **Version:** 1.0.0  
> **Last Updated:** 2025-07-14

---

## Overview

The LankaCommerce API Client provides a type-safe, feature-rich HTTP client layer built on Axios for the Next.js frontend. It includes authentication management, request/response interceptors, module-specific services, caching, rate limiting, and file handling utilities.

---

## Quick Start

```typescript
import {
  apiClient,
  authService,
  productService,
  salesService,
} from '@/services/api';
import type { Product, Order } from '@/services/api';

// Login
const { data } = await authService.login({
  email: 'admin@lankacommerce.com',
  password: 'password',
});

// Fetch products
const products = await productService.getProducts({ page: 1, pageSize: 20 });

// Create an order
const order = await salesService.createOrder({ ... });
```

---

## Architecture

```
services/api/
├── apiClient.ts          # Core Axios instance & factory
├── authService.ts        # Authentication (login, logout, refresh)
├── index.ts              # Barrel exports
│
├── interceptors/
│   ├── request.interceptor.ts   # Auth, tenant, request-id headers
│   └── response.interceptor.ts  # Token refresh queue, error routing
│
├── productService.ts     # Product CRUD, variants, images
├── categoryService.ts    # Category tree & CRUD
├── inventoryService.ts   # Stock levels, movements, transfers
├── warehouseService.ts   # Warehouse & location management
├── customerService.ts    # Customer CRUD, addresses, loyalty
├── vendorService.ts      # Vendor CRUD, POs, invoices, performance
├── salesService.ts       # Order CRUD, items, payments, shipments
├── invoiceService.ts     # Invoice lifecycle & PDF
├── employeeService.ts    # Employee, department, position CRUD
├── attendanceService.ts  # Check-in/out, attendance tracking
├── payrollService.ts     # Payroll runs & payslips
├── reportsService.ts     # Reports generation & export
└── settingsService.ts    # Tenant settings, features, tax rates

lib/
├── tokenStorage.ts       # JWT token persistence (localStorage)
├── apiError.ts           # ApiException class, retry logic
├── queryString.ts        # Query string builder & parser
├── urlBuilder.ts         # URL path builder with param replacement
├── formDataBuilder.ts    # FormData construction utility
├── fileHelpers.ts        # Upload/download with progress
├── apiCache.ts           # In-memory GET cache (LRU, TTL)
└── rateLimiter.ts        # Client-side rate limiter (token bucket)

hooks/
├── useAbortController.ts # React hook for request cancellation
└── useOnlineStatus.ts    # React hook for online/offline detection

types/
├── api.ts                # APIResponse, PaginatedResponse, etc.
├── auth.ts               # User, LoginRequest, tokens
├── product.ts            # Product, Variant, Category types
├── inventory.ts          # Stock, Warehouse, Movement types
├── customer.ts           # Customer, Address, Loyalty types
├── vendor.ts             # Vendor, PurchaseOrder types
├── sales.ts              # Order, OrderItem, Payment types
├── hr.ts                 # Employee, Attendance, Payroll types
└── reports.ts            # ReportConfig, SalesReport types

mocks/
├── data/index.ts         # Shared mock fixtures
├── handlers.ts           # MSW request handlers
├── browser.ts            # MSW browser worker
└── server.ts             # MSW Node server (testing)
```

---

## Core API Client

The `apiClient` is a pre-configured Axios instance:

| Setting | Value |
|---------|-------|
| Base URL | `NEXT_PUBLIC_API_URL` env variable |
| Timeout | 30 seconds |
| Credentials | `withCredentials: true` |
| Content-Type | `application/json` |

### Request Interceptor

Automatically attaches:
- `Authorization: Bearer <token>` (from localStorage)
- `X-Tenant-ID` (extracted from subdomain)
- `X-Request-ID` (UUID for distributed tracing)
- `metadata.startTime` (for response timing)

Skipped for public endpoints (`/auth/login`, `/auth/register`, etc.) via `skipAuth` config flag.

### Response Interceptor

- **401 Unauthorized:** Queues concurrent requests and refreshes token once. On success, replays queued requests. On failure, redirects to login.
- **403 Forbidden:** Throws `PermissionError`.
- **404 Not Found:** Throws `NotFoundError`.
- **422 Validation:** Throws `ValidationError` with field-level errors.
- **5xx Server:** Throws `ServerError` with `retryable` flag.

---

## Services Reference

### Auth Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `login(credentials)` | POST `/auth/login/` | Authenticate & store tokens |
| `logout()` | POST `/auth/logout/` | Clear tokens |
| `refreshToken()` | POST `/auth/token/refresh/` | Refresh access token |
| `getCurrentUser()` | GET `/auth/me/` | Get authenticated user |
| `forgotPassword(email)` | POST `/auth/forgot-password/` | Request reset email |
| `resetPassword(data)` | POST `/auth/reset-password/` | Set new password |
| `changePassword(data)` | POST `/auth/change-password/` | Change password |

### Product Service

| Method | Description |
|--------|-------------|
| `getProducts(params?)` | List with pagination/search |
| `getProductById(id)` | Get by ID |
| `getProductBySku(sku)` | Get by SKU |
| `createProduct(data)` | Create new product |
| `updateProduct(id, data)` | Partial update |
| `deleteProduct(id)` | Delete product |
| `bulkUpdateProducts(ops)` | Batch update |
| `getProductVariants(id)` | List variants |
| `uploadProductImage(id, file)` | Upload image |

### Sales / Order Service

| Method | Description |
|--------|-------------|
| `getOrders(params?)` | List with pagination |
| `createOrder(data)` | Create order |
| `cancelOrder(id, reason)` | Cancel with reason |
| `addOrderItem(orderId, item)` | Add line item |
| `recordPayment(orderId, payment)` | Record payment |
| `quickSale(data)` | POS quick sale flow |
| `getOrderSummary(params?)` | Sales summary stats |

### Inventory Service

| Method | Description |
|--------|-------------|
| `getStockLevels(params?)` | Current stock |
| `createStockMovement(data)` | Record movement |
| `createStockAdjustment(data)` | Adjust stock |
| `createStockTransfer(data)` | Transfer between warehouses |
| `getLowStockAlerts(params?)` | Low stock items |
| `reserveStock(productId, ...)` | Reserve for order |

*(See individual service files for complete method listings.)*

---

## Utilities

### Query String Builder

```typescript
import { buildQueryString, parseQueryString } from '@/lib/queryString';

buildQueryString({ search: 'tea', page: 1, tags: ['new', 'sale'] });
// → search=tea&page=1&tags=new&tags=sale

buildQueryString(
  { tags: ['a', 'b'] },
  { arrayFormat: 'comma' }
);
// → tags=a,b
```

### URL Builder

```typescript
import { buildUrl } from '@/lib/urlBuilder';

buildUrl('/users/:id', { pathParams: { id: 42 } });
// → /users/42

buildUrl('/users/:id', {
  baseUrl: 'https://api.example.com',
  pathParams: { id: 42 },
  queryParams: { include: 'profile' },
});
// → https://api.example.com/users/42?include=profile
```

### File Upload / Download

```typescript
import { uploadFile, downloadFile, validateFile } from '@/lib/fileHelpers';

// Validate
const result = validateFile(file, { maxSize: 5_000_000, allowedTypes: ['image/jpeg'] });

// Upload with progress
const controller = uploadFile(file, '/api/v1/upload/', {
  onProgress: (p) => console.log(`${p.percentage}%`),
  onSuccess: (res) => console.log('Done', res),
});

// Cancel
controller.abort();

// Download
await downloadFile('/api/v1/reports/42/pdf/', { filename: 'report.pdf' });
```

### API Cache

```typescript
import { ApiCache, getApiCache } from '@/lib/apiCache';

const cache = getApiCache({ maxAge: 60_000, maxSize: 50 });
cache.set('key', data);
const cached = cache.get('key');
cache.invalidatePattern(/\/products/);
```

### Rate Limiter

```typescript
import { RateLimiter } from '@/lib/rateLimiter';

const limiter = new RateLimiter({ maxRequests: 10, windowMs: 60_000 });

const data = await limiter.execute(() => apiClient.get('/api/v1/data'));
const retried = await limiter.executeWithRetry(() => apiClient.get('/api/v1/data'));
```

---

## React Hooks

### `useAbortController`

Auto-cancels in-flight requests on component unmount.

```typescript
import { useAbortController } from '@/hooks/useAbortController';

function MyComponent() {
  const { getSignal } = useAbortController();

  useEffect(() => {
    apiClient.get('/api/v1/data', { signal: getSignal() });
  }, []);
}
```

### `useOnlineStatus`

Track browser online/offline state.

```typescript
import { useOnlineStatus } from '@/hooks/useOnlineStatus';

function MyComponent() {
  const { isOnline, wasOffline } = useOnlineStatus();
  if (!isOnline) return <OfflineBanner />;
}
```

---

## Mock Server (MSW)

Development and testing use [Mock Service Worker](https://mswjs.io/) to intercept requests.

**Development mode:**
```typescript
// In app initialization
if (process.env.NODE_ENV === 'development') {
  const { worker } = await import('@/mocks/browser');
  worker.start();
}
```

**Test mode:**
```typescript
import { server } from '@/mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

---

## Error Handling

All API errors are normalized to `ApiException`:

```typescript
import { ApiException, parseApiError, isRetryable, retryRequest } from '@/lib/apiError';

try {
  await productService.getProductById('invalid');
} catch (err) {
  const apiErr = parseApiError(err);
  console.log(apiErr.code, apiErr.status, apiErr.message);

  if (isRetryable(apiErr)) {
    const data = await retryRequest(() => productService.getProductById('1'));
  }
}
```

---

## Multi-Tenancy

Tenant isolation is handled automatically via the request interceptor:

1. Subdomain is extracted from `window.location.hostname`
2. `X-Tenant-ID` header is set on every request
3. Backend uses django-tenants to route to the correct schema
4. Requests with `skipTenant: true` config bypass this header

---

## Type Exports

All types are available from the barrel export:

```typescript
import type {
  Product, Customer, Order, Employee,
  APIResponse, PaginatedResponse,
} from '@/services/api';
```
