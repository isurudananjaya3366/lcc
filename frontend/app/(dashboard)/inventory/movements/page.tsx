import type { Metadata } from 'next';
import { Suspense } from 'react';
import { MovementsPage } from '@/components/modules/inventory/Movements';

export const metadata: Metadata = {
  title: 'Stock Movements - LCC',
  description: 'Track all stock movements and transactions',
  openGraph: {
    title: 'Stock Movements - LCC',
    description: 'Track all stock movements and transactions',
    type: 'website',
  },
};

export default function StockMovementsPage() {
  return (
    <Suspense fallback={<MovementsSkeleton />}>
      <MovementsPage />
    </Suspense>
  );
}

function MovementsSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="flex gap-4">
        <div className="h-10 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="space-y-3">
        <div className="h-10 w-full rounded bg-gray-200 dark:bg-gray-700" />
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-12 w-full rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
