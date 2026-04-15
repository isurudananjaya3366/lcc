'use client';

import { useRouter } from 'next/navigation';
import { Skeleton } from '@/components/ui/skeleton';
import { useVendor, useDeleteVendor } from '@/hooks/crm/useVendors';
import { VendorHeader } from './VendorProfile/VendorHeader';
import { VendorTabs } from './VendorProfile/VendorTabs';

interface VendorDetailsProps {
  vendorId: string;
}

export function VendorDetails({ vendorId }: VendorDetailsProps) {
  const router = useRouter();
  const { data, isLoading, isError } = useVendor(vendorId);
  const deleteVendor = useDeleteVendor();

  const vendor = data?.data;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (isError || !vendor) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <h2 className="text-lg font-medium">Vendor not found</h2>
        <p className="text-sm text-muted-foreground">
          The vendor you&apos;re looking for doesn&apos;t exist or has been removed.
        </p>
      </div>
    );
  }

  function handleDelete() {
    if (!vendor) return;
    deleteVendor.mutate(vendor.id, {
      onSuccess: () => router.push('/vendors'),
    });
  }

  return (
    <div className="space-y-6">
      <VendorHeader
        vendor={vendor}
        onEdit={() => router.push(`/vendors/${vendorId}?edit=true`)}
        onDelete={handleDelete}
      />
      <VendorTabs vendorId={vendorId} vendor={vendor} />
    </div>
  );
}
