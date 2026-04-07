'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service in production
    console.error(error);
  }, [error]);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        fontFamily: 'var(--font-inter), system-ui, sans-serif',
      }}
    >
      <h2 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>
        Something went wrong!
      </h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        An unexpected error has occurred. Please try again.
      </p>
      <button
        onClick={() => reset()}
        style={{
          padding: '0.625rem 1.25rem',
          fontSize: '1rem',
          cursor: 'pointer',
          backgroundColor: '#0070f3',
          color: '#fff',
          border: 'none',
          borderRadius: '0.375rem',
        }}
      >
        Try Again
      </button>
      {process.env.NODE_ENV === 'development' && error.digest && (
        <p style={{ color: '#999', marginTop: '1rem', fontSize: '0.875rem' }}>
          Digest: {error.digest}
        </p>
      )}
    </div>
  );
}
