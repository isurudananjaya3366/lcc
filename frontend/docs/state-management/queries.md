# Query Hooks

## Overview

All server data is fetched through TanStack Query hooks in `hooks/queries/`.
Each hook uses a key factory from `lib/queryKeys.ts` and calls the
corresponding API service.

## Key Factories

Keys follow the factory pattern (`[resource, scope, ...args]`):

```ts
import { productKeys } from '@/lib/queryKeys';

productKeys.all       // ['products']
productKeys.lists()   // ['products', 'list']
productKeys.list({})  // ['products', 'list', { ...filters }]
productKeys.detail(id) // ['products', 'detail', id]
```

## Available Hooks

| Hook | Stale Time | Service |
|------|-----------|---------|
| `useProducts` | 5 min | productService |
| `useProduct` | 10 min | productService |
| `useCategories` | 30 min | categoryService |
| `useInventory` | 2 min | inventoryService |
| `useWarehouses` | 15 min | warehouseService |
| `useStockMovements` | 1 min | inventoryService |
| `useCustomers` | 3 min | customerService |
| `useCustomer` | 5 min | customerService |
| `useVendors` | 5 min | vendorService |
| `useOrders` | 1 min | salesService |
| `useOrder` | 2 min | salesService |
| `useInvoices` | 1 min | invoiceService |
| `useEmployees` | 10 min | employeeService |
| `useEmployee` | 15 min | employeeService |
| `useAttendance` | 30 sec | attendanceService |
| `useDashboardStats` | 1 min | reportsService |
| `useReports` | 5 min | reportsService |

## Usage

```tsx
import { useProducts } from '@/hooks/queries';

function ProductList() {
  const { data, isLoading, error } = useProducts({ status: 'active' });
  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;
  return <Table data={data.results} />;
}
```
