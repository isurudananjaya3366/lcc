import { Suspense } from 'react';
import { VendorDetails } from '@/components/modules/crm/Vendors/VendorDetails';
import { createCRMMetadata } from '@/lib/metadata/crm';

export const metadata = createCRMMetadata(
  'Vendor Details',
  'View vendor details and purchase history'
);

interface VendorDetailsPageProps {
  params: Promise<{ id: string }>;
}

export default async function VendorDetailsPage({ params }: VendorDetailsPageProps) {
  const { id } = await params;
  return (
    <Suspense fallback={<VendorDetailsSkeleton />}>
      <VendorDetails vendorId={id} />
    </Suspense>
  );
}

function VendorDetailsSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center gap-4">
        <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-6 w-20 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="h-64 rounded-lg bg-gray-200 dark:bg-gray-700" />
    </div>
  );
}
