# Infinite Queries

## Overview

For large scrollable lists, use the infinite query hooks in
`hooks/infiniteQueries/`. They use `useInfiniteQuery` from TanStack
Query with offset-based pagination.

## Available Hooks

| Hook | Page Size | Stale Time |
|------|----------|-----------|
| `useInfiniteProducts` | 20 | 5 min |
| `useInfiniteCustomers` | 20 | 3 min |
| `useInfiniteOrders` | 20 | 1 min |

## Usage

```tsx
import { useInfiniteProducts } from '@/hooks/infiniteQueries';

function ProductGrid() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteProducts({ status: 'active' });

  const allProducts = data?.pages.flatMap((page) => page.results) ?? [];

  return (
    <>
      {allProducts.map((p) => <ProductCard key={p.id} product={p} />)}
      {hasNextPage && (
        <button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          Load more
        </button>
      )}
    </>
  );
}
```

## How Pagination Works

Each hook passes `page` and `page_size` to the API service.
`getNextPageParam` calculates whether more pages exist by comparing
the total `count` from the API response against items loaded so far.
