'use client';

import Link from 'next/link';
import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div
      className="flex min-h-screen flex-col items-center justify-center font-[family-name:var(--font-inter)]"
      role="alert"
      aria-live="assertive"
    >
      <div className="mb-4 text-5xl">⚠️</div>
      <h2 className="mb-2 text-2xl font-semibold">Something Went Wrong</h2>
      <p className="mb-6 text-gray-500">
        An unexpected error has occurred. Please try again.
      </p>
      <div className="flex gap-3">
        <button
          onClick={() => reset()}
          className="rounded-md bg-blue-600 px-5 py-2.5 text-white hover:bg-blue-700"
        >
          Try Again
        </button>
        <Link
          href="/"
          className="rounded-md border border-gray-300 px-5 py-2.5 text-gray-700 hover:bg-gray-50"
        >
          Go Home
        </Link>
      </div>
      {process.env.NODE_ENV === 'development' && error.digest && (
        <p className="mt-4 text-sm text-gray-400">Digest: {error.digest}</p>
      )}
    </div>
  );
}
