'use client';

import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function QuoteDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4" role="alert">
      <AlertTriangle className="h-12 w-12 text-red-500" />
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Quote not found</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        {error.message || 'Failed to load quote details.'}
      </p>
      <div className="flex gap-3">
        <Button onClick={reset} variant="outline">
          Try again
        </Button>
        <Link href="/quotes">
          <Button variant="ghost">Back to Quotes</Button>
        </Link>
      </div>
    </div>
  );
}
