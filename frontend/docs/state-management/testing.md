# Testing State & Queries

## Testing Zustand Stores

Reset stores between tests using `resetAllStores()`:

```ts
import { resetAllStores } from '@/stores';

afterEach(() => resetAllStores());
```

Access store state directly in tests:

```ts
import { useUIStore } from '@/stores';

test('toggleSidebar flips isCollapsed', () => {
  const store = useUIStore.getState();
  expect(store.isCollapsed).toBe(false);
  store.toggleSidebar();
  expect(useUIStore.getState().isCollapsed).toBe(true);
});
```

## Testing Query Hooks

Wrap components with a test `QueryClientProvider`:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook } from '@testing-library/react';

function createWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

test('useProducts returns data', async () => {
  const { result } = renderHook(() => useProducts(), {
    wrapper: createWrapper(),
  });
  // ...assertions
});
```

## Testing Mutations

Mock the API service and assert cache invalidation:

```ts
vi.mock('@/services/api/productService', () => ({
  productService: {
    createProduct: vi.fn().mockResolvedValue({ data: { id: '1' } }),
  },
}));
```

## MSW Integration

For integration tests, prefer MSW handlers over direct mocks
to exercise the full Axios → TanStack Query pipeline.
