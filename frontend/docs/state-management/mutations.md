# Mutation Hooks

## Overview

Mutations live in `hooks/mutations/`. Each hook wraps `useMutation`
from TanStack Query with automatic cache invalidation.

## Product Mutations

```tsx
import { useCreateProduct, useUpdateProduct, useDeleteProduct } from '@/hooks/mutations';

function ProductForm() {
  const create = useCreateProduct();
  const update = useUpdateProduct();
  const remove = useDeleteProduct();

  const handleSave = () =>
    create.mutate({ name: 'Widget', price: 100 });

  const handleUpdate = () =>
    update.mutate({ id: '1', updates: { price: 120 } });

  const handleDelete = () =>
    remove.mutate('1');
}
```

## Mutation Factory

For resources that follow a standard CRUD pattern, use `createMutationHooks`:

```ts
import { createMutationHooks } from '@/hooks/mutations';
import { customerService } from '@/services/api/customerService';

const {
  useCreate: useCreateCustomer,
  useUpdate: useUpdateCustomer,
  useDelete: useDeleteCustomer,
} = createMutationHooks({
  resource: 'customers',
  createFn: customerService.createCustomer,
  updateFn: customerService.updateCustomer,
  deleteFn: customerService.deleteCustomer,
});
```

## Error Handling

All mutations disable automatic retries (`retry: false`).
Use `onError` to show user-facing messages:

```tsx
const create = useCreateProduct();

create.mutate(data, {
  onError: (error) => toast.error(error.message),
});
```
