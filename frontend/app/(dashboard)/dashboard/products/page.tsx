import type { Metadata } from 'next';
import { Suspense } from 'react';
import { ProductList } from '@/components/modules/products/ProductList';

export const metadata: Metadata = {
  title: 'Products',
  description: 'Manage your product catalog, inventory, pricing, and stock levels',
};

export default function ProductsPage() {
  return (
    <Suspense fallback={<ProductListSkeleton />}>
      <ProductList />
    </Suspense>
  );
}

function ProductListSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-7 w-32 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="h-10 w-36 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>
      {/* Filters skeleton */}
      <div className="flex gap-3">
        <div className="h-10 flex-1 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-36 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>
      {/* Table skeleton */}
      <div className="rounded-lg border border-gray-200 dark:border-gray-700">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-4 border-b border-gray-200 px-4 py-3 dark:border-gray-700"
          >
            <div className="h-4 w-4 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-10 w-10 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-4 flex-1 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-4 w-20 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-6 w-16 rounded-full bg-gray-200 dark:bg-gray-700" />
          </div>
        ))}
      </div>
    </div>
  );
}
