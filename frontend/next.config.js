import bundleAnalyzer from '@next/bundle-analyzer';

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
  openAnalyzer: true,
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  // ── Basic Settings ────────────────────────────────────────────
  reactStrictMode: true,
  poweredByHeader: false,
  output: 'standalone',
  compress: true,
  trailingSlash: false,
  productionBrowserSourceMaps: false,

  // ── Environment Variables ─────────────────────────────────────
  // Only NEXT_PUBLIC_ variables are exposed to the client bundle.
  // Server-only variables (NEXTAUTH_SECRET, API_BASE_URL, etc.)
  // are NOT included — validated at runtime via lib/env.ts.
  env: {
    NEXT_PUBLIC_SITE_NAME: process.env.NEXT_PUBLIC_SITE_NAME || 'LankaCommerce Cloud',
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'LCC',
    NEXT_PUBLIC_DEFAULT_CURRENCY: process.env.NEXT_PUBLIC_DEFAULT_CURRENCY || 'LKR',
    NEXT_PUBLIC_DEFAULT_TIMEZONE: process.env.NEXT_PUBLIC_DEFAULT_TIMEZONE || 'Asia/Colombo',
    NEXT_PUBLIC_DEFAULT_LOCALE: process.env.NEXT_PUBLIC_DEFAULT_LOCALE || 'en-LK',
  },

  // ── TypeScript ────────────────────────────────────────────────
  typescript: {
    ignoreBuildErrors: false,
    tsconfigPath: './tsconfig.json',
  },

  // ── Images ────────────────────────────────────────────────────
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
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
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
        port: '',
        pathname: '/**',
      },
    ],
  },

  // ── Server External Packages (moved from experimental) ───────
  serverExternalPackages: ['bcryptjs', 'sharp'],

  // ── Typed Routes (moved from experimental) ────────────────────
  typedRoutes: true,

  // ── Experimental ──────────────────────────────────────────────
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000', 'app.lankacommerce.cloud'],
      bodySizeLimit: '2mb',
    },
  },

  // ── On-Demand Entries (Dev Performance) ───────────────────────
  onDemandEntries: {
    maxInactiveAge: 60 * 1000,
    pagesBufferLength: 5,
  },

  // ── Security Headers ──────────────────────────────────────────
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-DNS-Prefetch-Control', value: 'on' },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Download-Options', value: 'noopen' },
          { key: 'X-Permitted-Cross-Domain-Policies', value: 'none' },
          { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
          },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
              "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
              "img-src 'self' data: https: http://localhost:*",
              "font-src 'self' data: https://cdn.jsdelivr.net",
              "connect-src 'self' http://localhost:* https://api.lankacommerce.lk https://*.lankacommerce.lk",
              "frame-ancestors 'self'",
            ].join('; '),
          },
        ],
      },
      {
        source: '/api/:path*',
        headers: [{ key: 'X-Content-Type-Options', value: 'nosniff' }],
      },
    ];
  },

  // ── Redirects ─────────────────────────────────────────────────
  async redirects() {
    return [
      // Trailing slash normalization
      {
        source: '/:path+/',
        destination: '/:path+',
        permanent: true,
      },
      // www to non-www
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.lankacommerce.lk' }],
        destination: 'https://lankacommerce.lk/:path*',
        permanent: true,
      },
      // Legacy admin → dashboard
      {
        source: '/admin/:path*',
        destination: '/dashboard/:path*',
        permanent: true,
      },
      // Auth shortcuts (removed — (auth) route group handles /login, /register, /logout directly)
      // Convenience shortcuts
      {
        source: '/docs',
        destination: '/documentation',
        permanent: true,
      },
      {
        source: '/help',
        destination: '/support/faq',
        permanent: true,
      },
      // HTTPS enforcement
      {
        source: '/:path*',
        has: [{ type: 'header', key: 'x-forwarded-proto', value: 'http' }],
        destination: 'https://:host/:path*',
        permanent: true,
      },
    ];
  },

  // ── Webpack: Vendor & Common Chunk Splitting (Task 44/45) ─────
  webpack(config, { isServer }) {
    if (!isServer) {
      config.optimization = config.optimization || {};
      config.optimization.splitChunks = {
        chunks: 'all',
        minSize: 20_000,
        maxSize: 244_000,
        minChunks: 1,
        maxAsyncRequests: 30,
        maxInitialRequests: 30,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/](react|react-dom|next|@tanstack)[\\/]/,
            name: 'vendor',
            chunks: 'all',
            priority: 20,
            reuseExistingChunk: true,
          },
          ui: {
            test: /[\\/]node_modules[\\/](@radix-ui|lucide-react|class-variance-authority|clsx)[\\/]/,
            name: 'ui-vendor',
            chunks: 'all',
            priority: 15,
            reuseExistingChunk: true,
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true,
          },
        },
      };
    }
    return config;
  },
};

export default withBundleAnalyzer(nextConfig);
