import { Suspense } from 'react';
import { VendorsList } from '@/components/modules/crm/Vendors/VendorsList';
import { createCRMMetadata } from '@/lib/metadata/crm';

export const metadata = createCRMMetadata('Vendors', 'Manage suppliers and view vendor details');

export default function VendorsPage() {
  return (
    <Suspense fallback={<VendorsListSkeleton />}>
      <VendorsList />
    </Suspense>
  );
}

function VendorsListSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="h-8 w-32 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="h-28 rounded-lg bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      {/* Filters */}
      <div className="flex gap-4">
        <div className="h-10 w-64 rounded bg-gray-200 dark:bg-gray-700" />
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
