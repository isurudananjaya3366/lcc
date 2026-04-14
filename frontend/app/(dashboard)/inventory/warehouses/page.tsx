import type { Metadata } from 'next';
import { Suspense } from 'react';
import { WarehouseList } from '@/components/modules/inventory/Warehouses';

export const metadata: Metadata = {
  title: 'Warehouses - LCC',
  description: 'Manage warehouse locations and configurations',
  openGraph: {
    title: 'Warehouses - LCC',
    description: 'Manage warehouse locations and configurations',
    type: 'website',
  },
};

export default function WarehousesPage() {
  return (
    <Suspense fallback={<WarehousesSkeleton />}>
      <WarehouseList />
    </Suspense>
  );
}

function WarehousesSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="flex gap-4">
        <div className="h-10 w-64 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-48 rounded-lg bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
