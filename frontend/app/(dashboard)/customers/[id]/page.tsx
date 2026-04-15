import { Suspense } from 'react';
import { CustomerDetails } from '@/components/modules/crm/Customers/CustomerDetails';
import { createCRMMetadata } from '@/lib/metadata/crm';

export const metadata = createCRMMetadata(
  'Customer Details',
  'View detailed customer information and 360-degree profile'
);

interface CustomerDetailsPageProps {
  params: Promise<{ id: string }>;
}

export default async function CustomerDetailsPage({ params }: CustomerDetailsPageProps) {
  const { id } = await params;
  return (
    <Suspense fallback={<CustomerDetailsSkeleton />}>
      <CustomerDetails customerId={id} />
    </Suspense>
  );
}

function CustomerDetailsSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center gap-4">
        <div className="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700" />
        <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="grid grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 rounded-lg bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      <div className="h-64 rounded-lg bg-gray-200 dark:bg-gray-700" />
    </div>
  );
}
