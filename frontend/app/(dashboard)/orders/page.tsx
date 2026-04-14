import type { Metadata } from 'next';
import { Suspense } from 'react';
import { OrdersList } from '@/components/modules/sales/Orders/OrdersList';

export const metadata: Metadata = {
  title: 'Orders - LCC',
  description: 'Manage and track all customer orders',
  openGraph: {
    title: 'Orders - LCC',
    description: 'Manage and track all customer orders',
    type: 'website',
  },
};

export default function OrdersPage() {
  return (
    <Suspense fallback={<OrdersListSkeleton />}>
      <OrdersList />
    </Suspense>
  );
}

function OrdersListSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      {/* Summary cards skeleton */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-28 rounded-lg bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      {/* Filters */}
      <div className="flex gap-4">
        <div className="h-10 w-64 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      {/* Table */}
      <div className="space-y-3">
        <div className="h-10 w-full rounded bg-gray-200 dark:bg-gray-700" />
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-12 w-full rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
