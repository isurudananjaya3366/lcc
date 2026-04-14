import type { Metadata } from 'next';
import { Suspense } from 'react';
import { TransfersList } from '@/components/modules/inventory/Transfers';

export const metadata: Metadata = {
  title: 'Warehouse Transfers - LCC',
  description: 'Manage stock transfers between warehouses',
  openGraph: {
    title: 'Warehouse Transfers - LCC',
    description: 'Manage stock transfers between warehouses',
    type: 'website',
  },
};

export default function TransfersPage() {
  return (
    <Suspense fallback={<TransfersSkeleton />}>
      <TransfersList />
    </Suspense>
  );
}

function TransfersSkeleton() {
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
