'use client';

import { useEffect } from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

interface ProductsErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ProductsError({ error, reset }: ProductsErrorProps) {
  useEffect(() => {
    console.error('Products error:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center px-4 py-16">
      <AlertTriangle className="h-12 w-12 text-red-500" />
      <h2 className="mt-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
        Something went wrong
      </h2>
      <p className="mt-2 max-w-md text-center text-sm text-gray-500 dark:text-gray-400">
        An error occurred while loading the products page. Please try again or contact support if
        the problem persists.
      </p>
      {error.digest && (
        <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">Error ID: {error.digest}</p>
      )}
      <button
        onClick={reset}
        className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        <RotateCcw className="h-4 w-4" />
        Try Again
      </button>
    </div>
  );
}
