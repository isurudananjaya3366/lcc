import type { Metadata } from 'next';
import { Suspense } from 'react';
import { CategoryListView } from './CategoryListView';

export const metadata: Metadata = {
  title: 'Categories',
  description: 'Manage product categories and organize your catalog',
};

function CategoriesSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-6 w-32 rounded bg-muted" />
          <div className="h-4 w-56 rounded bg-muted" />
        </div>
        <div className="h-10 w-36 rounded bg-muted" />
      </div>
      <div className="flex gap-3">
        <div className="h-10 flex-1 rounded bg-muted" />
        <div className="h-10 w-[140px] rounded bg-muted" />
      </div>
      <div className="h-64 rounded-lg bg-muted" />
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="h-24 rounded-lg bg-muted" />
        <div className="h-24 rounded-lg bg-muted" />
        <div className="h-24 rounded-lg bg-muted" />
      </div>
    </div>
  );
}

export default function CategoriesPage() {
  return (
    <Suspense fallback={<CategoriesSkeleton />}>
      <CategoryListView />
    </Suspense>
  );
}
