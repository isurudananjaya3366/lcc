import Link from 'next/link';

export default function NotFound() {
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
      <h1 style={{ fontSize: '6rem', fontWeight: 700, margin: 0 }}>404</h1>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
        Page Not Found
      </h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        The page you&apos;re looking for doesn&apos;t exist.
      </p>
      <Link
        href="/"
        style={{
          padding: '0.625rem 1.25rem',
          fontSize: '1rem',
          backgroundColor: '#0070f3',
          color: '#fff',
          textDecoration: 'none',
          borderRadius: '0.375rem',
        }}
      >
        Return to Home
      </Link>
    </div>
  );
}
