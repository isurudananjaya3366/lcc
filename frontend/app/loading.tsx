'use client';

/**
 * Root-level loading component.
 * Displayed by Next.js while navigating between routes.
 */
export default function Loading() {
  return (
    <div
      className="flex min-h-screen flex-col items-center justify-center"
      role="status"
      aria-live="polite"
      aria-label="Loading page content"
    >
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-500" />
      <p className="mt-4 text-sm text-gray-500">Loading...</p>
      <span className="sr-only">Loading page content...</span>
    </div>
  );
}
