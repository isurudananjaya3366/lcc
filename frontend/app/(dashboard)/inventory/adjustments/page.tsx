import type { Metadata } from 'next';
import { Suspense } from 'react';
import { AdjustmentsList } from '@/components/modules/inventory/Adjustments';

export const metadata: Metadata = {
  title: 'Stock Adjustments - LCC',
  description: 'View and manage stock adjustment records',
  openGraph: {
    title: 'Stock Adjustments - LCC',
    description: 'View and manage stock adjustment records',
    type: 'website',
  },
};

export default function AdjustmentsPage() {
  return (
    <Suspense fallback={<AdjustmentsSkeleton />}>
      <AdjustmentsList />
    </Suspense>
  );
}

function AdjustmentsSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
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
