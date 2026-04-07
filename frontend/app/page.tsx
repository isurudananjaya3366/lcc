export default function HomePage() {
  return (
    <main
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        fontFamily: 'var(--font-inter), system-ui, sans-serif',
      }}
    >
      <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
        LankaCommerce Cloud
      </h1>
      <p
        style={{
          fontSize: '1.25rem',
          color: '#666',
          marginBottom: '2rem',
        }}
      >
        Multi-tenant ERP Platform for Sri Lankan SMEs
      </p>

      <nav style={{ display: 'flex', gap: '1.5rem' }}>
        {/* TODO: Replace with actual links when routes are created */}
        <span style={{ color: '#999' }}>ERP Dashboard</span>
        <span style={{ color: '#999' }}>Webstore</span>
        <span style={{ color: '#999' }}>Admin Panel</span>
      </nav>
    </main>
  );
}
