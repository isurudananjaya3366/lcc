'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface POSErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function POSError({ error, reset }: POSErrorProps) {
  const router = useRouter();

  useEffect(() => {
    console.error('POS Terminal Error:', error);
  }, [error]);

  return (
    <div
      className="flex h-screen w-screen flex-col items-center justify-center bg-gray-100 dark:bg-gray-950"
      role="alert"
    >
      <div className="mx-auto max-w-md text-center">
        <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
        <h2 className="mt-4 text-xl font-semibold text-gray-900 dark:text-gray-100">
          Something went wrong
        </h2>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          The POS terminal encountered an unexpected error. Your cart data has been preserved.
        </p>
        {process.env.NODE_ENV === 'development' && (
          <p className="mt-2 rounded bg-gray-200 p-2 text-xs text-gray-500 dark:bg-gray-800">
            {error.message}
          </p>
        )}
        <div className="mt-6 flex items-center justify-center gap-3">
          <Button onClick={reset} variant="default">
            Try Again
          </Button>
          <Button onClick={() => router.push('/dashboard')} variant="outline">
            Return to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
