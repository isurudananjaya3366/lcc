/** @type {import('next').NextConfig} */
const nextConfig = {
  // ── Basic Settings ────────────────────────────────────────────
  reactStrictMode: true,
  poweredByHeader: false,
  output: 'standalone',

  // ── Environment Variables ─────────────────────────────────────
  // Only NEXT_PUBLIC_ variables are exposed to the client bundle.
  // Server-only variables (NEXTAUTH_SECRET, API_BASE_URL, etc.)
  // are NOT included — validated at runtime via lib/env.ts.
  env: {
    NEXT_PUBLIC_SITE_NAME:
      process.env.NEXT_PUBLIC_SITE_NAME || 'LankaCommerce Cloud',
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'LCC',
    NEXT_PUBLIC_DEFAULT_CURRENCY:
      process.env.NEXT_PUBLIC_DEFAULT_CURRENCY || 'LKR',
    NEXT_PUBLIC_DEFAULT_TIMEZONE:
      process.env.NEXT_PUBLIC_DEFAULT_TIMEZONE || 'Asia/Colombo',
    NEXT_PUBLIC_DEFAULT_LOCALE:
      process.env.NEXT_PUBLIC_DEFAULT_LOCALE || 'en-LK',
  },

  // ── TypeScript ────────────────────────────────────────────────
  typescript: {
    ignoreBuildErrors: false,
  },

  // ── Images ────────────────────────────────────────────────────
  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '*.lankacommerce.lk',
        port: '',
        pathname: '/images/**',
      },
      {
        protocol: 'https',
        hostname: 'cdn.lankacommerce.lk',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
        port: '',
        pathname: '/**',
      },
    ],
  },

  // ── Server External Packages (moved from experimental) ───────
  serverExternalPackages: ['bcryptjs', 'sharp'],

  // ── Typed Routes (moved from experimental) ────────────────────
  typedRoutes: true,
};

export default nextConfig;
