# Cache Management

## Invalidation Strategies

The `invalidateCache` function in `hooks/mutations/cacheInvalidation.ts`
supports five strategies:

| Strategy | Behaviour |
|----------|-----------|
| `EXACT` | Invalidates a single query by exact key match |
| `PARTIAL` | Invalidates all queries whose key starts with the resource |
| `ALL` | Invalidates every query whose first key segment matches |
| `RELATED` | Invalidates the resource + all related resources |
| `SELECTIVE` | Runs a custom predicate against every cached query |

## Usage

```ts
import { invalidateCache, getRelatedResources } from '@/hooks/mutations';

// After creating a product → invalidate product lists + inventory
invalidateCache(queryClient, {
  resource: 'products',
  strategy: 'PARTIAL',
  relatedResources: getRelatedResources('products', 'create'),
});
```

## Related Resources Matrix

| Resource | Action | Related |
|----------|--------|---------|
| products | create | inventory |
| products | update | orders, inventory |
| products | delete | orders, inventory |
| orders | create | products, customers |
| customers | update | orders |

## Removing from Cache

```ts
import { removeFromCache } from '@/hooks/mutations';

removeFromCache(queryClient, 'products', '42');
```
