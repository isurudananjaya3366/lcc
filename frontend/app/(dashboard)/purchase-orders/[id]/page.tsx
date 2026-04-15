import { Suspense } from 'react';
import { PODetails } from '@/components/modules/crm/PurchaseOrders/PODetails';
import { createCRMMetadata } from '@/lib/metadata/crm';

export const metadata = createCRMMetadata(
  'Purchase Order Details',
  'View purchase order details and receiving status'
);

interface PODetailsPageProps {
  params: Promise<{ id: string }>;
}

export default async function PODetailsPage({ params }: PODetailsPageProps) {
  const { id } = await params;
  return (
    <Suspense fallback={<PODetailsSkeleton />}>
      <PODetails poId={id} />
    </Suspense>
  );
}

function PODetailsSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center gap-4">
        <div className="h-8 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-6 w-20 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="h-16 rounded-lg bg-gray-200 dark:bg-gray-700" />
      <div className="h-64 rounded-lg bg-gray-200 dark:bg-gray-700" />
    </div>
  );
}
