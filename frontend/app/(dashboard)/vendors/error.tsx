'use client';

import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function VendorsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4" role="alert">
      <AlertTriangle className="h-12 w-12 text-red-500" />
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Something went wrong
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        {error.message || 'Failed to load vendors data.'}
      </p>
      <Button onClick={reset} variant="outline">
        Try again
      </Button>
    </div>
  );
}
