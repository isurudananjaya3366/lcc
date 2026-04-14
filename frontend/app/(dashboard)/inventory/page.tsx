import type { Metadata } from 'next';
import { Suspense } from 'react';
import { StockOverview } from '@/components/modules/inventory/StockOverview';

export const metadata: Metadata = {
  title: 'Inventory - LCC',
  description: 'View and manage stock levels across warehouses',
  openGraph: {
    title: 'Inventory - LCC',
    description: 'View and manage stock levels across warehouses',
    type: 'website',
  },
};

export default function InventoryPage() {
  return (
    <Suspense fallback={<StockOverviewSkeleton />}>
      <StockOverview />
    </Suspense>
  );
}

function StockOverviewSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      {/* Summary cards skeleton */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-28 rounded-lg bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      {/* Filters skeleton */}
      <div className="flex gap-4">
        <div className="h-10 w-64 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      {/* Table skeleton */}
      <div className="space-y-3">
        <div className="h-10 w-full rounded bg-gray-200 dark:bg-gray-700" />
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-12 w-full rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
