import type { Metadata } from 'next';
import { Suspense } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { CreateCategoryForm } from './CreateCategoryForm';

export const metadata: Metadata = {
  title: 'Create Category',
  description: 'Create a new product category',
  robots: { index: false, follow: false },
};

function CreateCategorySkeleton() {
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

export default function CategoryCreatePage() {
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

      <h2 className="text-xl font-semibold">Create Category</h2>

      <Suspense fallback={<CreateCategorySkeleton />}>
        <CreateCategoryForm />
      </Suspense>
    </div>
  );
}
