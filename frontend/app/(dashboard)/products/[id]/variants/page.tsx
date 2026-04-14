import type { Metadata } from 'next';
import { Suspense } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { VariantManagementView } from './VariantManagementView';

interface ProductVariantsPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: ProductVariantsPageProps): Promise<Metadata> {
  const { id } = await params;
  return {
    title: `Product ${id} Variants`,
    description: 'Manage product variants, options, and pricing',
    robots: { index: false, follow: false },
  };
}

function VariantsSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-4 w-32" />
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-36" />
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-20 rounded-lg" />
        ))}
      </div>
      <Skeleton className="h-96 w-full rounded-lg" />
    </div>
  );
}

export default async function ProductVariantsPage({ params }: ProductVariantsPageProps) {
  const { id } = await params;

  return (
    <Suspense fallback={<VariantsSkeleton />}>
      <VariantManagementView productId={id} />
    </Suspense>
  );
}
}
