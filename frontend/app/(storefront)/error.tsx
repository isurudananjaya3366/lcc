'use client';

import { useEffect } from 'react';

/**
 * Storefront error boundary — catches runtime errors and offers retry.
 */
export default function StorefrontError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Storefront error:', error);
  }, [error]);

  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <div className="max-w-md mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Something went wrong</h2>
        <p className="text-gray-600 mb-6">
          We&apos;re sorry, but something unexpected happened. Please try again or return to the
          homepage.
        </p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={reset}
            className="rounded-lg bg-green-600 px-6 py-2 text-white font-medium hover:bg-green-700 transition-colors"
          >
            Try Again
          </button>
          <a
            href="/"
            className="rounded-lg border border-gray-300 px-6 py-2 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Go Home
          </a>
        </div>
      </div>
    </div>
  );
}
