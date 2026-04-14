import type { Metadata } from 'next';
import { Suspense } from 'react';
import { InvoicesList } from '@/components/modules/sales/Invoices/InvoicesList';

export const metadata: Metadata = {
  title: 'Invoices - LCC',
  description: 'View and manage all invoices',
  openGraph: {
    title: 'Invoices - LCC',
    description: 'View and manage all invoices',
    type: 'website',
  },
};

export default function InvoicesPage() {
  return (
    <Suspense fallback={<InvoicesListSkeleton />}>
      <InvoicesList />
    </Suspense>
  );
}

function InvoicesListSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 rounded-lg bg-gray-200 dark:bg-gray-700" />
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
