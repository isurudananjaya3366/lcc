import type { Metadata } from 'next';
import { Suspense } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { EditCategoryForm } from './EditCategoryForm';

interface CategoryEditPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: CategoryEditPageProps): Promise<Metadata> {
  const { id } = await params;
  // TODO: Fetch category name from API
  return {
    title: `Edit Category ${id}`,
    description: 'Edit product category details',
    robots: { index: false, follow: false },
  };
}

function EditCategorySkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-4 w-40 rounded bg-muted" />
      <div className="h-7 w-48 rounded bg-muted" />
      <div className="h-64 rounded-lg bg-muted" />
      <div className="h-40 rounded-lg bg-muted" />
      <div className="h-40 rounded-lg bg-muted" />
    </div>
  );
}

export default async function CategoryEditPage({ params }: CategoryEditPageProps) {
  const { id } = await params;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/products/categories"
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Categories
        </Link>
      </div>

      <h2 className="text-xl font-semibold">Edit Category</h2>

      <Suspense fallback={<EditCategorySkeleton />}>
        <EditCategoryForm categoryId={id} />
      </Suspense>
    </div>
  );
}
