import type { Metadata } from 'next';
import { Suspense } from 'react';
import { AdjustmentForm } from '@/components/modules/inventory/Adjustments';

export const metadata: Metadata = {
  title: 'New Adjustment - LCC',
  description: 'Create a new stock adjustment entry',
  openGraph: {
    title: 'New Adjustment - LCC',
    description: 'Create a new stock adjustment entry',
    type: 'website',
  },
};

export default function NewAdjustmentPage() {
  return (
    <Suspense fallback={<AdjustmentFormSkeleton />}>
      <AdjustmentForm />
    </Suspense>
  );
}

function AdjustmentFormSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="flex gap-2">
          <div className="h-10 w-24 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-10 w-24 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
      <div className="space-y-4 rounded-lg border p-6">
        <div className="h-6 w-32 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="grid grid-cols-2 gap-4">
          <div className="h-10 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-10 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
      <div className="space-y-3 rounded-lg border p-6">
        <div className="h-6 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-12 w-full rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
