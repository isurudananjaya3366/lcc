import type { Metadata } from 'next';
import { Suspense } from 'react';
import { QuotesList } from '@/components/modules/sales/Quotes/QuotesList';

export const metadata: Metadata = {
  title: 'Quotes - LCC',
  description: 'Manage sales quotes and proposals',
  openGraph: {
    title: 'Quotes - LCC',
    description: 'Manage sales quotes and proposals',
    type: 'website',
  },
};

export default function QuotesPage() {
  return (
    <Suspense fallback={<QuotesListSkeleton />}>
      <QuotesList />
    </Suspense>
  );
}

function QuotesListSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
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
