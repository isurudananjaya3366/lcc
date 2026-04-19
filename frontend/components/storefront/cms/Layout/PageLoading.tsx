'use client';

import { Skeleton } from '@/components/ui/skeleton';

export function PageLoading() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-10 w-3/4" />
      <div className="space-y-4 mt-8">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    </div>
  );
}
