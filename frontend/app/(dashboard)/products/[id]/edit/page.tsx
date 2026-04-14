import type { Metadata } from 'next';
import { Suspense } from 'react';
import { EditProductForm } from './EditProductForm';
import { Skeleton } from '@/components/ui/skeleton';

interface ProductEditPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: ProductEditPageProps): Promise<Metadata> {
  const { id } = await params;
  // TODO: Fetch product name from API
  return {
    title: `Edit Product ${id}`,
    description: 'Edit product details, pricing, and inventory',
    robots: { index: false, follow: false },
  };
}

function EditProductSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-96 w-full rounded-lg" />
      <Skeleton className="h-64 w-full rounded-lg" />
      <Skeleton className="h-48 w-full rounded-lg" />
    </div>
  );
}

export default async function ProductEditPage({ params }: ProductEditPageProps) {
  const { id } = await params;

  return (
    <Suspense fallback={<EditProductSkeleton />}>
      <EditProductForm productId={id} />
    </Suspense>
  );
}
